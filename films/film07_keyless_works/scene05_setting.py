"""Film 7, scene 05 - "Setting the hands": the crown pulled out.

The keyless close-up, pulled out (keyless.py), feeding a flat setting train
built with Film 3's GearSet: setting wheel -> intermediate setting wheel ->
minute wheel (36) -> cannon pinion (12) and minute hand; the minute wheel's
pinion (10) -> hour wheel (40) and hour hand. 36/12 x 40/10 = 12 (Film 3). The
two setting wheels are idlers: their tooth counts cancel. Then the center
wheel's arbor, still turned by the going train (sped up, tagged): the cannon
pinion grips it only by friction, so when the crown turns the hands, the
cannon pinion slips on the arbor and the arbor's mark keeps its own slow pace.

Everything turns from two trackers: `arbor` (the center arbor, driven by the
train) and `slip` (the cannon pinion's turn relative to the arbor, driven from
the crown). The cannon pinion's angle is arbor + slip, and the setting train,
the sliding pinion and the crown follow it through the tooth ratios.

Build (render + voice + mux):   python build.py 7/scene05_setting
Render only (quick preview):    PYTHONPATH=.:films/film07_keyless_works manim -ql films/film07_keyless_works/scene05_setting.py Scene05
Narration lines and their start times live in scene05_setting.voice.txt.
"""
from manim import *
import prev  # noqa: F401  (first: earlier films' helpers on the path)
import figures as F
from movement import vignette, BG, GLOW, STEEL, STEEL_HI, STEEL_DK, BRASS
from ui import label, ftext, heading, tag, curtain, clock
from ui6 import callout
from dialside import DialSide

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds.
# Keep the timeline roughly in step with scene05_setting.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 1.0
HEAD_AT = 1.0                  # "Pulled out, the sliding pinion turns the setting wheel, which turns ..."
SET1 = (1.6, 17.6)             # the crown turns: the setting train and the hands follow
SET1_TURNS = -1.6              # cannon pinion turns during SET1 (the minute hand goes round 1.6 times)
LABEL_AT = dict(setting=2.0, intermediate=4.3, minute=6.8, cannon=10.2, minute_hand=12.2, hour=14.3,
                hour_hand=16.0)
RATIO_AT = 18.0                # "Thirty-six to twelve, times forty to ten, is twelve to one ..."
IDLER_AT = 26.6                # "The two setting wheels only pass the motion along; their tooth counts cancel."
ARBOR_AT = 32.6                # "But the cannon pinion sits on the center wheel's arbor ..."
RUN = (33.4, 57.6)             # the train turns the arbor (sped up)
ARBOR_TURNS = -0.16            # arbor turns during RUN
QUESTION_AT = 40.0             # "So how can the hands turn freely?"
FRICTION_AT = 43.2             # "The cannon pinion grips the arbor only by friction ..."
SET2 = (46.0, 51.6)            # turning the crown again: the cannon pinion slips on the arbor
SET2_TURNS = -1.2
CLUTCH_AT = 51.9               # "It is a slipping clutch. The hands move, and the train never feels it."
FINAL_HOLD_UNTIL = 57.6        # the last line ends about 56.7 s
FADE_OUT = 1.5

# --- layout ----------------------------------------------------------
KW_SCALE = 1.2
SW_SCREEN = np.array([-0.4, 1.5])            # where the setting wheel sits on screen
INTER_ANGLE, MINUTE_ANGLE, CANNON_ANGLE = 210, 190, 252   # each gear's direction from its driver (degrees)
MINUTE_HAND_L, HOUR_HAND_L = 1.45, 0.95
SET_COLOR = "#7fe0a0"

# --- on-screen text --------------------------------------------------
TEXT = dict(
    head=("SETTING THE HANDS", "crown pulled out"),
    pulled="pulled out: hand setting",
    setting="setting wheel", intermediate="intermediate\nsetting wheel", minute="minute wheel  ·  36,  pinion 10",
    cannon="cannon pinion  ·  12", minute_hand="minute hand", hour="hour wheel  ·  40", hour_hand="hour hand",
    ratio="36 / 12  ×  40 / 10  =  12", ratio_note="the hour hand turns once while the minute hand turns 12 times (Film 3)",
    idler="the setting wheels only pass the motion along:\ntheir tooth counts cancel",
    arbor="center wheel's arbor: turned by the going train", sped="train sped up",
    question="?", friction="friction fit", clutch="a slipping clutch: the hands move, the arbor keeps its pace",
    schematic="schematic; setting-wheel tooth counts illustrative",
    crown="crown", sliding="sliding pinion",
)
# =====================================================================


