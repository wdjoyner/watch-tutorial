"""Film 5, scene 05 - "The chain of error": four linked panels driven by one
tracker, the state of wind. The mainspring's torque falls over the power
reserve (Film 2), so less energy reaches the balance to pay its bill (Film 4),
the amplitude falls, and the rate slides along the parabola. Where the
amplitude settles is the escapement's story (a later film). Isochronism
adjustment: make df/dTheta small where the watch actually runs (schematic).

Build (render + voice + mux):   python build.py 5/scene05_chain
Render only (quick preview):    PYTHONPATH=.:films/film05_isochronism manim -ql films/film05_isochronism/scene05_chain.py Scene05
Narration lines and their start times live in scene05_chain.voice.txt. Numbers from figures.py.
The panels are qualitative (beta exaggerated, torque curve schematic) and tagged so.
The scene writes scene05_chain.ticks.txt on every render.
"""
from manim import *
import iso  # noqa: F401  (first: puts Film 4's helpers on the path)
import figures as F
from iso import IsoBalance, Plot, DEG
from movement import vignette, BG, GLOW
from balance import BeatLog
from ui import ftext, label, heading, tag, curtain, clock, WARM, COOL

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds.
# Keep the timeline roughly in step with scene05_chain.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 1.0
HEAD_AT = 1.2                         # "you get a chain"
PANEL_AT = (4.3, 11.0, 14.6, 16.2)    # torque, energy, amplitude, rate
RUN_AT, RUN_END = 6.0, 24.0           # the state of wind runs down between these times
FULLHALF_AT = 18.4                    # "keeps different time fully wound and half wound"
ESC_AT = 24.5                         # "Just where the amplitude settles is the escapement's story"
ADJUST_AT = 30.6                      # "Isochronism adjustment is the art..."
FLAT_AT = 34.4                        # "...as flat as possible where the watch actually runs"
FINAL_HOLD_UNTIL = 40.0               # the last line ends about 38.4 s
FADE_OUT = 1.5

# --- panels --------------------------------------------------------------
PANEL_X, PANEL_Y, PANEL_W, PANEL_H = (-5.15, -1.72, 1.72, 5.15), 1.05, 3.0, 2.5
WIND_END = 0.0                        # state of wind at RUN_END (1 = fully wound)
AMP_HI, AMP_LO = 270.0, 220.0         # REPRESENTATIVE amplitude at full wind and at WIND_END
AMP_DRAWN = 1.2                       # drawn swing at 270 degrees
RATE = 0.25                           # slow motion
OP_DEG = 245.0                        # the operating amplitude for the adjusted curve (schematic)
# =====================================================================


def panel(x, title, color=GREY_B):
    box = RoundedRectangle(width=PANEL_W, height=PANEL_H, corner_radius=0.12).set_stroke(color, 1.4, 0.8).set_fill(opacity=0)
    box.move_to([x, PANEL_Y, 0])
    return VGroup(box, label(title, 0.24, color, bold=True).next_to(box.get_top(), DOWN, buff=0.14))


