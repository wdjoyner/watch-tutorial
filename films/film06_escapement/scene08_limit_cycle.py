"""Film 6, scene 08 - "The limit cycle": the chapter's phase portrait (friction
EXAGGERATED: Q 12, mu_Cou 0.1, E_in 6.40 per cycle, scaled units I = omega0 = 1).
A small start spirals out and a large start spirals in, both onto the same loop;
beside it, the amplitude at each swing converges to Theta* = 4.24. Then
Petrangeli's one bookkeeping step for his Swiss lever at 270 deg: impulses
supply 8.6 % of the balance's energy per period, losses take 4.0 %; the surplus
raises the peak speed from 74.02 to 75.71 rad/s, so the amplitude climbs about 6 deg.

Build (render + voice + mux):   python build.py 6/scene08_limit_cycle
Render only (quick preview):    PYTHONPATH=.:films/film06_escapement manim -ql films/film06_escapement/scene08_limit_cycle.py Scene08
Narration lines and their start times live in scene08_limit_cycle.voice.txt. Numbers from figures.py.
"""
from manim import *
import prev  # noqa: F401  (first: Film 4 and 5 helpers on the path)
import ui6  # noqa: F401  (extra subscripts)
from ui6 import fmark
import figures as F
from iso import Plot
from movement import vignette, BG, GLOW
from ui import ftext, label, heading, tag, curtain, clock, WARM, COOL

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds.
# Keep the timeline roughly in step with scene08_limit_cycle.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 1.0
PLANE_AT = 1.2                        # "Here is the same idea in the phase plane ..."
SMALL_AT = 9.1                        # "Start small, and the balance spirals out."
LARGE_AT = 12.0                       # "Start large, and it spirals in."
LOOP_AT = 14.6                        # "Both end on the same loop, a limit cycle."
CHOOSES_AT = 17.4                     # "The watch chooses its own amplitude."
GP_AT = 20.9                          # "Petrangeli did this bookkeeping for his Swiss lever."
BARS_AT = 25.0                        # "... the impulses supplied about eight and a half percent ..."
LOSS_AT = 31.5                        # "... and the losses took about four."
SPEED_AT = 36.7                       # "The surplus raises the peak speed ..."
STEP_AT = 44.0                        # "... so the amplitude climbs about six degrees."
REPEAT_AT = 47.5                      # "Repeat, until gain equals loss."
FINAL_HOLD_UNTIL = 52.0               # the last line ends about 50.1 s
FADE_OUT = 1.5

CYCLES, N = 6, 400
O, S = np.array([-3.0, 0.1, 0.0]), 0.36       # phase-plane origin on screen, and scale (kept above the caption band)
TEXT = dict(phi="φ", vel="φ′ / ω₀", small="small start", large="large start", loop="limit cycle",
            exag="friction exaggerated about {:.0f}×: the chapter's scaled example".format(prev.figures4.Q / F.LC_Q), amp="amplitude at each swing",
            swing="swing", star="Θ* = {:.2f}", chooses="the watch chooses its own amplitude",
            gp="Petrangeli (2017): his Swiss lever, assumed at 270°", per="per period, as a share of the balance's energy",
            gain="impulses:  {:.1f}%", loss="losses:  {:.1f}%",
            speed="ω′<sub>max</sub> = √(ω<sub>max</sub>² + 2 ΔE / I)",
            speed_n="{:.2f}  →  {:.2f}  rad/s".format(F.GP_WMAX, F.GP_WMAX_NEW),
            step="ΔΘ ≈ Δω<sub>max</sub> / ω<sub>0</sub> ≈ {:.3f} rad ≈ {:.1f}°".format(F.GP_DTHETA, F.GP_DTHETA / F.DEG),
            repeat="repeat until gain = loss")
# =====================================================================


