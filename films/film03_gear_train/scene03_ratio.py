"""Film 3, scene 03 - "The ratio law": a 40-tooth wheel drives a 10-tooth pinion.
Counters under each gear show the same number of teeth passing the contact
point on both, so turns times teeth match: n1 z1 = n2 z2. One turn of the wheel
gives four of the pinion. Arrows show each mesh reversing the direction; a
third gear turns the same way as the first, like the center and fourth wheels
(minute and seconds hands both clockwise).

Build (render + voice + mux):   python build.py 3/scene03_ratio
Render only (quick preview):    PYTHONPATH=.:films/film03_gear_train manim -ql films/film03_gear_train/scene03_ratio.py Scene03
Narration lines and their start times live in scene03_ratio.voice.txt.
"""
from manim import *
from movement import vignette, BG, GLOW, FONT_SANS, FONT_SERIF
from train import GearSet

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds.
# Keep the timeline roughly in step with scene03_ratio.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 1.0
SPIN_AT = 1.0                          # the pair starts turning
CONTACT_AT = 3.2                       # "the contact point"
COUNTERS_AT = 6.6                      # "the same number of teeth go by on each gear"
FORMULA_AT, LEGEND_AT = 12.4, 16.6     # n1 z1 = n2 z2, then what n and z mean
STOP_AT = 19.6                         # the pair stops, the counters reset
ONE_TURN_AT, ONE_TURN_DURATION = 20.6, 4.4     # the wheel turns once; the pinion four times
INSTANCE_AT = 24.4                     # 1 x 40 = 4 x 10
ARROWS_AT = 26.4                       # "each mesh also reverses direction"
THIRD_AT = 29.2                        # "add a third gear"
ROLES_AT = {"center": 34.0, "fourth": 35.8}
CLOCKWISE_AT = 39.0                    # "both run clockwise"
FINAL_HOLD_UNTIL = 44.2                # the last line ends about 42.7 s
FADE_OUT = 1.5

# --- gears -------------------------------------------------------------
MOD = 0.09                             # one module for all three, so they mesh
Z = {"wheel": 40, "pinion": 10, "third": 30}
WHEEL_AT = (-2.7, -0.5)
SPEED = -0.26                          # radians per second for the wheel (negative = clockwise)

# --- text --------------------------------------------------------------
BLOCK_AT = (3.7, 0.2, 0)                 # the formula's place beside the pair; it moves up for the third gear
FORMULA = "n₁ z₁  =  n₂ z₂"
LEGEND = "n  turns per minute        z  number of teeth"
INSTANCE = "1 × 40  =  4 × 10"
ROLES = {"wheel": ("like the center wheel", "minute hand  ↻"), "third": ("like the fourth wheel", "seconds hand  ↻")}
COUNT_TEXT = ("teeth passed", "turns")
# =====================================================================


def ftext(s, scale=0.5, color=WHITE):
    return Text(s, font=FONT_SERIF, slant=ITALIC, color=color).scale(scale)


def label(s, scale=0.28, color=GREY_B, bold=False):
    return Text(s, font=FONT_SANS, weight=BOLD if bold else NORMAL, color=color).scale(scale)


def turn_arrow(center, r, clockwise, start_deg=70, sweep=70, color=GLOW):
    a = -sweep if clockwise else sweep
    arc = Arc(radius=r, start_angle=np.radians(start_deg), angle=np.radians(a), arc_center=center)
    return arc.set_stroke(color, 4).add_tip(tip_length=0.2, tip_width=0.2)


