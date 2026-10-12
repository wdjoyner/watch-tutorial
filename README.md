# watch-tutorial

**Animated, narrated tutorial videos on how a mechanical watch movement works, built entirely in code with [Manim](https://www.manim.community/).**

Every part of the movement (plate, going train, lever escapement, balance, bridges, winding and setting works) is generated procedurally. The model follows the **ETA 6497-1** (Unitas), a hand-wound 16½‴ movement: its layout is traced from ETA's technical communication, and its parts carry ETA's part numbers in the code. The parts move with physically consistent kinematics: wheels and pinions actually mesh, the escape wheel steps at 18,000 vibrations per hour, the small-seconds wheel turns once a minute and the center wheel once an hour. The narration is synthesized locally with the open-source Kokoro voice model. One command takes a scene from source to a finished MP4 with voice, an escapement tick track and captions, and a second joins the scenes into one film.

The series so far:

1. **Learning How Watches Work: Movement Architecture** (2:23) tours a hand-wound movement tier by tier.
2. **Learning How Watches Work: The Power Source** (about 5:10) is about the mainspring and barrel: what is inside the barrel, how winding works, the mainspring as a bent beam, how its torque falls as it unwinds, and two advanced chapters on the geometry of the coil and the best length for a spring in a given barrel.
3. **Learning How Watches Work: The Gear Train** (about 9:00) is about the going train and the arithmetic of tooth counts: the five wheels in order, why a wheel always drives a pinion, the ratio law n₁z₁ = n₂z₂ and the module, how stage ratios multiply while torque divides, designing a train backward from the balance, the 6497's real train checked tooth by tooth, the motion work's 12 : 1, and two advanced chapters on moon-phase gearing, continued fractions and the Stern–Brocot tree.
4. **Learning How Watches Work: The Regulating Organ** (about 7:50) is about the balance and hairspring, the watch's timekeeper: the two numbers that set its pace (the moment of inertia I and the hairspring's stiffness κ), Newton meets Hooke in I φ″ + κ φ = 0, the natural frequency f₀ = (1/2π)√(κ/I), a worked example at 2.5 Hz, how exact κ/I must be, regulation by the index pins or by masselottes, and three advanced chapters on temperature and its compensation, damping and Q, and whether the mainspring can pay for the swing.

The visual style is technical illustration: solid parts with visible thickness, Côtes de Genève striping, perlage, ruby jewels and blued screws, all shown against a dark studio background.

---

## Film 1 scenes (`films/film01_movement_architecture/`)

| # | File | Length | What it shows |
|---|------|--------|---------------|
| 00 | `scene00_title.py` | 10 s | Title card over the slowly orbiting, dimmed movement. |
| 01 | `scene01_vertical_city.py` | 33 s | "The Vertical City": an assembled hand-wound movement explodes into three tiers (dial side, middle engine, top works), then the camera tours each tier; at the dial stop the main plate turns over to show its dial side. |
| 02 | `scene02_dial_side.py` | 21 s | Tier 1, the dial side: a low tracking shot over the motion works to the keyless works; the crown is pushed in and the sliding clutch snaps onto the winding pinion. |
| 03 | `scene03_core_engine.py` | 22 s | Tier 2, the core engine: the bridges lift away and the camera pushes in from the barrel to the balance, while a glow traces the flow of power along the going train. |
| 04 | `scene04_top_modules.py` | 21 s | Tier 3, the top works: hovering over the bridges as the movement is wound (crown wheel, ratchet wheel, click), then over to the regulator on the balance bridge. |
| 05 | `scene05_spines.py` | 21 s | The spines: a cross-section descent down the center wheel's arbor to the hands, then the winding path from the crown to the mainspring. |
| 06 | `scene06_credits.py` | 15 s | End credits. |

## Film 2 scenes (`films/film02_power_source/`)

