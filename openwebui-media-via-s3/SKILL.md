---
name: openwebui-media-via-s3
description: Serve images, videos, and audio to Open WebUI by uploading media to the public S3 bucket (scr4agent), then embedding pure markdown URLs.
category: openwebui-media-via-s3
trigger: media delivery, Open WebUI images, Open WebUI video, OpenAI endpoint media, s3 media upload
---
# Open WebUI Media Delivery via S3

## Problem
When Hermes is used as an OpenAI-compatible endpoint for Open WebUI, media files delivered via `MEDIA:/path/to/file` appear as plain text — Open WebUI doesn't understand the `MEDIA:` protocol (Telegram does).

## Solution
Upload media to the public `scr4agent` S3 bucket and return **pure markdown** (no HTML — Open WebUI sanitizes it):
- **Images** → `![alt](url)` — renders inline
- **Videos** → Auto-converted to animated GIF via ffmpeg → `![alt](url.gif)` — renders inline
- **Audio** → `[♫ name](url)` — clickable link (no inline audio in markdown)

## S3 Bucket Details
- **Endpoint:** `https://s3.data.aip.de:9000`
- **Bucket:** `scr4agent`
- **Auth:** None required — public read/write (unauthenticated PUT via curl)
- **Base URL:** `https://s3.data.aip.de:9000/scr4agent/`

## Canonical Upload (use this)
The upload script auto-detects file type, converts videos to GIFs, and returns pure markdown:

```bash
python3 ~/.hermes/scripts/s3_media_upload.py <filepath>
```

**Output examples:**
- Image: `![plot.png](https://s3.data.aip.de:9000/scr4agent/hermes/abcd1234.png)`
- Video: `![animation.mp4 (as GIF)](https://s3.data.aip.de:9000/scr4agent/hermes/abcd1234.gif)`
- Video (fallback if conversion fails): `[▶ animation.mp4](https://s3.data.aip.de:9000/scr4agent/hermes/abcd1234.mp4)`
- Audio: `[♫ audio.mp3](https://s3.data.aip.de:9000/scr4agent/hermes/abcd1234.mp3)`

**Extra commands:**
```bash
python3 ~/.hermes/scripts/s3_media_upload.py --list          # list recent uploads
python3 ~/.hermes/scripts/s3_media_upload.py --delete <key>  # delete a file
```

**Environment overrides:**
```bash
HERMES_S3_ENDPOINT=https://s3.data.aip.de:9000
HERMES_S3_BUCKET=scr4agent
HERMES_S3_PREFIX=hermes/
```

## Hook (automated)
```bash
~/.hermes/hooks/on_media_deliver.sh <filepath>
```
Calls the upload script and returns the markdown.

## Manual Upload (curl, no SDK needed)
```bash
curl -X PUT \
  -H "Content-Type: image/png" \
  --upload-file /path/to/file.png \
  "https://s3.data.aip.de:9000/scr4agent/hermes/unique-uuid.png"
```

## Video to GIF Conversion (manual)
```bash
ffmpeg -y -i input.mp4 \
  -vf "fps=10,scale=480:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" \
  -loop 0 output.gif
```
The upload script does this automatically for `.mp4`, `.webm`, `.mov`, `.avi`, `.mkv` files.

## Response Format for Open WebUI
Instead of `MEDIA:/path/to/file.png`, return the markdown output from the upload script.

## Workflow
1. Generate media file locally (plot, animation, etc.)
2. Upload via: `python3 ~/.hermes/scripts/s3_media_upload.py <filepath>`
3. Script outputs markdown — include it directly in the response
4. Open WebUI renders it natively

## Pitfalls
- **HTML is sanitized by Open WebUI** — `<video>`, `<audio>`, and other HTML tags are stripped. Only use pure markdown (`![alt](url)`, `[link](url)`).
- **boto3 fails on public buckets** — the bucket requires unauthenticated PUT. boto3 sends AWS signature headers which cause `InvalidAccessKeyId` errors. Always use curl for uploads to this bucket.
- **No auth on uploads** — anyone who guesses a filename can overwrite. The script uses UUID-prefixed keys like `hermes/<uuid>.ext`.
- **No auto-expiry** — files persist until manually deleted. Consider cleanup scripts for long-term use.
- **Video-to-GIF conversion requires ffmpeg** — if ffmpeg is not available or fails, the script falls back to a clickable link `[▶ name](url)`.
- **GIF quality** — uses palette generation for better colors, 10fps, 480px wide. For longer animations, GIFs can be large.
- **Audio has no inline markdown** — only clickable links `[♫ name](url)`. Users must click to play in their browser.
- **Content-Type** — set correctly on upload (`image/png`, `image/gif`, `video/mp4`, `audio/mpeg`) so the browser renders it (the script detects this from file extension).
- **Large files** — works well (no base64 bloat), but be mindful of bucket storage.
- **Telegram vs Open WebUI** — on Telegram, use `MEDIA:` as normal. Only use S3 URLs when the delivery target is Open WebUI / OpenAI endpoint.
