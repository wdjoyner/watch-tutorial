"""Film 7, scene 04b - "The motion work": how the hands turn on their own.

First the flat dial side (dialside.py), crown pushed in, the keyless works
dimmed: the going train turns the center wheel's arbor (sped up, tagged), the
cannon pinion turns with it and carries the minute hand; the cannon pinion
drives the minute wheel (36), whose pinion (10) drives the hour wheel (40) and
the hour hand; 36/12 x 40/10 = 12 (Film 3). The setting wheels turn too, but the
sliding pinion is away from them. Then a schematic side view of the stack: the
main plate, the center arbor, the cannon pinion pressed onto it (the friction
fit), the minute wheel and its pinion, the hour wheel's tube riding freely over
the cannon pinion, the dial, and the two hands, each part labeled.

Build (render + voice + mux):   python build.py 7/scene04b_motion_work
Render only (quick preview):    PYTHONPATH=.:films/film07_keyless_works manim -ql films/film07_keyless_works/scene04b_motion_work.py Scene04b
Narration lines and their start times live in scene04b_motion_work.voice.txt.
"""
from manim import *
import prev  # noqa: F401  (first: earlier films' helpers on the path)
from movement import vignette, BG, GLOW, STEEL, STEEL_HI, STEEL_DK, BRASS
from ui import label, ftext, heading, tag, curtain, clock
from ui6 import callout
from dialside import DialSide

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds.
# Keep the timeline roughly in step with scene04b_motion_work.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 1.0
HEAD_AT = 1.0                  # "Before we set the hands, watch the motion work turn them on its own."
RUN = (3.0, 27.0)              # the train turns the center arbor (sped up)
RUN_TURNS = -1.2               # arbor turns during RUN (clockwise = negative)
LABEL_AT = dict(arbor=6.3, cannon=9.6, minute_hand=11.6, minute=15.2, mpin=16.8, hour=18.4, hour_hand=19.6)
RATIO_AT = 21.4                # "Thirty-six to twelve, times forty to ten: twelve to one, as in Film 3."
SIDE = (27.4, 29.4)            # crossfade to the side view
SIDE_BASE_AT = 29.0            # "From the side, the hands sit on tubes, one inside the other."
CANNON_AT = 33.8               # "The cannon pinion is a tube pressed onto the center arbor ..."
HOUR_AT = 40.7                 # "The hour wheel's tube turns freely over it, with the hour hand just above the dial."
FIT_AT = 47.3                  # "That press fit is the one place the hands can slip ..."
FINAL_HOLD_UNTIL = 54.0        # the last line ends about 53.2 s
FADE_OUT = 1.5

# --- flat view -------------------------------------------------------
KW_DIM = 0.3                   # the keyless works, dimmed (not the subject here)
SET_COLOR = "#7fe0a0"
ARBOR_COLOR = "#7fc4ff"

# --- side view (schematic, not to scale): x positions and levels ----
CX, MX = -0.6, -3.1            # center arbor axis; minute wheel stud
LEFT_X, RIGHT_X = -5.0, 3.0    # extent of the plate and the dial
PLATE = (-2.35, -1.85)
DIAL = (0.25, 0.38)
SIDE_K, SIDE_O = 1.3, (-0.6, -1.52)   # the side view is drawn small, then enlarged by SIDE_K about SIDE_O
SIDE_LABEL = 0.24

