"""Film 4, scene 10 - "Damping and Q" (advanced): a slowed balance runs down
while its swing is recorded as a decaying trace (damping exaggerated, and
tagged so). I phi'' + c phi' + kappa phi = 0 is the turning twin of
m x'' + b x' + k x = 0. Q = I omega0 / c; each cycle loses about 2 pi / Q of the
energy. At a representative Q of 300: 2.1 % a cycle, 0.23 microjoules, 0.57 microwatts,
and a free swing would halve in about 26 s.

Build (render + voice + mux):   python build.py 4/scene10_damping
Render only (quick preview):    PYTHONPATH=.:films/film04_regulating_organ manim -ql films/film04_regulating_organ/scene10_damping.py Scene10
Narration lines and their start times live in scene10_damping.voice.txt.
Numbers from figures.py. The scene writes scene10_damping.ticks.txt on every render.
"""
from manim import *
import figures as F
from movement import vignette, BG, GLOW
from balance import BalanceModel, BeatLog
from ui import ftext, label, heading, tag, curtain, clock, WARM, COOL

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds.
# Keep the timeline roughly in step with scene10_damping.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 1.0
HEAD_AT = 1.2
DECAY_AT = 2.0                        # "A real balance slowly runs down": damping on, trace starts
EQ_AT = 6.0                           # "add one more term, c times the angular velocity"
TWIN_AT = 10.0                        # "just as in a damped mass on a spring"
Q_AT = 14.4                           # "The quality factor, Q, equal to I omega nought over c"
LOSS_AT = 19.6                        # "each cycle loses about two pi over Q"
NUM_AT = (26.2, 29.6, 32.8)           # Q 300: two percent; six tenths of a microwatt; halves in half a minute
FINAL_HOLD_UNTIL = 38.4               # the last line ends about 36.5 s
FADE_OUT = 1.5

# --- the balance and its trace ------------------------------------------
BAL_AT, BAL_R, AMP = (-4.4, 0.9), 1.75, 1.1
RATE = 0.25                           # slow motion
Q_SHOWN = 12.0                        # exaggerated, so the decay is visible (tagged on screen)
TRACE_O, TRACE_W, TRACE_H = (-6.6, -2.6), 6.4, 0.85   # left end of the time axis, length, half-height
TRACE_SPAN = 24.0                     # seconds of scene time across the trace
# =====================================================================


class Scene10(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.add(vignette())
        wait_until = clock(self)

        bal = BalanceModel(center=BAL_AT, radius=BAL_R, amp=AMP)
        bal.rate.set_value(RATE)
        bal.attach(self)
        log = BeatLog(self, lambda: bal.model_t, 2 * bal.hz)
        exag = tag(f"slowed 4×,  damping exaggerated  (Q ≈ {Q_SHOWN:.0f})").move_to([BAL_AT[0], -1.12, 0])

        # the recorded swing: angle against time, drawn as it happens
        o = np.array([*TRACE_O, 0.0])
        trace_axis = VGroup(Line(o, o + RIGHT * TRACE_W).set_stroke(GREY_B, 1.2),
                            label("time", 0.22).next_to(o + RIGHT * TRACE_W, DOWN, buff=0.1).align_to(o + RIGHT * TRACE_W, RIGHT),
                            label("angle", 0.22).next_to(o + UP * TRACE_H, UP, buff=0.05).align_to(o, LEFT))
        trace = VMobject().set_stroke(GLOW, 2.5).set_fill(opacity=0)
        pts, t0 = [], {"t": None}

        def record(m, dt):
            if t0["t"] is None:
                return
            t = self.renderer.time - t0["t"]
            if 0 <= t <= TRACE_SPAN:
                pts.append(o + np.array([t / TRACE_SPAN * TRACE_W, TRACE_H * bal.angle() / AMP, 0]))
                if len(pts) > 1:
                    m.set_points_as_corners(pts)
        trace.add_updater(record)

        eq = ftext("I φ″  +  c φ′  +  κ φ  =  0", 0.66).move_to([3.0, 2.6, 0])
        new_term = SurroundingRectangle(eq[4:7], buff=0.08).set_stroke(WARM, 2)   # the c phi' term
        drag = label("pivot friction, air drag", 0.24, WARM).next_to(eq, DOWN, buff=0.16)
        twin = ftext("m x″  +  b x′  +  k x  =  0", 0.5, GREY_B).next_to(drag, DOWN, buff=0.25)
        q = ftext("Q  =  I ω₀ / c", 0.62, GLOW).move_to([3.0, 0.45, 0])
        loss = ftext("lost per cycle  ≈  (2π / Q) × energy", 0.48).next_to(q, DOWN, buff=0.22)

        rep = tag(f"representative:  Q = {F.Q:.0f}").move_to([3.0, -0.8, 0])
        nums = [ftext(f"2π / {F.Q:.0f}  =  {F.LOSS_FRAC * 100:.1f} %  a cycle", 0.46),
                ftext(f"{F.LOSS_6497 * 1e6:.2f} μJ  ×  {F.F_6497:g} a second  ≈  {F.POWER_6497 * 1e6:.2f} μW", 0.46, GLOW),
                ftext(f"a free swing halves in  ≈  {F.HALF_AMP_TIME:.0f} s", 0.46)]
        VGroup(*nums).arrange(DOWN, buff=0.2).next_to(rep, DOWN, buff=0.25)

        head = heading("DAMPING AND Q", "why the swing dies").to_corner(UL, buff=0.5)
        cur = curtain()
        self.add(trace, cur)

        # ---------------------------------------------------------- timeline
        self.play(cur.animate.set_fill(opacity=0), run_time=FADE_IN, rate_func=smooth)
        self.remove(cur)
        wait_until(HEAD_AT)
        self.play(FadeIn(head), run_time=0.6)
        wait_until(DECAY_AT)                                # runs down: damping on, start recording
        bal.damp.set_value(F.OMEGA0_6497 / (2 * Q_SHOWN))   # amplitude decay rate for Q_SHOWN
        t0["t"] = self.renderer.time
        self.play(FadeIn(exag), FadeIn(trace_axis), run_time=0.8)
        wait_until(EQ_AT)                                   # the new term
        self.play(Write(eq), run_time=1.4)
        self.play(Create(new_term), FadeIn(drag), run_time=0.8)
        wait_until(TWIN_AT)                                 # the mass on a spring
        self.play(FadeIn(twin, shift=UP * 0.1), run_time=0.9)
        wait_until(Q_AT)                                    # Q
        self.play(Write(q), run_time=1.2)
        wait_until(LOSS_AT)
        self.play(FadeIn(loss, shift=LEFT * 0.1), run_time=0.9)
        for i, t in enumerate(NUM_AT):                      # Q = 300
            wait_until(t)
            anims = [FadeIn(nums[i], shift=RIGHT * 0.1)] + ([FadeIn(rep)] if i == 0 else [])
            self.play(*anims, run_time=0.8)

        wait_until(FINAL_HOLD_UNTIL)
        cur.set_fill(opacity=0)
        self.add(cur)
        self.play(cur.animate.set_fill(opacity=1), run_time=FADE_OUT)
        log.write(__file__)
