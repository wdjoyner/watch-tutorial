#!/usr/bin/env python3
"""Render a scene and produce the finished video with narration and captions.

    python build.py scene01_vertical_city                 # 1080p30 (default)
    python build.py scene01_vertical_city -q l            # fast 480p preview
    python build.py scene01_vertical_city -q k            # 4K
    python build.py scene01_vertical_city --voice am_michael
    python build.py scene01_vertical_city --skip-render   # re-mix audio only

Steps: manim render -> Kokoro TTS for each line of <scene>.voice.txt ->
mix narration with a tick track synced to the escapement -> write .srt ->
mux into out/<scene>.mp4 (with soft subtitles).

Requires ffmpeg on PATH. Kokoro model files (~350 MB) are downloaded once
into models/ on first use.
"""
import argparse, glob, hashlib, os, re, subprocess, sys, urllib.request
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
MODELS = os.path.join(HERE, "models")
CACHE = os.path.join(HERE, "build_cache")
OUT = os.path.join(HERE, "out")
SR = 48000
KOKORO_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/"
KOKORO_FILES = ["kokoro-v1.0.onnx", "voices-v1.0.bin"]
QUALITY = {"l": "480p15", "m": "720p30", "h": "1080p30", "p": "1440p60", "k": "2160p60"}


def run(cmd):
    print("  $", " ".join(cmd))
    subprocess.run(cmd, check=True)


def scene_class(py):
    m = re.search(r"^class\s+(\w+)\s*\(", open(py).read(), re.M)
    if not m:
        sys.exit(f"no Scene class found in {py}")
    return m.group(1)


def read_voice(path):
    lines = []
    for raw in open(path, encoding="utf-8"):
        raw = raw.strip()
        if not raw or raw.startswith("#"):
            continue
        t, text = raw.split("|", 1)
        lines.append((float(t), text.strip()))
    return lines


def ensure_models():
    os.makedirs(MODELS, exist_ok=True)
    for f in KOKORO_FILES:
        p = os.path.join(MODELS, f)
        if not os.path.exists(p):
            print(f"downloading {f} (one time) ...")
            urllib.request.urlretrieve(KOKORO_URL + f, p)


def tts(lines, voice, speed):
    """Return [(start, samples)] at SR; each sentence is cached by text+voice."""
    import soundfile as sf
    os.makedirs(CACHE, exist_ok=True)
    kokoro, out = None, []
    for start, text in lines:
        key = hashlib.sha1(f"{voice}|{speed}|{text}".encode()).hexdigest()[:16]
        wav = os.path.join(CACHE, f"tts_{key}.wav")
        if not os.path.exists(wav):
            if kokoro is None:
                ensure_models()
                from kokoro_onnx import Kokoro
                kokoro = Kokoro(os.path.join(MODELS, KOKORO_FILES[0]), os.path.join(MODELS, KOKORO_FILES[1]))
            audio, sr = kokoro.create(text, voice=voice, speed=speed, lang="en-us")
            sf.write(wav, audio, sr)
        audio, sr = sf.read(wav)
        if sr != SR:   # simple linear resample (Kokoro outputs 24 kHz)
            x = np.arange(len(audio)) / sr
            audio = np.interp(np.arange(int(len(audio) * SR / sr)) / SR, x, audio)
        out.append((start, audio))
    return out


def ticks(duration, beats, level):
    rng = np.random.default_rng(1)
    n = int(SR * duration)
    out = np.zeros(n)
    L = int(0.012 * SR)
    env = np.exp(-np.linspace(0, 9, L))
    tt = np.arange(L) / SR
    for k in range(int(duration * beats)):
        t0 = int(k / beats * SR)
        f = 4200 if k % 2 == 0 else 3700           # alternate tick / tock
        if t0 + L < n:
            out[t0:t0 + L] += (np.sin(2 * np.pi * f * tt) * 0.6 + rng.normal(0, 0.4, L)) * env
    t = np.arange(n) / SR
    return out * np.clip(t / 1.6, 0, 1) * np.clip((duration - t) / 1.5, 0, 1) * level


