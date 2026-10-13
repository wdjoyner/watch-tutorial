"""Film 5, scene 01 - "Beyond Hooke's law": torque against angle beside a slowed
balance. Hooke's law tau = -kappa phi is a straight line, only the first term of
the true curve. A spring that acts the same both ways twisted has an odd torque,
so the next term is cubic: tau ~ -kappa phi - beta phi^3 (drawn exaggerated).
It is negligible near the center and matters only near the ends of a big swing,
so it changes the period, not the damping.

Build (render + voice + mux):   python build.py 5/scene01_beyond_hooke
Render only (quick preview):    PYTHONPATH=.:films/film05_isochronism manim -ql films/film05_isochronism/scene01_beyond_hooke.py Scene01
Narration lines and their start times live in scene01_beyond_hooke.voice.txt.
The scene writes scene01_beyond_hooke.ticks.txt on every render.
"""
from manim import *
import iso  # noqa: F401  (first: puts Film 4's helpers on the path)
from iso import IsoBalance, Plot
from movement import vignette, BG, GLOW
from balance import BeatLog
from ui import ftext, label, heading, tag, curtain, clock, WARM, COOL

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds.
# Keep the timeline roughly in step with scene01_beyond_hooke.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 1.0
HEAD_AT = 1.2
LINE_AT = 4.0                         # "twist it twice as far, and it pushes back twice as hard"
HOOKE_AT = 9.1                        # "That's Hooke's law"
FIRST_AT = 11.4                       # "only the first term of the true torque curve"
ODD_AT = 15.4                         # "the same whichever way it's twisted"
CUBIC_AT = 20.4                       # "minus beta phi cubed"
CENTER_AT = 24.6                      # "Near the center it's negligible"
ENDS_AT = 27.6                        # "near the ends of a big swing"
PERIOD_AT = 31.6                      # "changes how long each swing takes"
NOT_AT = 34.0                         # "not how quickly the swing dies"
FINAL_HOLD_UNTIL = 38.0               # the last line ends about 36.5 s
FADE_OUT = 1.5

# --- the balance -------------------------------------------------------
BAL_AT, BAL_R, AMP = (-4.5, 0.3), 1.6, 1.2
RATE = 0.25                           # slow motion (tagged)

# --- the torque plot (axes through its center) -------------------------
PLOT_O, PLOT_W, PLOT_H = (0.0, -2.6), 6.4, 4.8
PHI_MAX, TAU_MAX = 1.45, 2.2          # plot ranges, in units of AMP and kappa * AMP
B_SHOWN = 0.38                        # EXAGGERATED cubic coefficient, in these units (tagged)
NEAR = 0.45                           # "near the center": |phi| below this fraction of the swing
# =====================================================================


