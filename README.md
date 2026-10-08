# watch-tutorial

**Animated, narrated tutorial videos on how a mechanical watch movement works, built entirely in code with [Manim](https://www.manim.community/).**

Every part of the movement (plate, going train, lever escapement, balance, bridges, automatic rotor) is generated procedurally. The parts move with physically consistent kinematics: wheels and pinions share one tooth module and actually mesh, and the escape wheel steps at 28,800 vibrations per hour. The narration is synthesized locally with the open-source Kokoro voice model. One command takes a scene from source to a finished MP4 with voice, an escapement tick track and captions.

The visual style is technical illustration: solid parts with visible thickness, Côtes de Genève striping, perlage, ruby jewels and blued screws, all shown against a dark studio background.

---

## Scenes

| # | File | Length | What it shows |
|---|------|--------|---------------|
| 01 | `scene01_vertical_city.py` | 33 s | "The Vertical City": an assembled automatic movement explodes into three tiers (dial side, middle engine, top modules), then the camera tours each tier. |

## Quick start (macOS)

```bash
brew install ffmpeg pkg-config cairo pango
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python build.py scene01_vertical_city            # finished 1080p video -> out/
```

On first run, `build.py` downloads the Kokoro voice model (~350 MB) into `models/`. After that, everything runs offline.

## Building

```bash
python build.py scene01_vertical_city -q l            # fast 480p preview (~3 min)
python build.py scene01_vertical_city                 # 1080p30 (default)
python build.py scene01_vertical_city -q k            # 4K
python build.py scene01_vertical_city --skip-render   # re-voice / re-mix only, no re-render
python build.py scene01_vertical_city --voice am_michael --speed 1.0
python build.py scene01_vertical_city --tick-level 0  # no ticking
```

Each build writes `out/<scene>.mp4`, which has soft subtitles embedded, and `out/<scene>.srt`.

To render the picture alone, run Manim directly: `manim -ql scene01_vertical_city.py Scene01`.

## Making changes

Most adjustments need no code changes:

- **Timing, camera, labels, title, tier heights, glow:** use the `SETTINGS` block at the top of each scene file. Every value there is commented.
- **Narration:** use `<scene>.voice.txt`, which has one `start_seconds | sentence` line per sentence. Then run `build.py --skip-render` to re-voice without re-rendering. Sentences are cached, so only edited lines are regenerated.
- **Colors, fonts, rotor engraving:** these are at the top of `movement.py`.
- **Voice:** pass `--voice` to `build.py`. The default is `bm_george` (British male). Other options include `am_michael` and `am_onyx` (American male) and `bf_emma` (British female). Kokoro has many more.

Structural changes, such as new parts, new motion or new shots, go in `movement.py` or a new scene file.

## Project layout

```
movement.py                         the shared watch model: parts, kinematics, animation driver
scene01_vertical_city.py            scene 01 (SETTINGS block + timeline)
scene01_vertical_city.voice.txt     scene 01 narration with start times
build.py                            render -> TTS -> mix -> captions -> mux
CLAUDE.md                           working notes for AI-assisted editing
requirements.txt
media/  out/  build_cache/  models/ generated (git-ignored)
```

## How it works

**Geometry.** Parts are built as 2D [Shapely](https://shapely.readthedocs.io/) polygons, so holes, windows, spokes and clipped finishes are just boolean operations. They are then converted to Manim `VMobject`s. `slab()` gives each part visible thickness by drawing a darker copy beneath the top face. The movement is 6 scene units across, with the center wheel at the origin and +z pointing up toward the rotor.

**Three tiers.** `Movement` builds three groups: `dial` (main plate, motion works, keyless works), `engine` (barrel, going train, escapement, balance) and `top` (bridges, winding wheels, rotor). Individual parts are reachable through `Movement.parts[...]`.

**Kinematics.** The pivot layout follows from pitch radii, and `state(t)` returns every part's angle at time *t*. The escape wheel advances one half-tooth per beat at 8 beats per second, and the fourth, third, center and barrel wheels follow from their tooth ratios. The balance oscillates at 4 Hz, and the rotor swings freely.

**One driver.** `attach_driver()` installs a single updater that sets tier heights from an `explode` tracker, sets per-tier opacity from `dim` trackers, and rotates every moving part. Scenes animate the trackers, never the tiers themselves, because `.animate` on a group suspends its updaters.

**Draw order.** Parts are added bottom-to-top (painter's algorithm), which is correct while the camera looks down on the movement (`phi` < 90°).

## Relation to PAM

This project uses plain Manim rather than [PAM](https://github.com/wdjoyner/pam)'s character and screenplay system. It follows the same approach, though: animation as code, scripted from text files, and rendered reproducibly.

## Credits

- Animation: [Manim Community](https://www.manim.community/)
- Geometry: [Shapely](https://shapely.readthedocs.io/)
- Narration: [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M) (Apache 2.0) via [kokoro-onnx](https://github.com/thewh1teagle/kokoro-onnx)
