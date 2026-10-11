"""Film 3, scene 06 - "Designing backward": starting from the balance (18,000
beats an hour) and the 15-tooth escape wheel, n = B / (120 Z) gives ten turns a
minute. The seconds hand fixes the fourth wheel at one turn a minute (10 : 1 to
the escape pinion); the minute hand fixes the center wheel at one turn an hour
(60 : 1 to the fourth). Sixty is split into two small-number stages, 8 x 7.5.
At 21,600 beats only the last stage changes: 12 : 1, a 120-tooth wheel driving 10.

Build (render + voice + mux):   python build.py 3/scene06_backward
Render only (quick preview):    PYTHONPATH=.:films/film03_gear_train manim -ql films/film03_gear_train/scene06_backward.py Scene06
Narration lines and their start times live in scene06_backward.voice.txt.

The chain of arbors is built right to left, the way the designer works; the
arrows point the way power flows. 120/10 at 21,600 beats is the 3 Hz 6497 train.
"""
from manim import *
from movement import vignette, teeth_g, disk_g, vm, BG, GLOW, FONT_SANS, FONT_SERIF, BRASS, BRASS_HI, STEEL, STEEL_HI

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds.
# Keep the timeline roughly in step with scene06_backward.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 1.0
BALANCE_AT, BEATS_AT = 1.6, 6.0        # the balance; its beat
ESCAPE_AT, TWO_BEATS_AT = 10.4, 12.8   # the escape wheel; two beats per tooth
FORMULA_AT, INSTANCE_AT = 16.6, 19.6   # n = B / (120 Z); = 10 turns a minute
FOURTH_AT, RATIO10_AT = 22.6, 26.6     # the seconds hand: once a minute; 10 : 1
CENTER_AT, RATIO60_AT = 29.8, 34.4     # the minute hand: once an hour; 60 : 1
TOO_MUCH_AT, SPLIT_AT = 37.6, 40.6     # sixty is too much for one mesh; split it
FACTOR_AT = 45.6                       # small-number fractions
BEAT_UP_AT, LAST_STAGE_AT = 55.4, 61.2 # 21,600 beats: 12 turns a minute; only the last stage changes
FINAL_HOLD_UNTIL = 68.0                # the last line ends about 66.5 s
FADE_OUT = 1.5

# --- the chain of arbors -----------------------------------------------------
NODE_Y, NODE_R = 1.75, 0.5
NODE_X = {"center": -5.2, "third": -2.6, "fourth": 0.0, "escape": 2.6, "balance": 5.2}
NODE_Z = {"center": 80, "third": 60, "fourth": 70, "escape": 15}
NEW = "#ff9a5c"                        # what changes at 21,600 beats
BAD = "#ff5a4a"

# --- text --------------------------------------------------------------
TITLE = "DESIGNING BACKWARD"
NAMES = {"center": "center wheel", "third": "third wheel", "fourth": "fourth wheel", "escape": "escape wheel",
         "balance": "balance"}
SPECS = {"balance": "18,000 beats / hour", "escape": "15 teeth", "fourth": "1 turn / minute",
         "center": "1 turn / hour"}
HANDS = {"fourth": "seconds hand", "center": "minute hand"}
TWO_BEATS = "2 beats per tooth"
ESC_SPEED = "10 turns / minute"
FORMULA = "n  =  B / (120 Z)"
LEGEND = "n  escape-wheel turns per minute      B  beats per hour      Z  escape teeth      120 = 2 × 60"
INSTANCE = "18,000 / (120 × 15)  =  10"
RATIO10, RATIO10_TEETH = "10 : 1", "70 / 7"
RATIO60 = "60 : 1"
SPLIT = ("8 : 1", "7.5 : 1")
SPLIT_TEETH = ("80 / 10", "60 / 8")
SPLIT_EQ = "60  =  8 × 7.5  =  (80/10) × (60/8)"
CONSTRAINTS = ("pinion:  enough leaves to run smoothly", "wheel:  small enough to fit the case",
               "so each stage is a small-number fraction")
NEW_BEATS, NEW_ESC, NEW_INSTANCE = "21,600 beats / hour", "12 turns / minute", "21,600 / (120 × 15)  =  12"
NEW_RATIO, NEW_TEETH = "12 : 1", "120 / 10"
UNCHANGED = "unchanged"
# =====================================================================


