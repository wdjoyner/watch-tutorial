"""Film 5, scene 03 - "How small?": the chapter's example. The amplitude falls
from 270 to 220 degrees (4.71 to 3.84 rad, representative) over the power
reserve, and the rate may change by at most 1 s/day (11.6 ppm). The real
parabola at the bound, df/f = 3 beta Theta^2 / 8 kappa in ppm, shows that
drift; solving gives |beta|/kappa below about 4 x 10^-6 rad^-2. At the turning
point the cubic torque is then about 10^-4 of the linear torque, and the rate is
held to about 1 part in 100,000.

Build (render + voice + mux):   python build.py 5/scene03_how_small
Render only (quick preview):    PYTHONPATH=.:films/film05_isochronism manim -ql films/film05_isochronism/scene03_how_small.py Scene03
Narration lines and their start times live in scene03_how_small.voice.txt. Numbers from figures.py.
No balance on screen: the steady tick track plays.
"""
from manim import *
import iso  # noqa: F401  (first: puts Film 4's helpers on the path)
import figures as F
from iso import Plot, DEG
from movement import vignette, BG, GLOW
from ui import ftext, label, heading, tag, curtain, clock, sci, WARM, COOL

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds.
# Keep the timeline roughly in step with scene03_how_small.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 1.0
HEAD_AT = 1.2                         # "How small must beta be?"
PLOT_AT = 2.6
FALLS_AT = 5.6                        # "the amplitude falls from two hundred seventy degrees to two hundred twenty"
BUDGET_AT = 11.6                      # "allow the rate to change by one second a day"
SOLVE_AT = 17.5                       # "Then beta over kappa must be below about four millionths"
BOUND_AT = 19.4
BARS_AT = 23.5                        # "the cubic torque is then only one ten-thousandth"
PART_AT = 29.6                        # "held to about one part in a hundred thousand"
GAME_AT = 35.0                        # "a parts-per-hundred-thousand game"
FINAL_HOLD_UNTIL = 40.4               # the last line ends about 38.8 s
FADE_OUT = 1.5

# --- the plot -----------------------------------------------------------
PLOT_O, PLOT_W, PLOT_H = (-6.2, -2.7), 5.6, 4.4
X_MAX, Y_MAX = 300.0, 45.0            # degrees, ppm
RIGHT_X = 0.6                         # left edge of the formula column
# =====================================================================


