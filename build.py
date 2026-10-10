#!/usr/bin/env python3
"""Render a scene and produce the finished video with narration and captions.

    python build.py scene01_vertical_city                 # 1080p30 (default)
    python build.py scene01_vertical_city -q l            # fast 480p preview
    python build.py scene01_vertical_city -q k            # 4K
    python build.py scene01_vertical_city --voice am_michael
    python build.py scene01_vertical_city --skip-render   # re-mix audio only
    python build.py 2/scene00_title                       # <film>/<scene> when the name is in several films

Scenes live in films/filmNN_<name>/ (see films.py). The film can be given by
number (2), prefix (film02) or folder name; a bare scene name works when only
one film has it. Output goes to out/<film folder>/<scene>.mp4.

Steps: manim render -> Kokoro TTS for each line of <scene>.voice.txt ->
mix narration with a tick track synced to the escapement (and any sound
effects listed in <scene>.sfx.txt) -> write .srt ->
mux into out/<scene>.mp4 (with soft subtitles).

Requires ffmpeg on PATH. Kokoro model files (~350 MB) are downloaded once
into models/ on first use.
"""
import argparse, glob, hashlib, os, re, subprocess, sys, urllib.request
import numpy as np
from films import find_scene

HERE = os.path.dirname(os.path.abspath(__file__))
MODELS = os.path.join(HERE, "models")
CACHE = os.path.join(HERE, "build_cache")
OUT = os.path.join(HERE, "out")
SR = 48000
KOKORO_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/"
KOKORO_FILES = ["kokoro-v1.0.onnx", "voices-v1.0.bin"]
# Words Kokoro mispronounces, respelled for the voice only (captions keep the real
# spelling). Kokoro reads "wound" as the injury and "wind" as moving air; in these
# films both always mean winding. Whole words, case-insensitive.
PRONOUNCE = {"wound": "wownd", "wind": "wined"}
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


def spoken(text):
    """The text as Kokoro should say it (see PRONOUNCE)."""
    def fix(m):
        w = PRONOUNCE[m.group(0).lower()]
        return w[0].upper() + w[1:] if m.group(0)[0].isupper() else w
    return re.sub(r"\b(" + "|".join(PRONOUNCE) + r")\b", fix, text, flags=re.I)


def tts(lines, voice, speed):
    """Return [(start, samples)] at SR; each sentence is cached by text+voice."""
    import soundfile as sf
    os.makedirs(CACHE, exist_ok=True)
    kokoro, out = None, []
    for start, text in lines:
        text = spoken(text)
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


def click_sound():
    """A short metallic click: a filtered noise burst with a bright ring."""
    rng = np.random.default_rng(7)
    L = int(0.018 * SR)
    t = np.arange(L) / SR
    env = np.exp(-t / 0.0028)
    s = (np.sin(2 * np.pi * 5200 * t) * 0.5 + np.sin(2 * np.pi * 2900 * t) * 0.35 + rng.normal(0, 0.5, L)) * env
    return s / np.max(np.abs(s))


SOUNDS = {"click": click_sound}


def read_sfx(path):
    """<scene>.sfx.txt: one `time_in_seconds | sound [| level]` per line (sound: click)."""
    out = []
    for raw in open(path, encoding="utf-8"):
        raw = raw.strip()
        if not raw or raw.startswith("#"):
            continue
        parts = [x.strip() for x in raw.split("|")]
        out.append((float(parts[0]), parts[1], float(parts[2]) if len(parts) > 2 else 1.0))
    return out


