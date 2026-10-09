#!/usr/bin/env python3
"""Join the finished scenes into one film, with merged subtitles and chapters.

    python film.py                  # join the videos already in out/
    python film.py --build          # build every scene first (1080p30), then join
    python film.py --build -q l     # quick 480p preview of the whole film

Each scene is built separately by build.py into out/<scene>.mp4; this script
only joins them (no re-encoding), so after changing one scene, rebuild just
that scene and rerun `python film.py`. All scenes must be built at the same
quality. Output: out/<OUT_NAME>.mp4 (soft subtitles + chapter markers) and
out/<OUT_NAME>.srt, plus a YouTube chapter list printed at the end.
"""
import argparse, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")

# =====================================================================
# SETTINGS - the running order, chapter names, and the film's title.
# =====================================================================
TITLE = "Learning How Watches Work: Movement Architecture"
OUT_NAME = "movement_architecture"
SCENES = [
    ("scene00_title", "Title"),
    ("scene01_vertical_city", "The Vertical City"),
    ("scene02_dial_side", "Tier 1: The Dial Side"),
    ("scene03_core_engine", "Tier 2: The Core Engine"),
    ("scene04_top_modules", "Tier 3: The Top Works"),
    ("scene05_spines", "The Spines"),
    ("scene06_credits", "Credits"),
]
# =====================================================================


def run(cmd):
    print("  $", " ".join(cmd))
    subprocess.run(cmd, check=True)


def probe(path):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                   "stream=width,height,r_frame_rate:format=duration", "-of", "default=nw=1",
                                   path]).decode()
    info = dict(line.split("=", 1) for line in out.split())
    return (info["width"], info["height"], info["r_frame_rate"]), float(info["duration"])


def srt_seconds(s):
    h, m, rest = s.split(":")
    sec, ms = rest.split(",")
    return int(h) * 3600 + int(m) * 60 + int(sec) + int(ms) / 1000


def srt_time(s):
    ms = int(round(s * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def read_srt(path):
    if not os.path.exists(path):
        return []
    cues = []
    for block in re.split(r"\n\s*\n", open(path, encoding="utf-8").read().strip()):
        lines = block.strip().splitlines()
        if len(lines) >= 3 and "-->" in lines[1]:
            a, b = [srt_seconds(x.strip()) for x in lines[1].split("-->")]
            cues.append((a, b, "\n".join(lines[2:])))
    return cues


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--build", action="store_true", help="build every scene with build.py first")
    ap.add_argument("-q", "--quality", default="h", help="quality passed to build.py with --build (l m h p k)")
    a = ap.parse_args()

    if a.build:
        for name, _ in SCENES:
            print(f"\n=== building {name}")
            run([sys.executable, os.path.join(HERE, "build.py"), name, "-q", a.quality])

    # check that every scene exists and they all match
    vids, fmt0, missing = [], None, []
    for name, chapter in SCENES:
        p = os.path.join(OUT, name + ".mp4")
        if not os.path.exists(p):
            missing.append(name)
            continue
        fmt, dur = probe(p)
        vids.append((name, chapter, p, dur, fmt))
    if missing:
        sys.exit("not built yet: " + ", ".join(missing) + "\nrun `python build.py <scene>` for each, or use --build")
    fmts = {v[4] for v in vids}
    if len(fmts) > 1:
        lines = [f"  {n}: {f[0]}x{f[1]} @ {f[2]}" for n, _, _, _, f in vids]
        sys.exit("the scenes were built at different qualities; rebuild the odd ones out:\n" + "\n".join(lines))

    tmp = os.path.join(HERE, "build_cache", "film")
    os.makedirs(tmp, exist_ok=True)

    # 1) video + audio only from each scene (subtitle tracks differ between scenes), then join without re-encoding
    print("[1/3] joining", len(vids), "scenes")
    listing = os.path.join(tmp, "list.txt")
    with open(listing, "w") as f:
        for name, _, p, _, _ in vids:
            av = os.path.join(tmp, name + ".mp4")
            run(["ffmpeg", "-v", "error", "-y", "-i", p, "-map", "0:v", "-map", "0:a", "-c", "copy", av])
            f.write(f"file '{av}'\n")
    joined = os.path.join(tmp, "joined.mp4")
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", listing, "-c", "copy", joined])

    # 2) merged subtitles and chapter markers, offset by each scene's start time
    print("[2/3] subtitles and chapters")
    cues, chapters, start = [], [], 0.0
    for name, chapter, _, dur, _ in vids:
        cues += [(start + x, start + y, text) for x, y, text in read_srt(os.path.join(OUT, name + ".srt"))]
        chapters.append((start, start + dur, chapter))
        start += dur
    srt = os.path.join(OUT, OUT_NAME + ".srt")
    with open(srt, "w", encoding="utf-8") as f:
        for i, (x, y, text) in enumerate(cues, 1):
            f.write(f"{i}\n{srt_time(x)} --> {srt_time(y)}\n{text}\n\n")
    meta = os.path.join(tmp, "chapters.txt")
    with open(meta, "w", encoding="utf-8") as f:
        f.write(f";FFMETADATA1\ntitle={TITLE}\n")
        for x, y, chapter in chapters:
            f.write(f"\n[CHAPTER]\nTIMEBASE=1/1000\nSTART={int(x * 1000)}\nEND={int(y * 1000)}\ntitle={chapter}\n")

    # 3) final mux
    print("[3/3] muxing")
    final = os.path.join(OUT, OUT_NAME + ".mp4")
    run(["ffmpeg", "-v", "error", "-y", "-i", joined, "-i", srt, "-i", meta,
         "-map", "0:v", "-map", "0:a", "-map", "1", "-map_metadata", "2", "-map_chapters", "2",
         "-c:v", "copy", "-c:a", "copy", "-c:s", "mov_text", "-metadata:s:s:0", "language=eng", final])

    print(f"\ndone: {os.path.relpath(final)}  ({start:.1f} s)\n\nYouTube chapters:")
    for x, _, chapter in chapters:
        print(f"{int(x) // 60}:{int(x) % 60:02d} {chapter}")


if __name__ == "__main__":
    main()