def srt_time(s):
    ms = int(round(s * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("scene", help="scene file name, e.g. scene01_vertical_city (with or without .py)")
    ap.add_argument("-q", "--quality", default="h", choices=QUALITY, help="l=480p m=720p h=1080p p=1440p k=4K")
    ap.add_argument("--voice", default="bm_george", help="Kokoro voice, e.g. bm_george, am_michael, bf_emma")
    ap.add_argument("--speed", type=float, default=0.92, help="narration speed (1.0 = Kokoro default)")
    ap.add_argument("--tick-level", type=float, default=0.05, help="0 disables the tick track")
    ap.add_argument("--skip-render", action="store_true", help="reuse the last render, redo audio only")
    a = ap.parse_args()

    name = os.path.splitext(os.path.basename(a.scene))[0]
    py = os.path.join(HERE, name + ".py")
    cls = scene_class(py)
    fps_flag = ["--fps", "30"] if a.quality == "h" else []

    if not a.skip_render:
        print(f"[1/4] rendering {cls} at {QUALITY[a.quality]}")
        run(["manim", f"-q{a.quality}", *fps_flag, "--disable_caching", py, cls])
    video = os.path.join(HERE, "media", "videos", name, QUALITY[a.quality], cls + ".mp4")
    if not os.path.exists(video):
        cands = sorted(glob.glob(os.path.join(HERE, "media", "videos", name, "*", cls + ".mp4")), key=os.path.getmtime)
        if not cands:
            sys.exit("no rendered video found; run without --skip-render")
        video = cands[-1]
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                         "-of", "csv=p=0", video]).decode())

    print(f"[2/4] narration ({a.voice})")
    voice_file = os.path.join(HERE, name + ".voice.txt")
    lines = read_voice(voice_file) if os.path.exists(voice_file) else []
    clips = tts(lines, a.voice, a.speed)

    print("[3/4] mixing audio")
    import soundfile as sf
    mix = np.zeros(int(SR * dur))
    vo = np.zeros_like(mix)
    for start, audio in clips:
        i = int(start * SR)
        seg = audio[: max(0, len(vo) - i)]
        vo[i:i + len(seg)] += seg
    peak = np.max(np.abs(vo)) if vo.any() else 1.0
    mix += vo * (0.8 / peak)                        # narration peaks at -2 dBFS
    if a.tick_level > 0:
        sys.path.insert(0, HERE)
        from movement import BEATS
        mix += ticks(dur, BEATS, a.tick_level)
    os.makedirs(OUT, exist_ok=True)
    wav = os.path.join(CACHE, name + "_mix.wav")
    sf.write(wav, np.clip(mix, -1, 1), SR)

    srt = os.path.join(OUT, name + ".srt")
    with open(srt, "w", encoding="utf-8") as f:
        for i, (start, audio) in enumerate(clips, 1):
            f.write(f"{i}\n{srt_time(start)} --> {srt_time(start + len(audio) / SR + 0.2)}\n{lines[i - 1][1]}\n\n")

    print("[4/4] muxing")
    final = os.path.join(OUT, name + ".mp4")
    subs = ["-i", srt] if clips else []              # ffmpeg rejects an empty .srt (e.g. title cards)
    sub_maps = ["-map", "2", "-c:s", "mov_text", "-metadata:s:s:0", "language=eng"] if clips else []
    run(["ffmpeg", "-v", "error", "-y", "-i", video, "-i", wav, *subs,
         "-map", "0:v", "-map", "1:a", *sub_maps, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
         "-t", f"{dur:.3f}", final])
    print(f"\ndone: {os.path.relpath(final)}  ({dur:.1f} s)")


if __name__ == "__main__":
    main()