def srt_time(s):
    ms = int(round(s * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("scene", help="scene name, e.g. scene01_vertical_city, or <film>/<scene>, e.g. 2/scene00_title")
    ap.add_argument("-q", "--quality", default="h", choices=QUALITY, help="l=480p m=720p h=1080p p=1440p k=4K")
    ap.add_argument("--voice", default="bm_george", help="Kokoro voice, e.g. bm_george, am_michael, bf_emma")
    ap.add_argument("--speed", type=float, default=0.92, help="narration speed (1.0 = Kokoro default)")
    ap.add_argument("--tick-level", type=float, default=0.05, help="0 disables the tick track")
    ap.add_argument("--sfx-level", type=float, default=0.16, help="level of sound effects from <scene>.sfx.txt; 0 disables")
    ap.add_argument("--skip-render", action="store_true", help="reuse the last render, redo audio only")
    a = ap.parse_args()

    film, name = find_scene(a.scene)
    fdir = os.path.join(HERE, "films", film)
    py = os.path.join(fdir, name + ".py")
    if not os.path.exists(py):
        sys.exit(f"no scene file {os.path.relpath(py, HERE)}")
    cls = scene_class(py)
    fps_flag = ["--fps", "30"] if a.quality == "h" else []
    media = os.path.join(HERE, "media", film)       # one media dir per film: scene names repeat across films
    # scenes import the shared movement.py (repo root) and any helpers in their own film folder
    env = dict(os.environ, PYTHONPATH=os.pathsep.join([HERE, fdir] + [p for p in [os.environ.get("PYTHONPATH")] if p]))

    if not a.skip_render:
        print(f"[1/4] rendering {film}/{name} ({cls}) at {QUALITY[a.quality]}")
        print("  $ manim", f"-q{a.quality}", *fps_flag, "--disable_caching", "--media_dir", media, py, cls)
        subprocess.run(["manim", f"-q{a.quality}", *fps_flag, "--disable_caching", "--media_dir", media, py, cls],
                       check=True, env=env)
    video = os.path.join(media, "videos", name, QUALITY[a.quality], cls + ".mp4")
    if not os.path.exists(video):
        cands = sorted(glob.glob(os.path.join(media, "videos", name, "*", cls + ".mp4")), key=os.path.getmtime)
        if not cands:
            sys.exit("no rendered video found; run without --skip-render")
        video = cands[-1]
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                         "-of", "csv=p=0", video]).decode())

    print(f"[2/4] narration ({a.voice})")
    voice_file = os.path.join(fdir, name + ".voice.txt")
    lines = read_voice(voice_file) if os.path.exists(voice_file) else []
    clips = tts(lines, a.voice, a.speed)

    tail = max((s + len(c) / SR for s, c in clips), default=0.0) + 0.4
    pad = max(0.0, tail - dur)
    if pad > 0:
        print(f"  WARNING: the narration runs {pad:.2f} s past the end of the animation; the last frame is held"
              f" to fit. Lengthen the scene's final hold (or move the line earlier) to fix it properly.")
        dur += pad
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
    out = os.path.join(OUT, film)
    sfx_file = os.path.join(fdir, name + ".sfx.txt")
    if a.sfx_level > 0 and os.path.exists(sfx_file):
        bank = {}
        for t0, snd, lvl in read_sfx(sfx_file):
            clip = bank.setdefault(snd, SOUNDS[snd]())
            i = int(t0 * SR)
            seg = clip[: max(0, len(mix) - i)]
            mix[i:i + len(seg)] += seg * a.sfx_level * lvl
    os.makedirs(out, exist_ok=True)
    wav = os.path.join(CACHE, f"{film}_{name}_mix.wav")
    sf.write(wav, np.clip(mix, -1, 1), SR)

    srt = os.path.join(out, name + ".srt")
    with open(srt, "w", encoding="utf-8") as f:
        for i, (start, audio) in enumerate(clips, 1):
            f.write(f"{i}\n{srt_time(start)} --> {srt_time(start + len(audio) / SR + 0.2)}\n{lines[i - 1][1]}\n\n")

    print("[4/4] muxing")
    final = os.path.join(out, name + ".mp4")
    subs = ["-i", srt] if clips else []              # ffmpeg rejects an empty .srt (e.g. title cards)
    sub_maps = ["-map", "2", "-c:s", "mov_text", "-metadata:s:s:0", "language=eng"] if clips else []
    vcodec = ["-c:v", "copy"] if pad == 0 else \
        ["-vf", f"tpad=stop_mode=clone:stop_duration={pad:.3f}", "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p"]
    run(["ffmpeg", "-v", "error", "-y", "-i", video, "-i", wav, *subs,
         "-map", "0:v", "-map", "1:a", *sub_maps, *vcodec, "-c:a", "aac", "-b:a", "192k",
         "-t", f"{dur:.3f}", final])
    print(f"\ndone: {os.path.relpath(final)}  ({dur:.1f} s)")


if __name__ == "__main__":
    main()