| # | File | Length | What it shows |
|---|------|--------|---------------|
| 00 | `scene00_title.py` | 10 s | Title card over the opened mainspring barrel, slowly orbiting and dimmed. |
| 01 | `scene01_energy.py` | 25 s | Where the energy lives: the bridges lift, the barrel's teeth glow and the mainspring turns amber; then the energy flows down the going train. |
| 02 | `scene02_barrel.py` | 38 s | Inside the barrel: the barrel lifts out and explodes into cover, arbor, mainspring and drum; insets show the two hooks; the drum turns against the held arbor and drives the center pinion. |
| 03 | `scene03_winding.py` | 38 s | Winding: the crown turns the winding pinion, crown wheel and ratchet, which winds the arbor while the click holds it; close-up of the click, with its sound. |
| 04 | `scene04_beam.py` | 46 s | A bent beam: a piece of the coil becomes a band with its strain colors and neutral axis, building to κ = E b h³ / 12 L, and why thickness matters most. |
| 05 | `scene05_torque.py` | 46 s | Torque falls as it unwinds: the spring unwinds beside a torque plot; the straight line M = κθ and its stored energy, a real spring's curve, the S-shaped free form, and the firm stop of a hand-wound barrel. |
| 06 | `scene06_coil.py` | 38 s | Advanced, the geometry of the coil: an Archimedean spiral unrolls into a long thin rectangle and rolls back into a ring, giving L·h = π(r₂² − r₁²); applied to the 6497, about 455 mm against the catalog's 450. |
| 07 | `scene07_turns.py` | 52 s | Advanced, how many turns: two barrels, fully wound and let down; a slider sweeps the spring length while the turns curve N(L) traces out, peaking at half fill near the 6497's 450 mm spring (about 8 barrel turns, 30 crown turns). |
| 08 | `scene08_credits.py` | 17 s | End credits. |

Film 2's close-up barrel is in `films/film02_power_source/barrel.py`: an extruded drum, arbor, mainspring and cover that can open up along the axis (`BarrelModel`), plus a packed-coil model of the spring at the 6497's real dimensions (1.50 × 0.18 × 450 mm in a 15.0 mm barrel around a 4.1 mm arbor), used wherever the spring is drawn winding or unwinding.

## Film 3 scenes (`films/film03_gear_train/`)

| # | File | Length | What it shows |
|---|------|--------|---------------|
| 00 | `scene00_title.py` | 10 s | Title card over the slowly orbiting movement with its bridges off, dimmed. |
| 01 | `scene01_train.py` | 46 s | The train in order: the bridges lift away and the barrel, center, third, fourth and escape wheels are named and numbered ("second wheel" means the center wheel); power flows down the train, and each wheel's speed appears beside its name. |
| 02 | `scene02_wheel_pinion.py` | 37 s | Wheel drives pinion: a side view of three arbors shows the staircase of wheels and pinions, beside the same arbors from above, turning at their true ratios. |
| 03 | `scene03_ratio.py` | 46 s | The ratio law: a 40-tooth wheel drives a 10-tooth pinion while counters show equal teeth passing, n₁z₁ = n₂z₂, one turn giving four; each mesh reverses direction, so the center and fourth wheels turn the same way. |
| 04 | `scene04_module.py` | 41 s | Why teeth must match: the module m = D / z; two gears with different modules jam (the jam is found from the actual tooth outlines); equal modules mesh at a = m(z₁ + z₂)/2; the movement's own modules, about 0.20, 0.14, 0.14 and 0.11 mm. |
| 05 | `scene05_stages.py` | 57 s | Stages multiply: a bicycle in a high gear, then a log-scale chart of each arbor's speed rising and torque falling by 85/12, 80/10, 60/8 and 70/7 (4,250 in all); power, their product, is a flat line that friction steps down at each mesh. |
| 06 | `scene06_backward.py` | 70 s | Designing backward: from 18,000 beats an hour and a 15-tooth escape wheel, n = B / (120 Z) gives 10 turns a minute; the seconds and minute hands fix 10 : 1 and 60 : 1, and 60 splits into 8 × 7.5. At 21,600 beats only the last stage changes, to 120 / 10. |
| 07 | `scene07_real_train.py` | 64 s | The real train: the running movement beside a table that fills in tooth by tooth, mesh by mesh, ending with 15 × 2 × 10 × 60 = 18,000. |
| 08 | `scene08_motion_work.py` | 48 s | The motion work: the plate turns dial side up, then a sped-up close-up with hands: 36/12 × 40/10 = 12, and the cannon pinion slipping on the center arbor when the hands are set. |
| 09 | `scene09_moon.py` | 38 s | Advanced, the moon problem: a 59-tooth, two-moon disk under its dial window gives 29.5 days, 44 minutes short of a lunation, a full day off in about 2.6 years. |
| 10 | `scene10_fractions.py` | 68 s | Advanced, better fractions: the continued fraction [29; 1, 1, 7, 1, 2, …] computed step by step, its convergents and how long each stays within a day, a Stern–Brocot descent onto 29.530589, and 945/32 = (90/16) × (42/8) as a nearby fraction with small factors. |
| 11 | `scene11_credits.py` | 17 s | End credits. |