# --- on-screen text --------------------------------------------------
TEXT = dict(
    head=("THE MOTION WORK", "how the hands turn on their own"),
    pushed="pushed in: running",
    schematic="schematic; setting-wheel tooth counts illustrative",
    sped="train sped up {:.0f}×",
    arbor="center wheel's arbor: turned by the going train", cannon="cannon pinion  ·  12",
    minute_hand="minute hand", minute="minute wheel  ·  36", mpin="minute wheel's pinion  ·  10",
    hour="hour wheel  ·  40", hour_hand="hour hand",
    ratio="36 / 12  ×  40 / 10  =  12",
    ratio_note="the hour hand turns once while the minute hand turns 12 times (Film 3)",
    side="cut-away side view, schematic (not to scale)",
    s_plate="main plate", s_arbor="center arbor", s_cannon="cannon pinion", s_mhand="minute hand",
    s_minute="minute wheel", s_mpin="its pinion", s_hour="hour wheel", s_dial="dial", s_hhand="hour hand",
    s_fit="press fit: held\nby friction only",
    s_free="turns freely",
)
# =====================================================================


def box(x0, x1, y0, y1, color, stroke=None):
    r = Rectangle(width=x1 - x0, height=y1 - y0).move_to([(x0 + x1) / 2, (y0 + y1) / 2, 0])
    return r.set_fill(color, 1).set_stroke(stroke or BG, 1.2)


def toothed(x0, x1, y0, y1, color, pitch=0.09):
    """A wheel or pinion seen edge on: a slab with tooth lines."""
    g = VGroup(box(x0, x1, y0, y1, color))
    n = max(2, int((x1 - x0) / pitch))
    for i in range(1, n):
        x = x0 + (x1 - x0) * i / n
        g.add(Line([x, y0, 0], [x, y1, 0]).set_stroke(BG, 0.8, 0.6))
    return g


