# AstroAgent Skills Repository

Custom Hermes Agent skills developed by the AIP AstroAgent team. This repository intentionally keeps only project-specific/AIP-developed skills; stock Hermes skills and third-party vendor skills are excluded.

Total: **175** custom skills across **16** categories, plus **14** superseded skills retained in [`outdated-skills/`](outdated-skills/README.md).

> The inventory below is generated — run `python3 scripts/gen_readme.py` after changing skills instead of editing this file by hand.

## Repository layout

| Directory | Description | Skills |
|---|---|---|
| `agents/` | AstroAgent concepts and configuration | 1 |
| `astronomy/` | AIP-developed survey archives, TAP/ADQL and REST queries, stellar catalogs, and astronomy-specific plots/animations. See [`astronomy/README.md`](astronomy/README.md) for the grouped astronomy routing guide. | 24 |
| `autonomous-ai-agents/` | AIP-developed skills | 5 |
| `creative/` | AIP-developed educational animations, Manim, visual explainers, and media workflows | 15 |
| `data-science/` | AIP-developed scientific visualization and dense-data plotting workflows | 11 |
| `devops/` | AIP-developed operations, containers, deployment, service exposure, and runtime troubleshooting | 23 |
| `infrastructure/` | AIP-developed Hermes/OpenWebUI/API-server/MCP infrastructure, workspace backup, and integration workflows | 11 |
| `leisure/` | AIP-developed nearby places and leisure search workflows | 1 |
| `media/` | AIP-developed audio/video generation and media post-processing workflows | 2 |
| `mlops/` | AIP-developed local LLM serving, quantization, and inference workflows (vLLM, Ollama, GGUF) | 2 |
| `productivity/` | AIP-developed calendars, contacts, image-description, and document workflows | 5 |
| `python/` | AIP-developed Python data engineering, caching, plotting, symbolic math, and reusable scientific-programming workflows | 7 |
| `reana-workflows/` | AIP-developed REANA operations, client configuration, templates, execution recipes, monitoring, and workflow best practices | 21 |
| `research/` | AIP-developed academic research, literature, arXiv access, LaTeX manuscripts, DRP, Bayesian imaging (J-UBIK/NIFTy), and paper improvement workflows | 34 |
| `science/` | AIP-developed dt4acc digital twin, accelerator-science runbooks, EPICS/Tango, and host smoke tests | 7 |
| `software-development/` | AIP-developed coding workflows, docs-first development, and application-specific implementation guides | 6 |
| `outdated-skills/` | Superseded skills kept for provenance — see the [supersession map](outdated-skills/README.md). Not intended for new use. | 14 |

## Categories overview

**Agents (1)** — AstroAgent concepts and configuration

**Astronomy (24)** — AIP-developed survey archives, TAP/ADQL and REST queries, stellar catalogs, and astronomy-specific plots/animations

**Autonomous Ai Agents (5)** — AIP-developed skills

**Creative (15)** — AIP-developed educational animations, Manim, visual explainers, and media workflows

**Data Science (11)** — AIP-developed scientific visualization and dense-data plotting workflows

**Devops (23)** — AIP-developed operations, containers, deployment, service exposure, and runtime troubleshooting

**Infrastructure (11)** — AIP-developed Hermes/OpenWebUI/API-server/MCP infrastructure, workspace backup, and integration workflows

**Leisure (1)** — AIP-developed nearby places and leisure search workflows

**Media (2)** — AIP-developed audio/video generation and media post-processing workflows

**Mlops (2)** — AIP-developed local LLM serving, quantization, and inference workflows (vLLM, Ollama, GGUF)

**Productivity (5)** — AIP-developed calendars, contacts, image-description, and document workflows

**Python (7)** — AIP-developed Python data engineering, caching, plotting, symbolic math, and reusable scientific-programming workflows

**Reana Workflows (21)** — AIP-developed REANA operations, client configuration, templates, execution recipes, monitoring, and workflow best practices

**Research (34)** — AIP-developed academic research, literature, arXiv access, LaTeX manuscripts, DRP, Bayesian imaging (J-UBIK/NIFTy), and paper improvement workflows

**Science (7)** — AIP-developed dt4acc digital twin, accelerator-science runbooks, EPICS/Tango, and host smoke tests

**Software Development (6)** — AIP-developed coding workflows, docs-first development, and application-specific implementation guides

## Skills inventory

