# SH26 DevContainer (cross-platform VS Code)

Files: `.devcontainer/Dockerfile`, `.devcontainer/devcontainer.json`,
`.dockerignore` (repo root). Base:
`mcr.microsoft.com/devcontainers/python:3.11-bookworm`. Open the SH26
folder in VS Code → "Dev Containers: Reopen in Container" (any OS with
Docker); first build ~5 min. Committed 2026-08-16 (c28467b).

## Layout decisions

- `build.context: ".."`, `workspaceFolder: /workspaces/sh26` — the
  workspace mounts at the folder name's EXACT case; WORKDIR and
  PYTHONPATH must match or `python -m sh26` fails to import silently.
- `.dockerignore` at repo root EXCLUDES `data/` (~22 GB) — without it
  the build context ships the whole dataset (kill + rebuild if you
  discover a build is slow for no reason).
- Project is NOT pip-installable: `pyproject.toml` build-backend
  (`setuptools.backends._legacy:_Backend`) does not exist in any
  setuptools release. Container sets `PYTHONPATH=/workspaces/sh26/src`
  via Dockerfile ENV (inherited by VS Code terminals). Do not add
  `pip install -e .` (postCreateCommand included early was removed).
- Pinned analysis stack == production host (numpy 2.4.6, pandas 3.0.5,
  scipy 1.17.1, dask/distributed 2026.7.1, pyarrow 25.0.0,
  scikit-learn 1.9.0, umap-learn 0.5.12, hdbscan 0.8.44, pymupdf
  1.28.2) + jupyterlab/pytest/black; requirements.txt layered first.
- System deps: libgl1 + libglib2.0-0 (headless matplotlib),
  build-essential, git, curl.
- `shutdownAction: none`, `containerUser: vscode`,
  `remoteUser: vscode` not needed (containerUser covers it).

## User-creation pitfall (build failure, hit 2026-08-16)

The devcontainers python base ALREADY ships a `vscode` user (uid/gid
1000) with passwordless sudo — `groupadd`/`useradd` for it fails with
"group already exists". Remap instead:

```dockerfile
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=1000
RUN groupmod -o -g $USER_GID $USERNAME || groupadd -f --gid $USER_GID $USERNAME; \
    usermod -o -u $USER_UID -g $USER_GID -s /bin/bash $USERNAME; \
    mkdir -p /workspaces && chown -R $USER_UID:$USER_GID /workspaces
USER $USERNAME
```

devcontainer.json passes `"USER_UID": "${localEnv:UID:-1000}"` etc.

## Verification that was actually done

`docker build` succeeded; `docker run -v <repo>:/workspaces/sh26
-w /workspaces/sh26 sh26-devcontainer` → `python -m sh26 list` OK and a
full P73 200k run produced PDF+PNG+JSON. 50M works inside (peak ~3.5 GB)
but is slow on thin hosts — recommend the 200k cache there.
