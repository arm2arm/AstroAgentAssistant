Rehomed from skill `openwebui-media-via-s3`.

Summary:
- Upload media to the public S3 bucket `scr4agent` and return pure markdown URLs for Open WebUI.
- Use curl anonymous PUT for this bucket (boto3 fails due to signature headers).
- Provide upload script `~/.hermes/scripts/s3_media_upload.py` and on_media_deliver hook example.
- Video-to-GIF conversion via ffmpeg and fallbacks described.

See archived original for full examples and pitfalls.