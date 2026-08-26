---
name: workstation-security-audit
title: Linux workstation security audit for AI/GPU infra
description: "Read-only audit and hardening for GPU research workstations."
author: Arman Khalatyan & Hermi
date: 2026-08-06
tags: [security, audit, ssh, firewall, docker, gpu, hermes-infrastructure]
---

# Workstation Security Audit — Read-Only Evidence Collection + Approval-Gated Hardening

Use when auditing a Linux workstation (DGX, research VM, personal server) running AI agent infrastructure. Enforces two-phase discipline: collect evidence first, harden only after approval.

## Phase 1 — Read-only evidence collection

**Golden rule:** No writes, no service restarts, no config changes during this phase. All commands are read-only probes.

### Evidence checklist (run in parallel where possible)

#### SSH surface
```bash
cat /etc/ssh/sshd_config                                    # main config (note Includes)
for f in /etc/ssh/sshd_config.d/*.conf; do cat "$f"; done   # drop-in overrides
ls -la ~/.ssh/authorized_keys && wc -l ~/.ssh/authorized_keys  # key count + perms
```

Focus on: `PermitRootLogin`, `PasswordAuthentication` (commented = default yes), `UsePAM`, `KbdInteractiveAuthentication`

#### Listening ports and services
```bash
ss -tlnp                                                    # all TCP listeners with PIDs
systemctl list-units --type=service --state=running --no-pager  # active daemons
```

Audit each listener on `0.0.0.0`: should it be external? Is it auth'd?

#### Privilege escalation paths
```bash
groups $USER                                                # sudo, docker, etc.
ls -la /var/run/docker.sock                                 # docker group = root equiv
cat /etc/sudoers 2>/dev/null; ls /etc/sudoers.d/           # sudo policies
```

#### Firewall and network controls
```bash
iptables -L -n 2>/dev/null && iptables-save 2>/dev/null     # netfilter rules
ufw status 2>/dev/null                                       # UFW state
ss -tlnp | grep 'LISTEN'                                     # confirm all exposed ports
```

#### Setuid/setgid + file capabilities
```bash
find / -type f \( -perm /6000 \) 2>/dev/null | grep -v '/proc/' | head -50   # setuid/sgid
getcap -r /usr/bin/ /usr/sbin/ 2>/dev/null                                      # file caps
```

Flag any setuid binary outside `/usr` or that isn't standard distro.

#### Container posture
```bash
docker ps --format '{{.Names}} {{.Image}} {{.Status}}'              # running containers
docker inspect --format='P={{.HostConfig.Privileged}} CapAdd={{println .HostConfig.CapAdd}} NetMode={{.HostConfig.NetworkMode}} ReadonlyRoot={{.HostConfig.ReadonlyRootfs}}' <container>  per container
docker images                                                       # image list + tag discipline (:latest = risk)
```

#### Secrets in configs
```bash
grep -rn 'api_key\|API_KEY\|password\|secret\|token' ~/.hermes/config.yaml ~/.hermes/.env | grep -v '^#\|^$'
ls -la ~/.hermes/.env                                              # file permissions
find ~ -name '*.env' -o -name '*secret*' -o -name '*token*' 2>/dev/null  # surface-level secret files
```

#### Shared storage + scheduler
```bash
df -hT /lustre 2>/dev/null                                          # shared mounts
crontab -l 2>/dev/null                                              # user cron jobs
```

### Evidence capture discipline

- Run probes that don't depend on each other **in parallel** (SSH config, ports, sudoers, containers, secrets can all fire simultaneously)
- Record stdout — it IS the evidence. Don't interpret yet.
- If a command fails or returns empty, note it — empty is also evidence (e.g., no iptables = no firewall)

## Phase 2 — Report + approval-gated hardening

### Report structure

```
1. Executive risk summary (3-5 sentences)
2. Findings table: Severity | Finding ID | Evidence | Impact
3. Safe remediation order (by breakage risk, ascending)
4. Exact commands/diffs per fix + rollback steps for each
```

**Severity rubric:**
- 🔴 CRITICAL: Direct root compromise vector on network-exposed surface area
- 🟠 HIGH: Unauthenticated access to data/execution plane
- 🟡 MEDIUM: Information disclosure, resource abuse, hygiene violations
- 🟢 LOW: Standard compliance, defense-in-depth niceties

### Hardening rules

1. **Every proposed change includes:** exact command or diff, expected outcome, rollback steps
2. **Wait for approval** before applying anything — never auto-execute Phase 2
3. **Order by breakage risk:** localhost binding and image pinning first (trivial rollback), firewall last (lockout risk)
4. **Validate SSH access survives** before firewall changes — confirm authorized_keys works

### Common findings patterns for AI workstations

| Service | Typical port | Common exposure | Fix |
|---------|-------------|-----------------|-----|
| Ollama | 11434 | No auth, exposed on 0.0.0.0 | `OLLAMA_HOST=127.0.0.1:11434` systemd override |
| Memory API | custom (8420+) | Network-mapped containers | `-p 127.0.0.1:PORT:PORT` in docker run |
| Agent gateway | varies | Unauthenticated terminal access | Firewall deny + verify auth before re-opening |
| SSH root login | 22 | `PermitRootLogin yes` | Drop-in config with `PermitRootLogin no` |
| Docker socket | N/A (Unix sock) | User in docker group = root equiv | Accept risk or move to rootless-docker |

## Pitfalls

- **UFW enable can lock you out** — always confirm SSH key access works first. Use `--force` flag so it doesn't prompt mid-enable, test connectivity immediately after.
- **sshd_config includes take precedence** — drop-in `.conf` files in `sshd_config.d/` override main config. Check both before declaring findings.
- **Container health != API auth** — /health returning 200 doesn't mean data endpoints are protected. Test specific routes.
- **Redacted values aren't safe** — configs may show truncated keys (`sk-p...qg`) but the full value is on disk in plaintext. Check file perms and if other users can read them.
