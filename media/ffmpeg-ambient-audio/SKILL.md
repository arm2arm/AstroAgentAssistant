---
name: ffmpeg-ambient-audio
title: Generate Ambient Background Music with FFmpeg
description: >-
  Create layered ambient pad music using FFmpeg's aevalsrc filter.
  Generates loopable 15-second clips with slow vibrato, shimmer, and exponential decay,
  then loops to target duration. Mixes into video at low volume for BGM.
author: Hermi
date: 2026-04-16
tags: [audio, ffmpeg, manim, bgm, ambient]
---

## Overview

Generates quiet ambient background music for tutorial/animation videos using
pure FFmpeg — no external audio files or Python audio libraries needed.

## Prerequisites

- FFmpeg installed (usually available)

## Step‑by‑Step Procedure

### 1. Generate a 15-second ambient loop

```bash
ffmpeg -y -f lavfi \
  -i "aevalsrc='0.3*sin(2*PI*65.41*t)+0.25*sin(2*PI*98.0*t*(1+0.01*sin(2*PI*0.15*t)))+0.2*sin(2*PI*130.81*t)+0.15*sin(2*PI*164.81*t)*(0.5+0.5*sin(2*PI*0.05*t))+0.08*sin(2*PI*329.63*t)*exp(-0.02*t)':s=44100:d=15:c=stereo" \
  -af "afade=t=in:st=0:d=3,afade=t=out:st=12:d=3" \
  -c:a libvorbis -b:a 128k loop.ogg
```

Layered notes (C major chord progression):
- 65.41 Hz (C2) — deep bass drone, 30%
- 98.0 Hz (G2) — mid pad with slow vibrato, 25%
- 130.81 Hz (C3) — upper pad, 20%
- 164.81 Hz (E3) — shimmer with slow pulsing, 15%
- 329.63 Hz (C4) — ethereal high tone with exponential decay, 8%

Fade in/out of 3 seconds each for seamless looping.

### 2. Extend to full video duration

```bash
ffmpeg -y -stream_loop -1 -i loop.ogg -t <DURATION> -c:a libvorbis -b:a 128k bgm.ogg
```

`-stream_loop -1` repeats until `-t` duration is reached.

### 3. Mix into video

**If video has no audio track:**
```bash
ffmpeg -y -i video.mp4 -i bgm.ogg \
  -filter_complex "[1:a]volume=0.15[a]" \
  -map 0:v -map "[a]" \
  -c:v copy -c:a aac -b:a 192k -shortest output.mp4
```

**If video has existing audio, mix BGM underneath:**
```bash
ffmpeg -y -i video.mp4 -i bgm.ogg \
  -filter_complex "[1:a]volume=0.15[a];[0:a][a]amix=inputs=2:duration=first:dropout_transition=3[aout]" \
  -map 0:v -map "[aout]" \
  -c:v copy -c:a aac -b:a 192k -shortest output.mp4
```

### 4. Verify

```bash
ffprobe -v quiet -show_entries format=duration,size \
  -show_entries stream=codec_type,codec_name -of json output.mp4
```

## Key Parameters

| Parameter | Purpose |
|-----------|---------|
| `s=44100` | Sample rate (44.1 kHz CD quality) |
| `c=stereo` | Stereo output |
| `afade=t=in/out` | Smooth fade for loop seams |
| `volume=0.15` | BGM volume (15% — quiet background) |
| `amix=dropout_transition=3` | Graceful audio track blending |
| `-shortest` | Stop at shortest input (video duration) |

## Pitfalls

- **Don't use raw sine waves without mixing** — pure sine tones sound harsh. Layer at low volumes for ambient texture.
- **Volume 0.15 is quiet** — if too quiet, try 0.20-0.25. If too loud, try 0.10.
- **`-stream_loop -1`** means infinite loop — always pair with `-t <seconds>`.
- **Check if video has audio** first (`ffprobe -select_streams a`), because the mix command differs.
- **Vorbis for BGM** (smaller file), AAC for final video output (better compatibility).

## Verification

After mixing, the output video should have:
- Ambient pad music playing quietly underneath
- No audio clipping or distortion
- Smooth fade-in and fade-out at start/end
- Duration matches the video