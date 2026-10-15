"""Film 6, scene 05 - "Airy's theorem": the free balance goes round a circle in
the phase plane (angle across, speed / omega0 up). A kick is a jump straight up.
At the center (phi* = 0) that jump is radial: the circle grows, but the kicked
balance stays level with an unkicked "ghost" (same phase, same tick times).
Away from center the jump has a tangential part: the kicked balance falls
behind its ghost, and every later tick moves with it. Then the formula,
Delta T = (J/I) phi* / (A^2 omega0^2), proportional to J phi*. Kicks are drawn
large (exaggerated) so the effect can be seen.

Build (render + voice + mux):   python build.py 6/scene05_airy
Render only (quick preview):    PYTHONPATH=.:films/film06_escapement manim -ql films/film06_escapement/scene05_airy.py Scene05
Narration lines and their start times live in scene05_airy.voice.txt.
"""
from manim import *
import prev  # noqa: F401  (first: Film 4 and 5 helpers on the path)
import ui6  # noqa: F401  (extra subscripts)
from movement import vignette, BG, GLOW
from ui import ftext, label, heading, tag, curtain, clock, WARM, COOL

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds.
# Keep the timeline roughly in step with scene05_airy.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 1.0
AIRY_AT = 1.2                         # "In eighteen twenty-six, the astronomer George Airy ..."
PLANE_AT = 8.4                        # "Draw the swing in the phase plane ..."
CENTER_START, CENTER_KICK = 15.8, 18.6   # demo 1: start, and the kick at the top of the circle
OFF_START, OFF_KICK = 26.1, 28.4      # demo 2: start, and the kick away from center
FORMULA_AT = 35.0                     # "The shift is proportional to the kick ..."
RULE_AT = 40.8                        # "So deliver the impulse at the center."
FINAL_HOLD_UNTIL = 49.0               # the last line ends about 47.2 s
FADE_OUT = 1.5

# --- the phase plane -------------------------------------------------
O = np.array([-2.2, -0.45, 0.0])      # origin of the phase plane on screen
R0 = 1.9                              # free orbit radius
KICK = 0.75                           # EXAGGERATED jump (screen units)
W = 1.1                               # orbit angular speed, rad per video second (slow, for the eye)
OFF_DEG = 50.0                        # where the off-center kick lands, degrees from the top
TEXT = dict(airy="George Biddell Airy, 1826", phi="angle φ", vel="speed φ′ / ω₀", free="free swing: a circle",
            ghost="dashed: the same balance, unkicked", kick="kick", radial="radial: the amplitude grows",
            on_time="still on schedule", tang="tangential part: the phase shifts", late="falls behind",
            exag="kicks drawn much larger than real", formula="ΔT = (J / I) · φ* / (A² ω₀²)",
            prop="∝  J · φ*", rule="Airy's rule: impulse at the center")
# =====================================================================


def pt(r, th):
    """theta measured clockwise from the top: phi = r sin(theta), speed = r cos(theta)."""
    return O + np.array([r * np.sin(th), r * np.cos(th), 0.0])


class Orbit:
    """A balance going round the phase plane, kicked once (straight up) at t_kick."""

    def __init__(self, scene, t0, th0, t_kick, kick):
        self.scene, self.t0, self.th0, self.tk, self.k = scene, t0, th0, t_kick, kick
        thk = th0 + W * (t_kick - t0)
        p = pt(R0, thk) - O
        q = p + np.array([0, kick, 0])
        self.r1, self.th1 = np.hypot(q[0], q[1]), np.arctan2(q[0], q[1])
        self.thk = thk

    def real(self):
        t = self.scene.renderer.time
        if t < self.tk:
            return pt(R0, self.th0 + W * (t - self.t0))
        return pt(self.r1, self.th1 + W * (t - self.tk))

    def ghost(self):
        t = self.scene.renderer.time
        return pt(R0, self.th0 + W * (t - self.t0))

    def kicked(self):
        return self.scene.renderer.time >= self.tk


