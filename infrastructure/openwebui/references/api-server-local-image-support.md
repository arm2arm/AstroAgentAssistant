---
# api-server-local-image-support

Rehomed SKILL.md content from the original skill `api-server-local-image-support`.

Summary:
- Fixes the API server conversion pipeline so standard markdown images with local paths (`![alt](/tmp/file.png)`) are converted into HTTP URLs served via `/media/<hash>`.
- Adds a regex (LOCAL_PATH_MD_RE), a handler `_convert_local_path_image(match)`, and copies files to `/tmp/hermes-api-media` with content-hash filenames.
- Security: verifies absolute paths, allowed extensions, and file existence. Graceful fallback leaves markdown unchanged.

Implementation notes and verification steps are preserved in the original skill; see the archived skill for the full original text.
