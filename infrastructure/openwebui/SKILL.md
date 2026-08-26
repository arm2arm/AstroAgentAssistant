---
name: openwebui
title: Open WebUI Integration — Media Delivery, Tool Icons, and Image Display Fixes
description: >-
  Complete guide to integrating Hermes Agent with Open WebUI: S3-based media delivery,
  tool call emoji prefixing, image display fixes, and API server configuration.
author: Hermes Agent
date: 2026-04-30
tags: [openwebui, api-server, media, tool-icons, s3]
---

# Open WebUI Integration

This umbrella covers all Open WebUI integration patterns: media delivery, tool icon display, and image fix workarounds.

---

## 1. Media Delivery via S3

### Problem
`MEDIA:/path/to/file` appears as plain text in Open WebUI — it doesn't understand the `MEDIA:` protocol (Telegram does).

### Solution
Upload media to the public `scr4agent` S3 bucket and return **pure markdown**:

| Media type | Format |
|------------|--------|
| Images (png, jpg, gif, webp) | `![alt](url)` — renders inline |
| Videos | Auto-converted to GIF → `![alt](url.gif)` |
| Audio | `[♫ name](url)` — clickable link |
| Documents (PDF, TEX, DOCX) | `[name.pdf](url)` — clickable link, NEVER `![name](url)` |

### S3 Bucket Details
- **Endpoint**: `https://s3.data.aip.de:9000`
- **Bucket**: `scr4agent`
- **Auth**: None — public read/write (unauthenticated PUT via curl)
- **Base URL**: `https://s3.data.aip.de:9000/scr4agent/`

### S3 Upload Script
```bash
python3 ~/.hermes/scripts/s3_media_upload.py <filepath>
```
Uses curl internally (anonymous public PUT). No auth needed.

### Manual curl Upload
**Always use `-T`, NOT `--upload-file` or `Content-Type` headers.**
```bash
KEY="hermes/$(python3 -c "import uuid; print(uuid.uuid4().hex[:16])")<ext>"
curl -X PUT -T /path/to/file.<ext> "https://s3.data.aip.de:9000/scr4agent/$KEY"
```
**Why**: boto3 uses AWS auth headers → `InvalidAccessKeyId` on this unauthenticated bucket. curl without auth works.

**Note**: `~/.hermes/scripts/s3_media_upload.py` was updated to use curl instead of boto3 to avoid `InvalidAccessKeyId` errors.

### Video-to-GIF Conversion
```bash
ffmpeg -y -i input.mp4 \
  -vf "fps=10,scale=480:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" \
  -loop 0 output.gif
```

### Response Format Rule
```
image extension (png, jpg, jpeg, gif, webp, bmp, svg)  →  ![alt](url)
everything else (pdf, tex, docx, zip, mp4, mp3, etc.)  →  [name](url)
```

### Pitfalls
- **HTML is sanitized** — `<video>`, `<audio>` tags are stripped. Only use pure markdown.
- **boto3 fails on public buckets** — uses AWS signature headers → `InvalidAccessKeyId`. Always use curl.
- **No auto-expiry** — files persist until manually deleted.
- **GIF conversion may produce black frames** — try raw curl upload as fallback.
- **Telegram vs Open WebUI** — on Telegram, use `MEDIA:` normally. Only use S3 URLs for Open WebUI.

---

## 2. Tool Icon Display

### Root Cause
**Open WebUI does NOT support custom tool icons.**

Verified by analyzing `ToolCallDisplay.svelte` in compiled Open WebUI frontend:
- Always renders: 🔧 wrench (pending), ⏳ spinner (executing), ✅ checkmark (done)
- Displays `attributes.name` as plain text next to the icon
- Custom icon data (`icon_url`, emoji in events, HTML tags) is **silently ignored**

