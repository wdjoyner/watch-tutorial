"""Film 5, scene 04 - "Where it really comes from": the cubic term is a stand-in;
the hairspring metal is not measurably nonlinear at these strains. Three cards
show the real sources of amplitude dependence: escapement error (unlocking
just before center makes the watch lose, more at low amplitude), the
hairspring's off-center breathing about its pinning points, and, in the
vertical positions, the balance's residual unbalance in gravity. All three
feed one effective beta.

Build (render + voice + mux):   python build.py 5/scene04_real_sources
Render only (quick preview):    PYTHONPATH=.:films/film05_isochronism manim -ql films/film05_isochronism/scene04_real_sources.py Scene04
Narration lines and their start times live in scene04_real_sources.voice.txt.
The little pictures are schematic and slowed; the steady tick track plays.
"""
from manim import *
import iso  # noqa: F401  (first: puts Film 4's helpers on the path)
from iso import FlatSpring
from movement import vignette, BG, GLOW, GILT, BRASS_HI, STEEL, STEEL_HI
from ui import ftext, label, heading, tag, curtain, clock, WARM, COOL

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds.
# Keep the timeline roughly in step with scene04_real_sources.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 1.0
HEAD_AT = 1.2
STANDIN_AT = 2.2                      # "the cubic term is a stand-in"
METAL_AT = 5.4                        # "the hairspring's metal isn't measurably nonlinear"
THREE_AT = 9.6                        # "three sources"
CARD_AT = (14.1, 22.5, 27.7)          # escapement, breathing, gravity
LOSE_AT = 17.6                        # "which makes the watch lose, more so as the amplitude falls"
BETA_AT = 34.2                        # "Beta is an effective number that lumps all three together"
FINAL_HOLD_UNTIL = 39.8               # the last line ends about 38.3 s
FADE_OUT = 1.5

# --- cards ----------------------------------------------------------------
CARD_X, CARD_Y, CARD_W, CARD_H = (-4.45, 0.0, 4.45), 0.35, 4.1, 3.5
SWING_HZ = 0.35                       # slowed swing of the little pictures, cycles per second
CG_MAG = 14.0                         # magnification of the spring's center-of-gravity offset (tagged)
# =====================================================================


def card(x, title, color):
    box = RoundedRectangle(width=CARD_W, height=CARD_H, corner_radius=0.15).set_stroke(color, 1.6, 0.8).set_fill(opacity=0)
    box.move_to([x, CARD_Y, 0])
    t = label(title, 0.27, color, bold=True).next_to(box.get_top(), DOWN, buff=0.18)
    return VGroup(box, t)


