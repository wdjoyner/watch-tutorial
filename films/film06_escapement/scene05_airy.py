"""Film 6, scene 05 - "Airy's theorem", with every part of the picture named.
The phase plane: angle phi across, speed phi'/omega0 up (dividing by omega0 makes
both angles). A free balance, friction ignored, goes round a circle whose radius
is the amplitude Theta; it runs clockwise, one lap per full swing. The left and
right edges (+-Theta) are the ends of the swing, where the balance is still;
the top is the midpoint of the swing (phi = 0, the rest position), fastest.
A small balance wheel beside the plane swings in step with the dot.
A kick changes the speed, not the angle: the dot jumps straight up onto a
larger (orange) circle, the new amplitude. At the midpoint that jump is
radial: the circle grows, and the kicked balance stays level with its unkicked
twin (dashed), so the tick times do not move. Away from the midpoint the jump
has a part along the circle: the balance falls behind its twin. Then
Delta T = (J/I) phi_k / (Theta^2 omega0^2), with each symbol glossed, and Airy's rule.
Kicks are drawn far larger than real, and the laps are slowed (both tagged).

Build (render + voice + mux):   python build.py 6/scene05_airy
Render only (quick preview):    PYTHONPATH=.:films/film06_escapement manim -ql films/film06_escapement/scene05_airy.py Scene05
Narration lines and their start times live in scene05_airy.voice.txt.
"""
from manim import *
import prev  # noqa: F401  (first: Film 4 and 5 helpers on the path)
import ui6  # noqa: F401  (extra subscripts)
from ui6 import fmark
from balance import BalanceModel
from movement import vignette, BG, GLOW
from ui import ftext, label, heading, tag, curtain, clock, WARM, COOL

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds.
# Keep the timeline roughly in step with scene05_airy.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 1.0
AIRY_AT = 1.2                         # "In eighteen twenty-six, the astronomer George Airy ..."
PLANE_AT = 8.3                        # "Draw the swing in the phase plane: angle across, speed up ..."
DOT_AT = 12.0                         # "... with the speed divided by omega nought so that both are angles."
CIRCLE_AT = 16.6                      # "The free balance goes round a circle, and its radius is the amplitude, Theta."
ENDS_AT = 23.3                        # "At the left and right, the balance is at the ends of its swing, momentarily still."
TOP_AT = 28.2                         # "At the top, it passes the midpoint of the swing, its rest position, at full speed."
LAP_AT = 34.0                         # "One lap is one full swing, there and back."
JUMP_AT = 38.2                        # "A kick changes the speed but not the angle ..."
KICK1_AT = 41.6                       # "... so the point jumps straight up ..."  (demo 1: the kick at the midpoint)
NEW_AT = 43.9                         # "... onto a larger circle: the new amplitude."
TWIN_AT = 47.2                        # "At the midpoint, straight up points straight out from the circle ..."
ON_TIME_AT = 51.6                     # "The circle grows, but the balance stays on schedule with its unkicked twin."
OFF_START, OFF_KICK = 56.6, 58.9      # demo 2: "Away from the midpoint, part of the kick runs along the circle."
LATE_AT = 61.9                        # "That part shifts the phase, and every later tick moves with it."
FORMULA_AT = 66.3                     # "The shift is proportional to the kick J, and to phi sub k ..."
GLOSS_AT = 68.6                       # "... the angle where it lands. It shrinks as the amplitude, Theta, grows."
RULE_AT = 76.5                        # "So deliver the impulse at the midpoint of the swing."
FINAL_HOLD_UNTIL = 85.9               # the last line ends about 83.9 s
FADE_OUT = 1.5

