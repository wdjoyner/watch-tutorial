"""Film 4, scene 11 - "Paying for the swing" (advanced): can the mainspring pay
the balance's losses? On a log scale of microwatts: Film 2's mainspring spread
over 46 hours gives 2.5 to 4.9 microwatts (the linear model and the design-practice
estimate); the lever escapement passes on about a third, 0.7 to 2.0; the balance
needs about 0.57 at a representative Q of 300. The same order, with every
figure uncertain by a factor of two. So the watchmaker measures the one number
that sums the budget up: the amplitude (a timing machine's readout).

Build (render + voice + mux):   python build.py 4/scene11_energy_bill
Render only (quick preview):    PYTHONPATH=.:films/film04_regulating_organ manim -ql films/film04_regulating_organ/scene11_energy_bill.py Scene11
Narration lines and their start times live in scene11_energy_bill.voice.txt.
Numbers from figures.py (the barrel: Film 2's spring, ETA's 46 h; the escapement's 30-40 % from the chapter).
"""
from manim import *
import figures as F
from movement import vignette, BG, GLOW, GILT
from ui import ftext, label, heading, tag, curtain, clock, WARM, COOL

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds.
# Keep the timeline roughly in step with scene11_energy_bill.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 1.0
HEAD_AT = 1.2
NEED_AT = 1.6                         # "The escapement has to pay that back": the balance's need
ASK_AT = 4.4                          # "Can the mainspring afford it?"
BARREL_AT = 8.0                       # "Spread over forty-six hours, it delivers a few microwatts"
ESC_AT = 12.6                         # "the escapement passes on about a third"
SAME_AT = 15.6                        # "the same order as the balance needs"
FACTOR_AT = 18.6                      # "every figure uncertain by a factor of two"
READOUT_AT = 26.0                     # "the one number that sums it up: the amplitude"
FINAL_HOLD_UNTIL = 32.4               # the last line ends about 30.4 s
FADE_OUT = 1.5

# --- the log axis, microwatts ------------------------------------------
AX_X0, AX_X1, AX_Y = -3.6, 5.8, -2.0
LOG_MIN, LOG_MAX = -1, 1              # 0.1 to 10 microwatts
ROW_Y = {"barrel": 1.3, "escape": 0.25, "need": -0.8}
# =====================================================================


def x_of(uw):
    return AX_X0 + (np.log10(uw) - LOG_MIN) / (LOG_MAX - LOG_MIN) * (AX_X1 - AX_X0)


