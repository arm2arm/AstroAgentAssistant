Rehomed from skill `api-server-media-display`.

Summary:
- Diagnose and fix images not displaying in Open WebUI/API server frontends.
- Explains conversion pipeline in gateway/platforms/api_server.py: DATA_URI_RE, MEDIA_TAG_RE, LOCAL_PATH_MD_RE.
- Provides regex, handler, and pipeline insertion example to convert `![alt](/tmp/file.png)` into `http://{host}/media/<hash>.png`.
- Verification steps: py_compile, restart gateway, curl test, Open WebUI render checks.

Original archived at: ~/.hermes/skills/.archive/api-server-media-display (full SKILL.md moved there).