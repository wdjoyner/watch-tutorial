"""Film 4, scene 08 - "Temperature" (advanced): warming changes every term of
f0 = (1/2 pi) sqrt(E b h^3 / 12 L I): b, h and L grow by alpha_hs, I by 2 alpha_bal,
and the modulus E by beta_E. Added up, (1/f) df/dT = beta_E/2 + 3 alpha_hs/2 - alpha_bal
(b + 3h - L gives 3 alpha_hs). For plain steel, bars of the three terms in s/day per
degree show the modulus term swamping the rest: about -10 s/day per degree,
-100 s/day for 10 degrees.

Build (render + voice + mux):   python build.py 4/scene08_temperature
Render only (quick preview):    PYTHONPATH=.:films/film04_regulating_organ manim -ql films/film04_regulating_organ/scene08_temperature.py Scene08
Narration lines and their start times live in scene08_temperature.voice.txt.
Numbers from figures.py (beta_E for steel from the chapter; both expansion
coefficients at the chapter's order of magnitude, 1e-5 per degree).
"""
from manim import *
import figures as F
from movement import vignette, BG, GLOW
from ui import ftext, label, heading, curtain, clock, WARM, COOL, sci, m

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds.
# Keep the timeline roughly in step with scene08_temperature.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 1.0
F0_AT = 1.4                           # the formula
WARM_AT, WARM_DURATION = 2.4, 3.0     # "Warm a watch" (the thermometer rises)
CHIP_AT = {"spring": 5.6, "balance": 6.8, "modulus": 8.4}   # spring, balance, modulus E
RESULT_AT = 12.0                      # "Added up, the rate changes by ..."
WHY3_AT = 16.6                        # "...three halves of the spring's expansion"
BARS_AT = 22.2                        # "For a plain steel spring"
SWAMP_AT = 24.6                       # "the modulus term swamps the rest"
TOTAL_AT = 27.0                       # "about ten seconds a day per degree"
TEN_AT = 30.6                         # "Ten degrees warmer"
FINAL_HOLD_UNTIL = 35.2               # the last line ends about 33.4 s
FADE_OUT = 1.5

# --- bars (seconds a day per degree) ------------------------------------
BAR_X0, BAR_Y, BAR_DY = 0.6, -0.95, 0.62   # zero line x, first bar's y, spacing
SCALE = 0.42                          # scene units per s/day
# =====================================================================


