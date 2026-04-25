---
name: api-server-local-image-support
description: Fix Open WebUI image display by extending api_server.py to convert standard markdown ![alt](/local/path) images into HTTP URLs via /media/<path> route. Handles the gap between agent-generated image paths and the API server's media serving pipeline.
version: 1.0.0
author: Hermes Agent (Arman Khalatyan)
license: MIT
metadata:
  hermes:
    tags: [api-server, open-webui, media, images, devops]
    related_skills: [api-server, devops]
---

# API Server Local Image Support

## Problem

When Hermes generates images (e.g., via `image_generate`, `skill_view`, or plotting skills), the response contains standard markdown with local file paths:

```markdown
![Description](/tmp/file.png)
```

Messaging platforms (Telegram, Discord) intercept `MEDIA:/path` tags and deliver files natively. But the **API server** (used by Open WebUI, LobeChat, etc.) has no such interception — it passes the raw local path through, which Open WebUI cannot resolve.

The API server's `_convert_media_to_http_urls()` in `api_server.py` handles:
- `![alt](data:image/...;base64,...)` — data URIs ✓
- `MEDIA:/path/to/file` — MEDIA tags ✓

But NOT standard markdown with local paths.

## Root Cause

The `on_media_deliver` hook fires for Telegram/Discord but **not** for API server sessions. The API server relies on `_convert_media_to_http_urls()` to bridge local paths to HTTP URLs, but that function had no handler for standard markdown image syntax.

## Fix Applied (in `api_server.py`)

### 1. New regex — matches standard markdown `![alt](/local/path)`:

```python
LOCAL_PATH_MD_RE = re.compile(
    r'!\[([^\]]*)\]\(\s*(/[\w./\-]+\.[\w]{2,4})\s*\)'
)
```

### 2. New handler inside `_convert_media_to_http_urls()`:

```python
def _convert_local_path_image(match):
    """Convert standard markdown with local file path to HTTP URL.
    
    - ![alt](/path/to/file.png) → http://host/media/<copied_file>
    """
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
        import shutil
        shutil.copy2(file_path, dest_path)
    
    return f"![{alt_text}](http://{host}/media/{filename})"
```

### 3. Pipeline order (last step):

```python
result = DATA_URI_RE.sub(_save_base64_image, text)
result = MEDIA_TAG_RE.sub(_convert_media_tag, result)
result = LOCAL_PATH_MD_RE.sub(_convert_local_path_image, result)  # NEW
```

## Security Notes

- Only absolute paths starting with `/` are matched
- File existence is verified before processing
- Only allowed extensions are processed (png, jpg, gif, webp, svg, mp4, webm, ogg, mp3, wav, pdf)
- Files are copied with content-hash-based filenames to prevent collisions and path traversal
- Graceful fallback: if file can't be read, markdown is left unchanged

## Verification

1. Restart the Hermes gateway after editing `api_server.py`:
   ```bash
   # Find and kill the gateway process
   pkill -f "hermes gateway" || true
   # Or: kill $(cat ~/.hermes/gateway.pid)
   
   # Restart
   hermes gateway
   ```

2. Test with a simple image generation via Open WebUI or curl:
   ```bash
   curl http://localhost:8642/v1/chat/completions \
     -H "Authorization: Bearer <key>" \
     -H "Content-Type: application/json" \
     -d '{"model": "hermes-agent", "messages": [{"role": "user", "content": "Generate a simple plot"}], "stream": false}'
   ```

3. Check that the response contains HTTP URLs (not local paths):
   - Response should have `http://127.0.0.1:8642/media/<hash>.png`
   - Not `/tmp/...` local paths

4. Verify Open WebUI renders the image:
   - Navigate to the conversation in Open WebUI
   - Image should display inline

## Pitfalls

- Gateway must be restarted for the code change to take effect
- If the image file is deleted before the gateway serves it, the link breaks
- The `_handle_media` route still only serves from `/tmp/hermes-api-media/` — copied files must be in that directory
- If multiple images with the same content are generated, the hash prevents duplicate copies
- Content-hashed filenames (16 hex chars) prevent filename collisions but make debugging harder — check `/tmp/hermes-api-media/` to map hashes back
