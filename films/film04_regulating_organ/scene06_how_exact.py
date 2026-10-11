"""Film 4, scene 06 - "How exact?": since f goes as sqrt(kappa / I), the
logarithmic derivative gives df/f = (1/2) dkappa/kappa - (1/2) dI/I. A spring 0.02 %
stiffer gains 8.6 s/day (marked on a rate axis); 1 s/day is 11.57 ppm; and the
chronometer band, -4 to +6 s/day, holds kappa / I to about one part in ten thousand.

Build (render + voice + mux):   python build.py 4/scene06_how_exact
Render only (quick preview):    PYTHONPATH=.:films/film04_regulating_organ manim -ql films/film04_regulating_organ/scene06_how_exact.py Scene06
Narration lines and their start times live in scene06_how_exact.voice.txt.
Every number is formatted from figures.py. The rate axis is drawn by hand
(NumberLine's numbers go through LaTeX).
"""
from manim import *
import figures as F
from movement import vignette, BG, GLOW
from ui import ftext, label, heading, curtain, clock, WARM, m

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds.
# Keep the timeline roughly in step with scene06_how_exact.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 1.0
HEAD_AT = 1.2                         # "How exact must these two numbers be?"
PROP_AT = 5.0                         # "Frequency goes as the square root of kappa over I"
LOG_AT = 9.4                          # "...moves the rate by half as much"
EXAMPLE_AT = 15.4                     # "Stiffen the spring by two hundredths of a percent"
MARK_AT = 19.0                        # "...gains almost nine seconds a day"
PPM_AT = 23.2                         # "One second a day is about twelve parts per million"
BAND_AT = 29.2                        # "between minus four and plus six seconds a day"
TOL_AT = 34.4                         # "...about one part in ten thousand"
FINAL_HOLD_UNTIL = 40.2               # the last line ends about 38.2 s
FADE_OUT = 1.5

# --- rate axis -----------------------------------------------------------
AXIS_Y, AXIS_X0, AXIS_X1 = -1.55, -5.6, 5.6
AXIS_MIN, AXIS_MAX = -10, 10          # seconds per day
BAND = "#5fc48a"
# =====================================================================


def ax(v):
    return AXIS_X0 + (v - AXIS_MIN) / (AXIS_MAX - AXIS_MIN) * (AXIS_X1 - AXIS_X0)


class Scene06(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.add(vignette())
        wait_until = clock(self)

        head = heading("HOW EXACT?", "rate sensitivity").to_corner(UL, buff=0.5)
        prop = ftext("f  ∝  √(κ / I)", 0.65).move_to([0, 2.65, 0])
        logd = ftext("Δf / f   =   ½ Δκ / κ   −   ½ ΔI / I", 0.65).move_to([0, 1.65, 0])
        log_note = label("small fractional changes: half as much in the rate", 0.24).next_to(logd, DOWN, buff=0.15)

        pct = lambda x: f"{x * 100:+.2f} %"
        example = VGroup(ftext(f"Δκ / κ  =  {pct(F.EX_KAPPA_UP)}", 0.5), ftext("→", 0.5, GREY_B),
                         ftext(f"Δf / f  =  {pct(F.EX_RATE)}", 0.5), ftext("→", 0.5, GREY_B),
                         ftext(f"{F.EX_S_DAY:+.1f} s/day", 0.55, GLOW)).arrange(RIGHT, buff=0.3).move_to([0, 0.3, 0])
        day_note = label(f"one day = {F.DAY:,.0f} s", 0.22).next_to(example[4], DOWN, buff=0.12)

        # the rate axis, seconds per day
        axis = VGroup(Line([AXIS_X0, AXIS_Y, 0], [AXIS_X1, AXIS_Y, 0]).set_stroke(GREY_B, 2))
        for v in range(AXIS_MIN, AXIS_MAX + 1, 2):
            axis.add(Line([ax(v), AXIS_Y - 0.08, 0], [ax(v), AXIS_Y + 0.08, 0]).set_stroke(GREY_B, 1.5))
            axis.add(label(m(f"{v:+d}") if v else "0", 0.22).next_to([ax(v), AXIS_Y - 0.1, 0], DOWN, buff=0.08))
        axis.add(label("seconds a day", 0.24).move_to([0, AXIS_Y - 0.62, 0]))
        marker = VGroup(Dot([ax(F.EX_S_DAY), AXIS_Y, 0], radius=0.09, color=GLOW),
                        label("κ  +0.02 %", 0.24, GLOW).next_to([ax(F.EX_S_DAY), AXIS_Y + 0.12, 0], UP, buff=0.1))
        ppm = ftext(f"1 s/day  =  1 / {F.DAY:,.0f}  ≈  {F.PPM_PER_S_DAY:.2f} ppm", 0.48).move_to([0, -2.9, 0])

        lo, hi = F.COSC
        band = Rectangle(width=ax(hi) - ax(lo), height=0.34).move_to([(ax(lo) + ax(hi)) / 2, AXIS_Y, 0])
        band.set_fill(BAND, 0.35).set_stroke(BAND, 1.5)
        band_lab = label(m(f"chronometer (COSC):  {lo:+.0f} to {hi:+.0f} s/day"), 0.26, BAND)
        band_lab.next_to(band, UP, buff=0.32)
        tol = VGroup(ftext(f"{hi:.0f} s/day  =  {F.COSC_FRAC * 1e6:.0f} ppm in f  =  {F.COSC_KAPPA_OVER_I * 1e6:.0f} ppm in κ / I", 0.42),
                     ftext("κ / I  right to about 1 part in 10,000", 0.55, GLOW)).arrange(DOWN, buff=0.18)
        tol.move_to([0, -3.1, 0])

        cur = curtain()
        self.add(cur)

        # ---------------------------------------------------------- timeline
        self.play(cur.animate.set_fill(opacity=0), run_time=FADE_IN, rate_func=smooth)
        self.remove(cur)
        wait_until(HEAD_AT)
        self.play(FadeIn(head, shift=DOWN * 0.1), run_time=0.8)
        wait_until(PROP_AT)
        self.play(Write(prop), run_time=1.2)
        wait_until(LOG_AT)
        self.play(Write(logd), run_time=1.6)
        self.play(FadeIn(log_note), run_time=0.6)
        wait_until(EXAMPLE_AT)                              # 0.02 % stiffer
        self.play(FadeIn(example[:3], shift=RIGHT * 0.1), FadeIn(axis), run_time=1.2)
        wait_until(MARK_AT)                                 # +8.6 s/day
        self.play(FadeIn(example[3:], shift=RIGHT * 0.1), FadeIn(day_note), GrowFromCenter(marker[0]),
                  FadeIn(marker[1]), run_time=1.0)
        wait_until(PPM_AT)                                  # 11.57 ppm
        self.play(FadeIn(ppm, shift=UP * 0.1), run_time=0.9)
        wait_until(BAND_AT)                                 # the chronometer band
        self.play(FadeOut(ppm), GrowFromCenter(band), FadeIn(band_lab), run_time=1.0)
        wait_until(TOL_AT)                                  # one part in ten thousand
        self.play(FadeIn(tol, shift=UP * 0.1), run_time=1.0)

        wait_until(FINAL_HOLD_UNTIL)
        cur.set_fill(opacity=0)
        self.add(cur)
        self.play(cur.animate.set_fill(opacity=1), run_time=FADE_OUT)
