"""Film 6, scene 07 - "Energy in, energy out": the amplitude settles where the
books balance. Energy lost per cycle, W_loss = 4 mu_Cou Theta (dry, Coulomb) +
pi mu_vis omega0 Theta^2 (viscous), against the escapement's roughly constant
energy per cycle, E_in. They cross at Theta*; below it the balance gains, above
it loses, so Theta* is stable. Then the constant-impulse alternative,
E_in = 2 J omega0 Theta: a straight line, which the parabola still overtakes.

Numbers: the REPRESENTATIVE 6497 balance of figures.py (Film 4's I, Q 300),
with its losses at 270 deg split half dry, half viscous, and E_in chosen to
balance there. Tagged representative on screen.

Build (render + voice + mux):   python build.py 6/scene07_balance_sheet
Render only (quick preview):    PYTHONPATH=.:films/film06_escapement manim -ql films/film06_escapement/scene07_balance_sheet.py Scene07
Narration lines and their start times live in scene07_balance_sheet.voice.txt. Numbers from figures.py.
"""
from manim import *
import prev  # noqa: F401  (first: Film 4 and 5 helpers on the path)
from ui6 import fmark
import figures as F
from iso import Plot
from movement import vignette, BG, GLOW
from ui import label, heading, tag, curtain, clock, WARM, COOL

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds.
# Keep the timeline roughly in step with scene07_balance_sheet.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 1.0
AXES_AT = 1.2                         # "Each cycle, the balance loses energy in two ways."
DRY_AT = 7.0                          # "Dry, Coulomb friction is a fixed torque ..."
VISC_AT = 12.6                        # "Oil and air act like viscous drag ..."
SUM_AT = 16.6                         # the total
EIN_AT = 19.0                         # "The escapement turns the wheel through fixed angles ..."
CROSS_AT = 29.2                       # "Where the curves cross, the books balance."
LESS_AT = 35.9                        # "Swing less, and the escapement gives more than friction takes ..."
MORE_AT = 40.4                        # "Swing more, and it shrinks."
STABLE_AT = 42.9                      # "Theta star is stable."
IMPULSE_AT = 46.0                     # "Even if each kick were a fixed impulse instead ..."
FINAL_HOLD_UNTIL = 56.5               # the last line ends about 54.6 s
FADE_OUT = 1.5

THETA_MAX = 360.0                     # degrees on the x axis
Y_MAX = 0.40                          # microjoules on the y axis
TEXT = dict(x="amplitude Θ", y="energy per cycle (μJ)", dry="dry:  4 μ<sub>Cou</sub> Θ",
            visc="viscous:  π μ<sub>vis</sub> ω<sub>0</sub> Θ²", loss="lost:  W<sub>loss</sub>(Θ)",
            ein="E<sub>in</sub>:  the escapement", star="Θ*", gain="gain > loss", lose="loss > gain",
            stable="stable", impulse="if the kick were a fixed impulse:  E<sub>in</sub> = 2 J ω<sub>0</sub> Θ",
            repr="representative 6497 balance: losses half dry, half viscous at 270°")
# =====================================================================


