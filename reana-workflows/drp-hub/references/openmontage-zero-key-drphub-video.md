# OpenMontage zero-key DRP-Hub explainer pattern

Session-derived workflow for making a small DRP-Hub explainer video without cloud/API keys.

## Use case
- User asks for a short video about `drphub-p4n.aip.de` or DRP-Hub.
- No FAL/OpenAI/ElevenLabs/stock-media keys are available.
- Goal is a concise visual explainer, not AI-generated footage.

## Content beats that worked
1. **Hook:** "DRP Hub — Digital Research Products for reproducible science"
2. **Definition:** DRP packages code, data references, containers, workflow instructions, and results.
3. **Contrast:** static paper/files = inspect; DRP = rerun / executable evidence.
4. **Maturity ladder:** L0 seed → L1 runnable → L2 citable → L3 validated → L4 FAIR publication object.
5. **Infrastructure:** PUNCH4NFDI, AIP, REANA, DRP Hub.
6. **Closing line:** "Publish the path back to the result."

## OpenMontage / Remotion implementation notes
- Use Remotion components (`hero_title`, `callout`, `comparison`, `progress_bar`, `kpi_grid`) with a clean/minimalist theme. This avoids dependence on image/video generation keys.
- Local Piper TTS works for narration, but Remotion asset resolution is stricter than browser preview: copy local narration audio into `remotion-composer/public/` and reference it by relative path in props, e.g. `"src": "drphub-p4n-narration.wav"`.
- If `piper_tts` cannot resolve a model by name even after download, call the `piper` CLI with the full ONNX model path, e.g. `--model ~/.piper/models/en_US-lessac-medium.onnx`.
- Run the render from `remotion-composer/` so `npx remotion` resolves the installed Remotion binary.

## QA checklist
- Verify output with `ffprobe`: duration, resolution, FPS, video codec, audio codec.
- Sample representative frames with `ffmpeg -ss ... -frames:v 1` and inspect with vision tools for legibility/cropping.
- Watch for low-contrast title frames when using light/minimalist themes; darken text or background if the title/subtitle is washed out.
- Confirm narration duration fits the visual duration; add a few seconds of visual padding after narration if needed.

## Example verified output shape
- ~30 seconds
- 1920×1080, 30 fps
- H.264 video + AAC audio
- No cloud API keys required
