"""Film 4, scene 03 - "Newton meets Hooke": the balance is turned away from
rest and the hairspring pushes back, tau = -kappa phi (Hooke); Newton's law for
turning, tau = I phi''; together I phi'' + kappa phi = 0. Released, it swings like
a mass on a spring (shown beside it, in step). Slowed down, two bars show the
energy moving between the coiled spring and the moving rim, the total constant.

Build (render + voice + mux):   python build.py 4/scene03_newton_hooke
Render only (quick preview):    PYTHONPATH=.:films/film04_regulating_organ manim -ql films/film04_regulating_organ/scene03_newton_hooke.py Scene03
Narration lines and their start times live in scene03_newton_hooke.voice.txt.
The scene writes scene03_newton_hooke.ticks.txt (the balance's beats) on every render.
"""
from manim import *
from movement import vignette, BG, GLOW, STEEL, STEEL_HI
from balance import BalanceModel, BeatLog
from ui import ftext, label, tag, heading, curtain, clock, faded, WARM, COOL

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds, angles in radians.
# Keep the timeline roughly in step with scene03_newton_hooke.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 1.0
TURN_AT, TURN_DURATION = 2.0, 2.2     # "turn the balance away from rest"
ARROW_AT = 5.2                        # "pushes back with a torque"
HOOKE_AT = 7.0                        # "minus kappa phi. That's Hooke's law."
NEWTON_AT = 11.6                      # "torque equals I times the angular acceleration"
TOGETHER_AT = 17.6                    # "Together: ... equals zero"
RELEASE_AT = 25.0                     # "It's the equation of a mass on a spring"
SPRING_AT = 26.0                      # the mass on a spring appears
SLOW_AT, SLOW_DURATION = 32.3, 1.4    # "Slowed down"
BARS_AT = 34.0                        # "watch the energy change hands"
FINAL_HOLD_UNTIL = 43.2               # the last line ends about 41.5 s
FADE_OUT = 1.5

# --- balance -----------------------------------------------------------
BAL_AT, BAL_R = (-3.8, -0.4), 2.3
TURN = 0.9                            # how far it is turned by hand
SLOW = 0.1                            # clock rate in slow motion

# --- layout (right half) ------------------------------------------------
HOOKE_POS, NEWTON_POS = (2.0, 2.75), (5.2, 2.75)
EQ_POS = (3.4, 1.35)
SPRING_Y = -0.2                       # the mass on a spring
BARS_X, BARS_Y0, BARS_H = (1.6, 3.4, 5.2), -3.3, 2.0
# =====================================================================


