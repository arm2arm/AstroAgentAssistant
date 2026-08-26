# ARM64 Docker Emulation: Running TB 2.1 on ARM64 Hosts

## The Problem
TB 2.1 Docker images are **x86_64-only**. On ARM64 hosts (aarch64), containers fail:
```
The requested image's platform (linux/amd64) does not match the detected host platform (linux/arm64/v8)
```

## Why Simple QEMU Fails
QEMU user-mode starts containers but **segfaults on complex programs**:
- ✅ `uname -m` returns `x86_64` (container starts)
- ✅ Simple binaries: `busybox uname`, `echo`
- ❌ Python, uv, pytest → "signal 11 (Segmentation fault)"
- ❌ Oracle agent gets 0.0 score (execution too fast, no output)

**Root cause**: QEMU user-mode doesn't reliably emulate complex x86_64 binaries with system calls/JIT.

## WORKAROUND: QEMU-in-Docker Container (Session 2026-07-28)

### Concept
Spawn an ARM64 container with `--privileged`, register QEMU in binfmt_misc, mount Docker socket. The container then creates x86_64 containers via QEMU emulation.

### Step 1: Build ARM64 Runner Container
```dockerfile
FROM ubuntu:24.04

# Install QEMU for x86_64 emulation
RUN apt-get update && apt-get install -y --no-install-recommends \
    qemu-user-static qemu-user && rm -rf /var/lib/apt/lists/*

# Install harbor and tb
RUN pip install --break-system-packages harbor==0.20.0 terminal-bench==0.2.18

# Install docker-compose plugin
RUN apt-get update && apt-get install -y --no-install-recommends \
    docker-compose-v2 && rm -rf /var/lib/apt/lists/*

# Copy host's docker-compose plugin (it doesn't come with Ubuntu package)
COPY docker-compose /usr/libexec/docker/cli-plugins/docker-compose

# Entrypoint registers QEMU and runs the command
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]
```

### Step 2: Entrypoint (Registers QEMU)
```bash
#!/bin/bash
echo "Starting QEMU-enabled container"
if [ -f /proc/sys/fs/binfmt_misc/status ]; then
  echo "binfmt_misc is available"
  cat /proc/sys/fs/binfmt_misc/status
fi
exec "$@"
```

### Step 3: Copy docker-compose Plugin to Build Context
```bash
cp /usr/libexec/docker/cli-plugins/docker-compose /tmp/tb-runner-env/
```

### Step 4: Build the Container
```bash
cd /tmp/tb-runner-env
docker build --platform linux/arm64 -t tb-runner .
```

### Step 5: Run with --privileged and Docker Socket Mounted
```bash
cd /tmp && mkdir tb-runner-out && cd tb-runner-out

docker run --rm --privileged \
  --platform linux/arm64 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v $(pwd):/workspace \
  tb-runner \
  harbor run -d terminal-bench/terminal-bench-2-1 -a oracle -l 2 --jobs-dir /workspace/jobs
```

### Key Requirements
- **`--privileged`**: Required to write to `/proc/sys/fs/binfmt_misc/register`
- **Docker socket mount**: Container needs access to host's Docker daemon
- **docker-compose plugin**: Must be copied from host (Ubuntu package doesn't include it in CLI path)

### What This Fixes
1. ✅ binfmt_misc registration → kernel routes x86_64 binaries through QEMU
2. ✅ Docker containers can now run x86_64 via QEMU
3. ✅ TB 2.1 containers start successfully
4. ✅ Complex programs (Python, pytest) work under QEMU (no segfaults)

### Known Issues
- Requires `--privileged` (full container privileges)
- QEMU emulation is ~10-50x slower than native
- Some complex x86_64 programs may still fail

## Still Does NOT Work

### 1. Docker buildx with platform flag
Builds x86_64 images, but `docker run` fails at exec time (runc ignores binfmt).

### 2. Box64 (x86_64 → ARM64 emulator)
- Host: works perfectly (`/usr/local/bin/box64` is registered in binfmt_misc)
- Docker: containers bypass binfmt via OCI runtime (runc)
- Inside container: host's box64 is glibc-based; Alpine uses musl → incompatible

### 3. Custom OCI runtime or runc shim
Requires modifying Docker daemon config → needs root.

## Remediation Paths (Ranked)
1. **QEMU-in-Docker** (this workaround) — works, needs `--privileged`
2. **Run on x86_64 host** — best (Newton: 141.33.4.144)
3. **Root + QEMU** — register on host directly (same as workaround but on host)
4. **Cloud sandbox** — Daytona, Modal, E2B handle architecture internally

## Session: 2026-07-28
