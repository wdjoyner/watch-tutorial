"""Film 5, scene 02 - "Rate against amplitude": the Poincare-Lindstedt result
omega(Theta) ~ omega0 (1 + 3 beta Theta^2 / 8 kappa), so df/f ~ 3 beta Theta^2 / 8 kappa,
a parabola in the amplitude (beta exaggerated, and tagged so). A linear spring
gives a flat line. A slowed balance runs down, and a dot rides down the curve
with its amplitude: with beta > 0 the watch runs fast at large amplitude and
loses as the amplitude falls; then the curve flips over for beta < 0, which gains.

Build (render + voice + mux):   python build.py 5/scene02_parabola
Render only (quick preview):    PYTHONPATH=.:films/film05_isochronism manim -ql films/film05_isochronism/scene02_parabola.py Scene02
Narration lines and their start times live in scene02_parabola.voice.txt.
Numbers from figures.py. The scene writes scene02_parabola.ticks.txt on every render.
"""
from manim import *
import iso  # noqa: F401  (first: puts Film 4's helpers on the path)
import figures as F
from iso import IsoBalance, Plot, DEG
from movement import vignette, BG, GLOW
from balance import BeatLog
from ui import ftext, label, heading, tag, curtain, clock, WARM, COOL

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds.
# Keep the timeline roughly in step with scene02_parabola.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 1.0
HEAD_AT = 1.2
OMEGA_AT = 4.6                        # "the frequency rises with the square of the amplitude"
DF_AT = 8.2                           # "by three beta theta squared over eight kappa"
PLOT_AT = 12.5                        # "Plot rate against amplitude"
DECAY_AT = 14.0                       # the balance starts to run down; the dot rides the curve
FLAT_AT = 16.8                        # "A perfectly linear spring would give a flat line"
FAST_AT = 23.4                        # "runs fast while the swing is large"
LOSES_AT = 27.2                       # "and loses as the amplitude falls"
FLIP_AT = 30.8                        # "With beta negative, it gains"
FINAL_HOLD_UNTIL = 35.0               # the last line ends about 33.4 s
FADE_OUT = 1.5

# --- the balance -------------------------------------------------------
BAL_AT, BAL_R, AMP_FULL = (-4.7, 0.9), 1.45, 1.2   # AMP_FULL is drawn for 270 degrees
START_DEG, END_DEG = 300.0, 165.0     # amplitude when the decay starts, and at the fade-out
RATE = 0.25                           # slow motion (tagged)

# --- the plot -----------------------------------------------------------
PLOT_O, PLOT_W, PLOT_H = (-1.6, -2.9), 7.6, 4.7
X_MAX = 330.0                         # degrees
Y_SPAN = 0.026                        # omega / omega0 from 1 - Y_SPAN to 1 + Y_SPAN
# =====================================================================


