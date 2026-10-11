"""Film 4, scene 09 - "Beating temperature" (advanced): a cut bimetallic balance
(brass outside, steel inside, each half-rim fixed at one end) curls inward as it
warms, lowering I to offset the weakening spring. A schematic plot of rate
against temperature: a plain steel spring falls steeply; a compensated balance is
right at two temperatures and gains between them (the middle temperature
error); an Elinvar spring stays nearly flat. Then Guillaume's Nobel Prize (1920),
and the alloys and silicon springs that followed.

Build (render + voice + mux):   python build.py 4/scene09_compensation
Render only (quick preview):    PYTHONPATH=.:films/film04_regulating_organ manim -ql films/film04_regulating_organ/scene09_compensation.py Scene09
Narration lines and their start times live in scene09_compensation.voice.txt.
The plot is qualitative (tagged "schematic"): it carries no numbers.
"""
from manim import *
from movement import vignette, BG, GLOW, BRASS, STEEL, STEEL_HI, GILT
from ui import ftext, label, heading, tag, curtain, clock, WARM, COOL

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds.
# Keep the timeline roughly in step with scene09_compensation.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 1.0
HEAD_AT = 1.2
BALANCE_AT = 3.0                      # "cut bimetallic balances"
WARM_AT, WARM_DURATION = 5.8, 2.6     # "whose rims curl inward as they warm"
PLOT_AT = 10.2                        # "But they were exact at only two temperatures"
TWO_AT = 11.6                         # the two exact temperatures
HUMP_AT = 13.6                        # "In between they gained: the middle temperature error"
COOL_AT = 15.6                        # the balance cools back
NOBEL_AT = 18.6                       # "In nineteen twenty, Guillaume won the Nobel Prize"
ELINVAR_AT = 22.8                     # "alloys like Elinvar, whose stiffness hardly changes"
MODERN_AT = 27.4                      # "Nivarox and silicon springs carry the idea on"
FINAL_HOLD_UNTIL = 32.8               # the last line ends about 30.9 s
FADE_OUT = 1.5

# --- the cut balance ----------------------------------------------------
BAL_AT, BAL_R = (-4.0, -0.3), 1.9
CURL = 0.42                           # how far the free ends move in when warm (exaggerated)

# --- the plot -----------------------------------------------------------
PLOT_O, PLOT_W, PLOT_H = (0.6, -0.4), 5.6, 3.2     # origin (lower left of the axes), width, height
T_EXACT = (0.22, 0.78)                # the two temperatures where the compensated balance is right
# =====================================================================