class Scene08(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.add(vignette())
        wait_until = clock(self)
        head = heading("THE LIMIT CYCLE", "the watch chooses its amplitude").to_corner(UL, buff=0.5)

        P = lambda x, v: O + S * np.array([x, v, 0.0])
        ext = 2.75
        axes = VGroup(Arrow(O + LEFT * ext, O + RIGHT * ext, buff=0, stroke_width=2, color=GREY_B, tip_length=0.12),
                      Arrow(O + DOWN * ext, O + UP * ext, buff=0, stroke_width=2, color=GREY_B, tip_length=0.12))
        axl = VGroup(label(TEXT["phi"], 0.26).next_to(axes[0].get_end(), DOWN, buff=0.08),
                     label(TEXT["vel"], 0.24).next_to(axes[1].get_end(), RIGHT, buff=0.08))
        runs = {}
        for key, th0, col in (("small", F.LC_STARTS[0], COOL), ("large", F.LC_STARTS[1], WARM)):
            path, peaks = F.limit_cycle_run(th0, cycles=CYCLES, n=N)
            curve = VMobject().set_points_as_corners([P(x, v) for x, v in path[::2]]).set_stroke(col, 1.8, 0.9)
            start = Dot(P(th0, 0), radius=0.08, color=col)
            runs[key] = (curve, start, peaks, col)
        lc_path, _ = F.limit_cycle_run(F.LC_THETA, cycles=1, n=N)
        loop = DashedVMobject(VMobject().set_points_as_corners([P(x, v) for x, v in lc_path] + [P(*lc_path[0])]),
                              num_dashes=60).set_stroke(WHITE, 3)
        t_small = label(TEXT["small"], 0.22, COOL).next_to(runs["small"][1], DOWN, buff=0.12)
        t_large = label(TEXT["large"], 0.22, WARM).next_to(runs["large"][1], DOWN, buff=0.12)
        lp = P(F.LC_THETA * np.sin(-0.8), F.LC_THETA * np.cos(-0.8))
        t_loop = label(TEXT["loop"], 0.24, WHITE, bold=True).move_to(P(-6.6, 6.0))
        t_loop = VGroup(t_loop, Line(t_loop.get_bottom() + DOWN * 0.05, lp, stroke_width=1.2, color=WHITE))
        exag = tag(TEXT["exag"], GLOW, 0.18).to_corner(UR, buff=0.4)

        # amplitude at each swing
        npk = 2 * CYCLES + 1
        pa = Plot((1.3, -2.0), 5.0, 3.3, (0, npk - 1), (0, 7.2))
        dots = VGroup()
        for key in ("small", "large"):
            _, _, peaks, col = runs[key]
            dots.add(VGroup(*[Dot(pa.c2p(i, p), radius=0.05, color=col) for i, p in enumerate(peaks[:npk])]))
        star_line = DashedLine(pa.c2p(0, F.LC_THETA), pa.c2p(npk - 1, F.LC_THETA), stroke_width=1.6, color=WHITE)
        star_lbl = fmark(TEXT["star"].format(F.LC_THETA), 0.4, WHITE).next_to(star_line, UP, buff=0.06).align_to(star_line, LEFT).shift(RIGHT * 0.35)
        pal = VGroup(label(TEXT["amp"], 0.22).next_to(pa.y_axis, UP, buff=0.08).align_to(pa.y_axis, LEFT),
                     label(TEXT["swing"], 0.2).next_to(pa.x_axis, DOWN, buff=0.1).align_to(pa.x_axis, RIGHT))
        chooses = label(TEXT["chooses"], 0.3, GLOW, bold=True).move_to([3.8, 2.3, 0])

        # Petrangeli's step
        gp = tag(TEXT["gp"], GREY_B, 0.2).move_to([3.6, 2.6, 0])
        per = label(TEXT["per"], 0.2, GREY_B).next_to(gp, DOWN, buff=0.18)
        base, unit = np.array([2.2, 0.55, 0]), 0.15
        bar_g = Rectangle(width=0.9, height=unit * F.GP_GAIN_PCT).set_stroke(width=0).set_fill(GLOW, 0.9)
        bar_g.move_to(base, aligned_edge=DOWN)
        bar_l = Rectangle(width=0.9, height=unit * F.GP_LOSS_PCT).set_stroke(width=0).set_fill(WARM, 0.9)
        bar_l.move_to(base + RIGHT * 1.6, aligned_edge=DOWN)
        lab_g = label(TEXT["gain"].format(F.GP_GAIN_PCT), 0.22, GLOW).next_to(bar_g, DOWN, buff=0.1)
        lab_l = label(TEXT["loss"].format(F.GP_LOSS_PCT), 0.22, WARM).next_to(bar_l, DOWN, buff=0.1)
        speed = fmark(TEXT["speed"], 0.44).move_to([3.9, -0.45, 0])
        speed_n = ftext(TEXT["speed_n"], 0.42, GLOW).next_to(speed, DOWN, buff=0.2)
        step = fmark(TEXT["step"], 0.42).next_to(speed_n, DOWN, buff=0.25)
        repeat = label(TEXT["repeat"], 0.28, WHITE, bold=True).next_to(step, DOWN, buff=0.25)

        cur = curtain()
        self.add(cur)

        # ---------------------------------------------------------- timeline
        self.play(cur.animate.set_fill(opacity=0), run_time=FADE_IN, rate_func=smooth)
        self.remove(cur)
        wait_until(PLANE_AT)
        self.play(FadeIn(head), FadeIn(axes), FadeIn(axl), FadeIn(exag), run_time=1.0)
        self.play(FadeIn(pa), FadeIn(pal), run_time=0.8)
        wait_until(SMALL_AT)
        c, d, _, _ = runs["small"]
        self.play(FadeIn(d), FadeIn(t_small), run_time=0.4)
        self.play(Create(c), LaggedStart(*[FadeIn(x) for x in dots[0]], lag_ratio=0.5), run_time=2.4, rate_func=linear)
        wait_until(LARGE_AT)
        c, d, _, _ = runs["large"]
        self.play(FadeIn(d), FadeIn(t_large), run_time=0.4)
        self.play(Create(c), LaggedStart(*[FadeIn(x) for x in dots[1]], lag_ratio=0.5), run_time=2.2, rate_func=linear)
        wait_until(LOOP_AT)
        self.play(Create(loop), FadeIn(t_loop), Create(star_line), FadeIn(star_lbl), run_time=1.2)
        wait_until(CHOOSES_AT)
        self.play(FadeIn(chooses, shift=UP * 0.1), run_time=0.7)

        wait_until(GP_AT)
        self.play(FadeOut(VGroup(pa, pal, dots, star_line, star_lbl, chooses)), run_time=0.7)
        self.play(FadeIn(gp), FadeIn(per), run_time=0.7)
        wait_until(BARS_AT)
        self.play(GrowFromEdge(bar_g, DOWN), FadeIn(lab_g), run_time=0.8)
        wait_until(LOSS_AT)
        self.play(GrowFromEdge(bar_l, DOWN), FadeIn(lab_l), run_time=0.8)
        wait_until(SPEED_AT)
        self.play(FadeIn(speed), run_time=0.8)
        self.play(FadeIn(speed_n, shift=UP * 0.1), run_time=0.6)
        wait_until(STEP_AT)
        self.play(FadeIn(step, shift=UP * 0.1), run_time=0.7)
        wait_until(REPEAT_AT)
        self.play(FadeIn(repeat), run_time=0.6)

        wait_until(FINAL_HOLD_UNTIL)
        cur.set_fill(opacity=0)
        self.add(cur)
        self.play(cur.animate.set_fill(opacity=1), run_time=FADE_OUT)
