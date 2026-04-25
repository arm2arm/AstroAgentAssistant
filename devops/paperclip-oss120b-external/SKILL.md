---
name: paperclip-oss120b-external
title: Configure Paperclip to use an external OpenAI‑compatible OSS‑120B endpoint
description: |
  Step‑by‑step guide for turning a fresh Paperclip installation into a publicly reachable service that forwards LLM calls to a custom OSS‑120B model served via an OpenAI‑compatible endpoint. Handles deployment mode, bind settings, authentication exposure, board claim, and environment variables.
category: devops
---
steps:
  - "**1. Adjust server configuration**\\nEdit `~/.paperclip/instances/default/config.json` (or the config you used with `paperclipai onboard`). Replace or add the following keys under `server` and `auth`:\\n```json\\n{\n  \"deploymentMode\": \"authenticated\",\n  \"exposure\": \"public\",\n  \"bind\": \"custom\",\n  \"host\": \"0.0.0.0\",\n  \"customBindHost\": \"0.0.0.0\",\n  \"port\": 3100\n}\n```\\nThen under `auth` set:\\n```json\\n{\n  \"baseUrlMode\": \"explicit\",\n  \"publicBaseUrl\": \"http://<PUBLIC_IP>:3100\"\n}\n```\\n(Replace `<PUBLIC_IP>` with your public IP, e.g., `141.33.165.84`)."
  - "**2. Add LLM block**\\nInside the same config file add an `llm` object (anywhere at top level):\\n```json\\n{\n  \"llm\": {\n    \"provider\": \"openai\",\n    \"apiKey\": \"\",\n    \"model\": \"oss-120b\"\n  }\n}\n```\\nThe empty `apiKey` works because the external endpoint does not require authentication."
  - "**3. Export environment variables**\\n```bash\\nexport OPENAI_API_BASE=\"http://<PUBLIC_IP>:8000/v1\"\\nexport OPENAI_API_KEY=\"\"   # empty password\\nexport OPENAI_MODEL=\"oss-120b\"\\n```\\nAdd these lines to `~/.bashrc` (or your preferred shell rc) so they survive restarts."
  - "**4. Run Paperclip**\\n```bash\\nnpx paperclipai run\\n```\\nThe server will start on `0.0.0.0:3100` (or the next free port if 3100 is already in use, e.g., `3101`). The printed *board‑claim* URL will use the port you see in the startup logs, so keep an eye on the log line `Server listening on 0.0.0.0:<PORT>` and adjust your `publicBaseUrl` if you change the port."
  - "**5. Claim the board (if needed)**

   The simplest way to generate a one‑time admin bootstrap URL is now:
   ```bash
   npx paperclipai auth bootstrap-ceo --force
   ```
   This prints an `Invite URL` you can open in a browser to set (or reset) the admin password, even if an admin user already exists. The `--force` flag forces regeneration of a fresh invite.

   *(Optional quick‑reset via CLI – works if CSRF protection is not enabled)*
   ```bash
   INVITE=$(npx paperclipai auth bootstrap-ceo --force | grep -oP 'http://[^ ]+')
   TOKEN=$(basename "$INVITE")
   curl -X POST "http://141.33.55.137:3101/invite/$TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"email":"admin@paperclip.ai","password":"<NEW_PASS>"}'
   ```
   Replace `<NEW_PASS>` with the desired password.

   The original guide’s “board‑claim” wording is still valid – the URL points to
   `/invite/...` which internally maps to the same claim flow.

   Also, when the desired port is already in use, Paperclip will fall back to the next free port (e.g., 3102). Adjust `publicBaseUrl` accordingly.\\nOpen the URL printed in the console (it will look like `http://localhost:3100/board-claim/<token>?code=<code>`). Replace `localhost` with your public IP (`http://<PUBLIC_IP>:3100/...`).\\nCreate the first admin user — this converts the instance from `local_trusted` to a fully authenticated deployment.\\n\n**NOTE:** If the instance already has an admin user (as indicated by the log line “Instance already has an admin user”), you can skip this step and proceed directly to logging in.
"

   The simplest way to generate a one‑time admin bootstrap URL is now:
   ```bash
   npx paperclipai auth bootstrap-ceo --force
   ```
   This prints an `Invite URL` you can open in a browser to set the admin password.
   (Older versions used `paperclipai onboard` which no longer accepts `--force`.)
   
   *Note:* If the instance already has an admin user, you can still run the above command to reset the password.

   The original guide’s “board‑claim” wording is still valid – the URL points to
   `/invite/...` which internally maps to the same claim flow.

   Also, when the desired port is already in use, Paperclip will fall back to the next free port (e.g., 3102). Adjust `publicBaseUrl` accordingly.\\nOpen the URL printed in the console (it will look like `http://localhost:3100/board-claim/<token>?code=<code>`). Replace `localhost` with your public IP (`http://<PUBLIC_IP>:3100/...`).\\nCreate the first admin user — this converts the instance from `local_trusted` to a fully authenticated deployment.\\n\n**NOTE:** If the instance already has an admin user (as indicated by the log line “Instance already has an admin user”), you can skip this step and proceed directly to logging in.
  - "**6. Log in**\\nAfter claiming, go to `http://<PUBLIC_IP>:3100/login` (or click the sign‑in button in the UI) and use the credentials you just set."
  - "**7. Verify LLM routing**\\n```bash\\ncurl -X POST http://<PUBLIC_IP>:3100/v1/chat/completions \\\n     -H \"Content-Type: application/json\" \\
     -d '{\"model\":\"oss-120b\",\"messages\":[{\"role\":\"user\",\"content\":\"Say hello\"}],\"max_tokens\":10}'\n```\\nThe response should contain a short completion generated by the OSS‑120B model."
pitfalls: |
  - **Deployment mode**: `local_trusted` forces `bind: "loopback"`. Switch to `authenticated` before using a custom bind.
  - **Public exposure**: When `exposure` is `public`, Paperclip expects `auth.baseUrlMode` to be `explicit` and a valid `publicBaseUrl`. Forgetting this causes a doctor warning and may block external access.
  - **HTTPS**: The built‑in doctor warns that public deployments should use HTTPS. For production, place an Nginx (or similar) reverse proxy with TLS in front of Paperclip.
  - **Board claim**: After changing to `authenticated`, Paperclip will refuse UI access until the one‑time claim URL is visited and an admin user is created.
  - **Empty API key**: Ensure you really have no credential required at the external endpoint; otherwise set the appropriate key in `OPENAI_API_KEY`.
verification: |
  - `npx paperclipai doctor` shows *"Valid config"* with only the HTTPS warning.
  - The UI loads at `http://<PUBLIC_IP>:3100/` and you can sign in.
  - A `curl` request to `/v1/chat/completions` returns a JSON payload with a completion from `oss-120b`.