class Scene09(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.add(vignette())
        wait_until = clock(self)
        c = np.array([*BAL_AT, 0.0])
        warm = ValueTracker(0.0)

        # cut bimetallic balance: a crossbar, two half-rims each fixed at one end, with timing screws
        def half_rim(a0, sign):
            def build():
                w = warm.get_value()
                s = np.linspace(0, 1, 60)
                ang = a0 + sign * s * np.radians(160)
                r = BAL_R - CURL * w * s ** 2
                outer = VMobject().set_points_smoothly([c + (r[i] + 0.07) * np.array([np.cos(a), np.sin(a), 0]) for i, a in enumerate(ang)])
                inner = VMobject().set_points_smoothly([c + (r[i] - 0.05) * np.array([np.cos(a), np.sin(a), 0]) for i, a in enumerate(ang)])
                screws = VGroup(*[Dot(c + (r[i] + 0.2) * np.array([np.cos(ang[i]), np.sin(ang[i]), 0]), radius=0.06, color=GILT)
                                  for i in range(8, 60, 9)])
                return VGroup(outer.set_stroke(BRASS, 9), inner.set_stroke(STEEL_HI, 6), screws)
            return always_redraw(build)
        bar = Line(c + LEFT * BAL_R, c + RIGHT * BAL_R).set_stroke(STEEL, 9)
        hub = Dot(c, radius=0.12, color=STEEL_HI)
        rims = VGroup(half_rim(0.0, +1), half_rim(PI, +1))
        cut = VGroup(bar, rims, hub)
        cut_lab = VGroup(label("cut bimetallic balance", 0.28, WHITE),
                         label("brass outside, steel inside", 0.24)).arrange(DOWN, buff=0.08).next_to(c + DOWN * BAL_R, DOWN, buff=0.4)
        curl_lab = label("warmer: the free ends curl in, I falls", 0.26, WARM).next_to(cut_lab, DOWN, buff=0.18)

        # thermometer
        bulb = Circle(radius=0.2).set_fill(WARM, 1).set_stroke(WHITE, 1)
        tube = RoundedRectangle(width=0.18, height=1.4, corner_radius=0.09).set_stroke(WHITE, 1).set_fill(BG, 1)
        tube.next_to(bulb, UP, buff=-0.08)
        fill = always_redraw(lambda: Rectangle(width=0.09, height=1.2 * (0.2 + 0.7 * warm.get_value()))
                             .set_fill(WARM, 1).set_stroke(width=0)
                             .move_to(tube.get_bottom() + UP * (0.07 + 0.6 * (0.2 + 0.7 * warm.get_value()))))
        thermo = VGroup(tube, fill, bulb).move_to(c + np.array([-BAL_R - 0.55, BAL_R * 0.55, 0]))

        # schematic plot: rate against temperature
        o = np.array([*PLOT_O, 0.0])

        def P(x, y):                                       # x, y in 0..1 of the plot box; y = 0.5 is "right on time"
            return o + np.array([x * PLOT_W, y * PLOT_H, 0])
        axes = VGroup(Line(P(0, 0), P(1.03, 0)).set_stroke(GREY_B, 1.5), Line(P(0, 0), P(0, 1.03)).set_stroke(GREY_B, 1.5),
                      DashedLine(P(0, 0.5), P(1, 0.5), dash_length=0.08).set_stroke(GREY_B, 1, 0.6))
        axes.add(label("temperature", 0.24).next_to(P(1, 0), DOWN, buff=0.12).align_to(P(1, 0), RIGHT),
                 label("rate", 0.24).rotate(PI / 2).next_to(P(0, 0.75), LEFT, buff=0.1),
                 label("gains", 0.2).next_to(P(0, 0.88), RIGHT, buff=0.08),
                 label("loses", 0.2).next_to(P(0, 0.1), RIGHT, buff=0.08),
                 label("on time", 0.2).next_to(P(1, 0.5), RIGHT, buff=0.08))
        schem = tag("schematic", scale=0.2).next_to(P(1, 1.03), UP, buff=0.05).align_to(P(1, 0), RIGHT)

        def curve(fn, color, w=4):
            xs = np.linspace(0, 1, 80)
            return VMobject().set_points_smoothly([P(x, fn(x)) for x in xs]).set_stroke(color, w)
        steel = curve(lambda x: 0.95 - 0.85 * x, GREY_B, 3)
        steel_lab = label("plain steel", 0.22, GREY_B).next_to(P(0.86, 0.95 - 0.85 * 0.86), RIGHT, buff=0.1)
        a, b = T_EXACT
        comp = curve(lambda x: 0.5 + 2.2 * (x - a) * (b - x), WARM)
        comp_lab = label("bimetallic balance", 0.22, WARM).next_to(P(0.5, 0.5 + 2.2 * 0.28 * 0.28), UP, buff=0.12)
        marks = VGroup(*[VGroup(Dot(P(t, 0.5), radius=0.07, color=GLOW),
                                DashedLine(P(t, 0), P(t, 0.5), dash_length=0.06).set_stroke(GLOW, 1, 0.6)) for t in T_EXACT])
        hump = label("middle temperature error", 0.24, GLOW).next_to(P(0.5, 0.5 + 2.2 * 0.28 * 0.28), UP, buff=0.42)
        elinvar = curve(lambda x: 0.5 + 0.03 * (x - 0.5), COOL)
        el_lab = label("Elinvar spring", 0.22, COOL).next_to(P(1, 0.515), UP, buff=0.08).align_to(P(1, 0), RIGHT)

        card = VGroup(label("Charles-Édouard Guillaume", 0.32, WHITE),
                      label("Nobel Prize in Physics, 1920", 0.27, GLOW),
                      label("nickel steels: Invar, and Elinvar, “élasticité invariable”", 0.24)).arrange(DOWN, buff=0.1)
        card.move_to([3.4, -2.35, 0])
        modern = label("today:  Nivarox alloys,  silicon springs with an oxide layer", 0.26, COOL).next_to(card, DOWN, buff=0.22)

        head = heading("BEATING TEMPERATURE", "compensation").to_corner(UL, buff=0.5)
        cur = curtain()
        self.add(cur)

        # ---------------------------------------------------------- timeline
        self.play(cur.animate.set_fill(opacity=0), run_time=FADE_IN, rate_func=smooth)
        self.remove(cur)
        wait_until(HEAD_AT)
        self.play(FadeIn(head), run_time=0.8)
        wait_until(BALANCE_AT)                              # the cut balance
        self.play(FadeIn(cut), FadeIn(cut_lab), FadeIn(thermo), run_time=1.0)
        wait_until(WARM_AT)                                 # warm: the ends curl in
        self.play(warm.animate.set_value(1.0), FadeIn(curl_lab), run_time=WARM_DURATION)

        wait_until(PLOT_AT)                                 # rate against temperature
        self.play(FadeIn(axes), FadeIn(schem), Create(steel), FadeIn(steel_lab), run_time=1.0)
        wait_until(TWO_AT)                                  # right at two temperatures
        self.play(Create(comp), FadeIn(comp_lab), run_time=1.2)
        self.play(*[GrowFromCenter(mk) for mk in marks], run_time=0.6)
        wait_until(HUMP_AT)                                 # gains in between
        self.play(FadeIn(hump, shift=UP * 0.1), run_time=0.8)
        wait_until(COOL_AT)
        self.play(warm.animate.set_value(0.0), FadeOut(curl_lab), run_time=1.6)

        wait_until(NOBEL_AT)                                # Guillaume
        self.play(FadeIn(card, shift=UP * 0.1), run_time=1.0)
        wait_until(ELINVAR_AT)                              # Elinvar: nearly flat
        self.play(Create(elinvar), FadeIn(el_lab), run_time=1.2)
        wait_until(MODERN_AT)
        self.play(FadeIn(modern, shift=UP * 0.1), run_time=0.8)

        wait_until(FINAL_HOLD_UNTIL)
        cur.set_fill(opacity=0)
        self.add(cur)
        self.play(cur.animate.set_fill(opacity=1), run_time=FADE_OUT)
