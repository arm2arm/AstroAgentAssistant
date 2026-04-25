---
name: image-description-workflow
description: Workflow for handling user‑submitted images, generating a description via vision_analyze, and responding.
---

## Trigger
When a user sends an image (or provides an image path) and asks for a description.

## Steps
1. **Validate the image path**
   - Ensure the provided `image_url` points to a readable file (PNG, JPG, JPEG, GIF, BMP) inside the allowed cache directory (e.g., `/home/hermes/.hermes/image_cache/...`).
   - If the path is missing, empty, or the file does not exist, politely ask the user to resend the image.
2. **Run vision analysis**
   - Call `vision_analyze` with the `image_url`.
   - Capture the JSON response; it should contain a `description` field (or similar textual output).
3. **Check analysis success**
   - If a clear description is returned, format it for the user.
   - If the tool returns an error, an empty description, or unreadable content, fall back to a polite request for a different image.
4. **Compose the reply**
   - Begin with a brief acknowledgment (e.g., "Here’s what I see:").
   - Include the full description.
   - If the description is long, optionally add a short summary.
5. **Error handling**
   - For permission errors, unsupported formats, or corrupted files, inform the user of the specific issue and ask for a replacement image.

## Pitfalls
- The `vision_analyze` tool only accepts files inside the image cache; using any other path will fail.
- Some images may be corrupted; catching the error and asking for a new image prevents dead‑ends.
- Do not assume the user wants the image stored permanently; only generate a description.

## Verification
- After sending the description, ask the user if the output was helpful or if they need more detail.

## Example Output
```
Here’s what I see in the image:
- A blue‑green landscape with mountains in the background.
- A river flowing from left to right, reflecting the sky.
- Sunlight filtering through clouds, casting shadows.

Let me know if you’d like a closer look at any part of the picture!
```