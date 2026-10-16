"""Film 6, scene 06 - "Escapement error": how big Airy's effect is, and why
unlocking makes the watch lose.
1. Petrangeli's worked Swiss lever (2.5 Hz): a shock of 0.01 rad/s at 24 deg
   moves the tick by 7.5e-7 s, less than a microsecond.
2. Unlocking happens just before center and pushes against the motion: J < 0
   at phi_k < 0, so J phi_k > 0 and Delta T > 0: the tick comes late, the watch loses.
3. With Theta^2 (amplitude squared) in the denominator, the error is 1.51 times larger at 220 deg than at 270.
4. A boxed rough estimate, credited to Petrangeli's model: about 1.1 s/day lost
   at 270 deg, 1.7 at 220 (figures.UNLOCK_BOX).

Build (render + voice + mux):   python build.py 6/scene06_escapement_error
Render only (quick preview):    PYTHONPATH=.:films/film06_escapement manim -ql films/film06_escapement/scene06_escapement_error.py Scene06
Narration lines and their start times live in scene06_escapement_error.voice.txt. Numbers from figures.py.
"""
from manim import *
import prev  # noqa: F401  (first: Film 4 and 5 helpers on the path)
import ui6  # noqa: F401  (extra subscripts)
import figures as F
from iso import Plot
from movement import vignette, BG, GLOW
from ui import ftext, label, heading, tag, curtain, clock, sci, WARM, COOL

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds.
# Keep the timeline roughly in step with scene06_escapement_error.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 1.0
GP_AT = 1.2                           # "How big is the effect? Petrangeli worked a Swiss lever ..."
GP_VALUES_AT = 6.6                    # "A shock that changes the speed by a hundredth ..."
GP_RESULT_AT = 13.4                   # "... moves the tick by less than a microsecond."
UNLOCK_AT = 17.7                      # "But the escapement can't act exactly at center."
PUSH_AT = 23.8                        # "... and unlocking pushes against the motion."
LOSES_AT = 30.0                       # "A backward kick before center delays the tick, so the watch loses."
SQUARE_AT = 35.5                      # "With the amplitude squared in the denominator ..."
RATIO_AT = 40.5                       # "... half as large again at two hundred twenty degrees ..."
BOX_AT = 47.6                         # "A rough estimate built on Petrangeli's model ..."
FILM5_AT = 56.0                       # "This is the escapement error from Film five ..."
FINAL_HOLD_UNTIL = 62.5               # the last line ends about 60.5 s
FADE_OUT = 1.5

UNLOCK_SPAN = (-23.0, -11.0)          # degrees of balance angle while unlocking [GP: 12 deg, before the 24 + 10 deg impulse]
TEXT = dict(gp="Petrangeli (2017): a model Swiss lever at 2.5 Hz",
            formula="ΔT = (I / κ) · φₖ · Δφ′ / Θ²",
            values=(f"I = {sci(F.GP_I, 1)} kg m²,   κ = {sci(F.GP_K, 2)} N m / rad",
                    f"Δφ′ = {F.GP_DV} rad/s  at  φₖ = 24°,   Θ = 270°"),
            result=f"ΔT ≈ {sci(F.GP_DT, 1)} s:  less than a microsecond",
            sp="speed", unlock="unlocking:\npushes back", center="center", motion="motion",
            sign=("before center:  φₖ < 0", "pushing back:  J < 0", "so  J · φₖ > 0  and  ΔT > 0", "the tick comes late: the watch loses"),
            square="error  ∝  1 / Θ²", amp=("270°", "220°"), ratio="× {:.2f}",
            film5="the escapement error of Film 5, now with its formula")
# =====================================================================


