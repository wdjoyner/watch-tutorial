"""Film 6, scene 03b - "The symbols": a key to the letters used from scene 04 on,
all describing the balance. Left: one and a half swings of phi(t) with the
amplitude +-Theta dashed, a dot riding the curve and, once phi' is introduced,
its tangent (phi' is the slope: largest at the center, zero at the ends). Then
one kick, drawn a little off center so that its angle phi_k can be seen, at
time t_k, with its size J. Right: a table that fills in as each symbol is named:
phi, Theta, Theta*, phi', t_k, phi_k, J, I, kappa, omega0.

Build (render + voice + mux):   python build.py 6/scene03b_symbols
Render only (quick preview):    PYTHONPATH=.:films/film06_escapement manim -ql films/film06_escapement/scene03b_symbols.py Scene03b
Narration lines and their start times live in scene03b_symbols.voice.txt.
"""
from manim import *
import prev  # noqa: F401  (first: Film 4 and 5 helpers on the path)
import ui6  # noqa: F401  (extra subscripts)
from ui6 import fmark
from iso import Plot
from movement import vignette, BG, GLOW
from ui import label, heading, tag, curtain, clock, WARM, COOL

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds.
# Keep the timeline roughly in step with scene03b_symbols.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 1.0
HEAD_AT = 1.2                         # "Before the mathematics, here are the symbols we'll use."
PHI_AT = 7.3                          # "Phi is its angle at any moment, measured from rest."
SWING_AT = 11.6                       # "It swings back and forth, out to plus Theta and back to minus Theta."
THETA_AT = 16.9                       # "Theta is the amplitude: the largest angle of a swing."
STAR_AT = 21.3                        # "Theta star is the amplitude the watch finally settles at."
SPEED_AT = 26.3                       # "Phi prime is the angular speed ..."
SLOPE_AT = 31.0                       # "It is largest at the center, and zero at the ends of the swing."
TK_AT = 37.7                          # "The escapement kicks the balance at moments t sub k."
PHIK_AT = 41.6                        # "Phi sub k is the angle at that moment ..."
J_AT = 44.6                           # "... and J is the size of the kick, an angular impulse."
CONST_AT = (51.6, 53.6, 55.8)         # "I is the balance's inertia", "kappa ...", "omega nought is ..."
FINAL_HOLD_UNTIL = 60.8               # the last line ends about 58.8 s
FADE_OUT = 1.5

CYCLES = 1.5                          # swings shown on the plot, in full periods
DOT_SPEED = 0.045                     # periods per video second for the riding dot (slow, for the eye)
KICK_PHI = -0.3                       # where the illustrative kick lands, as a fraction of Theta (off center on purpose)
ROWS = [  # (symbol as Pango markup, meaning)
    ("φ", "the balance's angle, measured from rest"),
    ("Θ", "the amplitude: the largest angle of a swing"),
    ("Θ*", "the amplitude the watch settles at"),
    ("φ′", "the angular speed: how fast φ changes (rad/s)"),
    ("t<sub>k</sub>", "the moment of a kick"),
    ("φ<sub>k</sub>", "the angle at that moment"),
    ("J", "the size of the kick (an angular impulse)"),
    ("I", "the balance's inertia (Film 4)"),
    ("κ", "the hairspring's stiffness (Film 4)"),
    ("ω<sub>0</sub>", "2π f<sub>0</sub>, f<sub>0</sub> the frequency (Film 4)"),
]
TEXT = dict(t="time", phi="angle φ", plus="+Θ", minus="−Θ", slope="φ′ = slope", kick="J",
            off="kick drawn off center, so φₖ shows", key="SYMBOL KEY")
# =====================================================================