# --- the phase plane -------------------------------------------------
O = np.array([-1.5, 0.15, 0.0])       # origin of the phase plane on screen (kept above the caption band)
R0 = 1.55                             # free orbit radius (stands for the amplitude Theta)
KICK = 0.6                            # EXAGGERATED jump (screen units)
W = 1.1                               # orbit angular speed, rad per video second (slowed, for the eye)
OFF_DEG = 50.0                        # where the off-midpoint kick lands, degrees round from the top
# --- the balance beside it ---------------------------------------------
BAL_C, BAL_R = (-5.55, -0.75), 0.72
AMP_SHOW = 270.0                      # degrees: the balance's swing when the dot is on the blue circle
TEXT = dict(airy="George Biddell Airy, 1826", phi="angle φ", vel="speed φ′ / ω₀",
            legend=("the dot: the balance's state (angle across, speed up)",
                    "blue circle: the free swing; its radius Θ is the amplitude",
                    "left and right (±Θ): the ends of the swing, momentarily still",
                    "top (φ = 0): the midpoint of the swing, the rest position; fastest",
                    "clockwise; one lap = one full swing, there and back",
                    "a kick: the speed jumps, the angle does not",
                    "orange circle: the swing after the kick, a new amplitude"),
            friction="friction ignored here: circles, not spirals",
            plus="+Θ", minus="−Θ", still="still", top="φ = 0: midpoint, fastest", radius="Θ",
            bal="the balance,\nin step with the dot", rest="rest position (φ = 0)",
            key=("blue: before the kick", "orange: after the kick", "dashed: the unkicked twin"),
            exag="kicks drawn much larger than real", slow="slowed: one lap here ≈ 6 s, really 0.4 s",
            radial="at the midpoint the jump is radial:\nthe circle grows", on_time="still on schedule with its twin",
            tang="away from the midpoint, part of the jump\nruns along the circle", late="it falls behind: the ticks move",
            formula="ΔT = (J / I) · φₖ / (Θ² ω₀²)", prop="∝  J · φₖ",
            gloss=("ΔT: the shift in the tick times", "J: the kick    φₖ: the angle where it lands",
                   "Θ: the amplitude    I, ω₀: from Film 4"),
            rule="Airy's rule: impulse at the midpoint of the swing")
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

        ax = VGroup(Arrow(O + LEFT * 2.6, O + RIGHT * 2.6, buff=0, stroke_width=2, color=GREY_B, tip_length=0.14),
                    Arrow(O + DOWN * 2.5, O + UP * 2.8, buff=0, stroke_width=2, color=GREY_B, tip_length=0.14))
        ax_l = VGroup(label(TEXT["phi"], 0.24).next_to(ax[0].get_end(), DOWN, buff=0.1),
                      label(TEXT["vel"], 0.24).next_to(ax[1].get_end(), RIGHT, buff=0.1))
        circle = Circle(radius=R0, color=COOL, stroke_width=3).move_to(O)
        rad_dir = np.array([np.cos(np.radians(215)), np.sin(np.radians(215)), 0])
        radius = VGroup(Line(O, O + R0 * rad_dir).set_stroke(COOL, 2),
                        fmark(TEXT["radius"], 0.4, COOL).move_to(O + 0.55 * R0 * rad_dir + 0.22 * np.array([rad_dir[1], -rad_dir[0], 0])))
        ends = VGroup(Dot(pt(R0, PI / 2), radius=0.06, color=GLOW), Dot(pt(R0, -PI / 2), radius=0.06, color=GLOW),
                      fmark(TEXT["plus"], 0.36, GLOW).next_to(pt(R0, PI / 2), UR, buff=0.06),
                      fmark(TEXT["minus"], 0.36, GLOW).next_to(pt(R0, -PI / 2), UL, buff=0.06),
                      label(TEXT["still"], 0.18, GREY_A).next_to(pt(R0, PI / 2), DR, buff=0.06),
                      label(TEXT["still"], 0.18, GREY_A).next_to(pt(R0, -PI / 2), DL, buff=0.06))
        top = VGroup(Dot(pt(R0, 0), radius=0.06, color=GLOW),
                     fmark(TEXT["top"], 0.32, GLOW).next_to(pt(R0, 0), UR, buff=0.08))
        exag = tag(TEXT["exag"], GLOW, 0.17).to_corner(UR, buff=0.4)
        slow = tag(TEXT["slow"], GLOW, 0.17).next_to(exag, DOWN, buff=0.1, aligned_edge=RIGHT)

        # the balance, in step with the dot
        bal = BalanceModel(center=BAL_C, radius=BAL_R, show_spring=True)
        bal.drive.set_value(0.0)
        bal.vis.set_value(0.0)
        bal.attach(self)
        bal_l = label(TEXT["bal"], 0.2, GREY_A).next_to([BAL_C[0], BAL_C[1] + BAL_R, 0], UP, buff=0.15)
        rest = VGroup(DashedLine([BAL_C[0], BAL_C[1] - BAL_R * 0.25, 0], [BAL_C[0], BAL_C[1] - BAL_R * 1.25, 0],
                                 stroke_width=1.4, color=GLOW),
                      label(TEXT["rest"], 0.18, GLOW).next_to([BAL_C[0], BAL_C[1] - BAL_R * 1.25, 0], DOWN, buff=0.06))
        state = {"fn": None}
        follow = Mobject().add_updater(
            lambda m: bal.manual.set_value(-np.radians(AMP_SHOW) * (state["fn"]() - O)[0] / R0) if state["fn"] else None)
        self.add(follow)

        # the legend, right column
        col_x = 1.55
        legend = VGroup(*[label(t, 0.2, GREY_A) for t in TEXT["legend"]]).arrange(DOWN, aligned_edge=LEFT, buff=0.16)
        for i, c in ((1, COOL), (6, WARM)):
            legend[i].set_color(c)
        legend.move_to([col_x, 1.7, 0], aligned_edge=UL)
        friction = label(TEXT["friction"], 0.18, GREY_B).next_to(legend, DOWN, buff=0.22, aligned_edge=LEFT)
        key = VGroup(*[label(t, 0.18, c) for t, c in zip(TEXT["key"], (COOL, WARM, GREY_A))]).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
        key.next_to(rest, DOWN, buff=0.2).align_to(rest[1], LEFT).shift(LEFT * 0.2)

        # demo notes, formula, rule (same column, after the legend leaves)
        notes = dict(radial=label(TEXT["radial"], 0.24, GLOW), on_time=label(TEXT["on_time"], 0.26, COOL, bold=True),
                     tang=label(TEXT["tang"], 0.24, WARM), late=label(TEXT["late"], 0.26, WARM, bold=True))
        for k, y in (("radial", 1.95), ("on_time", 1.2), ("tang", 1.95), ("late", 1.2)):
            notes[k].move_to([col_x, y, 0], aligned_edge=LEFT)
        formula = ftext(TEXT["formula"], 0.52).move_to([col_x, 0.35, 0], aligned_edge=LEFT)
        prop = ftext(TEXT["prop"], 0.56, GLOW).next_to(formula, DOWN, buff=0.25, aligned_edge=LEFT)
        gloss = VGroup(*[label(g, 0.2, GREY_A) for g in TEXT["gloss"]]).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
        gloss.next_to(prop, DOWN, buff=0.22, aligned_edge=LEFT)
        rule = label(TEXT["rule"], 0.27, GLOW, bold=True)
        rule_box = VGroup(SurroundingRectangle(rule, buff=0.18, corner_radius=0.1).set_stroke(GLOW, 1.4), rule)
        rule_box.next_to(gloss, DOWN, buff=0.28, aligned_edge=LEFT)

        def demo(t0, t_kick, kick_th):
            """Objects for one demonstration: start so the kick lands at angle kick_th (from the top)."""
            ob = Orbit(self, t0, kick_th - W * (t_kick - t0), t_kick, KICK)
            dot = Dot(radius=0.11, color=WARM).add_updater(lambda m: m.move_to(ob.real()))
            ghost = DashedVMobject(Circle(radius=0.12, color=GREY_A, stroke_width=2), num_dashes=8)
            ghost.add_updater(lambda m: m.move_to(ob.ghost()))
            ray_g = DashedLine(O, O + UP, stroke_width=1.5, color=GREY_A)
            ray_g.add_updater(lambda m: m.put_start_and_end_on(O, O + 2.45 * (ob.ghost() - O) / max(np.linalg.norm(ob.ghost() - O), 1e-6)))
            ray_r = Line(O, O + UP, stroke_width=2.5, color=WARM)
            ray_r.add_updater(lambda m: m.put_start_and_end_on(O, O + 2.45 * (ob.real() - O) / max(np.linalg.norm(ob.real() - O), 1e-6)))
            big = Circle(radius=ob.r1, color=WARM, stroke_width=2.5).move_to(O).set_stroke(opacity=0.0)
            big.add_updater(lambda m: m.set_stroke(opacity=0.75 if ob.kicked() else 0.0))
            kp = pt(R0, ob.thk)
            arrow = Arrow(kp, kp + UP * KICK, buff=0, stroke_width=5, color=GLOW, tip_length=0.16)
            return ob, dot, VGroup(ghost, ray_g), ray_r, big, arrow, kp

        cur = curtain()
        self.add(cur)

        # ---------------------------------------------------------- timeline
        self.play(cur.animate.set_fill(opacity=0), run_time=FADE_IN, rate_func=smooth)
        self.remove(cur)
        wait_until(AIRY_AT)
        self.play(FadeIn(head), FadeIn(airy), run_time=0.9)
        wait_until(PLANE_AT)
        self.play(FadeIn(ax), FadeIn(ax_l), run_time=0.8)

        # demo 1 runs from here: the dot rides the blue circle and is kicked at the top at KICK1_AT
        ob1, dot1, twin1, ray1, big1, arr1, kp1 = demo(DOT_AT, KICK1_AT, 0.0)
        state["fn"] = ob1.real
        wait_until(DOT_AT)
        self.play(FadeIn(dot1), FadeIn(legend[0]), bal.vis.animate.set_value(1.0), FadeIn(bal_l), FadeIn(slow),
                  run_time=0.8)
        wait_until(CIRCLE_AT)
        self.play(Create(circle), FadeIn(radius), FadeIn(legend[1]), FadeIn(friction), run_time=1.2)
        wait_until(ENDS_AT)
        self.play(FadeIn(ends), FadeIn(legend[2]), run_time=0.8)
        wait_until(TOP_AT)
        self.play(FadeIn(top), FadeIn(legend[3]), FadeIn(rest), run_time=0.8)
        wait_until(LAP_AT)
        self.play(FadeIn(legend[4]), run_time=0.6)
        wait_until(JUMP_AT)
        self.play(FadeIn(legend[5]), FadeIn(exag), run_time=0.6)
        wait_until(KICK1_AT)
        self.add(big1, ray1)
        self.play(GrowArrow(arr1), run_time=0.3)
        wait_until(NEW_AT)
        self.play(FadeIn(legend[6]), FadeOut(arr1), run_time=0.6)

        wait_until(TWIN_AT - 0.8)
        self.play(FadeOut(legend), FadeOut(friction), FadeIn(key), run_time=0.8)
        self.play(FadeIn(twin1), FadeIn(notes["radial"]), run_time=0.7)
        wait_until(ON_TIME_AT)
        self.play(FadeIn(notes["on_time"]), run_time=0.6)

        # demo 2: the same kick, away from the midpoint
        wait_until(OFF_START - 0.7)
        self.play(FadeOut(VGroup(dot1, twin1, ray1, big1)), FadeOut(notes["radial"]), FadeOut(notes["on_time"]),
                  run_time=0.6)
        big1.clear_updaters()
        ob2, dot2, twin2, ray2, big2, arr2, kp2 = demo(OFF_START, OFF_KICK, np.radians(OFF_DEG))
        state["fn"] = ob2.real
        self.add(big2)
        self.play(FadeIn(dot2), FadeIn(twin2), FadeIn(ray2), run_time=0.5)
        wait_until(OFF_KICK)
        u = (kp2 - O) / np.linalg.norm(kp2 - O)
        tng = np.array([u[1], -u[0], 0.0])
        comp_r = Arrow(kp2, kp2 + u * KICK * u[1], buff=0, stroke_width=3, color=GLOW, tip_length=0.12)
        comp_t = Arrow(kp2, kp2 + tng * KICK * tng[1], buff=0, stroke_width=3, color=WARM, tip_length=0.12)
        self.play(GrowArrow(arr2), run_time=0.3)
        self.play(GrowArrow(comp_r), GrowArrow(comp_t), FadeIn(notes["tang"]), run_time=0.8)
        wait_until(LATE_AT)
        self.play(FadeOut(arr2), FadeOut(comp_r), FadeOut(comp_t), FadeIn(notes["late"]), run_time=0.6)

        wait_until(FORMULA_AT)
        self.play(Write(formula), run_time=1.4)
        self.play(FadeIn(prop, shift=UP * 0.1), run_time=0.6)
        wait_until(GLOSS_AT)
        self.play(FadeIn(gloss), run_time=0.8)
        wait_until(RULE_AT)
        self.play(FadeIn(rule_box, shift=UP * 0.1), run_time=0.8)

        wait_until(FINAL_HOLD_UNTIL)
        cur.set_fill(opacity=0)
        self.add(cur)
        self.play(cur.animate.set_fill(opacity=1), run_time=FADE_OUT)