class Scene04b(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.add(vignette())
        wait_until = clock(self)

        # ---------------------------------------------------------- the flat dial side, running
        ds = DialSide(pull=0.0)
        ds.add_to(self)
        gs, kw, c0, hands, arbor_mark = ds.gs, ds.kw, ds.c0, ds.hands, ds.arbor_mark
        kw.vis.set_value(0.0)

        head = heading(*TEXT["head"]).to_corner(UL, buff=0.45)
        pushed = tag(TEXT["pushed"], "#ffb54a", 0.24).next_to(head, DOWN, buff=0.15, aligned_edge=LEFT)
        schem = tag(TEXT["schematic"], GREY_B, 0.18).to_corner(UR, buff=0.4)
        sped = tag(TEXT["sped"].format(3600 / ((RUN[1] - RUN[0]) / abs(RUN_TURNS))), GLOW, 0.2)
        sped.next_to(schem, DOWN, buff=0.12, aligned_edge=RIGHT)

        gp = ds.gp

        def hand_pt(which, f):
            return lambda: c0 + f * np.array([np.cos(hands[which]._ang), np.sin(hands[which]._ang), 0])
        calls = dict(
            arbor=callout(TEXT["arbor"], lambda: c0 + 0.3 * np.array([np.cos(arbor_mark._ang),
                                                                     np.sin(arbor_mark._ang), 0]),
                          (0.2, -2.3), color=ARBOR_COLOR),
            cannon=callout(TEXT["cannon"], lambda: c0 + RIGHT * 0.25, (-1.4, -1.6), color=SET_COLOR),
            minute_hand=callout(TEXT["minute_hand"], hand_pt("minute", 1.1), (-6.2, -2.2), color=WHITE),
            minute=callout(TEXT["minute"], gp("minute", 120), (-4.4, 2.0), color=SET_COLOR),
            mpin=callout(TEXT["mpin"], gp("mpin", 60), (-1.4, 2.75), color=SET_COLOR),
            hour=callout(TEXT["hour"], gp("hour", 200, 0.95), (-6.1, 0.1), color=SET_COLOR),
            hour_hand=callout(TEXT["hour_hand"], hand_pt("hour", 0.7), (-6.35, -1.0), color=GLOW),
        )
        ratio = ftext(TEXT["ratio"], 0.5, SET_COLOR).move_to([3.3, -1.25, 0])
        rnote = label(TEXT["ratio_note"], 0.19, GREY_B).next_to(ratio, DOWN, buff=0.15)

        cur = curtain()
        self.add(cur)
        self.play(cur.animate.set_fill(opacity=0), kw.vis.animate.set_value(KW_DIM), ds.vis.animate.set_value(1.0),
                  ds.hands_vis.animate.set_value(1.0), ds.mark_vis.animate.set_value(1.0), run_time=FADE_IN)
        self.remove(cur)
        wait_until(HEAD_AT)
        self.play(FadeIn(head), FadeIn(pushed), FadeIn(schem), run_time=0.6)

        def at(t0, t, *anims, run_time=0.7):
            return Succession(Wait(max(0.0, t - t0)), AnimationGroup(*anims, run_time=run_time))

        wait_until(RUN[0])
        cues = [at(RUN[0], LABEL_AT[k], FadeIn(calls[k])) for k in LABEL_AT]
        cues.append(at(RUN[0], RUN[0] + 0.1, FadeIn(sped)))
        cues.append(at(RUN[0], RATIO_AT, FadeIn(ratio, shift=UP * 0.1), FadeIn(rnote), run_time=0.9))
        self.play(ds.arbor.animate(run_time=RUN[1] - RUN[0], rate_func=linear).set_value(RUN_TURNS), *cues)

        # ---------------------------------------------------------- crossfade to the side view
        wait_until(SIDE[0])
        flat_text = [*calls.values(), ratio, rnote, sped, schem, pushed]
        self.play(*[FadeOut(m) for m in flat_text], kw.vis.animate.set_value(0.0), ds.vis.animate.set_value(0.0),
                  ds.hands_vis.animate.set_value(0.0), ds.mark_vis.animate.set_value(0.0),
                  run_time=SIDE[1] - SIDE[0])
        self.remove(*gs.gears.values(), kw)

        side_tag = tag(TEXT["side"], GREY_B, 0.18).to_corner(UR, buff=0.4)
        plate = box(LEFT_X, RIGHT_X, *PLATE, GREY_D, GREY_C)
        arbor = box(CX - 0.07, CX + 0.07, PLATE[0], 1.55, ARBOR_COLOR)
        stud = box(MX - 0.06, MX + 0.06, PLATE[1], -0.65, STEEL_DK, GREY_C)

        def pair(r0, r1, y0, y1, color, teeth=False):
            """Both walls of a part cut through its axis: from radius r0 to r1 on each side."""
            f = (lambda a, b: toothed(a, b, y0, y1, color)) if teeth else (lambda a, b: box(a, b, y0, y1, color))
            return VGroup(f(CX - r1, CX - r0), f(CX + r0, CX + r1))
        # the cannon pinion: leaves at the bottom, a tube pressed onto the arbor up to the minute hand
        c_leaves = pair(0.07, 0.38, -1.75, -1.35, STEEL, teeth=True)
        c_tube = pair(0.07, 0.17, -1.35, 1.25, STEEL)
        m_hand = VGroup(box(CX + 0.07, CX + 2.6, 1.25, 1.33, WHITE), box(CX - 0.4, CX - 0.07, 1.25, 1.33, WHITE),
                        pair(0.07, 0.22, 1.2, 1.38, WHITE))
        # the minute wheel meshes with the cannon pinion's leaves; its pinion with the hour wheel
        m_wheel = toothed(MX - 2.02, CX - 0.38, -1.64, -1.48, STEEL)
        m_pin = toothed(MX - 0.45, MX + 0.45, -0.98, -0.78, STEEL_HI)
        # the hour wheel: a toothed disk and a tube riding loosely over the cannon pinion
        h_disk = VGroup(toothed(MX + 0.45, CX - 0.21, -0.95, -0.82, BRASS), toothed(CX + 0.21, CX + 2.05, -0.95, -0.82, BRASS))
        h_tube = pair(0.21, 0.32, -0.82, 0.72, BRASS)
        h_hand = VGroup(box(CX + 0.21, CX + 1.8, 0.72, 0.8, GLOW), pair(0.21, 0.34, 0.68, 0.84, GLOW))
        dial = VGroup(box(LEFT_X, CX - 0.38, *DIAL, "#e9e3d3"), box(CX + 0.38, RIGHT_X, *DIAL, "#e9e3d3"))
        fit = pair(0.07, 0.12, 0.92, 1.2, GLOW)
        fit.set_fill(opacity=0).set_stroke(opacity=0)
        side_parts = VGroup(plate, arbor, stud, c_leaves, c_tube, m_hand, m_wheel, m_pin, h_disk, h_tube, h_hand,
                            dial, fit)
        O = np.array([*SIDE_O, 0.0])
        side_parts.scale(SIDE_K, about_point=O)

        def sl(text, anchor, at, color=WHITE):
            p = O + SIDE_K * (np.array([*anchor, 0.0]) - O)
            return callout(text, lambda p=p: p, at, color=color, scale=SIDE_LABEL)
        lb = dict(
            plate=sl(TEXT["s_plate"], (2.7, -2.1), (5.4, -2.25), GREY_B),
            arbor=sl(TEXT["s_arbor"], (CX, 1.5), (1.5, 2.75), ARBOR_COLOR),
            minute=sl(TEXT["s_minute"], (MX - 1.4, -1.56), (-6.2, -1.1), SET_COLOR),
            cannon=sl(TEXT["s_cannon"], (CX + 0.38, -1.55), (5.4, -1.45), SET_COLOR),
            mhand=sl(TEXT["s_mhand"], (CX + 2.3, 1.29), (5.4, 1.95), WHITE),
            mpin=sl(TEXT["s_mpin"], (MX - 0.45, -0.88), (-6.2, -0.35), SET_COLOR),
            hour=sl(TEXT["s_hour"], (CX + 1.6, -0.88), (5.4, -0.6), SET_COLOR),
            dial=sl(TEXT["s_dial"], (RIGHT_X - 0.1, 0.32), (5.4, 0.87), GREY_A),
            hhand=sl(TEXT["s_hhand"], (CX + 1.5, 0.76), (5.4, 1.45), GLOW),
            free=sl(TEXT["s_free"], (CX - 0.27, 0.0), (-2.5, 0.1), GREY_B),
            fit=sl(TEXT["s_fit"], (CX - 0.1, 1.07), (-3.4, 2.15), GLOW),
        )

        wait_until(SIDE_BASE_AT)
        self.play(FadeIn(side_tag), FadeIn(plate), FadeIn(arbor), FadeIn(lb["plate"]), FadeIn(lb["arbor"]),
                  run_time=1.0)
        wait_until(CANNON_AT)
        self.play(FadeIn(c_leaves), FadeIn(c_tube), FadeIn(m_hand), FadeIn(lb["cannon"]), FadeIn(lb["mhand"]),
                  run_time=1.0)
        self.play(FadeIn(stud), FadeIn(m_wheel), FadeIn(lb["minute"]), run_time=0.8)
        wait_until(HOUR_AT)
        self.play(FadeIn(m_pin), FadeIn(h_disk), FadeIn(h_tube), FadeIn(lb["mpin"]), FadeIn(lb["hour"]),
                  run_time=1.0)
        self.play(FadeIn(dial), FadeIn(h_hand), FadeIn(lb["dial"]), FadeIn(lb["hhand"]), FadeIn(lb["free"]),
                  run_time=1.0)
        wait_until(FIT_AT)
        self.play(fit.animate.set_fill(opacity=0.95).set_stroke(opacity=1), FadeIn(lb["fit"]), run_time=0.8)
        self.play(Indicate(fit, color=GLOW, scale_factor=1.15), run_time=1.2)

        wait_until(FINAL_HOLD_UNTIL)
        cur.set_fill(opacity=0)
        self.add(cur)
        self.play(cur.animate.set_fill(opacity=1), run_time=FADE_OUT)