class Scene05(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.add(vignette())
        wait_until = clock(self)
        head = heading("AIRY'S THEOREM", "where to kick").to_corner(UL, buff=0.5)
        airy = label(TEXT["airy"], 0.3, GLOW).next_to(head, DOWN, buff=0.35, aligned_edge=LEFT)

        ax = VGroup(Arrow(O + LEFT * 3.0, O + RIGHT * 3.0, buff=0, stroke_width=2, color=GREY_B, tip_length=0.14),
                    Arrow(O + DOWN * 3.0, O + UP * 3.3, buff=0, stroke_width=2, color=GREY_B, tip_length=0.14))
        ax_l = VGroup(label(TEXT["phi"], 0.24).next_to(ax[0].get_end(), DOWN, buff=0.1),
                      label(TEXT["vel"], 0.24).next_to(ax[1].get_end(), RIGHT, buff=0.1))
        circle = Circle(radius=R0, color=COOL, stroke_width=3).move_to(O)
        free = label(TEXT["free"], 0.24, COOL).next_to(circle, DOWN, buff=0.15).shift(RIGHT * 1.4)
        exag = tag(TEXT["exag"], GLOW, 0.18).to_corner(DR, buff=0.4)

        # side notes, right column
        col_x = 1.55
        notes = dict(ghost=label(TEXT["ghost"], 0.22, GREY_A), radial=label(TEXT["radial"], 0.26, GLOW),
                     on_time=label(TEXT["on_time"], 0.26, COOL, bold=True),
                     tang=label(TEXT["tang"], 0.26, WARM), late=label(TEXT["late"], 0.26, WARM, bold=True))
        notes["ghost"].move_to([col_x, 2.35, 0], aligned_edge=LEFT)
        notes["radial"].move_to([col_x, 1.6, 0], aligned_edge=LEFT)
        notes["on_time"].move_to([col_x, 1.1, 0], aligned_edge=LEFT)
        notes["tang"].move_to([col_x, 1.6, 0], aligned_edge=LEFT)
        notes["late"].move_to([col_x, 1.1, 0], aligned_edge=LEFT)
        formula = ftext(TEXT["formula"], 0.52).move_to([col_x, -0.4, 0], aligned_edge=LEFT)
        prop = ftext(TEXT["prop"], 0.56, GLOW).next_to(formula, DOWN, buff=0.3, aligned_edge=LEFT)
        rule = label(TEXT["rule"], 0.32, GLOW, bold=True)
        rule_box = VGroup(SurroundingRectangle(rule, buff=0.2, corner_radius=0.1).set_stroke(GLOW, 1.4), rule)
        rule_box.move_to([col_x, -2.4, 0], aligned_edge=LEFT)

        def demo(t0, t_kick, kick_th):
            """Objects for one demonstration: start so the kick lands at angle kick_th (from the top)."""
            ob = Orbit(self, t0, kick_th - W * (t_kick - t0), t_kick, KICK)
            dot = Dot(radius=0.11, color=WARM).add_updater(lambda m: m.move_to(ob.real()))
            ghost = DashedVMobject(Circle(radius=0.12, color=GREY_A, stroke_width=2), num_dashes=8)
            ghost.add_updater(lambda m: m.move_to(ob.ghost()))
            ray_g = DashedLine(O, O + UP, stroke_width=1.5, color=GREY_A)
            ray_g.add_updater(lambda m: m.put_start_and_end_on(O, O + 2.9 * (ob.ghost() - O) / max(np.linalg.norm(ob.ghost() - O), 1e-6)))
            ray_r = Line(O, O + UP, stroke_width=2.5, color=WARM)
            ray_r.add_updater(lambda m: m.put_start_and_end_on(O, O + 2.9 * (ob.real() - O) / max(np.linalg.norm(ob.real() - O), 1e-6)))
            big = Circle(radius=ob.r1, color=WARM, stroke_width=2).move_to(O).set_stroke(opacity=0.0)
            big.add_updater(lambda m: m.set_stroke(opacity=0.6 if ob.kicked() else 0.0))
            kp = pt(R0, ob.thk)
            arrow = Arrow(kp, kp + UP * KICK, buff=0, stroke_width=5, color=GLOW, tip_length=0.16)
            return ob, VGroup(big, ray_g, ray_r, ghost, dot), arrow, kp

        cur = curtain()
        self.add(cur)

        # ---------------------------------------------------------- timeline
        self.play(cur.animate.set_fill(opacity=0), run_time=FADE_IN, rate_func=smooth)
        self.remove(cur)
        wait_until(AIRY_AT)
        self.play(FadeIn(head), FadeIn(airy), run_time=0.9)
        wait_until(PLANE_AT)
        self.play(FadeIn(ax), FadeIn(ax_l), run_time=0.8)
        self.play(Create(circle), FadeIn(free), run_time=1.4)

        # demo 1: the kick at the center (top of the circle)
        wait_until(CENTER_START - 0.6)
        ob1, g1, a1, kp1 = demo(CENTER_START, CENTER_KICK, 0.0)
        self.play(FadeIn(g1), FadeIn(notes["ghost"]), FadeIn(exag), run_time=0.6)
        wait_until(CENTER_KICK)
        self.play(GrowArrow(a1), run_time=0.3)
        self.play(FadeIn(notes["radial"]), run_time=0.5)
        self.wait(1.2)
        self.play(FadeOut(a1), FadeIn(notes["on_time"]), run_time=0.6)
        wait_until(OFF_START - 0.7)
        self.play(FadeOut(g1), FadeOut(notes["radial"]), FadeOut(notes["on_time"]), run_time=0.6)

        # demo 2: the same kick, off center
        ob2, g2, a2, kp2 = demo(OFF_START, OFF_KICK, np.radians(OFF_DEG))
        self.play(FadeIn(g2), run_time=0.5)
        wait_until(OFF_KICK)
        u = (kp2 - O) / np.linalg.norm(kp2 - O)
        tng = np.array([u[1], -u[0], 0.0])
        comp_r = Arrow(kp2, kp2 + u * KICK * u[1], buff=0, stroke_width=3, color=GLOW, tip_length=0.12)
        comp_t = Arrow(kp2, kp2 + tng * KICK * tng[1], buff=0, stroke_width=3, color=WARM, tip_length=0.12)
        self.play(GrowArrow(a2), run_time=0.3)
        self.play(GrowArrow(comp_r), GrowArrow(comp_t), FadeIn(notes["tang"]), run_time=0.8)
        self.wait(1.4)
        self.play(FadeOut(a2), FadeOut(comp_r), FadeOut(comp_t), FadeIn(notes["late"]), run_time=0.6)

        wait_until(FORMULA_AT)
        self.play(Write(formula), run_time=1.4)
        self.play(FadeIn(prop, shift=UP * 0.1), run_time=0.6)
        wait_until(RULE_AT)
        self.play(FadeIn(rule_box, shift=UP * 0.1), run_time=0.8)

        wait_until(FINAL_HOLD_UNTIL)
        cur.set_fill(opacity=0)
        self.add(cur)
        self.play(cur.animate.set_fill(opacity=1), run_time=FADE_OUT)