class Scene02(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.add(vignette())
        wait_until = clock(self)

        b = F.BETA_SHOWN
        amp0 = AMP_FULL * START_DEG / 270
        bal = IsoBalance(center=BAL_AT, radius=BAL_R, amp=amp0, amp_full=AMP_FULL, beta=b)
        bal.rate.set_value(RATE)
        bal.attach(self)
        log = BeatLog(self, lambda: bal.beats(), 1)
        tags = VGroup(tag("slowed 4×"), tag("β exaggerated")).arrange(RIGHT, buff=0.2).next_to(bal, DOWN, buff=0.35)

        p = Plot(PLOT_O, PLOT_W, PLOT_H, (0, X_MAX), (1 - Y_SPAN, 1 + Y_SPAN))
        sign = ValueTracker(1.0)
        shift = lambda deg: 3 * b * sign.get_value() * (deg * DEG) ** 2 / 8
        frame = VGroup(p, p.xlabel("amplitude  Θ"), p.ylabel("rate  ω / ω₀"),
                       *[p.xtick(d, f"{d}°") for d in (90, 180, 270)], p.ytick(1.0, "1"))
        flat = DashedLine(p.c2p(0, 1), p.c2p(X_MAX, 1), dash_length=0.1).set_stroke(COOL, 2.5)
        flat_lbl = label("perfectly linear spring", 0.24, COOL).next_to(p.c2p(X_MAX, 1), UP, buff=0.08).shift(LEFT * 1.2)
        curve = p.curve(lambda d: 1 + shift(d), 0, X_MAX * 0.97, color=GLOW, width=3.5)
        curve.add_updater(lambda m: m.set_points_smoothly(p.pts(lambda d: 1 + shift(d), 0, X_MAX * 0.97)))
        fast = label("fast", 0.26, WARM).move_to(p.c2p(X_MAX * 0.1, 1 + Y_SPAN * 0.8))
        slow = label("slow", 0.26, COOL).move_to(p.c2p(X_MAX * 0.1, 1 - Y_SPAN * 0.8))

        dot_vis = ValueTracker(0.0)
        dot = Dot(radius=0.09, color=WHITE)
        dot.add_updater(lambda m: m.move_to(p.c2p(bal.real_amp() / DEG, 1 + shift(bal.real_amp() / DEG)))
                        .set_opacity(dot_vis.get_value()))
        drop = Line(ORIGIN, RIGHT).set_stroke(WHITE, 1.2)
        drop.add_updater(lambda m: m.put_start_and_end_on(p.c2p(bal.real_amp() / DEG, 1 - Y_SPAN),
                                                          dot.get_center()).set_stroke(opacity=0.35 * dot_vis.get_value()))

        omega = ftext("ω(Θ)  ≈  ω₀ (1  +  3βΘ² / 8κ)", 0.56).move_to([2.2, 3.05, 0])
        df = ftext("Δf / f  ≈  3βΘ² / 8κ", 0.56, GLOW).next_to(omega, DOWN, buff=0.22)
        pl = label("Poincaré–Lindstedt", 0.24).next_to(omega, LEFT, buff=0.4)
        pos = label("β > 0:  stiffening spring", 0.26, WARM).move_to(p.c2p(X_MAX * 0.3, 1 + Y_SPAN * 0.55))
        loses = Arrow(p.c2p(285, 1 + shift(285)) + UP * 0.25 + LEFT * 0.1, p.c2p(200, 1 + shift(200)) + UP * 0.3,
                      buff=0, stroke_width=3, tip_length=0.16, color=WARM)
        loses_lbl = label("loses as Θ falls", 0.24, WARM).next_to(loses, UP, buff=0.05).shift(LEFT * 0.3)
        neg = label("β < 0:  gains as Θ falls", 0.26, COOL).move_to(p.c2p(X_MAX * 0.3, 1 - Y_SPAN * 0.55))

        head = heading("RATE AGAINST AMPLITUDE", "a parabola, not a line").to_corner(UL, buff=0.5)
        cur = curtain()
        self.add(sign, dot_vis, cur)

        # ---------------------------------------------------------- timeline
        self.play(cur.animate.set_fill(opacity=0), run_time=FADE_IN, rate_func=smooth)
        self.remove(cur)
        wait_until(HEAD_AT)
        self.play(FadeIn(head), FadeIn(tags), run_time=0.7)
        wait_until(OMEGA_AT)
        self.play(Write(omega), FadeIn(pl), run_time=1.4)
        wait_until(DF_AT)
        self.play(FadeIn(df, shift=DOWN * 0.1), run_time=0.9)
        wait_until(PLOT_AT)                                 # the plot and its parabola
        self.play(FadeIn(frame), run_time=0.7)
        self.add(curve)
        self.play(Create(curve), run_time=1.2)
        wait_until(DECAY_AT)                                # the balance runs down; the dot rides the curve
        bal.damp.set_value(np.log(START_DEG / END_DEG) / (RATE * (FINAL_HOLD_UNTIL + FADE_OUT - DECAY_AT)))
        self.add(dot, drop)
        self.play(dot_vis.animate.set_value(1.0), run_time=0.6)
        wait_until(FLAT_AT)                                 # the linear spring: a flat line
        self.play(Create(flat), FadeIn(flat_lbl), run_time=1.0)
        wait_until(FAST_AT - 1.6)
        self.play(FadeIn(pos), run_time=0.7)
        wait_until(FAST_AT)
        self.play(FadeIn(fast), FadeIn(slow), run_time=0.7)
        wait_until(LOSES_AT)
        self.play(GrowArrow(loses), FadeIn(loses_lbl), run_time=0.9)
        wait_until(FLIP_AT)                                 # beta < 0: the curve flips over
        self.play(FadeOut(loses), FadeOut(loses_lbl), FadeOut(pos), run_time=0.4)
        self.play(sign.animate.set_value(-1.0), bal.beta.animate.set_value(-b), FadeIn(neg), run_time=1.6)

        wait_until(FINAL_HOLD_UNTIL)
        cur.set_fill(opacity=0)
        self.add(cur)
        self.play(cur.animate.set_fill(opacity=1), run_time=FADE_OUT)
        log.write(__file__)