class Scene03(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.add(vignette())
        wait_until = clock(self)

        ppm = lambda deg: F.rate_shift(F.BETA_MAX, deg * DEG) * 1e6
        p = Plot(PLOT_O, PLOT_W, PLOT_H, (0, X_MAX), (0, Y_MAX))
        frame = VGroup(p, p.xlabel("amplitude  Θ"), p.ylabel("rate shift,  ppm"),
                       *[p.xtick(d, f"{d}°") for d in (90, 180, 270)],
                       *[p.ytick(y, f"{y}") for y in (10, 20, 30, 40)])
        curve = p.curve(ppm, 0, X_MAX, color=GLOW, width=3.5)
        hi, lo = 270.0, 220.0
        marks = VGroup()
        for d in (hi, lo):
            q = p.c2p(d, ppm(d))
            marks.add(DashedLine(p.c2p(d, 0), q, dash_length=0.07).set_stroke(GREY_B, 1.2),
                      DashedLine(p.c2p(0, ppm(d)), q, dash_length=0.07).set_stroke(GREY_B, 1.2),
                      Dot(q, radius=0.08, color=WHITE))
        arrow = CurvedArrow(p.c2p(hi, ppm(hi)) + UP * 0.25, p.c2p(lo, ppm(lo)) + UP * 0.25, angle=0.6,
                            color=WARM, stroke_width=3, tip_length=0.16)
        falls = label("over the power reserve", 0.22, WARM).next_to(arrow, LEFT, buff=0.1).shift(UP * 0.5)
        # the drift between the two amplitudes, on the y-axis: a hand-drawn bracket (Brace needs LaTeX)
        ya, yb = p.c2p(0, ppm(lo)), p.c2p(0, ppm(hi))
        bx = ya[0] + 0.28
        band = Rectangle(width=PLOT_W, height=yb[1] - ya[1]).set_stroke(width=0).set_fill(WARM, 0.16)
        band.move_to([p.c2p(X_MAX / 2, 0)[0], (ya[1] + yb[1]) / 2, 0])
        drift = label(f"{(ppm(hi) - ppm(lo)):.1f} ppm  =  1 s/day", 0.24, WARM).move_to(band.get_center() + LEFT * 1.55)

        rep = tag("representative amplitudes")
        amps = ftext(f"Θ:  270°  →  220°     ({F.AMP_FULL:.2f}  →  {F.AMP_LOW:.2f} rad)", 0.42)
        budget = ftext(f"budget:  1 s/day  =  {F.PPM_PER_S_DAY:.1f} ppm", 0.42)
        ineq = ftext(f"(3β / 8κ)({F.AMP_FULL:.2f}²  −  {F.AMP_LOW:.2f}²)  ≤  {sci(F.BUDGET, 2)}", 0.42)
        bound = ftext("|β| / κ  ≲  4 × 10⁻⁶  rad⁻²", 0.58, GLOW)
        col = VGroup(amps, rep, budget, ineq, bound).arrange(DOWN, buff=0.24, aligned_edge=LEFT)
        col.move_to([RIGHT_X, 1.55, 0], aligned_edge=LEFT)
        rep.shift(RIGHT * 0.1)

        # the two torques at the turning point: the cubic one is too thin to draw
        bar_w = 5.4
        lin_bar = Rectangle(width=bar_w, height=0.32).set_stroke(width=0).set_fill(COOL, 0.85)
        cub_bar = Rectangle(width=bar_w * F.CUBIC_OVER_LINEAR, height=0.32).set_stroke(width=0).set_fill(WARM, 1)
        lin_row = VGroup(label("linear torque  κΘ", 0.24, COOL), lin_bar).arrange(DOWN, buff=0.08, aligned_edge=LEFT)
        cub_row = VGroup(label("cubic torque  βΘ³", 0.24, WARM), cub_bar).arrange(DOWN, buff=0.08, aligned_edge=LEFT)
        bars = VGroup(lin_row, cub_row).arrange(DOWN, buff=0.22, aligned_edge=LEFT).move_to([RIGHT_X, -1.25, 0], aligned_edge=LEFT)
        thin = label(f"βΘ² / κ  ≈  10⁻⁴:  thinner than a hair at this scale", 0.22, WARM).next_to(cub_bar, RIGHT, buff=0.15)
        part = ftext("Δf / f  ≈  1 part in 100,000", 0.48, GLOW).next_to(bars, DOWN, buff=0.35, aligned_edge=LEFT)
        game = label("a parts-per-hundred-thousand game", 0.44, GLOW, bold=True).move_to([RIGHT_X, -3.35, 0], aligned_edge=LEFT)

        head = heading("HOW SMALL?", "the chapter's example").to_corner(UL, buff=0.5)
        cur = curtain()
        self.add(cur)

        # ---------------------------------------------------------- timeline
        self.play(cur.animate.set_fill(opacity=0), run_time=FADE_IN, rate_func=smooth)
        self.remove(cur)
        wait_until(HEAD_AT)
        self.play(FadeIn(head), run_time=0.7)
        wait_until(PLOT_AT)
        self.play(FadeIn(frame), Create(curve), run_time=1.4)
        wait_until(FALLS_AT)                                # 270 -> 220 degrees
        self.play(FadeIn(amps, shift=RIGHT * 0.1), FadeIn(rep), FadeIn(marks[:3]), run_time=0.9)
        self.play(FadeIn(marks[3:]), Create(arrow), FadeIn(falls), run_time=1.2)
        wait_until(BUDGET_AT)                               # 1 s/day
        self.play(FadeIn(budget, shift=RIGHT * 0.1), FadeIn(band), FadeIn(drift), run_time=1.0)
        wait_until(SOLVE_AT)                                # solve for beta
        self.play(Write(ineq), run_time=1.4)
        wait_until(BOUND_AT)
        self.play(FadeIn(bound, scale=1.1), run_time=0.9)
        wait_until(BARS_AT)                                 # the two torques
        self.play(FadeIn(lin_row[0]), GrowFromEdge(lin_bar, LEFT), run_time=1.0)
        self.play(FadeIn(cub_row), FadeIn(thin), run_time=0.9)
        wait_until(PART_AT)
        self.play(FadeIn(part, shift=UP * 0.1), run_time=0.8)
        wait_until(GAME_AT)
        self.play(FadeIn(game, scale=1.05), run_time=0.9)

        wait_until(FINAL_HOLD_UNTIL)
        cur.set_fill(opacity=0)
        self.add(cur)
        self.play(cur.animate.set_fill(opacity=1), run_time=FADE_OUT)
