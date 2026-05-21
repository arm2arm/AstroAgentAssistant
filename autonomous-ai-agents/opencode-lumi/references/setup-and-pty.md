Session notes: opencode + lumi-assistant (from 2026-05-21 session)

Summary
- opencode was installed locally at $HOME/.local/bin/opencode (v1.15.6) because global npm install failed with EACCES.
- First run can perform database migrations and model build steps which take time.
- Running opencode non-interactively may trigger TTY-control errors (tcsetattr) if the binary attempts to set terminal attributes. Run interactive TUI (with a PTY) for initialization or allow the process to finish its background migration tasks before retrying one-shot runs.

Quick commands used successfully
- Install locally (avoid sudo/global permission issues):
  npm install --location=global --prefix="$HOME/.local" opencode-ai@latest

- Verify binary:
  $HOME/.local/bin/opencode --version

- One-shot run (project config):
  OPENCODE_CONFIG=/home/hermes/tmp/lumi-assistant/config/opencode.json \ 
    $HOME/.local/bin/opencode run "Respond with exactly: OPENCODE_SMOKE_OK"

- Launch interactive TUI (attach a PTY):
  OPENCODE_CONFIG=/home/hermes/tmp/lumi-assistant/config/opencode.json \ 
    $HOME/.local/bin/opencode

Pitfalls & fixes
- npm EACCES when installing globally: avoid by installing to a per-user location ($HOME/.local) or use a node version manager (nvm) that avoids touching /usr/lib.
- tcsetattr / Inappropriate ioctl for device: indicates opencode is trying to control terminal settings. Solve by launching the binary with a real PTY (Hermes terminal(..., pty=true)) or by running the interactive TUI so initialization completes.
- Long first-run tasks: the binary can perform "one-time database migration" and "model build" steps. Allow extra time or run interactively so you can monitor progress.

Recommended workflows
1) Non-interactive automation (CI / scripts)
   - Pre-initialize opencode once interactively to allow migrations and model downloads to finish.
   - Use the one-shot `opencode run` command in scripts after initialization.

2) Hermes integration (recommended)
   - One-shot: use terminal(command="OPENCODE_CONFIG=... $HOME/.local/bin/opencode run 'prompt'", timeout large enough for expected work). Capture stdout and any files.
   - Interactive: terminal(background=true, pty=true, command="OPENCODE_CONFIG=... $HOME/.local/bin/opencode") and use process(action='submit'/'log') to interact.

Security notes
- Do not place credentials in repo files. Use opencode auth flows (opencode auth login) or env vars. Some lumi skills interact with cluster services (Rucio, Reana) and are denied by default in opencode permissions — grant these only when you intend to use them.

References
- Commands and outputs from the session are stored in the skill logs. For repeatability, use OPENCODE_CONFIG to point explicitly at the project config file.