class Scene01(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.add(vignette())
        wait_until = clock(self)

        bal = IsoBalance(center=BAL_AT, radius=BAL_R, amp=AMP, amp_full=AMP)
        bal.rate.set_value(RATE)
        bal.attach(self)
        log = BeatLog(self, lambda: bal.beats(), 1)
        slow = tag("slowed 4×").next_to(bal, DOWN, buff=0.35)

        p = Plot(PLOT_O, PLOT_W, PLOT_H, (-PHI_MAX, PHI_MAX), (-TAU_MAX, TAU_MAX))
        x_ax = Arrow(p.c2p(-PHI_MAX, 0), p.c2p(PHI_MAX, 0), buff=0, stroke_width=2, tip_length=0.15, color=GREY_B)
        y_ax = Arrow(p.c2p(0, -TAU_MAX), p.c2p(0, TAU_MAX), buff=0, stroke_width=2, tip_length=0.15, color=GREY_B)
        axes = VGroup(x_ax, y_ax,
                      label("angle  φ", 0.24).next_to(x_ax.get_end(), DOWN, buff=0.12).align_to(x_ax, RIGHT),
                      label("spring torque  τ", 0.24).next_to(y_ax.get_end(), LEFT, buff=0.12))
        turn = VGroup(*[DashedLine(p.c2p(s, -TAU_MAX * 0.9), p.c2p(s, TAU_MAX * 0.9), dash_length=0.06)
                        .set_stroke(GREY_C, 1.2) for s in (-1, 1)])
        turn_lbl = label("ends of the swing", 0.2, GREY_C).next_to(p.c2p(1, -TAU_MAX * 0.9), DOWN, buff=0.08)

        lin = p.curve(lambda x: -x, color=COOL, width=3)
        cub = p.curve(lambda x: -x - B_SHOWN * x ** 3, -1.22, 1.22, color=GLOW, width=3.5)
        # the gap between the curves near the ends (where the cubic matters)
        def gap(sign):
            xs = np.linspace(sign * NEAR * 1.4, sign * 1.0, 40)
            top = [p.c2p(x, -x) for x in xs]
            bot = [p.c2p(x, -x - B_SHOWN * x ** 3) for x in xs[::-1]]
            return Polygon(*top, *bot).set_stroke(width=0).set_fill(WARM, 0.35)
        gaps = VGroup(gap(1), gap(-1))
        center = Rectangle(width=p.c2p(NEAR, 0)[0] - p.c2p(-NEAR, 0)[0], height=PLOT_H * 0.9)
        center.move_to(p.c2p(0, 0)).set_stroke(width=0).set_fill(COOL, 0.12)
        near_lbl = label("near the center: the same", 0.22, COOL).next_to(center, DOWN, buff=0.08)

        # a dot riding the curve at the balance's current angle
        w_cubic = ValueTracker(0.0)
        dot_vis = ValueTracker(0.0)
        dot = Dot(radius=0.08, color=WHITE)

        def ride(m):
            x = bal.swing() / AMP
            m.move_to(p.c2p(x, -x - w_cubic.get_value() * B_SHOWN * x ** 3))
            m.set_opacity(dot_vis.get_value())
        dot.add_updater(ride)

        hooke = VGroup(ftext("τ  =  −κ φ", 0.6, COOL), label("Hooke's law", 0.26, COOL)).arrange(DOWN, buff=0.1)
        hooke.move_to(p.c2p(0.95, 1.55))
        first = label("only the first term", 0.24).next_to(hooke, DOWN, buff=0.12)
        odd = ftext("τ(−φ)  =  −τ(φ)    ⇒    no  φ²  term", 0.42).move_to(p.c2p(0, TAU_MAX) + UP * 0.55)
        cubic = ftext("τ  ≈  −κ φ  −  β φ³", 0.6, GLOW).move_to(p.c2p(-0.98, -1.05))
        exag = tag("β exaggerated").next_to(cubic, DOWN, buff=0.15)
        verdict = VGroup(label("changes the period", 0.36, GLOW, bold=True),
                         label("not the damping", 0.36, GREY_B)).arrange(DOWN, buff=0.12, aligned_edge=LEFT)
        verdict.move_to([BAL_AT[0], -2.9, 0])
        strike = Line(verdict[1].get_left(), verdict[1].get_right()).set_stroke(WARM, 2)

        head = heading("BEYOND HOOKE'S LAW", "the true torque curve").to_corner(UL, buff=0.5)
        cur = curtain()
        self.add(dot, w_cubic, dot_vis, cur)

        # ---------------------------------------------------------- timeline
        self.play(cur.animate.set_fill(opacity=0), run_time=FADE_IN, rate_func=smooth)
        self.remove(cur)
        wait_until(HEAD_AT)
        self.play(FadeIn(head), FadeIn(slow), run_time=0.7)
        wait_until(LINE_AT)                                 # the straight line
        self.play(FadeIn(axes), run_time=0.7)
        self.play(Create(lin), dot_vis.animate.set_value(1.0), run_time=1.4)
        self.play(FadeIn(turn), FadeIn(turn_lbl), run_time=0.6)
        wait_until(HOOKE_AT)
        self.play(FadeIn(hooke, shift=DOWN * 0.1), run_time=0.8)
        wait_until(FIRST_AT)
        self.play(FadeIn(first), run_time=0.6)
        wait_until(ODD_AT)                                  # symmetry: an odd torque
        self.play(Write(odd), run_time=1.3)
        wait_until(CUBIC_AT)                                # the cubic term
        self.play(Create(cub), w_cubic.animate.set_value(1.0), Write(cubic), run_time=1.6)
        self.play(FadeIn(exag), run_time=0.5)
        wait_until(CENTER_AT)                               # near the center: no difference
        self.play(FadeIn(center), FadeIn(near_lbl), run_time=0.8)
        wait_until(ENDS_AT)                                 # the ends of the swing
        self.play(FadeIn(gaps), Indicate(turn_lbl, color=WARM), run_time=1.0)
        wait_until(PERIOD_AT)
        self.play(FadeIn(verdict[0], shift=UP * 0.1), run_time=0.7)
        wait_until(NOT_AT)
        self.play(FadeIn(verdict[1]), run_time=0.5)
        self.play(Create(strike), run_time=0.5)

        wait_until(FINAL_HOLD_UNTIL)
        cur.set_fill(opacity=0)
        self.add(cur)
        self.play(cur.animate.set_fill(opacity=1), run_time=FADE_OUT)
        log.write(__file__)