class Scene05(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.add(vignette())
        wait_until = clock(self)
        wind = ValueTracker(1.0)
        amp_deg = lambda: AMP_LO + (AMP_HI - AMP_LO) * wind.get_value()
        torque = lambda w: 0.42 + 0.5 * w + 0.08 * w ** 3      # schematic falling torque, 1 at full wind

        # 1. mainspring torque against time (Film 2)
        p1 = panel(PANEL_X[0], "mainspring torque", WARM)
        q1 = Plot((PANEL_X[0] - 1.2, PANEL_Y - 0.95), 2.4, 1.45, (0, 1), (0, 1.05))
        c1 = q1.curve(lambda u: torque(1 - u), color=WARM, width=3)
        d1 = Dot(radius=0.07, color=WHITE).add_updater(lambda m: m.move_to(q1.c2p(1 - wind.get_value(), torque(wind.get_value()))))
        t1 = label("time →", 0.18).next_to(q1.x_axis, DOWN, buff=0.06).align_to(q1.x_axis, RIGHT)
        f2 = tag("Film 2", WARM, 0.18).next_to(p1[0], DOWN, buff=0.1)

        # 2. energy reaching the balance each swing (Film 4's bill)
        p2 = panel(PANEL_X[1], "energy to the balance", GLOW)
        base = np.array([PANEL_X[1] - 0.25, PANEL_Y - 0.95, 0])
        bar = Rectangle(width=0.5, height=1.4).set_stroke(width=0).set_fill(GLOW, 0.85)
        bar.add_updater(lambda m: m.stretch_to_fit_height(1.45 * torque(wind.get_value())).move_to(base, aligned_edge=DOWN))
        frame2 = Rectangle(width=0.5, height=1.45).set_stroke(GREY_B, 1).move_to(base, aligned_edge=DOWN)
        f4 = tag("Film 4: the energy bill", GLOW, 0.18).next_to(p2[0], DOWN, buff=0.1)

        # 3. the amplitude (a slowed balance)
        p3 = panel(PANEL_X[2], "amplitude", COOL)
        bal = IsoBalance(center=(PANEL_X[2], PANEL_Y - 0.25), radius=0.82, amp=AMP_DRAWN, amp_full=AMP_DRAWN,
                         beta=F.BETA_SHOWN)
        bal.rate.set_value(RATE)
        bal.vis.set_value(0.0)
        bal.attach(self)
        driver = Mobject().add_updater(lambda m: bal.amp.set_value(AMP_DRAWN * amp_deg() / 270))
        log = BeatLog(self, lambda: bal.beats(), 1)
        amp_txt = label("270°  →  220°", 0.2, COOL).next_to(p3[0], DOWN, buff=0.1)

        # 4. the rate, riding the parabola (beta exaggerated)
        p4 = panel(PANEL_X[3], "rate", GLOW)
        b = F.BETA_SHOWN
        rate = lambda d: 3 * b * (d * DEG) ** 2 / 8
        q4 = Plot((PANEL_X[3] - 1.2, PANEL_Y - 0.95), 2.4, 1.45, (150, 300), (rate(150), rate(300)))
        c4 = q4.curve(rate, 150, 300, color=GLOW, width=3)
        d4 = Dot(radius=0.07, color=WHITE).add_updater(lambda m: m.move_to(q4.c2p(amp_deg(), rate(amp_deg()))))
        t4 = label("amplitude →", 0.18).next_to(q4.x_axis, DOWN, buff=0.06).align_to(q4.x_axis, RIGHT)
        ex4 = tag("β exaggerated", GLOW, 0.18).next_to(p4[0], DOWN, buff=0.1)

        arrows = VGroup(*[Arrow([PANEL_X[i] + PANEL_W / 2, PANEL_Y, 0], [PANEL_X[i + 1] - PANEL_W / 2, PANEL_Y, 0],
                                buff=0.04, stroke_width=3, tip_length=0.14, color=GREY_B) for i in range(3)])
        esc_box = DashedVMobject(RoundedRectangle(width=1.3, height=0.9, corner_radius=0.1), num_dashes=24)
        esc_box.set_stroke(GREY_A, 1.6).move_to(arrows[1].get_center())
        esc_lbl = label("where it settles:\nthe escapement, a later film", 0.2, GREY_A).move_to([arrows[1].get_center()[0], -0.9, 0])

        fullhalf = VGroup(label("fully wound: runs fast", 0.28, WARM), label("→", 0.3),
                          label("half wound: slower", 0.28, COOL)).arrange(RIGHT, buff=0.3).move_to([0, -1.55, 0])

        # bottom: isochronism adjustment (schematic): flatten the curve where the watch runs
        qb = Plot((-3.2, -3.3), 6.4, 1.6, (150, 320), (-0.004, rate(320)))
        raw = qb.curve(rate, 150, 320, color=GREY_B, width=2.5)
        adj = qb.curve(lambda d: rate(OP_DEG) + 0.32 * 3 * b * ((d - OP_DEG) * DEG) ** 2 / 8, 150, 320, color=GLOW, width=3.5)
        band = Rectangle(width=qb.c2p(AMP_HI, 0)[0] - qb.c2p(AMP_LO, 0)[0], height=1.6).set_stroke(width=0).set_fill(COOL, 0.15)
        band.move_to([(qb.c2p(AMP_HI, 0)[0] + qb.c2p(AMP_LO, 0)[0]) / 2, -3.3 + 0.8, 0])
        run_lbl = label("where the watch runs", 0.2, COOL).next_to(band, UP, buff=0.05)
        tangent = Line(qb.c2p(OP_DEG - 40, rate(OP_DEG)), qb.c2p(OP_DEG + 40, rate(OP_DEG))).set_stroke(WHITE, 2)
        small = ftext("df / dΘ  ≈  0  here", 0.42, GLOW).next_to(qb.c2p(320, rate(320)), RIGHT, buff=0.3)
        keys = VGroup(label("as it comes", 0.2, GREY_B), label("adjusted", 0.2, GLOW)).arrange(DOWN, buff=0.08, aligned_edge=LEFT)
        keys.next_to(qb.y_axis, LEFT, buff=0.2).shift(UP * 0.4)
        sch = tag("schematic", GLOW, 0.18).next_to(keys, DOWN, buff=0.15)
        bottom = VGroup(qb, qb.xlabel("amplitude", 0.2), qb.ylabel("rate", 0.2), raw, band, run_lbl, keys, sch)

        head = heading("THE CHAIN OF ERROR", "from mainspring to rate").to_corner(UL, buff=0.5)
        cur = curtain()
        t_run = lambda: np.clip((self.renderer.time - RUN_AT) / (RUN_END - RUN_AT), 0, 1)
        wind.add_updater(lambda m: m.set_value(1 - (1 - WIND_END) * t_run()))
        self.add(wind, driver, cur)

        # ---------------------------------------------------------- timeline
        self.play(cur.animate.set_fill(opacity=0), run_time=FADE_IN, rate_func=smooth)
        self.remove(cur)
        wait_until(HEAD_AT)
        self.play(FadeIn(head), *[FadeIn(p[0]) for p in (p1, p2, p3, p4)], run_time=0.8)
        wait_until(PANEL_AT[0])                             # torque falls (Film 2)
        self.play(FadeIn(p1[1]), FadeIn(q1), Create(c1), FadeIn(t1), FadeIn(f2), run_time=1.0)
        self.add(d1)
        wait_until(RUN_AT)                                  # the state of wind runs down
        wait_until(PANEL_AT[1])                             # less energy to the balance (Film 4)
        self.play(FadeIn(p2[1]), FadeIn(frame2), FadeIn(bar), FadeIn(f4), GrowArrow(arrows[0]), run_time=0.8)
        wait_until(PANEL_AT[2])                             # the amplitude falls
        self.play(FadeIn(p3[1]), bal.vis.animate.set_value(1.0), FadeIn(amp_txt), GrowArrow(arrows[1]), run_time=0.8)
        wait_until(PANEL_AT[3])                             # the rate shifts
        self.play(FadeIn(p4[1]), FadeIn(q4), Create(c4), FadeIn(t4), FadeIn(ex4), GrowArrow(arrows[2]), run_time=1.0)
        self.add(d4)

        wait_until(FULLHALF_AT)
        self.play(FadeIn(fullhalf, shift=UP * 0.1), run_time=0.8)
        wait_until(ESC_AT)                                  # the escapement's story
        self.play(Create(esc_box), FadeIn(esc_lbl), run_time=0.9)
        wait_until(ADJUST_AT)                               # adjustment
        self.play(FadeOut(fullhalf), FadeIn(bottom), run_time=0.9)
        self.play(Create(adj), run_time=1.2)
        wait_until(FLAT_AT)
        self.play(Create(tangent), FadeIn(small), run_time=0.9)

        wait_until(FINAL_HOLD_UNTIL)
        cur.set_fill(opacity=0)
        self.add(cur)
        self.play(cur.animate.set_fill(opacity=1), run_time=FADE_OUT)
        log.write(__file__)