class Scene05(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.add(vignette())
        wait_until = clock(self)

        ds = DialSide(kw_scale=KW_SCALE, sw_screen=SW_SCREEN, pull=1.0,
                      angles=(INTER_ANGLE, MINUTE_ANGLE, CANNON_ANGLE),
                      minute_hand=MINUTE_HAND_L, hour_hand=HOUR_HAND_L)
        ds.add_to(self)
        gs, kw, c0, hands, arbor_mark = ds.gs, ds.kw, ds.c0, ds.hands, ds.arbor_mark
        arbor, slip, vis, hands_vis, mark_vis = ds.arbor, ds.slip, ds.vis, ds.hands_vis, ds.mark_vis
        kw.vis.set_value(0.0)

        # ---------------------------------------------------------- text
        head = heading(*TEXT["head"]).to_corner(UL, buff=0.45)
        pulled = tag(TEXT["pulled"], SET_COLOR, 0.24).next_to(head, DOWN, buff=0.15, aligned_edge=LEFT)
        schem = tag(TEXT["schematic"], GREY_B, 0.18).to_corner(UR, buff=0.4)

        gp = ds.gp
        calls = dict(
            crown=callout(TEXT["crown"], lambda: kw.anchor("crown"), (6.05, 2.1), color=WHITE),
            sliding=callout(TEXT["sliding"], lambda: kw.anchor("sliding_pinion"), (2.6, 3.25), color=WHITE),
            setting=callout(TEXT["setting"], gp("setting", 60), (0.75, 2.8), color=SET_COLOR),
            intermediate=callout(TEXT["intermediate"], gp("inter", 100), (-1.3, 2.55), color=SET_COLOR),
            minute=callout(TEXT["minute"], gp("minute", 120), (-4.4, 2.0), color=SET_COLOR),
            cannon=callout(TEXT["cannon"], lambda: c0 + RIGHT * 0.25, (-1.4, -1.6), color=SET_COLOR),
            minute_hand=callout(TEXT["minute_hand"], lambda: c0 + 0.8 * np.array(
                [np.cos(hands["minute"]._ang), np.sin(hands["minute"]._ang), 0]), (-6.2, -2.2), color=WHITE),
            hour=callout(TEXT["hour"], gp("hour", 200, 0.95), (-6.1, 0.1), color=SET_COLOR),
            hour_hand=callout(TEXT["hour_hand"], lambda: c0 + 0.55 * np.array(
                [np.cos(hands["hour"]._ang), np.sin(hands["hour"]._ang), 0]), (-2.1, -2.35), color=GLOW),
        )

        cur = curtain()
        self.add(cur)
        self.play(cur.animate.set_fill(opacity=0), kw.vis.animate.set_value(1.0), vis.animate.set_value(1.0),
                  run_time=FADE_IN)
        self.remove(cur)
        wait_until(HEAD_AT)
        self.play(FadeIn(head), FadeIn(pulled), FadeIn(schem), FadeIn(calls["crown"]), FadeIn(calls["sliding"]),
                  run_time=0.6)

        # ---------------------------------------------------------- setting: the train and the hands
        def at(t0, t, *anims, run_time=0.7):
            return Succession(Wait(max(0.0, t - t0)), AnimationGroup(*anims, run_time=run_time))

        cues = [at(SET1[0], LABEL_AT[k], FadeIn(calls[k]),
                   *([hands_vis.animate.set_value(1.0)] if k == "minute_hand" else []))
                for k in ("setting", "intermediate", "minute", "cannon", "minute_hand", "hour", "hour_hand")]
        self.play(slip.animate(run_time=SET1[1] - SET1[0], rate_func=rate_functions.ease_in_out_sine)
                  .increment_value(SET1_TURNS), *cues)

        wait_until(RATIO_AT)
        ratio = ftext(TEXT["ratio"], 0.5, SET_COLOR).move_to([3.3, -1.25, 0])
        rnote = label(TEXT["ratio_note"], 0.19, GREY_B).next_to(ratio, DOWN, buff=0.15)
        self.play(FadeOut(calls["minute_hand"]), FadeOut(calls["hour_hand"]), FadeIn(ratio, shift=UP * 0.1),
                  FadeIn(rnote), run_time=0.9)
        self.play(slip.animate.increment_value(-0.5), run_time=4.0, rate_func=smooth)

        wait_until(IDLER_AT)
        idler = label(TEXT["idler"], 0.24, WHITE).move_to([3.3, -2.15, 0])
        self.play(FadeIn(idler), Indicate(calls["setting"][0], color=WHITE), Indicate(calls["intermediate"][0],
                                                                                         color=WHITE), run_time=1.0)

        # ---------------------------------------------------------- the arbor keeps turning
        wait_until(ARBOR_AT)
        a_lbl = callout(TEXT["arbor"], lambda: c0 + 0.3 * np.array([np.cos(arbor_mark._ang),
                                                                    np.sin(arbor_mark._ang), 0]), (0.2, -2.3))
        sped = tag(TEXT["sped"], GLOW, 0.2).next_to(schem, DOWN, buff=0.12, aligned_edge=RIGHT)
        q = label(TEXT["question"], 0.9, GLOW, bold=True).move_to(c0 + np.array([1.1, 1.0, 0]))
        ring = Circle(radius=0.2).move_to(c0).set_stroke(GLOW, 5, 0)
        fric = label(TEXT["friction"], 0.26, GLOW, bold=True).move_to(c0 + np.array([1.55, 0.45, 0]))
        clutch = label(TEXT["clutch"], 0.26, GLOW, bold=True).move_to([1.6, -2.42, 0])
        self.play(FadeOut(ratio), FadeOut(rnote), FadeOut(idler), *[FadeOut(c) for k, c in calls.items()
                                                                    if k not in ("cannon", "minute_hand", "hour_hand")],
                  mark_vis.animate.set_value(1.0), FadeIn(a_lbl), FadeIn(sped),
                  run_time=0.8)
        run = arbor.animate(run_time=RUN[1] - RUN[0], rate_func=linear).set_value(ARBOR_TURNS)
        t0 = RUN[0]
        wait_until(t0)
        self.play(run,
                  at(t0, QUESTION_AT, FadeIn(q, scale=0.8)),
                  at(t0, FRICTION_AT, FadeOut(q), ring.animate.set_stroke(opacity=0.9), FadeIn(fric)),
                  at(t0, SET2[0], slip.animate(run_time=SET2[1] - SET2[0], rate_func=smooth)
                     .increment_value(SET2_TURNS), run_time=SET2[1] - SET2[0]),
                  at(t0, CLUTCH_AT, FadeOut(a_lbl), FadeIn(clutch, shift=UP * 0.1), run_time=0.9))

        wait_until(FINAL_HOLD_UNTIL)
        cur.set_fill(opacity=0)
        self.add(cur)
        self.play(cur.animate.set_fill(opacity=1), run_time=FADE_OUT)
