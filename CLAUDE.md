# Notes for AI-assisted editing

Read this first. Read code only as needed. For a SETTINGS or voice-text change, open just that block or file.

## Files
- `movement.py`: shared watch model, based on the ETA 6497-1 (hand-wound, 18,000 vph, no rotor). Palette and fonts, tooth counts (`TEETH`), pivot layout (`P`), `state(t)` kinematics, geometry helpers (`vm`, `slab`, `wheel_g`, `teeth_g`, `stripes_g`, …), the `Movement` class (tiers `dial` / `engine` / `top`, `parts` dict, `rot` list), `attach_driver()`.
- `films/filmNN_<name>/`: one folder per film. Film 1 is `film01_movement_architecture`; Film 2 (mainspring and barrel) is `film02_power_source`.
  - `sceneNN_*.py`: one Manim scene per file. `SETTINGS` block at the top, then the timeline. Scenes import from the shared `movement.py` (build.py puts the repo root on `PYTHONPATH`).
  - `sceneNN_*.voice.txt`: narration, `start_seconds | sentence`.
  - `running_order.py`: `TITLE`, `OUT_NAME`, and `SCENES` (file, chapter name) for that film.
  - Film-local helper modules may sit beside the scenes (build.py also puts the film folder on `PYTHONPATH`). Film 2's `barrel.py` is the close-up mainspring barrel (`BarrelModel`: trackers `explode`, `lift`, `drum_turn`, `arbor_turn`, `show_cover`; `anchor()` gives points on parts for labels).
- `films.py`: resolves a film (`2`, `film02`, or folder name) and a scene (`scene03_x`, or `2/scene00_title` when the name occurs in several films).
- `build.py`: render → Kokoro TTS (cached per sentence) → tick track → .srt → `out/<film>/<scene>.mp4`. Manim media goes to `media/<film>/`.
- `film.py <film>`: joins that film's built scenes in running order into `out/<OUT_NAME>.mp4` with merged subtitles and chapters; no re-encoding. Each film's `scene00_title.py` and last scene are the title and credits cards (no narration).

## Rules that matter
- Never `.animate` a tier or a rotating part, because that suspends the driver updater. Animate the trackers returned by `attach_driver` instead (`explode`, `dim[tier]`), or the camera.
- Add parts bottom-to-top within a tier (painter's algorithm). Use `lift(m, dz)` for small z offsets inside a tier.
- A new rotating part needs an entry in `Movement.rot`: `(mobject, pivot_xy, tier, lambda s: angle)`. Derive its angle from `state()` so speeds stay consistent with the gear ratios.
- A train wheel's center distance must equal the sum of the pitch radii. Each going-train mesh has its own module (`MESH`), chosen so the traced 6497 pivot positions mesh exactly; use `R[...]` for radii.
- The dial tier is built dial side up (its own frame: positions mirrored with `dv()`, dial face at z = 0) and fitted dial side down under the plate. Animate `mv.flip` (0 -> 1) to turn it over; `Movement(dial_up=True)` starts it turned. Dial-tier `rot` pivots and angles are in that dial-up frame; `mv.world(tier, xy, z)` converts to world coordinates.
- Winding and regulating: animate `mv.wind` (crown turns) and `mv.regulate` (degrees), never the parts.
- Screen-fixed text uses `add_fixed_in_frame_mobjects`.
- Timed cues during a camera move: build the move with `camera_move()` and wrap each cue in `cue(when, ..., start=, end=)`, both in `movement.py`. `move_camera(added_anims=...)` passes its run_time and rate_func to every added animation, which stretches the cues.
- To center a 3D point on screen, use `camera_move(..., target=p, frame_origin=<the scene's starting frame_center>)`. Manim's Cairo 3D camera shifts the picture by the starting frame_center, so a plain `frame_center=p` lands off-center.
- Check framing in a real `-q l` video, not a `-s` still: a still only renders the last frame, so it hides the frame_center offset.
- Don't render several scenes in parallel: they share Manim's text cache and can corrupt it (fix: `find media -path "*texts*" -size 0 -delete`).
- Fonts: Helvetica Neue / Georgia on macOS, DejaVu elsewhere (set in `movement.py`).
- Use American English spelling in all text, comments and docstrings.

## Efficient workflow
- The user renders final videos on a Mac Studio with `python build.py <scene>` (or `<film>/<scene>`) and `python film.py <film>`.
- For a quick check in the cloud workspace, run `python build.py <film>/<scene> -q l` and inspect only a few stills (`ffmpeg -ss T -i out/<film>/<scene>.mp4 -frames:v 1 x.png`). Skip stills for trivial changes.
- Prefer targeted edits over rewriting files. Batch the user's notes into one pass.
- In the cloud workspace, installing Manim needs `apt-get install libcairo2-dev libpango1.0-dev pkg-config`. If the `srt` package fails to build, install it from its sdist by copying `srt.py` into site-packages.