class Scene03b(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.add(vignette())
        wait_until = clock(self)
        head = heading("THE SYMBOLS", "all about the balance").to_corner(UL, buff=0.5)

        # ---------------- the swing, phi(t) = Theta sin(2 pi t)
        p = Plot((-6.3, -2.2), 6.3, 4.2, (0, CYCLES), (-1.3, 1.3))
        phi = lambda t: np.sin(TAU * t)
        curve = p.curve(phi, 0, CYCLES, color=COOL, width=3, n=240)
        zero = DashedLine(p.c2p(0, 0), p.c2p(CYCLES, 0), stroke_width=1, color=GREY_D)
        axl = VGroup(label(TEXT["t"], 0.22).next_to(p.x_axis, DOWN, buff=0.12).align_to(p.x_axis, RIGHT),
                     label(TEXT["phi"], 0.22, COOL).next_to(p.y_axis, UP, buff=0.08).align_to(p.y_axis, LEFT))
        amp = VGroup(DashedLine(p.c2p(0, 1), p.c2p(CYCLES, 1), stroke_width=1.6, color=GLOW),
                     DashedLine(p.c2p(0, -1), p.c2p(CYCLES, -1), stroke_width=1.6, color=GLOW))
        amp_l = VGroup(fmark(TEXT["plus"], 0.4, GLOW).next_to(p.c2p(0, 1), LEFT, buff=0.1),
                       fmark(TEXT["minus"], 0.4, GLOW).next_to(p.c2p(0, -1), LEFT, buff=0.1))

        tt = ValueTracker(0.0)          # time on the plot, in periods
        run = ValueTracker(0.0)         # 0 = dot parked, DOT_SPEED = riding
        driver = Mobject().add_updater(lambda m, dt: tt.set_value((tt.get_value() + dt * run.get_value()) % CYCLES))
        dot = always_redraw(lambda: Dot(p.c2p(tt.get_value(), phi(tt.get_value())), radius=0.09, color=WARM))
        drop = always_redraw(lambda: DashedLine(p.c2p(tt.get_value(), 0), p.c2p(tt.get_value(), phi(tt.get_value())),
                                                stroke_width=1.6, color=WARM))
        sx, sy = p.c2p(1, 0)[0] - p.c2p(0, 0)[0], p.c2p(0, 1)[1] - p.c2p(0, 0)[1]   # screen units per period, per Theta

        def tangent():
            t = tt.get_value()
            d = np.array([sx, sy * TAU * np.cos(TAU * t), 0.0])
            d = d / np.linalg.norm(d) * 0.9
            c = p.c2p(t, phi(t))
            return Line(c - d, c + d).set_stroke(WHITE, 3)
        tan = always_redraw(tangent)
        slope_l = always_redraw(lambda: fmark(TEXT["slope"], 0.36, WHITE)
                                .next_to(p.c2p(tt.get_value(), phi(tt.get_value())), UR, buff=0.32))

        # one kick, off center on purpose
        tk = 1.0 - np.arcsin(-KICK_PHI) / TAU      # rising through KICK_PHI just before the second center crossing
        kp = p.c2p(tk, KICK_PHI)
        k_t = VGroup(DashedLine(p.c2p(tk, -1.3), kp, stroke_width=1.4, color=GLOW),
                     fmark("t<sub>k</sub>", 0.4, GLOW).next_to(p.c2p(tk, -1.3), DOWN, buff=0.08))
        k_phi = VGroup(DashedLine(p.c2p(0, KICK_PHI), kp, stroke_width=1.4, color=GLOW),
                       fmark("φ<sub>k</sub>", 0.4, GLOW).next_to(p.c2p(0, KICK_PHI), LEFT, buff=0.1))
        k_dot = Dot(kp, radius=0.1, color=GLOW)
        k_J = VGroup(Arrow(kp + LEFT * 0.55 + DOWN * 0.1, kp + LEFT * 0.08, buff=0, stroke_width=5, color=GLOW, tip_length=0.16),
                     fmark(TEXT["kick"], 0.44, GLOW))
        k_J[1].next_to(k_J[0], LEFT, buff=0.08)
        off = tag(TEXT["off"], GLOW, 0.17).next_to(p.x_axis, DOWN, buff=0.12).align_to(p.x_axis, LEFT)

        # ---------------- the table
        key = label(TEXT["key"], 0.26, GLOW, bold=True)
        rows = VGroup()
        for sym, txt in ROWS:
            s = fmark(sym, 0.44, WHITE)
            m = MarkupText(txt, font="DejaVu Sans", color=GREY_A).scale(0.22) if "<" in txt else label(txt, 0.22, GREY_A)
            rows.add(VGroup(s, m))
        x_sym, x_txt, y0, dy = 0.95, 1.75, 2.15, 0.44
        key.move_to([x_sym, y0 + 0.5, 0], aligned_edge=LEFT)
        for i, (s, m) in enumerate(rows):
            s.move_to([x_sym + 0.3, y0 - i * dy, 0])
            m.move_to([x_txt, y0 - i * dy, 0], aligned_edge=LEFT)
        line = Line([x_sym, y0 + 0.25, 0], [6.7, y0 + 0.25, 0]).set_stroke(GREY_D, 1)

        cur = curtain()
        self.add(cur, driver)

        def row(i):
            return FadeIn(rows[i], shift=LEFT * 0.1)

        # ---------------------------------------------------------- timeline
        self.play(cur.animate.set_fill(opacity=0), run_time=FADE_IN, rate_func=smooth)
        self.remove(cur)
        wait_until(HEAD_AT)
        self.play(FadeIn(head), FadeIn(key), Create(line), run_time=0.8)
        wait_until(PHI_AT)
        self.play(FadeIn(p), FadeIn(zero), FadeIn(axl), Create(curve), row(0), run_time=1.4)
        self.play(FadeIn(dot), FadeIn(drop), run_time=0.5)
        wait_until(SWING_AT)
        self.play(run.animate.set_value(DOT_SPEED), Create(amp), FadeIn(amp_l), run_time=1.0)
        wait_until(THETA_AT)
        self.play(row(1), Indicate(amp_l, color=WHITE), run_time=0.8)
        wait_until(STAR_AT)
        self.play(row(2), run_time=0.6)
        wait_until(SPEED_AT)
        self.play(row(3), FadeIn(tan), FadeIn(slope_l), FadeOut(drop), run_time=0.8)
        wait_until(SLOPE_AT)
        self.play(run.animate.set_value(DOT_SPEED * 1.6), run_time=0.5)
        wait_until(TK_AT - 0.6)
        self.play(FadeOut(tan), FadeOut(slope_l), FadeOut(dot), run.animate.set_value(0.0), run_time=0.6)
        self.play(row(4), Create(k_t), FadeIn(k_dot, scale=1.6), FadeIn(off), run_time=0.8)
        wait_until(PHIK_AT)
        self.play(row(5), Create(k_phi), run_time=0.8)
        wait_until(J_AT)
        self.play(row(6), GrowArrow(k_J[0]), FadeIn(k_J[1]), run_time=0.8)
        for i, t in enumerate(CONST_AT):
            wait_until(t)
            self.play(row(7 + i), run_time=0.6)

        wait_until(FINAL_HOLD_UNTIL)
        cur.set_fill(opacity=0)
        self.add(cur)
        self.play(cur.animate.set_fill(opacity=1), run_time=FADE_OUT)
