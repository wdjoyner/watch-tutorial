# Notes for AI-assisted editing

Read this first. Read code only as needed. For a SETTINGS or voice-text change, open just that block or file.

## Files
- `movement.py`: shared watch model. Palette and fonts, tooth counts (`TEETH`), pivot layout (`P`), `state(t)` kinematics, geometry helpers (`vm`, `slab`, `wheel_g`, `teeth_g`, `stripes_g`, …), the `Movement` class (tiers `dial` / `engine` / `top`, `parts` dict, `rot` list), `attach_driver()`.
- `sceneNN_*.py`: one Manim scene per file. `SETTINGS` block at the top, then the timeline.
- `sceneNN_*.voice.txt`: narration, `start_seconds | sentence`.
- `build.py`: render → Kokoro TTS (cached per sentence) → tick track → .srt → `out/<scene>.mp4`.

## Rules that matter
- Never `.animate` a tier or a rotating part, because that suspends the driver updater. Animate the trackers returned by `attach_driver` instead (`explode`, `dim[tier]`), or the camera.
- Add parts bottom-to-top within a tier (painter's algorithm). Use `lift(m, dz)` for small z offsets inside a tier.
- A new rotating part needs an entry in `Movement.rot`: `(mobject, pivot_xy, tier, lambda s: angle)`. Derive its angle from `state()` so speeds stay consistent with the gear ratios.
- A train wheel's center distance must equal the sum of the pitch radii (`MOD * teeth / 2`).
- Screen-fixed text uses `add_fixed_in_frame_mobjects`.
- Timed cues during a camera move: build the move with `camera_move()` and wrap each cue in `cue(when, ..., start=, end=)`, both in `movement.py`. `move_camera(added_anims=...)` passes its run_time and rate_func to every added animation, which stretches the cues.
- To center a 3D point on screen, use `camera_move(..., target=p, frame_origin=<the scene's starting frame_center>)`. Manim's Cairo 3D camera shifts the picture by the starting frame_center, so a plain `frame_center=p` lands off-center.
- Check framing in a real `-q l` video, not a `-s` still: a still only renders the last frame, so it hides the frame_center offset.
- Don't render several scenes in parallel: they share Manim's text cache and can corrupt it (fix: `find media/texts -size 0 -delete`).
- Fonts: Helvetica Neue / Georgia on macOS, DejaVu elsewhere (set in `movement.py`).
- Use American English spelling in all text, comments and docstrings.

## Efficient workflow
- The user renders final videos on a Mac Studio with `python build.py <scene>`.
- For a quick check in the cloud workspace, run `python build.py <scene> -q l` and inspect only a few stills (`ffmpeg -ss T -i out/<scene>.mp4 -frames:v 1 x.png`). Skip stills for trivial changes.
- Prefer targeted edits over rewriting files. Batch the user's notes into one pass.
- In the cloud workspace, installing Manim needs `apt-get install libcairo2-dev libpango1.0-dev pkg-config`. If the `srt` package fails to build, install it from its sdist by copying `srt.py` into site-packages.
