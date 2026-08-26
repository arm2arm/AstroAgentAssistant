# ALFWorld Docker Build Failure (Python 3.9)

**Date**: 2026-07-15  
**Issue**: `textworld` package fails to build on Python 3.9  
**Impact**: ALFWorld service in AgentBench Docker stack cannot start

## Error Transcript

```
ERROR: Failed building wheel for textworld
error: failed-wheel-build-for-install
× Failed to build installable wheels for some pyproject.toml based projects
╰─> textworld
```

## Attempts Made (All Failed)

1. **Different versions**: `textworld==1.4.0`, `textworld==1.6.0`, `textworld==1.7.0`
2. **`--no-deps` flag**: `pip install textworld --no-deps`
3. **`--no-build-isolation`**: `pip install --no-build-isolation textworld`
4. **GitHub URL**: `textworld @ https://github.com/MarcCote/TextWorld/archive/...`
5. **Stub module**: Created `sitecustomize.py` to inject fake `textworld` module
6. **Dependency removal**: Removed `textworld` from requirements.txt

## Root Cause

`textworld` has complex C extensions and build system dependencies that are incompatible with Python 3.9 on the current base image (`python:3.9-bookworm`). The package uses `pyproject.toml` build isolation which fails to resolve/build required dependencies.

## Workarounds

### Option 1: Skip ALFWorld (Recommended)
```bash
docker compose -f extra/docker-compose.yml up -d controller redis dbbench-std os_interaction-std knowledgegraph-std freebase
```

### Option 2: Use Direct API Method
Bypass Docker entirely. The Direct API method works perfectly for all tasks including ALFWorld (if you have the environment set up separately).

### Option 3: Upgrade to Python 3.10+
Change Dockerfile base image to `python:3.10` or higher. This may break other services that depend on Python 3.9.

### Option 4: Fork and Patch textworld
Significant effort required. Not recommended unless ALFWorld is critical.

## Recommendation

**Use Direct API method** for benchmarking. The Docker stack is useful for full environment simulation, but for LLM benchmarking:
- Direct API: 98% success, 2s/sample, 10 min total
- Docker stack: Complex setup, ALFWorld broken, same results via Direct API

## References

- textworld PyPI: https://pypi.org/project/textworld/
- textworld GitHub: https://github.com/Microsoft/TextWorld
- AgentBench ALFWorld: https://github.com/THUDM/AgentBench/tree/main/src/server/tasks/alfworld