class Scene03(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.add(vignette())
        wait_until = clock(self)

        bal = BalanceModel(center=BAL_AT, radius=BAL_R, amp=TURN)
        bal.drive.set_value(0.0)                            # held by hand to begin with
        bal.attach(self)
        log = BeatLog(self, lambda: bal.model_t, 2 * bal.hz, active=lambda: bal.drive.get_value() > 0.5)
        c = np.array([*BAL_AT, 0.0])

        # angle arc and restoring-torque arrow, redrawn from the balance's angle
        rest = DashedLine(c, c + RIGHT * BAL_R * 1.1, dash_length=0.08).set_stroke(GREY_B, 1.5, 0.7)
        rest.rotate(PI / 2, about_point=c)                  # rest direction: straight up
        show_arc = ValueTracker(0.0)

        def arc_now():
            a = bal.angle()
            g = VGroup()
            if abs(a) > 0.02 and show_arc.get_value() > 0:
                arm = Line(c, c + BAL_R * 1.1 * np.array([np.cos(PI / 2 + a), np.sin(PI / 2 + a), 0]))
                arc = Arc(radius=BAL_R * 1.02, start_angle=PI / 2, angle=a, arc_center=c)
                phi = ftext("φ", 0.5, GLOW).move_to(c + BAL_R * 1.2 * np.array([np.cos(PI / 2 + a / 2), np.sin(PI / 2 + a / 2), 0]))
                g.add(arm.set_stroke(GLOW, 2, 0.8), arc.set_stroke(GLOW, 3), phi)
                faded(g, show_arc.get_value())
            return g
        arc = always_redraw(arc_now)
        show_torque = ValueTracker(0.0)

        def torque_now():
            a = bal.angle()
            if abs(a) < 0.05 or show_torque.get_value() <= 0:
                return VGroup()
            r = BAL_R * 0.72
            tip = Arc(radius=r, start_angle=PI / 2 + a, angle=-a * 0.75, arc_center=c).set_stroke(WARM, 6)
            tip.add_tip(tip_length=0.26, tip_width=0.26)
            t = label("torque", 0.26, WARM).move_to(c + (r - 0.42) * np.array([np.cos(PI / 2 + a * 0.6), np.sin(PI / 2 + a * 0.6), 0]))
            return faded(VGroup(tip, t), show_torque.get_value())
        torque = always_redraw(torque_now)

        hooke = VGroup(label("Hooke", 0.28, GLOW), ftext("τ  =  −κ φ", 0.62)).arrange(DOWN, buff=0.15).move_to([*HOOKE_POS, 0])
        newton = VGroup(label("Newton, for turning", 0.28, GLOW), ftext("τ  =  I φ″", 0.62)).arrange(DOWN, buff=0.15)
        newton.move_to([*NEWTON_POS, 0])
        acc = label("φ″  angular acceleration", 0.24).next_to(newton, DOWN, buff=0.12)
        eq = ftext("I φ″  +  κ φ  =  0", 0.9, WHITE).move_to([*EQ_POS, 0])
        eq_box = SurroundingRectangle(eq, buff=0.18, corner_radius=0.08).set_stroke(GLOW, 2)

        # a mass on a spring, in step with the balance
        x0, amp_x = 3.6, 0.7
        wall = Line([x0 - 2.6, SPRING_Y - 0.35, 0], [x0 - 2.6, SPRING_Y + 0.35, 0]).set_stroke(STEEL_HI, 4)
        vis_spring = ValueTracker(0.0)

        def mass_now():
            x = x0 + amp_x * bal.angle() / TURN
            n, L0 = 10, x - 0.3 - (x0 - 2.6)
            zig = [[x0 - 2.6 + L0 * i / (2 * n), SPRING_Y + (0.18 if i % 2 else -0.18) * (0 < i < 2 * n), 0] for i in range(2 * n + 1)]
            s = VMobject().set_points_as_corners(zig).set_stroke(STEEL_HI, 2)
            m = Square(0.6).set_fill(STEEL, 1).set_stroke(WHITE, 1).move_to([x, SPRING_Y, 0])
            tx = ftext("m", 0.4).move_to(m)
            return faded(VGroup(s, m, tx), vis_spring.get_value())
        mass = always_redraw(mass_now)
        mx = ftext("m x″  +  k x  =  0", 0.5, GREY_B).move_to([x0, SPRING_Y - 0.75, 0])

        # energy bars: in the spring (phi^2) and in the rim (phi'^2), total constant
        vis_bars = ValueTracker(0.0)

        def bars_now():
            v = vis_bars.get_value()
            if v <= 0:
                return VGroup()
            ps = np.sin(bal.phase()) ** 2
            parts = VGroup()
            for x, f, col, name in ((BARS_X[0], ps, COOL, "spring"), (BARS_X[1], 1 - ps, WARM, "rim"), (BARS_X[2], 1.0, GLOW, "total")):
                frame = Rectangle(width=0.7, height=BARS_H).move_to([x, BARS_Y0 + BARS_H / 2, 0]).set_stroke(GREY_B, 1)
                fill = Rectangle(width=0.7, height=max(1e-3, BARS_H * f)).move_to([x, BARS_Y0 + BARS_H * f / 2, 0])
                fill.set_fill(col, 0.9).set_stroke(width=0)
                parts.add(frame, fill, label(name, 0.26, WHITE).next_to(frame, DOWN, buff=0.12))
            return faded(parts, v)
        bars = always_redraw(bars_now)
        bars_head = label("energy", 0.28, GLOW).move_to([BARS_X[1], BARS_Y0 + BARS_H + 0.3, 0])
        slow_tag = tag("slowed 10×").to_corner(UL, buff=0.45)

        cur = curtain()
        self.add(rest, arc, torque, mass, bars, cur)
        self.add(show_arc, show_torque, vis_spring, vis_bars)

        # ---------------------------------------------------------- timeline
        self.play(cur.animate.set_fill(opacity=0), run_time=FADE_IN, rate_func=smooth)
        self.remove(cur)
        wait_until(TURN_AT)                                 # turned away from rest
        self.play(show_arc.animate.set_value(1.0), bal.manual.animate.set_value(TURN),
                  run_time=TURN_DURATION, rate_func=smooth)
        wait_until(ARROW_AT)                                # the spring pushes back
        self.play(show_torque.animate.set_value(1.0), run_time=0.8)
        wait_until(HOOKE_AT)
        self.play(FadeIn(hooke, shift=DOWN * 0.1), run_time=1.0)
        wait_until(NEWTON_AT)
        self.play(FadeIn(newton, shift=DOWN * 0.1), run_time=1.0)
        self.play(FadeIn(acc), run_time=0.6)
        wait_until(TOGETHER_AT)                             # together
        self.play(TransformFromCopy(VGroup(hooke[1], newton[1]), eq), run_time=1.6)
        self.play(Create(eq_box), run_time=0.8)

        wait_until(RELEASE_AT)                              # let go: it swings
        bal.model_t = 1 / (4 * bal.hz)                      # start the swing at its turning point, where it was let go
        self.play(bal.drive.animate.set_value(1.0), show_arc.animate.set_value(0.0),
                  show_torque.animate.set_value(0.0), run_time=0.3)
        wait_until(SPRING_AT)
        self.play(vis_spring.animate.set_value(1.0), FadeIn(wall), FadeIn(mx, shift=UP * 0.1), run_time=1.0)

        wait_until(SLOW_AT)                                 # slow motion
        self.play(bal.rate.animate.set_value(SLOW), FadeIn(slow_tag), run_time=SLOW_DURATION)
        wait_until(BARS_AT)                                 # the energy changes hands
        self.play(vis_spring.animate.set_value(0.0), FadeOut(wall), FadeOut(mx),
                  vis_bars.animate.set_value(1.0), FadeIn(bars_head), run_time=1.0)

        wait_until(FINAL_HOLD_UNTIL)
        cur.set_fill(opacity=0)
        self.add(cur)
        self.play(cur.animate.set_fill(opacity=1), run_time=FADE_OUT)
        log.write(__file__)
