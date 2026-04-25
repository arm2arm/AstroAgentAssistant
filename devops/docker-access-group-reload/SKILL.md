---
name: docker-access-group-reload
description: Resolve Docker permission errors by ensuring the user is in the docker group and reloading group membership.
---

## Steps
1. **Verify Docker group membership**
   ```bash
   grep -i docker /etc/group
   id
   ```
   Ensure the target user appears in the `docker` group entry.
2. **Add user to docker group (if missing)**
   ```bash
   sudo usermod -aG docker <username>
   ```
   Replace `<username>` with the actual user. This requires sudo privileges.
3. **Reload group membership**
   - The simplest way is to log out and log back in, or start a new login shell:
     ```bash
     exec su - $USER
     ```
   - If you cannot log out, you can run Docker commands under the group directly:
     ```bash
     sg docker -c "docker ps"
     ```
4. **Verify Docker access**
   ```bash
   docker ps
   ```
   You should see a list of running containers without a permission error.

## Pitfalls & Tips
- Adding the user to the group does **not** automatically grant access in the current session; a new session is required.
- `newgrp docker` only affects the current shell process; subsequent commands launched from a fresh process will still lack the group unless you start a new login shell.
- Using `sg docker -c "<command>"` is a quick workaround when you cannot log out.
- Ensure the Docker socket has appropriate permissions (`srw-rw---- 1 root docker … /var/run/docker.sock`).

## Verification
After completing the steps, `docker ps` should list containers without any `permission denied` message.