class Scene08(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.add(vignette())
        wait_until = clock(self)

        head = heading("TEMPERATURE", "how heat changes the rate").to_corner(UL, buff=0.5)
        f0 = ftext("f₀  =  (1 / 2π) √( E b h³ / 12 L I )", 0.62).move_to([0.7, 2.75, 0])

        # thermometer
        bulb = Circle(radius=0.22).set_fill(WARM, 1).set_stroke(WHITE, 1)
        tube = RoundedRectangle(width=0.2, height=1.6, corner_radius=0.1).set_stroke(WHITE, 1).set_fill(BG, 1)
        tube.next_to(bulb, UP, buff=-0.08)
        level = ValueTracker(0.25)
        fill = always_redraw(lambda: Rectangle(width=0.1, height=1.4 * level.get_value())
                             .set_fill(WARM, 1).set_stroke(width=0).move_to(tube.get_bottom() + UP * (0.07 + 0.7 * level.get_value())))
        thermo = VGroup(tube, fill, bulb).move_to([-6.0, 1.25, 0])

        chips = {
            "spring": label("spring:  b, h, L  grow by  αₛ  per °C", 0.26, WHITE),
            "balance": label("balance rim:  I  grows by  2 αᵣ", 0.26, WHITE),
            "modulus": label("spring's modulus  E  changes by  β  per °C", 0.26, WARM),
        }
        VGroup(*chips.values()).arrange(DOWN, aligned_edge=LEFT, buff=0.16).move_to([0.7, 1.55, 0])
        result = ftext("(1/f) df/dT   =   β / 2   +   3 αₛ / 2   −   αᵣ", 0.6, GLOW).move_to([0.7, 0.45, 0])
        why3 = label("b  +  3h  −  L   →   αₛ + 3αₛ − αₛ  =  3 αₛ", 0.24).next_to(result, DOWN, buff=0.14)

        # bars for steel, in seconds a day per degree
        rows = [("β / 2", "modulus", F.TEMP_TERMS["modulus"], WARM),
                ("+ 3 αₛ / 2", "spring", F.TEMP_TERMS["spring"], COOL),
                ("− αᵣ", "balance", F.TEMP_TERMS["balance"], COOL)]
        zero = Line([BAR_X0, BAR_Y + 0.35, 0], [BAR_X0, BAR_Y - 2 * BAR_DY - 0.35, 0]).set_stroke(GREY_B, 1.5)
        bars = VGroup()
        for i, (name, key, v, col) in enumerate(rows):
            y = BAR_Y - i * BAR_DY
            r = Rectangle(width=abs(v) * SCALE, height=0.32).set_fill(col, 0.9).set_stroke(width=0)
            r.move_to([BAR_X0 + v * SCALE / 2, y, 0])
            n = ftext(name, 0.36, WHITE).move_to([-5.4, y, 0], aligned_edge=LEFT)
            val = label(m(f"{v:+.1f}"), 0.26, col).next_to(r, LEFT if v < 0 else RIGHT, buff=0.1)
            bars.add(VGroup(n, r, val))
        unit = label("seconds a day, per °C warmer  (plain steel spring)", 0.24).next_to(zero, UP, buff=0.08)
        note = label(m(f"steel: β ≈ {sci(F.BETA_E_STEEL)} per °C;   αₛ, αᵣ ~ {sci(F.ALPHA_ORDER, 0)} per °C"), 0.22)
        note.move_to([0.7, BAR_Y - 2 * BAR_DY - 0.65, 0])
        total = ftext(m(f"total  ≈  {F.TEMP_TOTAL:.0f} s/day per °C"), 0.5, GLOW).move_to([3.9, BAR_Y - 2 * BAR_DY - 1.25, 0])
        ten = ftext(m(f"10 °C warmer:  ≈  {round(F.TEMP_10C, -1):.0f} s/day"), 0.5, WARM).next_to(total, LEFT, buff=0.9)

        cur = curtain()
        self.add(cur)

        # ---------------------------------------------------------- timeline
        self.play(cur.animate.set_fill(opacity=0), run_time=FADE_IN, rate_func=smooth)
        self.remove(cur)
        wait_until(F0_AT)
        self.play(FadeIn(head), Write(f0), run_time=1.0)
        wait_until(WARM_AT)                                 # warm it
        self.play(FadeIn(thermo), run_time=0.5)
        self.play(level.animate.set_value(0.85), run_time=WARM_DURATION - 0.5)
        for k in ("spring", "balance", "modulus"):
            wait_until(CHIP_AT[k])
            self.play(FadeIn(chips[k], shift=RIGHT * 0.1), run_time=0.7)
        wait_until(RESULT_AT)                               # added up
        self.play(Write(result), run_time=1.6)
        wait_until(WHY3_AT)
        self.play(FadeIn(why3), run_time=0.7)

        wait_until(BARS_AT)                                 # steel, term by term
        self.play(Create(zero), FadeIn(unit), *[FadeIn(b[0]) for b in bars], run_time=0.8)
        self.play(*[GrowFromEdge(b[1], RIGHT if rows[i][2] < 0 else LEFT) for i, b in enumerate(bars)],
                  *[FadeIn(b[2]) for b in bars], FadeIn(note), run_time=1.0)
        wait_until(SWAMP_AT)                                # the modulus term swamps the rest
        self.play(Indicate(bars[0][1], color=WARM, scale_factor=1.05), run_time=1.2)
        wait_until(TOTAL_AT)
        self.play(FadeIn(total, shift=UP * 0.1), run_time=0.8)
        wait_until(TEN_AT)                                  # ten degrees
        self.play(FadeIn(ten, shift=UP * 0.1), run_time=0.8)

        wait_until(FINAL_HOLD_UNTIL)
        cur.set_fill(opacity=0)
        self.add(cur)
        self.play(cur.animate.set_fill(opacity=1), run_time=FADE_OUT)
