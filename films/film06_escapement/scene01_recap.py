"""Film 6, scene 01 - "Where we left off": a short recap of Films 4 and 5.
Left: Film 4's balance, swinging in slow motion, with f0 = (1/2 pi) sqrt(kappa / I)
(f0 is the frequency; I and kappa glossed) and the energy bill (about 2 % of the
energy lost per cycle, from Film 4's representative Q of 300; Q itself is not
named on screen). Right: Film 5's chain, mainspring torque -> energy ->
amplitude -> rate, with "rate" defined (seconds a day gained or lost) and the
open question: where does the amplitude settle?

Build (render + voice + mux):   python build.py 6/scene01_recap
Render only (quick preview):    PYTHONPATH=.:films/film06_escapement manim -ql films/film06_escapement/scene01_recap.py Scene01
Narration lines and their start times live in scene01_recap.voice.txt. Numbers from Film 4's figures.py.
The scene writes scene01_recap.ticks.txt on every render (the slowed balance's beats).
"""
from manim import *
import prev  # noqa: F401  (first: Film 4 and 5 helpers on the path)
from prev import figures4 as F4
from balance import BalanceModel, BeatLog
from movement import vignette, BG, GLOW
from ui import ftext, label, heading, tag, curtain, clock, WARM, COOL

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds.
# Keep the timeline roughly in step with scene01_recap.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 1.0
FILM4_AT = 1.2                        # "Two films ago, we met the balance and hairspring."
GLOSS_AT = 5.0                        # "Two numbers, the balance's inertia I and the hairspring's stiffness kappa ..."
FORMULA_AT = 9.8                      # "... set how often it swings: its frequency, f nought, equals ..."
BILL_AT = 18.4                        # "Friction takes about two percent ..."
FILM5_AT = 26.4                       # "Last film, we saw the frequency shift with the amplitude ..."
RATE_AT = 32.4                        # "That changes the watch's rate: how many seconds a day it gains or loses."
QUESTION_AT = 42.0                    # "One question was left open: where does the amplitude settle?"
ANSWER_AT = 45.6                      # "The answer lies in the escapement."
FINAL_HOLD_UNTIL = 50.2               # the last line ends about 48.2 s
FADE_OUT = 1.5

# --- layout ----------------------------------------------------------
BAL_CENTER, BAL_R, RATE = (-3.6, 0.75), 1.4, 0.25
CHAIN_X, CHAIN_Y = (1.15, 3.0, 4.85, 6.7), 0.6
TEXT = dict(film4="Film 4: the regulating organ", film5="Film 5: isochronism",
            formula="f₀ = (1 / 2π) √(κ / I)", freq="f₀: the frequency, in full swings (there and back) per second",
            gloss="I: the balance's inertia     κ: the hairspring's stiffness",
            bill="about {:.0f}% of its energy lost each cycle (representative)",
            rate="rate: seconds a day gained or lost",
            boxes=("mainspring\ntorque", "energy to\nthe balance", "amplitude", "rate"),
            question="where does it settle?", answer="the escapement", slow="slowed 4×")
# =====================================================================