class Scene03(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.add(vignette())

        def wait_until(when):
            d = when - self.renderer.time
            if d > 1e-3:
                self.wait(d)

        gs = GearSet()
        wheel = gs.gear("wheel", Z["wheel"], MOD, center=WHEEL_AT, spokes=4)
        pinion = gs.gear("pinion", Z["pinion"], MOD, driven_by="wheel", angle=0, kind="pinion")
        third = gs.gear("third", Z["third"], MOD, driven_by="pinion", angle=0, spokes=4)
        gs.hide("third")
        gs.attach(self)

        contact = Circle(radius=0.22).move_to(wheel.pivot + RIGHT * wheel.r).set_stroke(GLOW, 4, 0)

        # counters: teeth passed and turns, measured from base
        base = {"turn": 0.0}

        def teeth_passed():
            return abs(gs.turn.get_value() - base["turn"]) * Z["wheel"] / TAU

        def counter(name, x):
            k = abs(gs[name].k)
            t_lab, n_lab = label(COUNT_TEXT[0]), label(COUNT_TEXT[1])
            rows = VGroup(t_lab, n_lab).arrange(DOWN, aligned_edge=RIGHT, buff=0.2).move_to([x - 0.45, -3.0, 0])

            def values():                                  # Text, not LaTeX numbers
                tv = label(str(int(teeth_passed() + 1e-6)), 0.36, WHITE)
                nv = label(f"{abs(gs.turn.get_value() - base['turn']) * k / TAU:.2f}", 0.36, GLOW)
                tv.next_to(t_lab, RIGHT, buff=0.2)
                nv.next_to(n_lab, RIGHT, buff=0.2)
                return VGroup(tv, nv)
            return VGroup(rows, always_redraw(values))
        counters = VGroup(counter("wheel", wheel.pivot[0]), counter("pinion", pinion.pivot[0] + 0.6))

        formula = ftext(FORMULA, 0.75).move_to([0.0, 2.95, 0])
        legend = label(LEGEND, 0.26).next_to(formula, DOWN, buff=0.2)
        instance = ftext(INSTANCE, 0.55, GLOW).next_to(legend, DOWN, buff=0.22)
        block = VGroup(formula, legend, instance)
        top_spot = block.get_center()
        block.move_to(BLOCK_AT)                            # beside the pair, until the third gear needs the room

        arrows = {"wheel": turn_arrow(wheel.pivot, wheel.r + 0.35, True, start_deg=140),
                  "pinion": turn_arrow(pinion.pivot, 1.0, False, start_deg=60, sweep=60),
                  "third": turn_arrow(third.pivot, third.r + 0.35, True, start_deg=110)}
        roles = {}
        for k, (a, b) in ROLES.items():
            g = gs[k]
            roles[k] = VGroup(label(a, 0.28, WHITE), label(b, 0.26, GLOW)).arrange(DOWN, buff=0.1)
            roles[k].move_to([g.pivot[0], -3.0, 0])

        curtain = FullScreenRectangle().set_fill(BG, 1).set_stroke(width=0)
        self.add(curtain)

        # ---------------------------------------------------------- timeline
        self.play(curtain.animate.set_fill(opacity=0), gs.speed.animate.set_value(SPEED),
                  run_time=FADE_IN, rate_func=smooth)
        self.remove(curtain)
        wait_until(CONTACT_AT)                             # the contact point
        self.add(contact)
        self.play(contact.animate(rate_func=there_and_back).set_stroke(opacity=1), run_time=1.6)
        self.play(contact.animate.set_stroke(opacity=0.6), run_time=0.4)

        wait_until(COUNTERS_AT)                            # the same number of teeth on each
        base["turn"] = gs.turn.get_value()
        self.play(FadeIn(counters, shift=UP * 0.1), run_time=0.8)

        wait_until(FORMULA_AT)                             # n1 z1 = n2 z2
        self.play(Write(formula), run_time=1.6)
        wait_until(LEGEND_AT)
        self.play(FadeIn(legend, shift=UP * 0.1), run_time=0.8)

        wait_until(STOP_AT)                                # stop and reset the counters
        self.play(gs.speed.animate.set_value(0.0), run_time=0.6)
        base["turn"] = gs.turn.get_value()
        wait_until(ONE_TURN_AT)                            # one turn of the wheel: four of the pinion
        self.play(gs.turn.animate.increment_value(-TAU), run_time=ONE_TURN_DURATION, rate_func=smooth)
        wait_until(INSTANCE_AT)
        self.play(FadeIn(instance, shift=UP * 0.1), run_time=0.8)

        wait_until(ARROWS_AT)                              # each mesh reverses direction
        self.play(FadeOut(counters), Create(arrows["wheel"]), gs.speed.animate.set_value(SPEED), run_time=1.0)
        self.play(Create(arrows["pinion"]), run_time=0.8)
        wait_until(THIRD_AT)                               # a third gear turns like the first
        self.play(*gs.show("third"), block.animate.move_to(top_spot), run_time=1.0)
        self.play(Create(arrows["third"]), run_time=0.8)

        for k, name in (("center", "wheel"), ("fourth", "third")):
            wait_until(ROLES_AT[k])                        # the center and fourth wheels
            self.play(FadeIn(roles[name], shift=UP * 0.1), run_time=0.8)
        wait_until(CLOCKWISE_AT)                           # both clockwise
        self.play(Indicate(arrows["wheel"], color=WHITE), Indicate(arrows["third"], color=WHITE),
                  Indicate(roles["wheel"][1]), Indicate(roles["third"][1]), run_time=1.4)

        wait_until(FINAL_HOLD_UNTIL)
        curtain.set_fill(opacity=0)
        self.add(curtain)
        self.play(curtain.animate.set_fill(opacity=1), run_time=FADE_OUT)
