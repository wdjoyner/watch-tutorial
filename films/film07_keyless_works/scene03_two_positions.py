"""Film 7, scene 03 - "One stem, two positions": the heart of the film.

A flat close-up of the keyless works, from the dial side (keyless.py). Pushed
in: the yoke spring holds the sliding pinion against the winding pinion, and a
zoom shows their Breguet teeth locking as the crown turns forward. Then the
crown is pulled out slowly: the stem's groove turns the setting lever, its beak
swings the yoke, the yoke slides the sliding pinion inward onto the setting
wheel, and the jumper snaps into its second notch (a soft click). Pushed back,
every step reverses. A short demonstration: turning the crown drives the
winding pinion when pushed in and the setting wheel when pulled out. Last, a
key: the reference text's positions 0 / 1 / 2 against the 6497's two.

Build (render + voice + mux):   python build.py 7/scene03_two_positions
Render only (quick preview):    PYTHONPATH=.:films/film07_keyless_works manim -ql films/film07_keyless_works/scene03_two_positions.py Scene03
Narration lines and their start times live in scene03_two_positions.voice.txt.
The scene writes scene03_two_positions.sfx.txt (the jumper's clicks) on every render.
"""
from manim import *
import prev  # noqa: F401  (first: earlier films' helpers on the path)
from movement import vignette, BG, GLOW
from ui import label, heading, tag, curtain, clock
from ui6 import callout, write_sfx
from keyless import KeylessWorks, WP_X, BREG_H

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds.
# Keep the timeline roughly in step with scene03_two_positions.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 1.0
HEAD_AT = 1.0                  # "Here is the keyless works drawn flat."
WIND_POS_AT = 4.2              # "Pushed in, the crown is in the winding position."
SPRING_AT = 7.8                # "The yoke spring holds the sliding pinion against the winding pinion."
ZOOM_IN_AT, ZOOM_SCALE = 13.3, 2.8   # "Their facing teeth are Breguet teeth ..."
TURN_AT, TURN_END = 15.6, 19.2  # the crown turns forward: the teeth lock and both pinions turn
ZOOM_OUT_AT = 19.4
PULL_SAY_AT = 20.9             # "Now pull the crown out, slowly."
PULL_START = 22.6              # the slow pull, up to the jumper's hump
LEVER_AT = 24.0                # "The groove in the stem turns the setting lever."
YOKE_AT = 27.9                 # "The lever swings the yoke, and the yoke slides the sliding pinion ..."
HUMP_AT = 36.3                 # the knob reaches the top of the hump ...
SNAP = 0.35                    # ... and the jumper snaps it into the second notch
JUMPER_AT = 36.4               # "The jumper snaps into its second notch and holds it there."
PUSH_AT, PUSH_SLOW = 41.6, 2.0  # "Pushing the crown back reverses every step."
DEMO_AT = 45.0                 # "The crown only ever turns the stem; sliding the stem chooses ..."
DEMO_WIND = (45.4, 47.9)       # turning, pushed in: the winding pinion follows
DEMO_PULL_AT = 48.1            # a quick pull (both phases)
DEMO_SET = (48.9, 51.4)        # turning, pulled out: the setting wheel follows
KEY_AT = 52.0                  # "The reference text numbers three positions ..."
KEY_6497_AT = 59.0             # "The 6497 has no date, so its stem has just two ..."
FINAL_HOLD_UNTIL = 68.6        # the last line ends about 67.9 s
FADE_OUT = 1.5

# --- layout ----------------------------------------------------------
KW_ORIGIN, KW_SCALE = (-4.84, 1.73), 1.6
CLUTCH_LOCAL = (WP_X[0] - BREG_H / 2 - 0.15, 0.0)   # zoom target: where the Breguet teeth meet
ZOOM_SCREEN = (-1.6, 1.2)
WIND_COLOR, SET_COLOR = "#ffb54a", "#7fe0a0"     # the two paths, as in scenes 04-06
SFX_LEVEL = 0.7                                  # the jumper's click (soft)