Film 3's flat gears come from `films/film03_gear_train/train.py`: `GearSet` builds wheels and pinions from the same tooth outlines as the 3D model, places each driven gear so its teeth interleave with its driver's, and turns every gear from one tracker, so speeds follow the tooth ratios exactly. `elevation_arbor()` draws arbors in side view. Film 3 uses the documented 6497 tooth counts (barrel 85 → center pinion 12, center 80 → third pinion 10, third 60 → fourth pinion 8, fourth 70 → escape pinion 7, escape wheel 15), set with `movement.use_train(movement.TEETH_6497)`; the center-to-escape counts are from R. Allen, *Horological Times*, September 2006, and the barrel's 85/12 is inferred from the movement's barrel-to-center distance. Films 1 and 2 keep the model's original counts, so they render as before.

## Film 4 scenes (`films/film04_regulating_organ/`)

| # | File | Length | What it shows |
|---|------|--------|---------------|
| 00 | `scene00_title.py` | 10 s | Title card over the slowly orbiting movement with its bridges off, dimmed. |
| 01 | `scene01_timekeeper.py` | 36 s | The timekeeper: the bridges lift and the camera pushes in to the balance; wheel, staff and hairspring are labeled, the balance is slowed ten times, and its two numbers, I and κ, are named. |
| 02 | `scene02_two_numbers.py` | 42 s | Two numbers: the moment of inertia as mass weighted by the square of its distance (twice as far counts four times as much), then the hairspring's stiffness κ = E b h³ / 12 L, with hairspring and mainspring cross-sections to scale (the mainspring about 330 times stiffer). |
| 03 | `scene03_newton_hooke.py` | 45 s | Newton meets Hooke: the restoring torque −κφ and Newton's law for turning give I φ″ + κ φ = 0, the equation of a mass on a spring, shown swinging in step; slowed, energy bars show it passing between spring and rim. |
| 04 | `scene04_frequency.py` | 45 s | The natural frequency: ω₀ = √(κ/I), T₀ and f₀ as one timebase; 2.5 Hz gives 5 beats a second and 18,000 an hour, Film 3's B, and the 15-tooth escape wheel steps in time at 10 turns a minute. |
| 05 | `scene05_example.py` | 44 s | A worked example with representative values: I = 4.0 × 10⁻⁹ kg m² at 2.5 Hz needs κ ≈ 9.9 × 10⁻⁷ N m/rad and holds about 11 μJ at 270°; a 0.20 × 0.040 mm ribbon reaches that stiffness at about 21 cm, drawn to scale beside a 4 Hz balance's 13 cm. |
| 06 | `scene06_how_exact.py` | 42 s | How exact: Δf/f = ½Δκ/κ − ½ΔI/I; stiffening the spring by 0.02 % gains almost 9 s/day; one second a day is about 12 ppm, and the chronometer band of −4 to +6 s/day asks for κ/I to about one part in 10⁴. |
| 07 | `scene07_regulation.py` | 48 s | Regulation: the regulator index moves the curb pins along the hairspring's outer coil, changing its active length (κ ∝ 1/L); about 0.05 mm is worth 10 s/day; free-sprung balances turn masselottes on the rim instead. |
| 08 | `scene08_temperature.py` | 37 s | Advanced, temperature: warming changes every term of f₀; (1/f) df/dT = β/2 + 3αₛ/2 − αᵣ, and for a plain steel spring the modulus term swamps the rest: about −10 s/day per degree, −100 s/day for 10 °C. |
| 09 | `scene09_compensation.py` | 34 s | Advanced, beating temperature: a cut bimetallic balance curls inward as it warms; a schematic plot of rate against temperature (plain steel, the bimetallic balance's middle temperature error, a nearly flat Elinvar spring); Guillaume's 1920 Nobel Prize, and Nivarox and silicon springs today. |
| 10 | `scene10_damping.py` | 40 s | Advanced, damping and Q: a slowed balance with exaggerated damping runs down while its swing is traced; I φ″ + c φ′ + κ φ = 0 and Q = I ω₀ / c; at a representative Q of 300 it loses 2.1 % a cycle, about 0.57 μW, and a free swing would halve in about 26 s. |
| 11 | `scene11_energy_bill.py` | 34 s | Advanced, paying for the swing: on a log scale, the mainspring's 2.5 to 4.9 μW over 46 hours, about a third passed on by the escapement, and the balance's 0.57 μW are the same order, each uncertain by about two; so the watchmaker reads the amplitude instead. |
| 12 | `scene12_credits.py` | 16 s | End credits. |

Film 4's numbers all come from `films/film04_regulating_organ/figures.py`, which computes each one from its inputs and cites its source (`python figures.py` prints the table). ETA does not publish the 6497's balance inertia, hairspring dimensions, amplitude or Q, so those are the reference chapter's representative values, and the film labels them so. The flat balance in `balance.py` (`BalanceModel`) has a hairspring that breathes as it swings, its outer end held at the stud or at the regulator's pins. Where the balance is shown in slow motion (marked on screen), the scene writes `<scene>.ticks.txt`, and `build.py` times the ticks to the slowed beats instead of the steady five a second.

## Quick start (macOS)

```bash
brew install ffmpeg pkg-config cairo pango
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python build.py scene01_vertical_city            # one finished 1080p scene -> out/film01_movement_architecture/
python film.py 1 --build                         # every scene of Film 1, joined into one film
python film.py 2 --build                         # the same for Film 2
python film.py 3 --build                         # and Film 3
python film.py 4 --build                         # and Film 4
```

On Linux, install the system libraries with `sudo apt install libcairo2-dev libpango1.0-dev pkg-config ffmpeg`, then use a fresh environment (for example `conda create -n watch python=3.12`) and `pip install -r requirements.txt`. Installing into an existing base environment can leave mismatched NumPy and SciPy versions.

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

Each film's scenes live in `films/filmNN_<name>/`. A bare scene name works when only one film has a scene of that name; otherwise prefix the film, by number or folder name: `python build.py 2/scene00_title`. Each build writes `out/<film>/<scene>.mp4`, which has soft subtitles embedded, and `out/<film>/<scene>.srt`.

To render the picture alone, run Manim directly from the repo root, with the root on the import path: `PYTHONPATH=. manim -ql films/film01_movement_architecture/scene01_vertical_city.py Scene01`.

Render scenes one after another, not in parallel: parallel Manim runs share a text cache and can corrupt it.

## Joining the film

```bash
python film.py 1                # join Film 1's scenes already built in out/film01_movement_architecture/
python film.py 1 --build        # build every scene at 1080p first, then join
python film.py 1 --build -q l   # quick 480p preview of the whole film
```

`film.py <film>` joins `out/<film>/<scene>.mp4` in the order given by the `SCENES` list in that film's `running_order.py`, without re-encoding. It writes `out/<OUT_NAME>.mp4` (`out/movement_architecture.mp4` for Film 1, `out/power_source.mp4` for Film 2, `out/gear_train.mp4` for Film 3, `out/regulating_organ.mp4` for Film 4) with merged soft subtitles and chapter markers, plus a matching `.srt` for uploading captions, and it prints a chapter list ready to paste into a YouTube description. All scenes must be built at the same quality; the script says which ones to rebuild if they are not. After changing one scene, rebuild only that scene and rerun `python film.py <film>`.

## Making changes

Most adjustments need no code changes:

- **Timing, camera, labels, title, tier heights, glow:** use the `SETTINGS` block at the top of each scene file. Every value there is commented.
- **Narration:** use `<scene>.voice.txt`, which has one `start_seconds | sentence` line per sentence. Then run `build.py --skip-render` to re-voice without re-rendering. Sentences are cached, so only edited lines are regenerated.
- **Colors, fonts:** these are at the top of `movement.py`.
- **Title and credits wording:** `TITLE`, `TAGLINE` in the film's `scene00_title.py`; the `CREDITS` list in its credits scene.
- **Running order and chapter names:** the `SCENES` list in the film's `running_order.py`.
- **Pronunciation:** if Kokoro misreads a word, add a respelling to the `PRONOUNCE` table in `build.py` (for example "wound" → "wownd", "ETA" → "E-T-A"). It changes only what the voice says; captions keep the real spelling.
- **Sound effects:** an optional `<scene>.sfx.txt` lists `time | click [| level]` lines, mixed in at `--sfx-level`. Film 2's winding scene writes its own from its winding schedule, so the clicks follow the ratchet teeth. Film 4's slow-motion scenes write a `<scene>.ticks.txt` of beat times, which replaces the steady tick track.
- **Voice:** pass `--voice` to `build.py`. The default is `bm_george` (British male). Other options include `am_michael` and `am_onyx` (American male) and `bf_emma` (British female). Kokoro has many more.

Structural changes, such as new parts, new motion or new shots, go in `movement.py` or a new scene file.

## Project layout

```
movement.py                         the shared watch model: parts, kinematics, animation driver
films/
  film01_movement_architecture/     Film 1
    running_order.py                title, output name, scenes and chapter names
    scene00_title.py                title card (no narration)
    scene01_vertical_city.py        scene 01 (SETTINGS block + timeline)
    scene01_vertical_city.voice.txt scene 01 narration with start times
    scene02 ... scene05             the remaining scenes, each with a .voice.txt
    scene06_credits.py              end credits (no narration)
  film02_power_source/              Film 2: the mainspring and barrel
    running_order.py
    barrel.py                       close-up barrel model and packed-coil spring (film-local helper)
    scene00_title.py ... scene08_credits.py, each narrated scene with its .voice.txt
  film03_gear_train/                Film 3: the going train and its tooth counts
    running_order.py
    train.py                        flat meshing gears and side-view arbors (film-local helper)
    scene00_title.py ... scene11_credits.py, each narrated scene with its .voice.txt
  film04_regulating_organ/          Film 4: the balance and hairspring
    running_order.py
    figures.py                      every number in the film, computed and sourced
    balance.py                      flat balance with a breathing hairspring; beat log for slow motion
    ui.py                           shared text, formula and layout helpers
    scene00_title.py ... scene12_credits.py, each narrated scene with its .voice.txt
films.py                            finds films and scenes by name (used by build.py and film.py)
build.py                            render -> TTS -> mix -> captions -> mux, one scene
film.py                             join one film's built scenes into a film with chapters
CLAUDE.md                           working notes for AI-assisted editing
requirements.txt
media/  out/  build_cache/  models/ generated (git-ignored)
```

## How it works

**Geometry.** Parts are built as 2D [Shapely](https://shapely.readthedocs.io/) polygons, so holes, windows, spokes and clipped finishes are just boolean operations. They are then converted to Manim `VMobject`s. `slab()` gives each part visible thickness by drawing a darker copy beneath the top face. The movement is 6 scene units across (1 unit = 6.1 mm of the 36.6 mm 6497), with the center wheel at the origin, the stem along +x and +z pointing up out of the bridge side.

**Three tiers.** `Movement` builds three groups: `dial` (main plate, motion works, keyless works), `engine` (barrel, going train, escapement, balance) and `top` (bridges, winding wheels, click, regulator). Individual parts are reachable through `Movement.parts[...]`. The motion and keyless works hang under the plate, on its dial side, as in the real movement; the `mv.flip` tracker turns the dial tier over to show them, and `Movement(dial_up=True)` starts it dial side up.

**Kinematics.** Pivot positions are traced from ETA's drawing, and each mesh gets the tooth module that makes its center distance exact. `state(t)` returns every part's angle at time *t*: the escape wheel advances one half-tooth per beat at 5 beats per second (18,000 vph), and the seconds, third, center and barrel wheels follow from their tooth ratios (1 rev/min, 7.5 min, 1 h, 8 h). Those are the model's original tooth counts, which Films 1 and 2 use; `use_train()` switches to others (Film 3 uses the documented 6497 counts) without moving any pivot, because each mesh's module is recomputed from the traced center distances. The balance oscillates at 2.5 Hz with a reduced amplitude so it doesn't strobe. The winding train (crown wheel, ratchet wheel, click) follows the `mv.wind` tracker, and the regulator follows `mv.regulate`.

**One driver.** `attach_driver()` installs a single updater that sets tier heights from an `explode` tracker, sets per-tier opacity from `dim` trackers, and rotates every moving part. Scenes animate the trackers, never the tiers themselves, because `.animate` on a group suspends its updaters.

**Draw order.** Parts are added bottom-to-top (painter's algorithm), which is correct while the camera looks down on the movement (`phi` < 90°). Scene 05 splits its arbor into segments interleaved with the tiers so it passes behind and under them correctly.

**Narration timing.** If a scene's narration runs past the end of its animation, `build.py` prints a warning and holds the last frame so nothing is cut off. The proper fix is to lengthen that scene's final hold in its `SETTINGS` block.

**Camera and cues.** `camera_move()` and `cue()` in `movement.py` keep narration-timed cues (labels, glows) on time during a camera move; Manim's `move_camera(added_anims=...)` would stretch them over the whole move. `camera_move(target=...)` centers a 3D point on screen, correcting for an offset in Manim's Cairo 3D camera that shifts the picture by the scene's starting `frame_center`.

**Screen-fixed text in 3D scenes.** With a nonzero starting `frame_center`, Manim's Cairo 3D camera also shifts screen-fixed mobjects (labels, tables) by −`frame_center`; Film 3's scene 07 shifts its fixed layer back. Labels pinned to parts use the camera's own `project_point` with the camera held still.

## Relation to PAM

This project uses plain Manim rather than [PAM](https://github.com/wdjoyner/pam)'s character and screenplay system. It follows the same approach, though: animation as code, scripted from text files, and rendered reproducibly.

## Credits

Film 1: produced by David Joyner; overall design by Gemini; design and text by ChatGPT; Python code, design, text, and rendering with Manim by Claude.

Film 2: produced by David Joyner; Python code, design, text, and rendering with Manim by Claude. References: *The Mathematics of the Automatic Mechanical Watch* (AI and W. David Joyner, 2026); C.-A. Reymondin et al., *The Theory of Horology* (WOSTEP); mainspring dimensions from Dr. Ranfft's watch movement archive; ETA's technical communication for the 6497-1 / 6498-1.

Film 3: produced by David Joyner; Python code, design, text, and rendering with Manim by Claude. References: *The Mathematics of the Automatic Mechanical Watch* (AI and W. David Joyner, 2026); going-train tooth counts from R. Allen, "Coincidental Time, Part 1," *Horological Times*, September 2006; the 3 Hz train from Horology Student's notes on the Unitas / ETA 6497–6498; ETA's technical communication for the 6497-1 / 6498-1.

Film 4: produced by David Joyner; Python code, design, text, and rendering with Manim by Claude. References: *The Mathematics of the Automatic Mechanical Watch* (AI and W. David Joyner, 2026), section "The regulating organ"; ETA's technical communication for the 6497-1 / 6498-1. The balance inertia, hairspring dimensions, amplitude and Q are the chapter's representative values; ETA does not publish them.

- Animation: [Manim Community](https://www.manim.community/)
- Geometry: [Shapely](https://shapely.readthedocs.io/)
- Narration: [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M) (Apache 2.0) via [kokoro-onnx](https://github.com/thewh1teagle/kokoro-onnx)

## License

BSD 2-Clause. See [LICENSE](LICENSE).