class Scene11(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.add(vignette())
        wait_until = clock(self)

        head = heading("PAYING FOR THE SWING", "the energy budget").to_corner(UL, buff=0.5)

        axis = VGroup(Line([AX_X0, AX_Y, 0], [AX_X1, AX_Y, 0]).set_stroke(GREY_B, 2))
        for e in (-1, 0, 1):
            for k in range(1, 10):
                v = k * 10.0 ** e
                if LOG_MIN <= np.log10(v) <= LOG_MAX:
                    h = 0.14 if k == 1 else 0.06
                    axis.add(Line([x_of(v), AX_Y - h, 0], [x_of(v), AX_Y + h, 0]).set_stroke(GREY_B, 1.2))
            axis.add(label(f"{10.0 ** e:g}", 0.24).next_to([x_of(10.0 ** e), AX_Y - 0.14, 0], DOWN, buff=0.08))
        axis.add(label("microwatts  (log scale)", 0.24).next_to([(AX_X0 + AX_X1) / 2, AX_Y - 0.5, 0], DOWN, buff=0.05))

        def row(key, lo, hi, color, name, note):
            y = ROW_Y[key]
            if hi > lo:
                mark = RoundedRectangle(width=x_of(hi) - x_of(lo), height=0.34, corner_radius=0.08)
                mark.move_to([(x_of(lo) + x_of(hi)) / 2, y, 0]).set_fill(color, 0.85).set_stroke(width=0)
                vals = label(f"{lo:.1f} – {hi:.1f} μW", 0.24, color).next_to(mark, RIGHT, buff=0.15)
            else:
                mark = Dot([x_of(lo), y, 0], radius=0.13, color=color)
                vals = label(f"{lo:.2f} μW", 0.24, color).next_to(mark, RIGHT, buff=0.15)
            guide = DashedLine([x_of(lo), y, 0], [x_of(lo), AX_Y, 0], dash_length=0.06).set_stroke(color, 1, 0.5)
            names = VGroup(label(name, 0.27, WHITE), label(note, 0.21)).arrange(DOWN, aligned_edge=RIGHT, buff=0.05)
            names.move_to([AX_X0 - 0.25, y, 0], aligned_edge=RIGHT)
            return VGroup(names, guide, mark, vals)
        uw = 1e6
        barrel = row("barrel", F.P_BARREL[0] * uw, F.P_BARREL[1] * uw, GILT, "mainspring",
                     f"{F.U_LINEAR:.2f} – {F.U_DESIGN:.2f} J over {F.RESERVE_S / 3600:.0f} h")
        esc = row("escape", F.P_AT_BALANCE[0] * uw, F.P_AT_BALANCE[1] * uw, WARM, "after the escapement",
                  f"about a third ({F.ESC_EFF[0] * 100:.0f}–{F.ESC_EFF[1] * 100:.0f} %)")
        need = row("need", F.POWER_6497 * uw, F.POWER_6497 * uw, COOL, "the balance needs",
                   f"at Q = {F.Q:.0f} (representative)")
        same = SurroundingRectangle(VGroup(esc[2], esc[3], need[2], need[3]), buff=0.18, corner_radius=0.1).set_stroke(GLOW, 2)
        same_lab = label("the same order", 0.26, GLOW).next_to(same, UP, buff=0.08).align_to(same, RIGHT)
        factor = tag("every figure uncertain by about ×2", WARM).move_to([1.8, 2.3, 0])
        ask = label("can the mainspring afford it?", 0.3, WHITE).move_to([1.8, 2.3, 0])

        # a timing machine's amplitude readout (illustrative)
        panel = RoundedRectangle(width=5.4, height=4.5, corner_radius=0.15).set_fill(BG, 0.95).set_stroke(GREY_B, 1)
        panel.move_to([0.0, 0.0, 0])
        gauge_c = panel.get_center() + UP * 0.25
        dial = Arc(radius=1.5, start_angle=PI, angle=-PI, arc_center=gauge_c).set_stroke(GREY_B, 3)
        ticks = VGroup()
        for deg in range(0, 361, 45):
            a = PI - deg / 360 * PI
            p = gauge_c + 1.5 * np.array([np.cos(a), np.sin(a), 0])
            ticks.add(Line(p, p + 0.15 * (gauge_c - p) / 1.5).set_stroke(GREY_B, 2))
            if deg % 90 == 0:
                ticks.add(label(f"{deg}°", 0.22).move_to(gauge_c + 1.85 * np.array([np.cos(a), np.sin(a), 0])))
        a270 = PI - 270 / 360 * PI
        needle = Line(gauge_c, gauge_c + 1.35 * np.array([np.cos(a270), np.sin(a270), 0])).set_stroke(GLOW, 4)
        hubdot = Dot(gauge_c, radius=0.07, color=GLOW)
        read = VGroup(label("amplitude", 0.3, WHITE), ftext("≈ 270°", 0.6, GLOW)).arrange(RIGHT, buff=0.3)
        read.next_to(gauge_c, DOWN, buff=0.45)
        sub = label("the watchmaker's main diagnostic", 0.24).next_to(read, DOWN, buff=0.12)
        illus = tag("illustrative readout", scale=0.2).next_to(panel.get_corner(DR), UL, buff=0.15)
        readout = VGroup(panel, dial, ticks, needle, hubdot, read, sub, illus)

        cur = curtain()
        self.add(cur)

        # ---------------------------------------------------------- timeline
        self.play(cur.animate.set_fill(opacity=0), run_time=FADE_IN, rate_func=smooth)
        self.remove(cur)
        wait_until(HEAD_AT)
        self.play(FadeIn(head), FadeIn(axis), run_time=0.8)
        wait_until(NEED_AT)                                 # the bill
        self.play(FadeIn(need[0]), Create(need[1]), GrowFromCenter(need[2]), FadeIn(need[3]), run_time=1.0)
        wait_until(ASK_AT)
        self.play(FadeIn(ask, shift=UP * 0.1), run_time=0.7)
        wait_until(BARREL_AT)                               # what the mainspring supplies
        self.play(FadeOut(ask), FadeIn(barrel[0]), Create(barrel[1]), GrowFromEdge(barrel[2], LEFT), FadeIn(barrel[3]),
                  run_time=1.2)
        wait_until(ESC_AT)                                  # a third gets through the escapement
        self.play(FadeIn(esc[0]), Create(esc[1]), TransformFromCopy(barrel[2], esc[2]), FadeIn(esc[3]), run_time=1.2)
        wait_until(SAME_AT)                                 # the same order
        self.play(Create(same), FadeIn(same_lab), run_time=1.0)
        wait_until(FACTOR_AT)                               # every figure uncertain by x2
        self.play(FadeIn(factor, shift=UP * 0.1), run_time=0.8)

        wait_until(READOUT_AT)                              # amplitude sums it up
        self.play(FadeOut(VGroup(axis, barrel, esc, need, same, same_lab, factor)), run_time=0.6)
        self.play(FadeIn(readout, shift=UP * 0.15), run_time=0.9)

        wait_until(FINAL_HOLD_UNTIL)
        cur.set_fill(opacity=0)
        self.add(cur)
        self.play(cur.animate.set_fill(opacity=1), run_time=FADE_OUT)