class Scene04(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.add(vignette())
        wait_until = clock(self)
        clk = ValueTracker(0.0)
        clk.add_updater(lambda m, dt: m.increment_value(dt))
        swing = lambda: np.sin(TAU * SWING_HZ * clk.get_value())

        # the formula, with its cubic term marked as a stand-in
        eq = ftext("τ  ≈  −κ φ  −  β φ³", 0.62).move_to([0, 2.95, 0])
        box = SurroundingRectangle(eq[6:], buff=0.08).set_stroke(WARM, 2)
        standin = label("a stand-in", 0.26, WARM).next_to(box, RIGHT, buff=0.18)
        metal = label("the metal is linear at these strains", 0.24, GREY_B).next_to(eq, DOWN, buff=0.12)

        # 1. escapement error: the swing as an arc, the unlocking window just before center
        c1 = card(CARD_X[0], "escapement error", WARM)
        o1 = np.array([CARD_X[0], CARD_Y - 0.75, 0])
        R1 = 1.35
        arc = Arc(radius=R1, start_angle=PI * 0.12, angle=PI * 0.76, arc_center=o1).set_stroke(GREY_B, 2)
        center_tick = Line(o1 + UP * (R1 - 0.12), o1 + UP * (R1 + 0.12)).set_stroke(WHITE, 2)
        center_lbl = label("center", 0.2).next_to(center_tick, UP, buff=0.04)
        v1, v2, v3 = ValueTracker(0.0), ValueTracker(0.0), ValueTracker(0.0)
        moving_right = lambda: np.cos(TAU * SWING_HZ * clk.get_value()) > 0
        windows = VGroup(*[AnnularSector(inner_radius=R1 - 0.13, outer_radius=R1 + 0.13, angle=0.32, start_angle=a,
                                         arc_center=o1).set_stroke(width=0).set_fill(WARM, 0.8)
                           for a in (PI / 2 + 0.02, PI / 2 - 0.34)])
        windows.add_updater(lambda m: [m[0].set_fill(opacity=0.85 * v1.get_value() * moving_right()),
                                       m[1].set_fill(opacity=0.85 * v1.get_value() * (not moving_right()))])
        win_lbl = label("unlocking: just before center", 0.2, WARM).next_to(center_lbl, UP, buff=0.06)
        bob = Dot(radius=0.08, color=WHITE)
        bob.add_updater(lambda m: m.move_to(o1 + R1 * np.array([np.cos(PI / 2 - 0.38 * PI * swing()),
                                                                np.sin(PI / 2 - 0.38 * PI * swing()), 0]))
                        .set_opacity(v1.get_value()))
        lose = label("the watch loses,\nmore at low amplitude", 0.22, WARM).move_to(o1 + DOWN * 0.15)
        pic1 = VGroup(arc, center_tick, center_lbl, win_lbl)

        # 2. the hairspring breathes off-center about its pinning points
        c2 = card(CARD_X[1], "off-center breathing", COOL)
        sp = FlatSpring(center=(CARD_X[1], CARD_Y - 0.35), r_in=0.12, r_out=1.05, turns=7, stud_deg=-50)
        sp.add_updater(lambda m: m.draw(1.1 * swing()).set_stroke(opacity=v2.get_value()))
        stud = Square(0.14).set_fill(STEEL, 1).set_stroke(STEEL_HI, 1).move_to(sp.stud_pt())
        collet = Dot(sp.c, radius=0.07, color=STEEL)
        axis_mark = VGroup(Line(sp.c + LEFT * 0.16, sp.c + RIGHT * 0.16), Line(sp.c + DOWN * 0.16, sp.c + UP * 0.16))
        axis_mark.set_stroke(WHITE, 1.2)
        cg = Dot(radius=0.07, color=WARM)
        cg.add_updater(lambda m: m.move_to(sp.c + CG_MAG * (sp.cg(1.1 * swing()) - sp.c)).set_opacity(v2.get_value()))
        pins_lbl = label("stud", 0.2, STEEL_HI).next_to(stud, RIGHT, buff=0.08)
        cg_lbl = tag(f"center of gravity (dot), offset ×{CG_MAG:.0f}", WARM, 0.2).move_to([CARD_X[1], CARD_Y - CARD_H / 2 + 0.25, 0])
        pic2 = VGroup(stud, collet, axis_mark, pins_lbl)

        # 3. vertical position: a heavy spot on the rim, in gravity
        c3 = card(CARD_X[2], "unbalance in gravity", GLOW)
        o3 = np.array([CARD_X[2] - 0.35, CARD_Y - 0.4, 0])
        R3 = 0.95
        wheel = VGroup(Annulus(inner_radius=R3 * 0.84, outer_radius=R3, color=GILT).set_fill(GILT, 1).set_stroke(BRASS_HI, 1),
                       *[Line(o3 * 0, R3 * 0.86 * np.array([np.cos(a), np.sin(a), 0])).set_stroke(GILT, 4)
                         for a in (0.35, 0.35 + TAU / 3, 0.35 + 2 * TAU / 3)],
                       Dot(radius=0.07, color=STEEL_HI),
                       Dot(R3 * 0.92 * np.array([np.cos(-0.5), np.sin(-0.5), 0]), radius=0.1, color=WARM)).move_to(o3)
        wheel.shift(o3 - wheel[-2].get_center())
        wheel._a = 0.0

        def turn_wheel(m):
            a = 1.6 * swing()
            m.rotate(a - m._a, about_point=o3)
            m._a = a
            m.set_opacity(v3.get_value())
        wheel.add_updater(turn_wheel)
        g_arrow = Arrow(o3 + RIGHT * 1.45 + UP * 0.5, o3 + RIGHT * 1.45 + DOWN * 0.6, buff=0, stroke_width=4,
                        tip_length=0.18, color=GREY_B)
        g_lbl = label("g", 0.3).next_to(g_arrow, RIGHT, buff=0.08)
        heavy = label("heavy\nspot", 0.2, WARM).move_to(o3 + RIGHT * 1.5 + DOWN * 1.0)
        vert = label("dial vertical", 0.2).move_to([CARD_X[2], CARD_Y - CARD_H / 2 + 0.25, 0])
        pic3 = VGroup(g_arrow, g_lbl, heavy, vert)

        # all three -> one effective beta
        beta = VGroup(ftext("β", 0.8, GLOW), label("(effective)", 0.26, GLOW)).arrange(RIGHT, buff=0.15).move_to([0, -2.95, 0])
        feeds = VGroup(*[Arrow([x, CARD_Y - CARD_H / 2, 0], beta.get_top() + RIGHT * 0.25 * np.sign(x), buff=0.1,
                               stroke_width=3, tip_length=0.16, color=GREY_B) for x in CARD_X])
        slow = tag("schematic, slowed").to_corner(UR, buff=0.5)

        head = heading("WHERE IT REALLY COMES FROM", "three sources, one β").to_corner(UL, buff=0.5)
        cur = curtain()
        self.add(clk, v1, v2, v3, windows, bob, sp, cg, wheel, cur)

        # ---------------------------------------------------------- timeline
        self.play(cur.animate.set_fill(opacity=0), run_time=FADE_IN, rate_func=smooth)
        self.remove(cur)
        wait_until(HEAD_AT)
        self.play(FadeIn(head), FadeIn(eq), run_time=0.7)
        wait_until(STANDIN_AT)
        self.play(Create(box), FadeIn(standin), run_time=0.8)
        wait_until(METAL_AT)
        self.play(FadeIn(metal), run_time=0.7)
        wait_until(THREE_AT)                                # three empty cards
        self.play(*[FadeIn(c[0]) for c in (c1, c2, c3)], FadeIn(slow), run_time=0.8)
        wait_until(CARD_AT[0])                              # escapement error
        self.play(FadeIn(c1[1]), FadeIn(pic1), v1.animate.set_value(1.0), run_time=0.8)
        wait_until(LOSE_AT)
        self.play(FadeIn(lose), run_time=0.7)
        wait_until(CARD_AT[1])                              # off-center breathing
        self.play(FadeIn(c2[1]), FadeIn(pic2), FadeIn(cg_lbl), v2.animate.set_value(1.0), run_time=0.8)
        wait_until(CARD_AT[2])                              # gravity
        self.play(FadeIn(c3[1]), FadeIn(pic3), v3.animate.set_value(1.0), run_time=0.8)
        wait_until(BETA_AT)                                 # one effective beta
        self.play(*[GrowArrow(a) for a in feeds], run_time=0.8)
        self.play(FadeIn(beta, scale=1.1), run_time=0.7)

        wait_until(FINAL_HOLD_UNTIL)
        cur.set_fill(opacity=0)
        self.add(cur)
        self.play(cur.animate.set_fill(opacity=1), run_time=FADE_OUT)
