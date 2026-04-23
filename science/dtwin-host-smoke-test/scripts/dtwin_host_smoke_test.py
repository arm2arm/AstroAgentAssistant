#!/usr/bin/env python3
"""Host-side smoke test for the dt4acc digital twin stack.

This script validates the currently checked-out local repos under a dtwin root,
without requiring MongoDB, TANGO, or Apptainer.
"""

from __future__ import annotations

import asyncio
import json
import math
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import at
from dt4acc.core.bl.translating_command_execution_engine import (
    TranslatingCommandExecutionEngine,
)
from dt4acc.custom_facility.bessyii.liasion_translator_setup import load_managers
from dt4acc_lib.bl.command_rewritter import CommandRewriter
from dt4acc_lib.model.utils.command import BehaviourOnError, Command
from dt4acc_lib.pyat_simulator.accelerator_simulator import PyATAcceleratorSimulator
from dt4acc_lib.pyat_simulator.simulator_backend import SimulatorBackend
from lat2db.tools.factories.pyat import factory


@dataclass
class SmokeResult:
    repo_root: str
    lattice_json: str
    lattice_elements: int
    closed_orbit_points: int
    quadrupole: str
    translated_device: str
    translated_property: str
    translated_targets_count: int
    baseline_strength: float
    perturbed_strength: float
    restored_strength: float
    baseline_tune_x: float
    baseline_tune_y: float
    perturbed_tune_x: float
    perturbed_tune_y: float
    restored_tune_x: float
    restored_tune_y: float
    delta_tune_x: float
    delta_tune_y: float
    restore_delta_x: float
    restore_delta_y: float
    track_points: int
    twiss_points: int
    success: bool


def _tune_pair(tune_obj: Any) -> tuple[float, float]:
    return float(tune_obj.x), float(tune_obj.y)


def _resolve_repo_root() -> Path:
    if len(sys.argv) > 1:
        root = Path(sys.argv[1]).expanduser().resolve()
    else:
        root = Path("/tmp/dtwin-build").resolve()
    required = [root / "dt4acc", root / "dt4acc-lib", root / "lat2db"]
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        raise SystemExit(f"Missing required repo paths under {root}: {missing}")
    return root


def _build_ring(repo_root: Path) -> tuple[at.Lattice, Path]:
    lattice_json = (
        repo_root
        / "dt4acc"
        / "src"
        / "dt4acc"
        / "custom_facility"
        / "bessyii"
        / "resources"
        / "storage_ring"
        / "input"
        / "bessy2_storage_ring_reflat.json"
    )
    if not lattice_json.exists():
        raise FileNotFoundError(f"Lattice JSON not found: {lattice_json}")

    with lattice_json.open("rt") as fp:
        payload = json.load(fp)

    seq = factory(payload, energy=1.7185e9)
    ring = at.Lattice(seq, name="BESSY II storage ring", energy=1.7185e9)
    ring.enable_6d()
    ring.cavpts = "CAV*"
    ring.set_cavity_phase(cavpts=ring.cavpts)
    return ring, lattice_json