def label(s, scale=0.28, color=GREY_B, bold=False):
    return Text(s, font=FONT_SANS, weight=BOLD if bold else NORMAL, color=color).scale(scale)


def ftext(s, scale=0.5, color=WHITE):
    return Text(s, font=FONT_SERIF, slant=ITALIC, color=color).scale(scale)


def node_icon(k):
    c = np.array([NODE_X[k], NODE_Y, 0])
    if k == "balance":
        rim = Circle(radius=NODE_R * 0.85).set_stroke(BRASS_HI, 5)
        arms = VGroup(*[Line(ORIGIN, NODE_R * 0.85 * np.array([np.cos(a), np.sin(a), 0])).set_stroke(BRASS, 3)
                        for a in (PI / 2, PI / 2 + TAU / 3, PI / 2 + 2 * TAU / 3)])
        return VGroup(rim, arms, Dot(radius=0.05, color=STEEL_HI)).move_to(c)
    z = NODE_Z[k]
    m = 2 * NODE_R * 0.86 / z
    steel = k == "escape"
    g = teeth_g(NODE_R * 0.86, z, m=m).difference(disk_g(NODE_R * 0.12))
    return vm(g, STEEL if steel else BRASS, 1, STEEL_HI if steel else BRASS_HI, 0.6).move_to(c)