class Scene01(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.add(vignette())
        wait_until = clock(self)

        head = heading("WHERE WE LEFT OFF", "Films 4 and 5").to_corner(UL, buff=0.5)

        # Film 4: the balance, its frequency, its energy bill
        bal = BalanceModel(center=BAL_CENTER, radius=BAL_R)
        bal.rate.set_value(RATE)
        bal.vis.set_value(0.0)
        bal.attach(self)
        log = BeatLog(self, lambda: bal.model_t, F4.BEATS_PER_S)
        f4 = tag(TEXT["film4"], COOL, 0.22).next_to([BAL_CENTER[0], BAL_CENTER[1] + BAL_R, 0], UP, buff=0.35)
        slow = tag(TEXT["slow"], GLOW, 0.18).next_to([BAL_CENTER[0] + BAL_R, BAL_CENTER[1] + BAL_R, 0], RIGHT, buff=0.1)
        gloss = label(TEXT["gloss"], 0.2, GREY_B).next_to([BAL_CENTER[0], BAL_CENTER[1] - BAL_R, 0], DOWN, buff=0.25)
        formula = ftext(TEXT["formula"], 0.58).next_to(gloss, DOWN, buff=0.22)
        freq = label(TEXT["freq"], 0.2, GREY_B).next_to(formula, DOWN, buff=0.12)
        bill = label(TEXT["bill"].format(F4.LOSS_FRAC * 100), 0.24, WARM).next_to(freq, DOWN, buff=0.28)

        # Film 5: the chain
        boxes = VGroup()
        for x, t in zip(CHAIN_X, TEXT["boxes"]):
            lbl = label(t, 0.24, WHITE)
            b = RoundedRectangle(width=1.5, height=1.0, corner_radius=0.1).set_stroke(GREY_B, 1.4).set_fill(BG, 0.9)
            boxes.add(VGroup(b, lbl).move_to([x - 2.0, CHAIN_Y, 0]))
        boxes.shift(RIGHT * 1.0)
        arrows = VGroup(*[Arrow(boxes[i].get_right(), boxes[i + 1].get_left(), buff=0.06, stroke_width=3,
                                tip_length=0.14, color=GREY_B) for i in range(3)])
        f5 = tag(TEXT["film5"], WARM, 0.22).next_to(boxes, UP, buff=0.45).align_to(boxes, LEFT)
        amp_box = boxes[2][0]
        rate_def = label(TEXT["rate"], 0.2, GLOW).next_to(boxes[3], UP, buff=0.14)
        q = label(TEXT["question"], 0.28, GLOW, bold=True).next_to(boxes[2], DOWN, buff=0.45)
        qmark = label("?", 0.9, GLOW, bold=True).next_to(boxes[2], UP, buff=0.12)
        ans = VGroup(Arrow(q.get_bottom(), q.get_bottom() + DOWN * 0.9, buff=0.08, stroke_width=3, color=GLOW,
                           tip_length=0.16), label(TEXT["answer"], 0.36, GLOW, bold=True))
        ans[1].next_to(ans[0], DOWN, buff=0.1)

        cur = curtain()
        self.add(cur)

        # ---------------------------------------------------------- timeline
        self.play(cur.animate.set_fill(opacity=0), run_time=FADE_IN, rate_func=smooth)
        self.remove(cur)
        wait_until(FILM4_AT)
        self.play(FadeIn(head), bal.vis.animate.set_value(1.0), FadeIn(f4), FadeIn(slow), run_time=1.0)
        wait_until(GLOSS_AT)
        self.play(FadeIn(gloss), run_time=0.8)
        wait_until(FORMULA_AT)
        self.play(Write(formula), FadeIn(freq), run_time=1.5)
        wait_until(BILL_AT)
        self.play(FadeIn(bill, shift=UP * 0.1), run_time=0.9)
        wait_until(FILM5_AT)
        self.play(FadeIn(f5), LaggedStart(*[FadeIn(b) for b in boxes], lag_ratio=0.25), run_time=1.4)
        self.play(LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.3), run_time=1.2)
        wait_until(RATE_AT)
        self.play(boxes[3][0].animate.set_stroke(GLOW, 2.5), FadeIn(rate_def, shift=DOWN * 0.1), run_time=0.8)
        wait_until(QUESTION_AT)
        self.play(amp_box.animate.set_stroke(GLOW, 3), FadeIn(qmark, shift=DOWN * 0.1), FadeIn(q), run_time=0.9)
        wait_until(ANSWER_AT)
        self.play(GrowArrow(ans[0]), FadeIn(ans[1], shift=DOWN * 0.1), run_time=0.9)

        wait_until(FINAL_HOLD_UNTIL)
        cur.set_fill(opacity=0)
        self.add(cur)
        self.play(cur.animate.set_fill(opacity=1), run_time=FADE_OUT)
        log.write(__file__)