# --- on-screen text --------------------------------------------------
TEXT = dict(
    head=("ONE STEM, TWO POSITIONS", "the keyless works, seen from the dial side"),
    schematic="schematic (proportions and travel exaggerated)",
    pos_in="pushed in: winding", pos_out="pulled out: hand setting",
    slowed="slowed", zoom="magnified",
    yoke_spring="yoke spring", sliding="sliding pinion", winding="winding pinion",
    breguet="Breguet teeth: they lock\nwhen the crown turns forward",
    groove="groove in the stem", lever="setting lever", yoke="yoke", setting_wheel="setting wheel",
    jumper="setting lever jumper:\na notch for each position",
    crown="crown", stem="stem",
    demo_wind="turning the crown pushed in:\nthe winding pinion turns",
    demo_set="turning the crown pulled out:\nthe setting wheel turns",
    key_head="crown positions",
    key_rows=[("reference text", "0   winding", "1   date setting", "2   hand setting"),
              ("ETA 6497", "pushed in   =  0", "(no date)", "pulled out  =  2")],
)
# =====================================================================


class Scene03(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.add(vignette())
        wait_until = clock(self)
        sfx = []

        kw = KeylessWorks(origin=KW_ORIGIN, scale=KW_SCALE)
        kw.vis.set_value(0.0)
        self.add(kw, *kw.trackers())
        # while zoomed in, the lower parts run into the caption band: a mask keeps it clear
        mask = Rectangle(width=16, height=2.0).set_fill(BG, 1).set_stroke(width=0).move_to([0, -3.65, 0])
        mask.set_fill(opacity=0)
        self.add(mask)

        head = heading(*TEXT["head"]).to_corner(UL, buff=0.45)
        schem = tag(TEXT["schematic"], GREY_B, 0.2).next_to(head, DOWN, buff=0.15, aligned_edge=LEFT)
        pos_in = tag(TEXT["pos_in"], WIND_COLOR, 0.28).move_to([4.6, 2.9, 0])
        pos_out = tag(TEXT["pos_out"], SET_COLOR, 0.28).move_to(pos_in)
        slowed = tag(TEXT["slowed"], GLOW, 0.2).next_to(pos_in, DOWN, buff=0.15)
        zoom_tag = tag(TEXT["zoom"], GLOW, 0.2).move_to([1.6, 2.9, 0])

        def glow(parts, v, run_time=0.6):
            return [kw.glow[p].animate(run_time=run_time).set_value(v) for p in parts]

        cur = curtain()
        self.add(cur)

        # ---------------------------------------------------------- pushed in
        self.play(cur.animate.set_fill(opacity=0), kw.vis.animate.set_value(1.0), run_time=FADE_IN)
        self.remove(cur)
        wait_until(HEAD_AT)
        self.play(FadeIn(head), FadeIn(schem), run_time=0.8)
        wait_until(WIND_POS_AT)
        c_crown = callout(TEXT["crown"], lambda: kw.anchor("crown"), (1.3, 2.75))
        c_stem = callout(TEXT["stem"], lambda: kw.anchor("stem"), (-2.0, 0.9))
        self.play(FadeIn(pos_in, shift=DOWN * 0.1), FadeIn(c_crown), FadeIn(c_stem), *glow(["crown"], 1.0),
                  run_time=0.7)
        self.play(*glow(["crown"], 0.0), run_time=0.6)

        wait_until(SPRING_AT)
        c_spring = callout(TEXT["yoke_spring"], lambda: kw.anchor("yoke_spring"), (-6.0, -1.6))
        c_slide = callout(TEXT["sliding"], lambda: kw.anchor("sliding_pinion"), (-3.3, 2.45))
        c_wind = callout(TEXT["winding"], lambda: kw.anchor("winding_pinion"), (-0.6, 2.45))
        self.play(FadeIn(c_spring), *glow(["yoke_spring"], 1.0), run_time=0.7)
        self.play(FadeIn(c_slide), FadeIn(c_wind), *glow(["sliding_pinion", "winding_pinion"], 1.0), run_time=0.8)
        self.wait(1.2)
        self.play(*glow(["yoke_spring", "sliding_pinion", "winding_pinion"], 0.0), run_time=0.8)

        # ---------------------------------------------------------- the Breguet teeth, magnified
        wait_until(ZOOM_IN_AT)
        self.play(FadeOut(c_spring), FadeOut(c_slide), FadeOut(c_wind), FadeOut(c_crown), FadeOut(c_stem), run_time=0.4)
        self.play(*kw.zoom_to(CLUTCH_LOCAL, ZOOM_SCREEN, ZOOM_SCALE), FadeIn(zoom_tag), mask.animate.set_fill(opacity=1),
                  run_time=1.6, rate_func=smooth)
        c_breg = callout(TEXT["breguet"], lambda: kw.anchor("breguet"), (2.9, -1.6))
        self.play(FadeIn(c_breg), run_time=0.6)
        wait_until(TURN_AT)
        self.play(kw.spin.animate.set_value(TAU * 0.7), run_time=TURN_END - TURN_AT, rate_func=smooth)
        wait_until(ZOOM_OUT_AT)
        self.play(FadeOut(c_breg), FadeOut(zoom_tag), *kw.zoom_to((0, 0), KW_ORIGIN, KW_SCALE),
                  mask.animate.set_fill(opacity=0), run_time=1.4)

        # ---------------------------------------------------------- the slow pull
        wait_until(PULL_SAY_AT)
        c_crown2 = callout(TEXT["crown"], lambda: kw.anchor("crown"), (1.3, 2.75))
        self.play(FadeIn(slowed, shift=DOWN * 0.1), FadeIn(c_crown2), *glow(["crown"], 1.0), run_time=0.6)
        wait_until(PULL_START)
        pull_up = kw.pull.animate(run_time=HUMP_AT - PULL_START, rate_func=linear).set_value(0.5)
        c_groove = callout(TEXT["groove"], lambda: kw.anchor("groove"), (2.9, 2.45))
        c_lever = callout(TEXT["lever"], lambda: kw.anchor("setting_lever"), (3.5, -0.55))
        c_yoke = callout(TEXT["yoke"], lambda: kw.anchor("yoke"), (-6.1, -0.5))
        c_slide2 = callout(TEXT["sliding"], lambda: kw.anchor("sliding_pinion"), (-3.3, 2.45))
        c_sw = callout(TEXT["setting_wheel"], lambda: kw.anchor("setting_wheel"), (-5.7, -2.25))

        def at(t, *anims, run_time=0.7):
            """A cue at absolute time t, inside the long pull."""
            return Succession(Wait(max(0.0, t - PULL_START)), AnimationGroup(*anims, run_time=run_time))
        self.play(pull_up,
                  at(PULL_START, *glow(["crown"], 0.0)),
                  at(LEVER_AT, FadeIn(c_groove), FadeIn(c_lever), *glow(["stem", "setting_lever"], 1.0)),
                  at(YOKE_AT, FadeIn(c_yoke), *glow(["stem"], 0.0), *glow(["yoke"], 1.0)),
                  at(YOKE_AT + 3.2, FadeIn(c_slide2), FadeIn(c_sw), *glow(["sliding_pinion", "setting_wheel"], 1.0)))
        # the snap
        self.play(kw.pull.animate.set_value(1.0), *glow(["jumper"], 1.0, run_time=SNAP),
                  run_time=SNAP, rate_func=rate_functions.ease_in_quad)
        sfx.append((self.renderer.time, "click", SFX_LEVEL))
        c_jump = callout(TEXT["jumper"], lambda: kw.anchor("jumper"), (4.6, -1.75))
        self.play(FadeIn(c_jump), FadeOut(pos_in), FadeIn(pos_out), run_time=0.7)
        self.wait(2.0)
        self.play(*glow(["setting_lever", "yoke", "sliding_pinion", "setting_wheel", "jumper"], 0.0),
                  *[FadeOut(c) for c in (c_groove, c_lever, c_yoke, c_slide2, c_sw, c_jump, c_crown2)], run_time=0.8)

        # ---------------------------------------------------------- push back
        wait_until(PUSH_AT)
        self.play(kw.pull.animate.set_value(0.5), run_time=PUSH_SLOW, rate_func=linear)
        self.play(kw.pull.animate.set_value(0.0), run_time=SNAP, rate_func=rate_functions.ease_in_quad)
        sfx.append((self.renderer.time, "click", SFX_LEVEL))
        self.play(FadeOut(pos_out), FadeIn(pos_in), FadeOut(slowed), run_time=0.6)

        # ---------------------------------------------------------- one input, two destinations
        wait_until(DEMO_AT)
        d_wind = label(TEXT["demo_wind"], 0.26, WIND_COLOR).move_to([5.1, 1.6, 0])
        d_set = label(TEXT["demo_set"], 0.26, SET_COLOR).move_to([5.1, 0.6, 0])
        wait_until(DEMO_WIND[0])
        self.play(FadeIn(d_wind), *glow(["winding_pinion"], 1.0), run_time=0.5)
        self.play(kw.spin.animate.increment_value(TAU * 0.8), run_time=DEMO_WIND[1] - DEMO_WIND[0] - 0.5)
        self.play(*glow(["winding_pinion"], 0.0), run_time=0.2)
        self.play(kw.pull.animate.set_value(1.0), run_time=0.6, rate_func=smooth)
        sfx.append((self.renderer.time, "click", SFX_LEVEL))
        self.play(FadeOut(pos_in), FadeIn(pos_out), run_time=0.2)
        wait_until(DEMO_SET[0])
        self.play(FadeIn(d_set), *glow(["setting_wheel"], 1.0), run_time=0.5)
        self.play(kw.spin.animate.increment_value(TAU * 0.8), run_time=DEMO_SET[1] - DEMO_SET[0] - 0.5)
        self.play(*glow(["setting_wheel"], 0.0), run_time=0.4)

        # ---------------------------------------------------------- the positions key
        wait_until(KEY_AT)
        key_head = label(TEXT["key_head"], 0.3, GLOW, bold=True)
        cols = []
        for i, (title, *rows) in enumerate(TEXT["key_rows"]):
            col = VGroup(label(title, 0.26, WHITE, bold=True),
                         *[label(r, 0.24, GREY_B) for r in rows]).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
            cols.append(col)
        cols = VGroup(*cols).arrange(RIGHT, buff=0.5, aligned_edge=UP)
        key = VGroup(key_head, cols).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        box = SurroundingRectangle(key, buff=0.22, corner_radius=0.1).set_stroke(GREY_B, 1.2).set_fill(BG, 0.92)
        panel = VGroup(box, key).move_to([4.95, 0.75, 0])
        self.play(FadeOut(d_wind), FadeOut(d_set), FadeIn(box), FadeIn(key_head), FadeIn(cols[0]), run_time=0.9)
        wait_until(KEY_6497_AT)
        self.play(FadeIn(cols[1], shift=LEFT * 0.1), run_time=0.9)
        rows6497 = cols[1]
        self.play(rows6497[1].animate.set_color(WIND_COLOR), cols[0][1].animate.set_color(WIND_COLOR), run_time=0.6)
        self.play(rows6497[3].animate.set_color(SET_COLOR), cols[0][3].animate.set_color(SET_COLOR), run_time=0.6)

        wait_until(FINAL_HOLD_UNTIL)
        cur.set_fill(opacity=0)
        self.add(cur)
        self.play(cur.animate.set_fill(opacity=1), run_time=FADE_OUT)
        write_sfx(__file__, sfx)