async def _run(repo_root: Path) -> SmokeResult:
    ring, lattice_json = _build_ring(repo_root)
    backend = SimulatorBackend(
        name="dtwin-host-smoke-test",
        acc=PyATAcceleratorSimulator(at_lattice=ring),
    )

    tune0 = await backend.read("tune", "transversal")
    track0 = await backend.read("track", "pos")
    twiss0 = await backend.read("twiss", "parameters")

    _, liaison_manager, translation_service = load_managers()
    rewriter = CommandRewriter(
        liaison_manager=liaison_manager,
        translation_service=translation_service,
    )
    mexec = TranslatingCommandExecutionEngine(
        backend=backend,
        cmd_rewriter=rewriter,
        expected_view_for_output="device",
        num_readings=1,
    )

    quadrupole = "Q1M2D1R"
    baseline_strength = float(await backend.read(quadrupole, "main_strength"))

    translated = rewriter.forward(
        Command(
            id=quadrupole,
            property="main_strength",
            value=baseline_strength,
            behaviour_on_error=BehaviourOnError.stop,
        )
    )
    device_cmd = next(cmd for cmd in translated if cmd.property == "set_current")

    perturbed_device_cmd = Command(
        id=device_cmd.id,
        property=device_cmd.property,
        value=float(device_cmd.value) + 0.01,
        behaviour_on_error=BehaviourOnError.stop,
    )
    inverse_targets = rewriter.inverse(perturbed_device_cmd)

    await mexec.set([perturbed_device_cmd])
    tune1 = await backend.read("tune", "transversal")
    strength1 = float(await backend.read(quadrupole, "main_strength"))

    await mexec.set([device_cmd])
    tune2 = await backend.read("tune", "transversal")
    strength2 = float(await backend.read(quadrupole, "main_strength"))

    tune0x, tune0y = _tune_pair(tune0)
    tune1x, tune1y = _tune_pair(tune1)
    tune2x, tune2y = _tune_pair(tune2)

    delta_tune_x = tune1x - tune0x
    delta_tune_y = tune1y - tune0y
    restore_delta_x = tune2x - tune0x
    restore_delta_y = tune2y - tune0y

    success = all(
        [
            len(ring) > 100,
            len(track0.track) > 100,
            len(twiss0.twiss) > 100,
            len(inverse_targets) >= 1,
            math.isfinite(delta_tune_x),
            math.isfinite(delta_tune_y),
            abs(delta_tune_x) > 1e-6 or abs(delta_tune_y) > 1e-6,
            abs(strength1 - baseline_strength) > 1e-9,
            abs(strength2 - baseline_strength) < 1e-12,
            abs(restore_delta_x) < 1e-12,
            abs(restore_delta_y) < 1e-12,
        ]
    )

    return SmokeResult(
        repo_root=str(repo_root),
        lattice_json=str(lattice_json),
        lattice_elements=len(ring),
        closed_orbit_points=len(ring.get_optics(at.All)[2]["closed_orbit"]),
        quadrupole=quadrupole,
        translated_device=device_cmd.id,
        translated_property=device_cmd.property,
        translated_targets_count=len(inverse_targets),
        baseline_strength=baseline_strength,
        perturbed_strength=strength1,
        restored_strength=strength2,
        baseline_tune_x=tune0x,
        baseline_tune_y=tune0y,
        perturbed_tune_x=tune1x,
        perturbed_tune_y=tune1y,
        restored_tune_x=tune2x,
        restored_tune_y=tune2y,
        delta_tune_x=delta_tune_x,
        delta_tune_y=delta_tune_y,
        restore_delta_x=restore_delta_x,
        restore_delta_y=restore_delta_y,
        track_points=len(track0.track),
        twiss_points=len(twiss0.twiss),
        success=success,
    )


def main() -> int:
    repo_root = _resolve_repo_root()
    result = asyncio.run(_run(repo_root))
    results_path = repo_root / "dtwin_smoke_test_results.json"
    results_path.write_text(json.dumps(asdict(result), indent=2) + "\n")

    print("== dtwin host smoke test ==")
    print(f"repo_root: {result.repo_root}")
    print(f"lattice_json: {result.lattice_json}")
    print(f"lattice_elements: {result.lattice_elements}")
    print(f"track_points: {result.track_points}")
    print(f"twiss_points: {result.twiss_points}")
    print(f"quadrupole: {result.quadrupole}")
    print(
        f"device_translation: {result.translated_device}.{result.translated_property} -> {result.translated_targets_count} lattice target(s)"
    )
    print(
        f"tune: ({result.baseline_tune_x:.6f}, {result.baseline_tune_y:.6f}) -> ({result.perturbed_tune_x:.6f}, {result.perturbed_tune_y:.6f}) -> ({result.restored_tune_x:.6f}, {result.restored_tune_y:.6f})"
    )
    print(
        f"delta_tune: dx={result.delta_tune_x:.6e}, dy={result.delta_tune_y:.6e}; restore: dx={result.restore_delta_x:.6e}, dy={result.restore_delta_y:.6e}"
    )
    print(f"results_json: {results_path}")
    print(f"success: {result.success}")
    return 0 if result.success else 1


if __name__ == "__main__":
    raise SystemExit(main())
