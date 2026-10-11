"""Film 4, scene 05 - "A worked example": numbers for a balance the size of this
movement's. ETA does not publish them, so they are the chapter's representative
values (tagged on screen): I = 40 mg cm^2; at 2.5 Hz, kappa = I omega0^2, about
9.9e-7 N m/rad; at 270 degrees it holds E = kappa A^2 / 2, about 11 microjoules;
a ribbon 0.20 x 0.040 mm (E = 190 GPa) reaches that stiffness at about 21 cm,
drawn to scale beside the chapter's 4 Hz wristwatch spring (about 13 cm).

Build (render + voice + mux):   python build.py 4/scene05_example
Render only (quick preview):    PYTHONPATH=.:films/film04_regulating_organ manim -ql films/film04_regulating_organ/scene05_example.py Scene05
Narration lines and their start times live in scene05_example.voice.txt.
Every number is formatted from figures.py.
"""
from manim import *
import figures as F
from movement import vignette, BG, GLOW
from balance import HAIRSPRING
from ui import ftext, label, tag, heading, curtain, clock, sci

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds.
# Keep the timeline roughly in step with scene05_example.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 1.0
HEAD_AT = 1.4                         # "Let's put in numbers"
TAG_AT = 3.6                          # "ETA doesn't publish them"
ROW_AT = {"I": 10.2, "kappa": 15.4, "E": 23.4, "L": 31.0}
RIBBON_AT, RIBBON_DURATION = 35.6, 2.2    # "...at about twenty-one centimeters long"
WRIST_AT = 38.6                       # the 4 Hz wristwatch spring, for comparison
FINAL_HOLD_UNTIL = 42.0               # the last line ends about 39.5 s
FADE_OUT = 1.5

# --- layout ------------------------------------------------------------
ROW_Y = {"I": 2.0, "kappa": 1.05, "E": 0.1, "L": -0.85}
COL_X = (-6.4, -3.3, 2.0)             # left edges: what, formula, value
CM = 0.4                              # scene units per centimeter, for the ribbons
RIBBON_X0, RIBBON_Y = -5.6, (-2.75, -3.35)
# =====================================================================


class Scene05(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.add(vignette())
        wait_until = clock(self)

        head = heading("A WORKED EXAMPLE", "a balance the size of this movement's").to_corner(UL, buff=0.5)
        rep = tag("representative values, not ETA's specification").next_to(head, RIGHT, buff=0.6, aligned_edge=UP)

        rows = {   # what, formula, its inputs (small, beneath), value
            "I": ("moment of inertia", f"I  =  {sci(F.I_6497)} kg m²", "", f"{F.I_6497 * 1e10:.0f} mg cm²"),
            "kappa": ("stiffness at 2.5 Hz", "κ  =  I ω₀²", f"ω₀  =  2π × {F.F_6497:g}  =  {F.OMEGA0_6497:.1f} rad/s",
                      f"≈  {sci(F.K_6497)} N m/rad"),
            "E": ("energy at 270°", "energy  =  ½ κ A²", f"A  =  270°  =  {F.AMP:.2f} rad", f"≈  {F.E_6497 * 1e6:.0f} μJ"),
            "L": ("hairspring length", "L  =  E b h³ / 12 κ",
                  f"E = {F.E_HS / 1e9:.0f} GPa,   b = {F.B_HS_6497 * 1e3:.2f} mm,   h = {F.H_HS_6497 * 1e3:.3f} mm",
                  f"≈  {F.L_HS_6497 * 100:.0f} cm"),
        }
        groups = {}
        for k, (what, formula, inputs, value) in rows.items():
            y = ROW_Y[k]
            a = label(what, 0.27, GREY_B).move_to([COL_X[0], y, 0], aligned_edge=LEFT)
            b = ftext(formula, 0.46).move_to([COL_X[1], y, 0], aligned_edge=LEFT)
            sub = label(inputs, 0.22).next_to(b, DOWN, buff=0.1, aligned_edge=LEFT) if inputs else VMobject()
            c = ftext(value, 0.48, GLOW).move_to([COL_X[2], y, 0], aligned_edge=LEFT)
            groups[k] = VGroup(a, VGroup(b, sub), c)
        rule = Line([COL_X[0], ROW_Y["L"] - 0.6, 0], [6.6, ROW_Y["L"] - 0.6, 0]).set_stroke(GREY_D, 1)

        # ribbons to scale, with a ruler
        def ribbon(cm, y, color, text):
            bar = Rectangle(width=cm * CM, height=0.12).set_fill(color, 1).set_stroke(width=0)
            bar.move_to([RIBBON_X0, y, 0], aligned_edge=LEFT)
            return VGroup(bar, label(text, 0.24, color).next_to(bar, RIGHT, buff=0.2))
        r1 = ribbon(F.L_HS_6497 * 100, RIBBON_Y[0], HAIRSPRING, f"{F.L_HS_6497 * 100:.0f} cm,  2.5 Hz,  this balance")
        r2 = ribbon(F.L_HS_4HZ * 100, RIBBON_Y[1], GREY_B,
                    f"{F.L_HS_4HZ * 100:.0f} cm,  4 Hz wristwatch balance  ({F.I_4HZ * 1e10:.0f} mg cm²,  {F.E_4HZ * 1e6:.1f} μJ)")
        ruler = VGroup(Line([RIBBON_X0, RIBBON_Y[0] + 0.35, 0], [RIBBON_X0 + 25 * CM, RIBBON_Y[0] + 0.35, 0]).set_stroke(GREY_B, 1.2))
        for cm in range(0, 26):
            h = 0.16 if cm % 5 == 0 else 0.07
            x = RIBBON_X0 + cm * CM
            ruler.add(Line([x, RIBBON_Y[0] + 0.35, 0], [x, RIBBON_Y[0] + 0.35 + h, 0]).set_stroke(GREY_B, 1.2))
            if cm % 5 == 0:
                ruler.add(label(f"{cm} cm" if cm == 25 else str(cm), 0.2).next_to([x, RIBBON_Y[0] + 0.5, 0], UP, buff=0.04))

        cur = curtain()
        self.add(cur)

        # ---------------------------------------------------------- timeline
        self.play(cur.animate.set_fill(opacity=0), run_time=FADE_IN, rate_func=smooth)
        self.remove(cur)
        wait_until(HEAD_AT)
        self.play(FadeIn(head, shift=DOWN * 0.1), run_time=0.8)
        wait_until(TAG_AT)
        self.play(FadeIn(rep, shift=LEFT * 0.1), run_time=0.8)
        for k in ("I", "kappa", "E", "L"):
            wait_until(ROW_AT[k])
            g = groups[k]
            self.play(FadeIn(g[0]), Write(g[1]), run_time=1.2)
            self.play(FadeIn(g[2], shift=LEFT * 0.15), run_time=0.7)
        self.play(Create(rule), run_time=0.5)
        wait_until(RIBBON_AT)                               # to scale
        self.play(FadeIn(ruler), GrowFromEdge(r1[0], LEFT), run_time=RIBBON_DURATION)
        self.play(FadeIn(r1[1]), run_time=0.6)
        wait_until(WRIST_AT)
        self.play(GrowFromEdge(r2[0], LEFT), FadeIn(r2[1]), run_time=1.2)

        wait_until(FINAL_HOLD_UNTIL)
        cur.set_fill(opacity=0)
        self.add(cur)
        self.play(cur.animate.set_fill(opacity=1), run_time=FADE_OUT)
