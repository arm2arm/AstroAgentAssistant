---
name: manim-video-audio
description: "Add audio to Manim-rendered videos — background music, TTS narration, or SRT subtitles. Handles common pitfalls with MP3 decoding, volume mixing, and timing."
version: 1.0.0
---

# Manim Video Audio — Best Practices

## Background Music

### Step 1: Source the music
```bash
# Fesliyan Studios (royalty-free, calm/ambient) — use curl, NOT Python urllib
curl -L -o /tmp/bgm_tranquility.mp3 \
  -H "Referer: https://www.fesliyanstudios.com/" \
  -H "User-Agent: Mozilla/5.0" \
  "https://www.fesliyanstudios.com/download-link.php?src=i&id=331"
```

**⚠️ Common pitfall**: `urllib.request.urlretrieve()` gets HTTP 403 Forbidden from Fesliyan. Use `curl -L -H "Referer: ..."` instead.

**⚠️ Common pitfall**: The downloaded MP3 has ID3 metadata that causes `ffmpeg -c:a aac` to fail:
```
[mp3] Invalid audio stream. Exactly one MP3 audio stream is required.
```

**Fix**: Never convert MP3→AAC directly. Always use WAV as intermediate:
```bash
# Get video duration
ffprobe -v error -show_entries format=duration \
  -of default=noprint_wrappers=1:nokey=1 video.mp4

# Extract audio, loop if needed, set background volume, output to WAV first
ffmpeg -y -stream_loop -1 -i bgm.mp3 \
  -t <video_duration> \
  -af volume=0.2 \
  -c:a pcm_s16le -ar 44100 -channels 2 \
  /tmp/bgm_audio.wav

# Then convert WAV → AAC
ffmpeg -y -i /tmp/bgm_audio.wav \
  -c:a aac -b:a 192k \
  /tmp/bgm_audio.mp3
```

### Step 2: Mix with video
```bash
ffmpeg -y -i video.mp4 -i /tmp/bgm_audio.mp3 \
  -c:v copy -c:a aac -b:a 192k -shortest \
  output.mp4
```

**Volume levels:**
- Background music: `volume=0.2` (20%)
- Narration priority: `volume=0.8` (80%)
- Very subtle ambience: `volume=0.08` (8%)

## SRT Subtitles (Burned In)

```bash
ffmpeg -y -i video.mp4 \
  -vf "subtitles=subtitles.srt:force_style='Fontsize=24,PrimaryColour=&H00FFFF,OutlineColour=&H00000000,BorderStyle=3,Outline=2,MarginV=40'" \
  -c:a copy \
  output.mp4
```

**Pitfalls:**
- SRT timestamps must fit within video duration — check with `ffprobe`
- Emojis may not render (libass font fallback handles this but may be slow)
- Use `&H00BBGGRR` color format (BGR, not RGB) for `PrimaryColour`

## TTS Narration (German)

```bash
# espeak-ng with German voice
espeak-ng -v de -s 180 -p 35 -a 150 -w audio.wav "Text hier"

# Or for longer texts, split into segments
espeak-ng -v de -s 200 -p 35 -a 150 -w scene.wav "compressed text"
```

**Known issues with espeak-ng:**
- Sound quality is robotic — not suitable for professional videos
- Use TTS only when no human voiceover is available
- For better quality, consider external TTS APIs (ElevenLabs, etc.)

## Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| HTTP 403 on download | Missing Referer header | Use curl with `-H "Referer: ..."`, not urllib |
| Exit 234 / "Invalid audio stream" | MP3 ID3 metadata breaks AAC encoder | Output to WAV (pcm_s16le) first, then WAV→AAC |
| Subtitles not showing | Font missing or SRT timing wrong | Verify timestamps; libass auto-falls back to DejaVuSans |
| Audio cuts off early | `-shortest` picks shortest stream | Ensure audio ≥ video duration (use `-stream_loop -1`) |
| TTS too slow / robotic | espeak-ng voice quality | Acceptable for quick demos; not for professional use |
