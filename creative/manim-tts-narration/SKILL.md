---
name: manim-tts-narration
description: "Add German TTS narration to Manim educational videos using espeak-ng. Handles scene-by-scene audio generation, duration management, and merging with video."
version: 1.0.0
---

# Manim TTS Narration — Adding German Voiceover

## Overview

This skill adds German text-to-speech narration to Manim-rendered educational videos using `espeak-ng`.

## Step-by-Step Procedure

### 1. Prepare the TTS script

Create a Python script that defines narration per scene:

```python
#!/usr/bin/env python3
"""Add German TTS narration to a Manim video."""
import subprocess
import os

AUDIO_DIR = "/tmp/tts_audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

scenes = [
    ("scene01_intro.mp3", "Kurzer Text für die Einleitung.", 5),
    ("scene02_explanation.mp3", "Etwas längerer Erklärungstext hier.", 10),
    ("scene03_summary.mp3", "Zusammenfassung.", 5),
]
```

**Key rules:**
- Each tuple: `(filename, german_text, duration_hint_in_seconds)`
- **Condense text** to fit the video — TTS at 200 wpm reads ~3-4 chars/sec
- Use single quotes inside the script, double quotes for string delimiters
- Avoid complex punctuation; use periods and commas only

### 2. Generate WAV files with espeak-ng

```python
for fname, text, _ in scenes:
    out_path = os.path.join(AUDIO_DIR, fname)
    cmd = [
        "espeak-ng",
        "-v", "de",           # German voice
        "-s", "200",          # Speaking rate (155=default, 200=faster)
        "-p", "35",           # Pitch (0-99, 50=high, 35=natural)
        "-a", "150",          # Amplitude (0-200)
        "-w", out_path.replace(".mp3", ".wav"),
        text,
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    # Convert WAV to MP3
    subprocess.run([
        "ffmpeg", "-y", "-i", out_path.replace(".mp3", ".wav"),
        "-b:a", "192k", out_path
    ], capture_output=True, check=True)
```

**Voice parameters tuned for educational content:**
- `-s 200` — faster rate for classroom pacing
- `-p 35` — natural mid-range pitch
- `-a 150` — clear volume

### 3. Concatenate audio clips

```python
# Build concat list
concat_file = os.path.join(AUDIO_DIR, "concat.txt")
with open(concat_file, "w") as f:
    for fname, _, _ in scenes:
        f.write(f"file '{os.path.join(AUDIO_DIR, fname)}'\n")

# Concatenate into single narration
final_audio = os.path.join(AUDIO_DIR, "narration.mp3")
subprocess.run([
    "ffmpeg", "-y", "-f", "concat", "-safe", "0",
    "-i", concat_file, "-b:a", "192k", final_audio
], capture_output=True, check=True)
```

### 4. Merge with video

```python
video = "/path/to/manim_output.mp4"
output = "/path/to/with_narration.mp4"
subprocess.run([
    "ffmpeg", "-y",
    "-i", video,
    "-i", final_audio,
    "-c:v", "copy",    # No video re-encode
    "-c:a", "aac",
    "-b:a", "192k",
    output
], capture_output=True, check=True)
```

## Troubleshooting

| Problem | Solution |
|---|---|
| Narration too long for video | Increase `-s` rate to 200-220, or shorten text |
| Narration too short | Decrease `-s` rate, or add `wait()` pauses in Manim |
| `ValueError: too many values to unpack` | Check tuple commas — multi-line strings need all commas on correct lines |
| `SyntaxError: unterminated string` | Don't use nested quotes; use single-quoted strings with double quotes inside or vice versa |
| `NameError: log not defined` | Import numpy: `import numpy as np`, use `np.log(x)/np.log(base)` |
| TTS sounds robotic | Adjust `-p` (pitch) and `-s` (speed); try `-p 40` for warmer tone |

## Text Duration Estimation

At 200 wpm (~115 words/min), German text reads at roughly **1.9 words/sec** or **~10 chars/sec**. Use this rule of thumb:
- 100 chars ≈ 10 seconds
- 200 chars ≈ 20 seconds
- 300 chars ≈ 30 seconds

## Delivering to Telegram

After merging:
```
MEDIA:/path/to/with_narration.mp4
```