class Scene06(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.add(vignette())

        def wait_until(when):
            d = when - self.renderer.time
            if d > 1e-3:
                self.wait(d)

        title = label(TITLE, 0.36, GLOW, True).to_corner(UL, buff=0.45)
        icons = {k: node_icon(k) for k in NODE_X}
        names = {k: label(NAMES[k], 0.27, WHITE).next_to(icons[k], DOWN, buff=0.18) for k in NODE_X}
        specs = {k: label(SPECS[k], 0.26, GLOW).next_to(names[k], DOWN, buff=0.1) for k in SPECS}
        hands = {k: label(HANDS[k], 0.24).next_to(specs[k], DOWN, buff=0.08) for k in HANDS}
        two_beats = label(TWO_BEATS, 0.24).next_to(specs["escape"], DOWN, buff=0.08)
        esc_speed = label(ESC_SPEED, 0.26, GLOW).next_to(two_beats, DOWN, buff=0.08)

        def arrow(a, b):
            return Arrow([NODE_X[a] + NODE_R + 0.1, NODE_Y, 0], [NODE_X[b] - NODE_R - 0.1, NODE_Y, 0], buff=0,
                         stroke_width=3, tip_length=0.16, color=GREY_B)

        def ratio_label(text, teeth, a, b, color=WHITE):
            x = (NODE_X[a] + NODE_X[b]) / 2
            return VGroup(label(text, 0.32, color, True).move_to([x, NODE_Y + 0.42, 0]),
                          label(teeth, 0.24).move_to([x, NODE_Y - 0.28, 0]) if teeth else VGroup())

        a_fe, a_cf = arrow("fourth", "escape"), arrow("center", "fourth")
        a_ct, a_tf = arrow("center", "third"), arrow("third", "fourth")
        r10 = ratio_label(RATIO10, RATIO10_TEETH, "fourth", "escape")
        r60 = ratio_label(RATIO60, "", "center", "fourth")
        r60[0].move_to([NODE_X["third"], NODE_Y + 0.42, 0])
        rs1 = ratio_label(SPLIT[0], SPLIT_TEETH[0], "center", "third")
        rs2 = ratio_label(SPLIT[1], SPLIT_TEETH[1], "third", "fourth")
        strike = Line(r60[0].get_corner(DL) + LEFT * 0.1, r60[0].get_corner(UR) + RIGHT * 0.1).set_stroke(BAD, 5)

        formula = ftext(FORMULA, 0.7).move_to([-2.4, -0.95, 0])
        legend = label(LEGEND, 0.22).move_to([0, -1.55, 0])
        instance = ftext(INSTANCE, 0.55, GLOW).next_to(formula, RIGHT, buff=0.8)
        split_eq = ftext(SPLIT_EQ, 0.55, WHITE).move_to([0, -2.35, 0])
        constraints = VGroup(*[label(c, 0.27, WHITE if i < 2 else GLOW) for i, c in enumerate(CONSTRAINTS)])
        constraints.arrange(DOWN, aligned_edge=LEFT, buff=0.14).move_to([0, -3.25, 0])

        new_beats = label(NEW_BEATS, 0.26, NEW).move_to(specs["balance"])
        new_esc = label(NEW_ESC, 0.26, NEW).move_to(esc_speed)
        new_instance = ftext(NEW_INSTANCE, 0.55, NEW).move_to(instance, aligned_edge=LEFT)
        new_r = ratio_label(NEW_RATIO, NEW_TEETH, "fourth", "escape", NEW)
        unchanged = label(UNCHANGED, 0.26).move_to([NODE_X["third"], NODE_Y + 0.85, 0])

        curtain = FullScreenRectangle().set_fill(BG, 1).set_stroke(width=0)
        self.add(curtain)

        def node(k):
            return [FadeIn(icons[k], scale=0.8), FadeIn(names[k], shift=UP * 0.1)]

        # ---------------------------------------------------------- timeline
        self.add(title)
        self.bring_to_front(curtain)
        self.play(curtain.animate.set_fill(opacity=0), run_time=FADE_IN, rate_func=smooth)
        self.remove(curtain)
        wait_until(BALANCE_AT)                             # start from the balance
        self.play(*node("balance"), run_time=0.8)
        wait_until(BEATS_AT)
        self.play(FadeIn(specs["balance"], shift=UP * 0.1), run_time=0.6)

        wait_until(ESCAPE_AT)                              # the escape wheel: 15 teeth, 2 beats each
        self.play(*node("escape"), FadeIn(specs["escape"], shift=UP * 0.1), run_time=0.8)
        wait_until(TWO_BEATS_AT)
        self.play(FadeIn(two_beats, shift=UP * 0.1), run_time=0.6)
        wait_until(FORMULA_AT)                             # n = B / (120 Z)
        self.play(Write(formula), FadeIn(legend), run_time=1.4)
        wait_until(INSTANCE_AT)
        self.play(FadeIn(instance, shift=LEFT * 0.1), FadeIn(esc_speed, shift=UP * 0.1), run_time=0.8)

        wait_until(FOURTH_AT)                              # the seconds hand: the fourth wheel
        self.play(*node("fourth"), FadeIn(specs["fourth"]), FadeIn(hands["fourth"]), run_time=0.8)
        wait_until(RATIO10_AT)
        self.play(GrowArrow(a_fe), FadeIn(r10), run_time=0.8)

        wait_until(CENTER_AT)                              # the minute hand: the center wheel
        self.play(*node("center"), FadeIn(specs["center"]), FadeIn(hands["center"]), run_time=0.8)
        wait_until(RATIO60_AT)
        self.play(GrowArrow(a_cf), FadeIn(r60), run_time=0.8)

        wait_until(TOO_MUCH_AT)                            # too much for one mesh
        self.play(Create(strike), run_time=0.6)
        wait_until(SPLIT_AT)                               # split into two stages
        self.play(FadeOut(VGroup(strike, r60, a_cf)), run_time=0.5)
        self.play(*node("third"), GrowArrow(a_ct), GrowArrow(a_tf), FadeIn(rs1), FadeIn(rs2), run_time=1.0)
        self.play(FadeIn(split_eq, shift=UP * 0.1), run_time=0.8)

        wait_until(FACTOR_AT)                              # small-number fractions
        self.play(LaggedStart(*[FadeIn(c, shift=RIGHT * 0.15) for c in constraints], lag_ratio=0.6, run_time=3.2))

        wait_until(BEAT_UP_AT)                             # 21,600 beats: the escape wheel at 12
        self.play(FadeOut(constraints), Transform(specs["balance"], new_beats), run_time=0.8)
        self.play(Transform(instance, new_instance), Transform(esc_speed, new_esc), run_time=0.8)
        wait_until(LAST_STAGE_AT)                          # only the last stage changes
        self.play(Transform(r10, new_r), Indicate(a_fe, color=NEW), FadeIn(unchanged), run_time=1.0)

        wait_until(FINAL_HOLD_UNTIL)
        curtain.set_fill(opacity=0)
        self.add(curtain)
        self.play(curtain.animate.set_fill(opacity=1), run_time=FADE_OUT)