| Skill | Description |
|---|---|
| `agents/astroagent-concept/` | Use the AstroAgent concept framing for architecture, positioning, and design discussions. |
| `astronomy/arepo-simulations/` | Complete guide to working with Arepo simulation HDF5 files: structure inspection, unit conversion, radial profiles, slice projections, and dimensionality reduction (UMAP/t-SNE) for clustering analysis. |
| `astronomy/astro-catalog-plotting-cache/` | Use when turning astronomy catalog data into reproducible cached products and publication-ready plots, especially CMDs, RA/Dec maps, Galactic projections, hexbin density plots, Datashader outputs, and proven... |
| `astronomy/astro-data-access-umbrella/` | Use when an astronomy task needs data access and the agent must choose between TAP/ADQL/pyvo catalogs, Gaia@AIP REST/Daiquiri, S3/Parquet object storage, local StarHorse-style datasets, plotting/cache workfl... |
| `astronomy/astronomical-catalogs/` | Unified guide for querying major astronomical catalogs: Gaia DR3 (photometry, astrometry, cross-matches) and RAVE DR6 (radial velocities, spectroscopic parameters). Covers TAP querying via pyvo/curl, CSV/Par... |
| `astronomy/astronomy-analysis-project/` | Build reproducible Parquet astronomy analysis projects. |
| `astronomy/astronomy-research-umbrella/` | Umbrella for astronomy data workflows, TAP queries, simulation analysis, and domain-specific RAG/LLM patterns. |
| `astronomy/data-aip-de-s3/` | Work with data.aip.de and S3-backed datasets using reproducible local caching, Dask-first reads for huge data, and plotting workflows that scale to large astronomy catalogs. |
| `astronomy/drphub-cards/` | Manage DRP Hub Digital Research Products via the production REST API at drp-term.kube.aip.de/api/v1/. Supports full CRUD, clone, maturity, publish, audit, lineage, human-review, bookmarks, likes, sharing, an... |
| `astronomy/gaia-dr3-daiquiri-rest/` | FALLBACK Gaia access (prefer gaia-dr3-tap-query). Query Gaia DR3 at gaia.aip.de via its Daiquiri REST API for full-table COUNTs and very large async scans — CSRF handling, async jobs, queue names, JSON resul... |
| `astronomy/gaia-dr3-plot-with-dust/` | Retrieve nearby Gaia DR3 stars (via the AIP TAP service) and produce a two-panel research-paper figure — RA/Dec on the left, a Galactic XY projection overlaid with the SFD all-sky dust-extinction map on the... |
| `astronomy/gaia-dr3-tap-query/` | Query Gaia DR3 at gaia.aip.de via TAP/pyvo — the DEFAULT way to get Gaia data. ADQL queries, uniform random subsampling, Parquet caching, and ready-made sky / Galactic-XY plots. Access 1.8 billion sources. |
| `astronomy/rave-dr6-3d-animation/` | Step‑by‑step workflow to query the RAVE DR6 catalog for the 100 nearest stars (by parallax), process the data, generate 2‑D visualisations and a public‑talk‑ready 3‑D rotating animation using Matplotlib. |
| `astronomy/rave-dr6-3d-public-animation/` | Generate a public‑talk‑ready 3‑D animation of the 100 nearest RAVE DR6 stars using matplotlib. |
| `astronomy/rave-dr6-nearest-100-plot/` | Query the 100 nearest RAVE DR6 stars and generate two clear PNG plots: Galactic projection and RA/Dec scatter, with reproducible local parquet output. |
| `astronomy/rave-dr6-public-talk-visualizations/` | Turn a nearest-100 RAVE DR6 query into dark-theme, public-talk-ready PNG visualizations with clear titles, readable scaling, and presentation-friendly styling. |
| `astronomy/rave-dr6-recent-observations-plot/` | Retrieve the most recent 100 entries from the RAVE DR6 `dr6_obsdata` table and generate a simple RA‑Dec scatter plot. Handles missing Python dependencies, installs them if necessary, and falls back to astrop... |
| `astronomy/rave-dr6-shboost-distance-query/` | Query RAVE DR6 stars with SHboost24 distances via Gaia source_id crossmatch |
| `astronomy/rave-dr6-starhorse-access/` | Query RAVE DR6 via TAP and crossmatch with SHboost24 distances for nearby star analysis. |
| `astronomy/rave-dr6/` | Query the RAVE DR6 catalog at https://www.rave-survey.org/tap/ using pyvo (TAPService.run_sync). Access stellar parameters, Gaia cross-matches, distances, and Galactic coordinates (l, b). Includes galactic a... |
| `astronomy/scientific-sky-map/` | Generate all-sky and sky-region maps with custom physics models, celestial coordinate transformations, and projection rendering. Covers Mollweide, Aitoff, orthographic, hammer, and equirectangular projection... |
| `astronomy/sh26-plot-production/` | Use when producing SH26 paper figures and 50M Dask runs. |
| `astronomy/starhorse-access/` | Access StarHorse data products including SHboost-2024 and the SH21 EDR3 catalog via gaia.aip.de TAP. |
| `astronomy/stellar-catalog-comparison/` | Use when comparing matched stellar-catalog parameters. |
| `astronomy/tap-pyvo-adql-access/` | Use when querying astronomy TAP services with ADQL through pyvo or curl, including service probes, metadata discovery, TOP-based queries, VOTable/FITS conversion, pandas/Parquet caching, and robust network f... |
| `autonomous-ai-agents/coding-agent-troubleshooting/` | Use when Claude Code, Codex, or OpenCode fail to connect. |
| `autonomous-ai-agents/deepseek-harness-dsh/` | Use when running coding tasks via dsh (DeepSeek Harness). |
| `autonomous-ai-agents/external-coder-orchestration/` | Use when running multi-stage plans via external coding CLIs. |
| `autonomous-ai-agents/kanban-codex-lane/` | Use when a Hermes Kanban worker wants to run Codex CLI as an isolated implementation lane while Hermes keeps ownership of task lifecycle, reconciliation, testing, and handoff. |
| `autonomous-ai-agents/pi-coding-agent/` | Reusable Hermes skill: spawn a focused 'pi' coding subagent to run tests, implement fixes, and run reviewers using a safe, TDD-first workflow. |
| `creative/4most-spectrograph-animation/` | Manim CE animation explaining the 4MOST spectrograph for 11th-grade physics class. Full optical path from starlight through telescope, collimator, slit, dispersion element, fibre positioner, spectrographs, t... |
| `creative/animate-sine-cosine-matplotlib/` | Generate an MP4 animation of sine (green) and cosine (red) curves using matplotlib for frame rendering and ffmpeg for encoding. The skill avoids privileged operations and destructive commands. |
| `creative/blender-rendering/` | Headless Blender 5 rendering from Docker with Cycles CPU, material creation patterns, and S3 delivery. Use when rendering 3D scenes via Blender in container. |
| `creative/fourmost-educational-animation/` | Create a short Manim animation that explains the 4MOST spectrograph for 11th‑grade physics classes. Includes installation, script writing, rendering, common pitfalls, and fallback to external video. |
| `creative/fourmost-spectrograph-animation/` | Generates a 60-90s educational animation of the 4MOST spectrograph on the VISTA 4-m telescope using Manim Community Edition. Follows a schematic-first workflow: static matplotlib plot for review, then Manim... |
| `creative/fourmost-spectrograph-schematic/` | Generate a static schematic illustration of the 4MOST spectrograph system as a precursor to a full Manim animation. |
| `creative/fractal-edm-showcase/` | Automated workflow to generate a short fractal showcase video with a synthetic fast‑paced EDM soundtrack, including Seahorse and Elephant valley visual elements. |
| `creative/fractal-showcase-animation/` | Generate a short Manim video showcasing famous fractals (Mandelbrot set, Sierpinski triangle, Barnsley fern, Barnsley elephant) and add a simple background music track. The process includes on‑the‑fly genera... |
| `creative/fractals-edm-showcase/` | Create a high‑energy fractal showcase video with a synthetic EDM soundtrack, including custom Seahorse and Elephant‑jet visuals, a slow zoom, and final audio‑video merge. |
| `creative/galaxy-formation-animation/` | Create a concise Manim animation explaining galaxy formation for 11th‑grade students. Includes best‑practice steps, common pitfalls, and reusable code snippets. |
| `creative/manim-020-gotchas/` | Gotchas and API changes specific to Manim Community Edition 0.20.1. Includes ImageMobject, animation names, and font handling. |
| `creative/manim-educational-animation/` | Creating clean, non-overlapping Manim animations for educational explainers (Gymnasium/school level). Avoids text overlap bugs, guides pacing, and structures single-scene vs multi-scene approaches. |
| `creative/manim-tts-narration/` | Add German TTS narration to Manim educational videos using espeak-ng. Handles scene-by-scene audio generation, duration management, and merging with video. |
| `creative/plot-sine-cosine-matplotlib/` | Generate a PNG plot of sin(x) in red and cos(x) in green using matplotlib, handling missing dependencies in a managed Python environment. |
| `creative/sin-unit-circle-animation/` | Create animations showing the Unit Circle → Sine Wave connection. Uses ValueTracker + always_redraw for smooth rotating point that traces out the sine wave. Perfect for educational content (11th grade math,... |
| `data-science/data-visualization-umbrella/` | Umbrella for large-data visualization, Datashader, Dask, Matplotlib patterns, and reproducible plotting workflows. Consolidates shboost, datashader, dask-large-parquet-joins, matplotlib-figs, and related plo... |
| `data-science/datashader-019-pipeline/` | Generate density plots (CMD, hexbin, 2D histograms) using datashader 0.19.0 with Dask for lazy data loading and matplotlib for final rendering. Handles the 0.19.0 API: no Canvas.hexbin(), no tf.to_rgba(), tf... |
| `data-science/jupyter-live-kernel/` | Iterative Python via live Jupyter kernel (hamelnb). |
| `data-science/matplotlib-pitfalls/` | Common matplotlib gotchas that silently produce wrong output — hexbin+log+inverted-axis blank plots, LogNorm usage, notebook cell source joining pitfalls. |
| `data-science/memory-bounded-parquet-analysis/` | Use Dask for large Parquet data safely. |
| `data-science/notebook-plot-migration/` | Migrate plots from older analysis notebooks into a consolidated target notebook, converting from hvplot/holoviews to matplotlib. |
| `data-science/numpy-3d-raycaster/` | NumPy raycaster for 3D equirectangular video frames. |
| `data-science/physics-chaos-sim/` | Interactive physics & chaos simulations as single-file HTML/JS apps. Covers double pendulum, coupled oscillators, N-body gravity, fluid dynamics, Ising model, reaction-diffusion, and more. |
| `data-science/scientific-figure-production-qa/` | Use for large-catalog scientific figure QA. |
| `data-science/sh26-data-sampling/` | Use when sampling or refreshing the ~5M row SH26 dataset. |
| `data-science/starhorse-plots/` | Class-level plotting skill for working with StarHorse outputs (SH/SH26). Encodes preferred plot types, axis ranges, column conventions, and reproducible notebook patches used across sessions. Designed to be... |
| `devops/api-server-local-image-support/` | Fix Open WebUI image display by extending api_server.py to convert standard markdown ![alt](/local/path) images into HTTP URLs via /media/<path> route. Handles the gap between agent-generated image paths and... |
| `devops/docker-access-group-reload/` | Resolve Docker permission errors by ensuring the user is in the docker group and reloading group membership. |
| `devops/docker-access/` | Verify Docker availability and run containers on this host. |
| `devops/kanban-worker/` | Complete guide to the Hermes Kanban system: the orchestrator decomposition playbook, specialist roster conventions, anti-temptation rules, and the deeper worker pitfalls, examples, and edge cases. The core l... |
| `devops/manim-headless-rendering/` | Guidelines for rendering Manim animations in a headless Linux environment (no GUI). Includes troubleshooting common errors, choosing correct renderer, managing long renders, and concatenating partial video f... |
| `devops/manim-telegram-animation/` | Guide to creating concise educational animations with Manim, handling common errors, rendering in low‑resolution, and delivering the final MP4 via Telegram (including ffmpeg concat handling). |
| `devops/manim-telegram-delivery/` | Generate a Manim animation, extract a short preview, concatenate full‑resolution fragments, and deliver the MP4 directly via Telegram. Handles common rendering pitfalls (partial movie files, missing renderer... |
| `devops/manim-video-audio/` | Add audio to Manim-rendered videos — background music, TTS narration, or SRT subtitles. Handles common pitfalls with MP3 decoding, volume mixing, and timing. |
| `devops/paperclip-oss120b-external/` | Step‑by‑step guide for turning a fresh Paperclip installation into a publicly reachable service that forwards LLM calls to a custom OSS‑120B model served via an OpenAI‑compatible endpoint. Handles deployment... |
| `devops/run-on-newton/` | Use when you want the agent to run, manage, and fetch SLURM jobs on the Newton cluster (141.33.4.144) using the enforced workdir /lustre/<user>/hermes. |
| `devops/s3-benchmarking/` | Benchmark read/write performance of S3-compatible storage endpoints (MinIO, VersityGW, rustfs). |
| `devops/s3-minio-utilities/` | General-purpose utilities for S3-compatible storage (MinIO, rustfs, Ceph, AWS S3). Covers endpoint testing via boto3, mc CLI troubleshooting, and recursive project upload/download workflows. Use when accessi... |
| `devops/s3-storage-benchmark/` | Run comprehensive S3-compatible storage benchmarks — read speed comparison, synthetic write/read across object sizes (1KB, 1MB, 1GB), with automated plot generation and cleanup. |
| `devops/s3-storage/` | S3/MinIO operations: connectivity, transfers, read benchmarks, and matplotlib visualization templates. |
| `devops/slurm-workflow-management/` | Manage SLURM cluster access, submit jobs, monitor runs, and collect outputs reproducibly. |
| `devops/telegram-auth-troubleshooting/` | Diagnose and fix cases where the Hermes Telegram bot silently ignores messages from group members (auth allowlist issues). |
| `devops/tencentdb-agent-memory-integration/` | TencentDB deploy, asset creation, and Hermes proxy wiring. |
| `devops/webxr-deployment/` | Deploy WebXR apps via Docker, nginx, and HAProxy. |
| `devops/webxr-dev/` | Build WebXR portals and AR/VR browser apps in Three.js. |
| `devops/webxr-experience/` | Build WebXR portal doors. Use when creating portal doors. |
| `devops/webxr-hit-test-pitfalls/` | Debug hit-test failures and placement marker issues. |
| `devops/webxr-portal/` | Build WebXR portal AR apps for 3D browser portals. |
| `devops/workstation-security-audit/` | Read-only audit and hardening for GPU research workstations. |
| `infrastructure/api-server-media-display/` | Diagnose and fix images not displaying in Open WebUI / API server frontends. |
| `infrastructure/docs-mcp-at-aip/` | Access the AIP documentation MCP server at https://docs-mcp-server.kube.aip.de. Search, scrape, and fetch documentation for 15+ indexed libraries including reana, pandas, snakemake, dask, unsloth, and more.... |
| `infrastructure/hermes-api-server/` | Enable and expose the Hermes OpenAI-compatible API server safely for frontends and integrations. |
| `infrastructure/hermes-native-mcp/` | Configure and use Hermes Agent's built-in MCP client for stdio and HTTP MCP servers, including testing, troubleshooting, and TLS trust fixes for internal HTTPS endpoints. |
| `infrastructure/mcporter-cli/` | Use the mcporter CLI for ad-hoc MCP server discovery, testing, schema inspection, and tool calls without changing Hermes configuration. |
| `infrastructure/native-mcp/` | Complete guide to MCP in Hermes: the built-in native MCP client (config, transport types, security, troubleshooting), the mcporter CLI for ad-hoc server calls, and the AIP docs MCP server for library documen... |
| `infrastructure/openwebui-hermes/` | Connect Hermes Agent to Open WebUI using the OpenAI-compatible API server and document image/file-delivery caveats. |
| `infrastructure/openwebui-media-via-s3/` | Serve images, videos, and audio to Open WebUI by uploading media to the public S3 bucket (scr4agent), then embedding pure markdown URLs. |
| `infrastructure/openwebui/` | Complete guide to integrating Hermes Agent with Open WebUI: S3-based media delivery, tool call emoji prefixing, image display fixes, and API server configuration. |
| `infrastructure/web-search-backend-management/` | Manage web search in Hermes Agent: backend switching (firecrawl, tavily, exa, parallel, duckduckgo), API key management, and the standalone DuckDuckGo skill for CLI-based searching. Covers diagnosis, switchi... |
| `infrastructure/workspace-backup/` | Back up the REANA workspace (data, code, figures, chat/agent state, skills) to a downloadable tar.gz — recipes and results, never venv binaries. Restore = untar; skill venvs re-provision themselves. |
| `leisure/find-nearby/` | Find nearby places (restaurants, cafes, bars, pharmacies, etc.) using OpenStreetMap. Works with coordinates, addresses, cities, zip codes, or Telegram location pins. No API keys needed. |
| `media/ffmpeg-ambient-audio/` | Create layered ambient pad music using FFmpeg's aevalsrc filter. Generates loopable 15-second clips with slow vibrato, shimmer, and exponential decay, then loops to target duration. Mixes into video at low v... |
| `media/fractal-preference-mandelbrot-elephant/` | When the user asks for a fractal showcase, they want a video that shows ONLY a Mandelbrot zoom transitioning to the Elephant's Valley image. The transition should use a very small scaling factor (~1e-7). No... |
| `mlops/local-llm-setup/` | Diagnose local LLMs, bridge formats for Claude Code, Codex. |
| `mlops/vllm-docker-local-serving/` | Use when running vLLM in Docker on a local GPU host. |
| `productivity/aip-member-contact-retrieval/` | Retrieve phone number (and email) for a staff member of the Leibniz Institute for Astrophysics Potsdam (AIP) from the public website. |
| `productivity/image-description-workflow/` | Workflow for handling user‑submitted images, generating a description via vision_analyze, and responding. |
| `productivity/nextcloud-caldav-calendar-management/` | Create, read, update, and delete calendar events via Nextcloud CalDAV API. Includes auth patterns, calendar paths, and quirks for Nextcloud v29+. |
| `productivity/nextcloud-caldav/` | Access and manage calendars on cloud.aip.de Nextcloud via CalDAV. List, create, edit, and delete events in personal and shared calendars. Credentials are passed via environment variables — never hardcode them. |
| `productivity/powerpoint-deck-customization/` | Generate, customize, and export PowerPoint decks with python-pptx — styling, white backgrounds, accent colors, PDF conversion via LibreOffice headless mode. |
| `python/calculator/` | Exact symbolic + numeric math with sympy/mpmath — derive formulas, evaluate constants, propagate errors, convert units. Use for ANY multi-step arithmetic or algebra instead of mental math. |
| `python/cmd-plotting/` | Generate astronomy colour-magnitude diagrams in Python with reproducible plotting choices. |
| `python/dask-hvplot-datashader-scientific-plots/` | Build scalable scientific plots from large tabular datasets using Dask for processing, hvPlot for plotting, and Datashader for dense large-data rendering. |
| `python/hdf5-on-s3-cached/` | Access HDF5 files stored on S3 by creating a reliable local cache first, extracting reusable subsets, and converting repeated tabular work products to local Parquet. |
| `python/s3-parquet-sampling-plot-cached/` | Efficiently sample a subset of a massive Parquet dataset stored on an S3‑compatible bucket, cache the sampled rows locally as a Parquet file for fast reuse, and produce high‑resolution PNG plots suitable for... |
| `python/s3-parquet-sampling/` | Sample or reduce massive Parquet datasets on S3 using local Parquet caching, Dask-first processing for large inputs, and hvPlot/Datashader for scalable scientific visualization. |
| `python/seaborn-paper-plots/` | Create clean seaborn/matplotlib plots suitable for papers, notes, and reproducible reports. |
| `reana-workflows/drp-hub/` | Digital Research Product Hub — federated infrastructure for reproducible science in particle physics & astrophysics. PUNCH4NFDI consortium project. |
| `reana-workflows/reana-aip/` | Author, validate, and run REANA workflows under AIP conventions — canonical reana.yaml template, the approved environment images, mandatory reana-client validate, submit/monitor recipe, GitLab + DRP-card han... |
| `reana-workflows/reana-client-config/` | Configure REANA client authentication with multi-profile `.reana/config.yaml` or `~/.reana/config.yaml`, store tokens safely, and select dev/prod back-ends reproducibly. |
| `reana-workflows/reana-client-docker/` | Use the Dockerized REANA client to ping a REANA server, list workflows, and format output with jq. |
| `reana-workflows/reana-client-failover/` | Use when a REANA workflow operation needs a robust client launcher: prefer native reana-client when installed, automatically fall back to Dockerized reanahub/reana-client when native client is missing, verif... |
| `reana-workflows/reana-client-multi-backend/` | Reusable instructions to set up a .reana/config.yaml with dev and prod profiles and run reana‑client via Docker using REANA_PROFILE. |
| `reana-workflows/reana-cmd-plot-workflow-external-script/` | Create a REANA workflow that runs a large S3 Parquet data plot using an external Python script. The script is stored as a separate file and referenced in the workflow inputs. This avoids inline script blocks... |
| `reana-workflows/reana-cmd-plot-workflow/` | REANA workflow that caches a large S3 Parquet dataset and plots bprp0 vs mg0 as a hex‑bin PNG. |
| `reana-workflows/reana-dev-workflow-setup/` | Set up a REANA development workflow in its own directory, place a minimal reana.yaml, and run it using the Dockerized REANA client. |
| `reana-workflows/reana-operator/` | Use when operating REANA from natural language: check job status, list available backends, show recent jobs by status, scaffold reana.yaml projects, run code as REANA workflows, inspect logs, validate YAML,... |
| `reana-workflows/reana-run-script-with-workspace/` | Run a Python (or other) script in a REANA workflow ensuring the script is found via $REANA_WORKSPACE. |
| `reana-workflows/reana-selflearn-workflows/` | Self‑learn REANA by listing finished workflows on the development backend, downloading their `reana.yaml` files, and providing guidelines for writing correct REANA workflows. |
| `reana-workflows/reana-serial-python-analysis-template/` | Reusable template for REANA serial workflows that run a Python analysis script on remote data, cache processed results locally as Parquet, and produce PNG outputs. Designed for SHBoost-like analyses where on... |
| `reana-workflows/reana-serial-python/` | When explicitly asked, use it to build a REANA serial workflow (Python analysis on remote data, Parquet cache, PNG outputs). |
| `reana-workflows/reana-shboost24/` | Run SHboost24 plotting and sampling workflows on REANA with cached parquet inputs and explicit script packaging. |
| `reana-workflows/reana-sin-plot-workflow/` | Minimal REANA workflow that plots a sine curve in green using pandas and matplotlib. Includes `reana.yaml`, `plot_sin.py` (and optional `requirements.txt`). |
| `reana-workflows/reana-version-info/` | Quick reference for REANA client and server versions for dev and production backends used by the user. |
| `reana-workflows/reana-workflow-best-practices/` | How to write a correct REANA workflow YAML that complies with the organization’s policies. |
| `reana-workflows/reana-workflow-sin-plot/` | Automates creation, submission, monitoring, and retrieval of a REANA workflow that plots a green sine curve using pandas and matplotlib. |
| `reana-workflows/reana-workflow-with-env/` | Create a REANA workflow respecting the organization’s environment repository and default memory limit. |
| `reana-workflows/reana/` | Complete guide to the REANA reproducible analytics platform: Dockerized client setup, multi-backend profiles, workflow authoring patterns, S3 dataset workflows, and best practices. Covers dev/prod backends,... |
| `research/2026-agentic-astronomy-literature/` | Summarize and apply the key 2026 literature on agentic systems in astronomy and scientific analysis. |
| `research/agentbench-benchmarking/` | Complete guide to running AgentBench FC benchmarks with LLM agents |
| `research/agentbench-dbbench-benchmark/` | Run AgentBench DBBench benchmark against LLMs and generate standardized comparison dashboard. Use when testing any model on DBBench (SQL generation task). |
| `research/agentbench-ollama-benchmarking/` | Benchmark LLMs using AgentBench suite with local Ollama models |
| `research/agentic-benchmarks/` | Overview and comparison of benchmarks that evaluate LLMs as autonomous agents: GAIA, WebArena, OSWorld, ToolBench, LiveAgentBench, BrowseComp, WebVoyager, Tau-Bench. Includes guidance on running AgentBench D... |
| `research/agentic-benchmarks/agent-benchmark-workflows/` | Class-level guide for running AI agent benchmarks — Terminal-Bench, SWE-Bench, DBBench, and related evaluation frameworks. Includes platform compatibility, container setup, and result interpretation. |
| `research/arxiv/` | Search and retrieve academic papers from arXiv using the free REST API. Query by keyword, author, category, or paper ID. Fetch abstracts, full PDFs, generate BibTeX, and explore citations via Semantic Scholar. |
| `research/astro-llm-research/` | Procedures, queries, pitfalls, and reproducible recipes for finding, verifying, and harvesting papers on large language models and agentic/LLM-based data analysis applied to galaxy formation, cosmology, and... |
| `research/astroagent-github-skills-repo-bootstrap/` | Scaffold a shareable GitHub repository for Hermes skills focused on AstroAgent, astronomy workflows, REANA, Open WebUI integration, and local dataset operations. |
| `research/blogwatcher/` | Monitor blogs and RSS/Atom feeds via blogwatcher-cli tool. |
| `research/cold-streams-monitoring/` | Automated arXiv monitoring for cold gas filament accretion in galaxy formation. Discovers new papers on cold mode accretion, cold flows, cosmological filaments, and related topics. Runs as a scheduled cron job. |
| `research/drp-agentic-assistants/` | Integrate agentic assistants into DRP / reproducibility papers, slides, and architecture with grounded, non-hype framing; especially Hermes + DRP-Hub + REANA style workflows. |
| `research/drp-card-workflow/` | Full lifecycle for creating reproducible DRP cards: scaffolding with reana.yaml, Beamer/LaTeX or Python workflows, GitLab publishing, and DRP-Hub registration via REST API. Covers the complete path from proj... |
| `research/drp-paper-workflow/` | Class-level skill: reproducible paper build, DRP-Hub screenshot capture, BibTeX sweep, and final packaging workflow for agentic-astronomy papers. Use when preparing/finishing a DRP-style manuscript and integ... |
| `research/drp-paper/` | Create and maintain the DRP white paper project with REANA integration |
| `research/drphub-anon-access/` | Query DRP Hub public cards without auth. |
| `research/iterative-paper-improvement/` | Structured multi-round improvement workflow for LaTeX academic papers — each round targets specific improvements (structure, prose, figures, compilation). Also covers merging multiple papers and multi-phase... |
| `research/jubik/` | J-UBIK (JAX-accelerated Universal Bayesian Imaging Kit) + NIFTy 9.x re API for variational inference. |
| `research/latex-compilation-pitfalls/` | Common LaTeX compilation errors, debugging patterns, and fixes — especially for agent-generated Beamer decks, TikZ/pgfplots variable mismatches, block/column nesting issues, and systematic error diagnosis wo... |
| `research/latex-journal-submission-package/` | Convert a working LaTeX manuscript into a journal-style submission package with separate BibTeX, build helper, manifest, and zip archive; useful when TeX is unavailable locally. |
| `research/latex-paper-iteration/` | Iteratively improve LaTeX research papers — structural fixes, prose polishing, figure integration, compilation cycles. Also covers merging multiple papers into a unified manuscript. |
| `research/latex-paper-workflow/` | Complete guide to writing, iterating, compiling, and packaging LaTeX research papers. Covers monolithic paper generation, multi-round improvement, merging papers, figure generation, MNRAS/journal submission... |
| `research/latex-research-paper/` | Generate complete, compilable LaTeX research papers in formal academic style with full section structure, BibTeX references, and figure support. |
| `research/llm-agent-benchmarking/` | Run LLM agent benchmarks (AgentBench FC) to evaluate multi-turn agent performance |
| `research/llm-benchmarking/` | Systematic LLM benchmarking on AgentBench, DBBench, and other standardized evaluations |
| `research/llm-wiki/` | Karpathy's LLM Wiki: build/query interlinked markdown KB. |
| `research/mnras-latex-compile-portability-fixes/` | Fix common MNRAS LaTeX portability issues on Ubuntu/Debian TeX Live installs, compile successfully, and package submission artifacts. |
| `research/mnras-latex-portable-build-and-package/` | Build and package an MNRAS LaTeX manuscript portably on Ubuntu, avoiding missing-font-package failures and fixing common two-column table issues. |
| `research/mnras-latex-portable/` | Build and package an MNRAS LaTeX manuscript portably on Ubuntu, avoiding missing-font-package failures and fixing common two-column table issues. |
| `research/multi-section-latex-whitepaper/` | Generate comprehensive LaTeX white papers from multiple sources — Markdown sections, existing papers, or user ideas. Converts and assembles into a single compiled PDF. |
| `research/nasa-ads-citations/` | Guide for verifying and extracting BibTeX metadata from NASA Astrophysics Data System (ADS). Includes verified API endpoints, search strategies, and CrossRef fallback. |
| `research/polymarket/` | Query Polymarket: markets, prices, orderbooks, history. |
| `research/research-paper-writing/` | Write ML papers for NeurIPS/ICML/ICLR: design→submit. |
| `research/terminal-bench/` | Benchmarking LLM agents in terminal environments using Harbor and Terminal-Bench datasets (2.0, 2.1, Pro). Covers installation, custom endpoint configuration, oracle smoke tests, dataset selection, ARM64 pit... |
| `science/dt4acc-container-troubleshooting/` | Debugging dt4acc digital twin containers — the twin requires accelerator lattice data in MongoDB to initialize, or use HIFIS pre-built images with BESSY II data pre-loaded. |
| `science/dtwin-burnin-tests/` | Run comprehensive burn-in tests on the dt4acc Digital Twin IOC to verify EPICS PV stability, throughput, and read/write resilience |
| `science/dtwin-epics-runbook/` | EPICS-first runbook for dt4acc using the current local-repo workflow, with host-side smoke test first and direct EPICS startup for the faster path. |
| `science/dtwin-host-smoke-test/` | Reproducible host-side smoke test for the dt4acc digital twin stack using local dt4acc, dt4acc-lib, and lat2db repos without MongoDB, TANGO, or Apptainer. |
| `science/dtwin-setup/` | Build and run the dt4acc Digital Twin for particle accelerators using Apptainer |
| `science/dtwin-tango-runbook/` | SOLEIL-oriented TANGO runbook for dt4acc, including Tango DB container startup, private data prerequisites, and the recommended debug order after the public host smoke test. |
| `science/dtwin/` | Umbrella for the dt4acc Digital Twin (particle accelerator simulation) covering Apptainer builds, host-side smoke tests, EPICS and TANGO runbooks, container troubleshooting, and burn-in testing. |
| `software-development/dask-mcp-docs-first/` | Generate or review Dask Python code only after consulting indexed MCP documentation, using strict version lookup and focused query templates for current APIs and best practices. |
| `software-development/pandas-datashader-mcp-docs-first/` | Write or review pandas and Datashader plotting code only after consulting indexed MCP documentation, using focused query templates for current IO, dtype, aggregation, and rendering APIs. |
| `software-development/paperclip-enable-llm-api/` | Configure the top-level LLM provider block in Paperclip so the instance recognizes the OpenAI backend in current Paperclip versions. |
| `software-development/paperclip-ensure-oss-120b-assistant/` | Verify and, if needed, create the oss-120b-assistant agent in Paperclip after server startup, ensuring it is visible in the agents dashboard. |
| `software-development/python-mcp-docs-first/` | When writing or revising Python code, consult the docs MCP server first for indexed libraries and base API usage on the latest available indexed documentation. |
| `software-development/skills-repo-maintenance/` | Maintain the AstroAgentAssistant-style public skills repository by auditing secrets, syncing README coverage, resolving vague issues into concrete skill changes, and keeping taxonomy consistent. |

## Superseded skills (`outdated-skills/`)

The 2026-07 skill sync from the production Hermes deployment at AIP ([PR #4](https://github.com/arm2arm/AstroAgentAssistant/pull/4)) replaced these with curated successors. They are kept (not deleted) for provenance and easy restore; the per-skill supersession map lives in [`outdated-skills/README.md`](outdated-skills/README.md).

- `gaia-aip-data-access`
- `gaia-aip-de-adql`
- `gaiadr3-aip-de-adql`
- `gaiadr3-aip-query-api`
- `rave-dr6-data-access`
- `rave-dr6-tap-query`
- `s3-parquet-astro-access`
- `shboost-cmd-plot`
- `shboost-cmd-visualization`
- `shboost-plot-s3`
- `shboost-public-s3-cmd-plot`
- `shboost24-cmd`
- `shboost_cmd_plot_and_animation`
- `shboost_full_cmd_datashader`