class Scene06(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.add(vignette())
        wait_until = clock(self)
        head = heading("ESCAPEMENT ERROR", "why unlocking makes a watch lose").to_corner(UL, buff=0.5)

        # 1. Petrangeli's numbers
        src = tag(TEXT["gp"], GREY_B, 0.2)
        formula = ftext(TEXT["formula"], 0.6)
        vals = VGroup(*[ftext(v, 0.42, GREY_A) for v in TEXT["values"]]).arrange(DOWN, buff=0.18)
        result = ftext(TEXT["result"], 0.55, GLOW)
        gp = VGroup(src, formula, vals, result).arrange(DOWN, buff=0.35).move_to([0, 0.3, 0])

        # 2. unlocking before center: the speed profile, the unlocking zone, the push back
        PE_Y, PE_H = -2.15, 2.1                 # bottom and height of the speed profile (above the caption band)
        pe = Plot((-6.3, PE_Y), 5.4, PE_H, (-90, 90), (0, 1.2))
        prof = pe.curve(lambda u: np.sqrt(max(0.0, 1 - (u / 90) ** 2)), -90, 90, color=WARM, width=3)   # schematic: +-90 stands for +-A
        x0, x1 = pe.c2p(UNLOCK_SPAN[0], 0)[0], pe.c2p(UNLOCK_SPAN[1], 0)[0]
        zone = Rectangle(width=x1 - x0, height=PE_H).set_stroke(width=0).set_fill(COOL, 0.25)
        zone.move_to([(x0 + x1) / 2, PE_Y + PE_H / 2, 0])
        um = (UNLOCK_SPAN[0] + UNLOCK_SPAN[1]) / 2
        top = pe.c2p(um, np.sqrt(1 - (um / 90) ** 2))
        push = Arrow(top + UP * 0.05, top + DOWN * 0.75, buff=0, stroke_width=5, color=COOL, tip_length=0.16)
        zl = label(TEXT["unlock"], 0.22, COOL).next_to(zone, LEFT, buff=0.3).shift(DOWN * 0.55)
        cl = VGroup(DashedLine(pe.c2p(0, 0), pe.c2p(0, 1.15), stroke_width=1.2, color=GREY_B),
                    label(TEXT["center"], 0.2).next_to(pe.c2p(0, 0), DOWN, buff=0.1))
        mot = Arrow(pe.c2p(-60, 1.12), pe.c2p(-25, 1.12), buff=0, stroke_width=3, color=GREY_A, tip_length=0.12)
        motl = label(TEXT["motion"], 0.2, GREY_A).next_to(mot, UP, buff=0.05)
        spl = label(TEXT["sp"], 0.2, WARM).next_to(pe.y_axis, UP, buff=0.06)
        diag = VGroup(pe, spl, prof, cl, zone, zl, mot, motl)

        sign = VGroup(*[ftext(s, 0.42, c) for s, c in zip(TEXT["sign"], (GREY_A, COOL, WHITE, WARM))])
        sign.arrange(DOWN, aligned_edge=LEFT, buff=0.2).move_to([2.6, -1.2, 0])

        # 3. 1 / Theta^2
        sq = ftext(TEXT["square"], 0.55, GLOW).move_to([2.6, -0.65, 0])
        base_y, bw, unit = -2.25, 0.8, 0.8
        bars = VGroup()
        for i, (a, h) in enumerate(zip(TEXT["amp"], (1.0, F.ESC_ERR_RATIO))):
            r = Rectangle(width=bw, height=unit * h).set_stroke(width=0).set_fill(COOL if i == 0 else WARM, 0.85)
            r.move_to([1.6 + 1.6 * i, base_y + unit * h / 2, 0])
            bars.add(VGroup(r, label(a, 0.24).next_to(r, DOWN, buff=0.1)))
        ratio = label(TEXT["ratio"].format(F.ESC_ERR_RATIO), 0.3, WARM, bold=True).next_to(bars[1][0], RIGHT, buff=0.2)

        # 4. the boxed rough estimate (credited to Petrangeli's model)
        lines = VGroup(label(F.UNLOCK_BOX[0], 0.22, GLOW, bold=True),
                       *[label(t, 0.22, WHITE) for t in F.UNLOCK_BOX[1:]]).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        box = VGroup(SurroundingRectangle(lines, buff=0.22, corner_radius=0.1).set_stroke(GLOW, 1.4).set_fill(BG, 0.92), lines)
        box.move_to([3.2, 1.05, 0])
        f5 = tag(TEXT["film5"], WARM, 0.22).move_to([3.2, -0.05, 0])

        cur = curtain()
        self.add(cur)

        # ---------------------------------------------------------- timeline
        self.play(cur.animate.set_fill(opacity=0), run_time=FADE_IN, rate_func=smooth)
        self.remove(cur)
        wait_until(GP_AT)
        self.play(FadeIn(head), FadeIn(src), Write(formula), run_time=1.4)
        wait_until(GP_VALUES_AT)
        self.play(FadeIn(vals, shift=UP * 0.1), run_time=0.9)
        wait_until(GP_RESULT_AT)
        self.play(FadeIn(result, shift=UP * 0.1), run_time=0.8)
        wait_until(UNLOCK_AT)
        small = VGroup(formula, result)
        self.play(FadeOut(src), FadeOut(vals), small.animate.arrange(RIGHT, buff=0.6).scale(0.75).move_to([1.0, 2.6, 0]),
                  run_time=1.0)
        self.play(FadeIn(pe), FadeIn(spl), Create(prof), FadeIn(cl), GrowArrow(mot), FadeIn(motl), run_time=1.2)
        self.play(FadeIn(zone), FadeIn(zl), run_time=0.7)
        wait_until(PUSH_AT)
        self.play(GrowArrow(push), run_time=0.7)
        wait_until(LOSES_AT)
        self.play(LaggedStart(*[FadeIn(s, shift=RIGHT * 0.1) for s in sign], lag_ratio=0.45), run_time=2.6)
        wait_until(SQUARE_AT)
        self.play(FadeOut(sign), FadeIn(sq), run_time=0.8)
        self.play(FadeIn(bars[0]), run_time=0.6)
        wait_until(RATIO_AT)
        self.play(GrowFromEdge(bars[1][0], DOWN), FadeIn(bars[1][1]), FadeIn(ratio), run_time=1.0)
        wait_until(BOX_AT)
        self.play(FadeIn(box, shift=UP * 0.1), run_time=0.9)
        wait_until(FILM5_AT)
        self.play(FadeIn(f5), run_time=0.7)

        wait_until(FINAL_HOLD_UNTIL)
        cur.set_fill(opacity=0)
        self.add(cur)
        self.play(cur.animate.set_fill(opacity=1), run_time=FADE_OUT)