class Scene07(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.add(vignette())
        wait_until = clock(self)
        head = heading("ENERGY IN, ENERGY OUT", "where the amplitude settles").to_corner(UL, buff=0.5)

        uj = 1e6
        D = F.DEG
        dry = lambda d: 4 * F.MU_COU * d * D * uj
        visc = lambda d: np.pi * F.MU_VIS * F.OMEGA0 * (d * D) ** 2 * uj
        loss = lambda d: dry(d) + visc(d)
        e_in = F.E_IN * uj
        imp = lambda d: 2 * F.J_CONST * F.OMEGA0 * d * D * uj
        star = F.AMP / D                                       # 270 by construction

        p = Plot((-5.6, -3.2), 9.0, 5.4, (0, THETA_MAX), (0, Y_MAX))
        ticks = VGroup(*[p.xtick(d, f"{d:.0f}°", 0.2) for d in (90, 180, 270, 360)],
                       *[p.ytick(y, f"{y:.1f}", 0.2) for y in (0.1, 0.2, 0.3, 0.4)])
        xl, yl = p.xlabel(TEXT["x"], 0.24), p.ylabel(TEXT["y"], 0.24)
        c_dry = p.curve(dry, 0, THETA_MAX, color=GREY_B, width=2.5)
        c_visc = p.curve(visc, 0, THETA_MAX, color=COOL, width=2.5)
        c_loss = p.curve(loss, 0, THETA_MAX, color=WARM, width=4)
        c_in = Line(p.c2p(0, e_in), p.c2p(THETA_MAX, e_in)).set_stroke(GLOW, 4)
        l_dry = fmark(TEXT["dry"], 0.4, GREY_B).next_to(p.c2p(THETA_MAX, dry(THETA_MAX)), RIGHT, buff=0.1)
        l_visc = fmark(TEXT["visc"], 0.4, COOL).next_to(p.c2p(THETA_MAX, visc(THETA_MAX)), RIGHT, buff=0.1)
        l_loss = fmark(TEXT["loss"], 0.42, WARM).next_to(p.c2p(THETA_MAX, loss(THETA_MAX)), RIGHT, buff=0.1)
        l_in = fmark(TEXT["ein"], 0.42, GLOW).next_to(p.c2p(THETA_MAX, e_in), RIGHT, buff=0.1)
        rep = tag(TEXT["repr"], GREY_B, 0.18).to_corner(UR, buff=0.4)

        dot = Dot(p.c2p(star, e_in), radius=0.1, color=WHITE)
        drop = DashedLine(p.c2p(star, e_in), p.c2p(star, 0), stroke_width=1.5, color=WHITE)
        sl = fmark(TEXT["star"], 0.55, WHITE).next_to(p.c2p(star, e_in * 0.55), LEFT, buff=0.12)
        a_less = Arrow(p.c2p(150, 0.02), p.c2p(240, 0.02), buff=0, stroke_width=5, color=GLOW, tip_length=0.18)
        a_more = Arrow(p.c2p(355, 0.02), p.c2p(300, 0.02), buff=0, stroke_width=5, color=WARM, tip_length=0.18)
        t_less = label(TEXT["gain"], 0.22, GLOW).next_to(a_less, UP, buff=0.06)
        t_more = label(TEXT["lose"], 0.22, WARM).next_to(a_more, UP, buff=0.06).shift(LEFT * 0.2)
        stable = label(TEXT["stable"], 0.3, WHITE, bold=True).next_to(dot, UP, buff=0.25)
        c_imp = DashedVMobject(p.curve(imp, 0, THETA_MAX, color=GREY_A, width=2.5), num_dashes=40)
        l_imp = fmark(TEXT["impulse"], 0.38, GREY_A).move_to(p.c2p(150, 0.36))

        cur = curtain()
        self.add(cur)

        # ---------------------------------------------------------- timeline
        self.play(cur.animate.set_fill(opacity=0), run_time=FADE_IN, rate_func=smooth)
        self.remove(cur)
        wait_until(AXES_AT)
        self.play(FadeIn(head), FadeIn(p), FadeIn(ticks), FadeIn(xl), FadeIn(yl), FadeIn(rep), run_time=1.0)
        wait_until(DRY_AT)
        self.play(Create(c_dry), FadeIn(l_dry), run_time=1.2)
        wait_until(VISC_AT)
        self.play(Create(c_visc), FadeIn(l_visc), run_time=1.2)
        wait_until(SUM_AT)
        self.play(Create(c_loss), FadeIn(l_loss), run_time=1.2)
        wait_until(EIN_AT)
        self.play(Create(c_in), FadeIn(l_in), run_time=1.2)
        wait_until(CROSS_AT)
        self.play(FadeIn(dot, scale=2), Create(drop), FadeIn(sl), run_time=1.0)
        wait_until(LESS_AT)
        self.play(GrowArrow(a_less), FadeIn(t_less), run_time=0.8)
        wait_until(MORE_AT)
        self.play(GrowArrow(a_more), FadeIn(t_more), run_time=0.8)
        wait_until(STABLE_AT)
        self.play(FadeIn(stable, shift=UP * 0.1), run_time=0.6)
        wait_until(IMPULSE_AT)
        self.play(Create(c_imp), FadeIn(l_imp), run_time=1.6)

        wait_until(FINAL_HOLD_UNTIL)
        cur.set_fill(opacity=0)
        self.add(cur)
        self.play(cur.animate.set_fill(opacity=1), run_time=FADE_OUT)