### Implemented Fix
In `gateway/platforms/api_server.py`:
1. Added `_TOOL_EMOJI` dict with 50+ tool→emoji mappings
2. Added `_get_tool_display_name()` prepends emoji to tool names
3. Applied in 4 places: chat completions SSE, responses API, non-streaming, tool progress

### Verification
```bash
# Restart gateway
sudo systemctl restart hermes-gateway

# Test SSE stream
curl -N http://localhost:8642/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"hermes","messages":[{"role":"user","content":"test"}],"stream":true}'
```

Tool labels should show `🔍 web_search` instead of just `web_search`.

### What Does NOT Work (false leads)
- `icon_url` in SSE events — ignored by frontend
- `<details type="tool_calls">` HTML — not parsed
- Custom `hermes.tool.progress` events — ignored by Open WebUI
- Adding emoji to content text — doesn't appear during tool phase

---

## 4. API Server Local Image Fix

When Open WebUI via Hermes Agent's API server doesn't display images inline
(shown as broken icons or raw markdown), the fix is to extend
`api_server.py`'s `_convert_media_to_http_urls()` to handle standard markdown
with local paths.

### Problem
Hermes generates `![alt](/tmp/file.png)` — standard markdown with local paths.
The API server has no `MEDIA:` interception, and the conversion pipeline had
no handler for this format.

### Fix Applied in `api_server.py`

Add the regex for standard markdown local path images:
```python
LOCAL_PATH_MD_RE = re.compile(
    r'!\[([^\]]*)\]\(\s*([\w./\-]+\.[\w]{2,4})\s*\)'
)
```

Add the handler inside `_convert_media_to_http_urls()`:
```python
def _convert_local_path_image(match):
    alt_text = match.group(1)
    file_path = match.group(2)
    if not file_path.startswith("/"):
        return match.group(0)
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in ALLOWED_MEDIA_EXTENSIONS:
        return match.group(0)
    if not os.path.isfile(file_path):
        return match.group(0)
    try:
        with open(file_path, "rb") as f:
            file_bytes = f.read()
    except Exception:
        return match.group(0)
    content_hash = hashlib.sha256(file_bytes).hexdigest()[:16]
    filename = f"{content_hash}{ext}"
    dest_path = os.path.join("/tmp/hermes-api-media", filename)
    if not os.path.exists(dest_path):
        import shutil; shutil.copy2(file_path, dest_path)
    return f"![{alt_text}](http://{host}/media/{filename})"
```

Add to pipeline (last step):
```python
result = LOCAL_PATH_MD_RE.sub(_convert_local_path_image, result)
```

### Verification
1. Restart gateway: `pkill -f "hermes gateway" || true; hermes gateway`
2. Test: `curl http://localhost:8642/v1/chat/completions -d '...'`
3. Check response contains `http://127.0.0.1:8642/media/<hash>.png`, not `/tmp/...`

### Pitfalls
- Gateway must be restarted for code changes to take effect
- Files must be absolute paths starting with `/`
- Only allowed extensions: png, jpg, gif, webp, svg, mp4, webm, ogg, mp3, wav, pdf
- Content-hashed filenames prevent collisions but make debugging harder

---

## 3. API Server Media Display Fix

When Open WebUI via Hermes Agent's API server doesn't display images inline (shows broken image icons), the fix is:

1. Ensure images are uploaded to S3 first (see section 1)
2. Return markdown `![alt](url)` not `MEDIA:/path`
3. Verify the S3 URL is publicly accessible (no auth required)

### Debug Steps
```bash
# Check if file exists at S3
curl -I "https://s3.data.aip.de:9000/scr4agent/hermes/<uuid>.png"
# Should return 200 OK

# Check Content-Type header
curl -I "https://s3.data.aip.de:9000/scr4agent/hermes/<uuid>.png" | grep Content-Type
# Should be image/png, image/gif, etc.
```

### Hook for Automated Upload
```bash
~/.hermes/hooks/on_media_deliver.sh <filepath>
```
Calls the upload script and returns the markdown URL.