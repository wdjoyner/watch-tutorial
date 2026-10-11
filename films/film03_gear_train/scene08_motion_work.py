"""Film 3, scene 08 - "The motion work": the bridges and train fade and the
plate turns over, dial side up, to show the motion work. Then a flat close-up,
sped up, with the hands: the cannon pinion (12) on the center arbor carries the
minute hand and drives the minute wheel (36, 3 : 1); the minute wheel's pinion
(10) drives the hour wheel (40, 4 : 1), which carries the hour hand: 3 x 4 = 12.
Last, the cannon pinion's friction grip: when the hands are set it slips on
the center arbor, which stays still.

Build (render + voice + mux):   python build.py 3/scene08_motion_work
Render only (quick preview):    PYTHONPATH=.:films/film03_gear_train manim -ql films/film03_gear_train/scene08_motion_work.py Scene08
Narration lines and their start times live in scene08_motion_work.voice.txt.

In the close-up the parts are drawn larger than the train would allow, and in
an order chosen for clarity: the cannon pinion and hands on top.
"""
from manim import *
import movement
movement.use_train(movement.TEETH_6497)
from movement import (Movement, attach_driver, vignette, polar, BG, GLOW, FONT_SANS, FONT_SERIF, BRASS, STEEL,
                      STEEL_HI, STEEL_DK)
from train import GearSet

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds.
# Keep the timeline roughly in step with scene08_motion_work.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 1.2
CLEAR_AT, CLEAR_DURATION = 1.2, 1.6    # the bridges and train fade away
FLIP_AT, FLIP_DURATION = 2.6, 3.0      # the plate turns over, dial side up
MOTION_AT = 6.0                        # "it's called the motion work"
CLOSEUP_AT = 7.8                       # crossfade to the flat close-up
CANNON_AT, MINUTE_HAND_AT = 8.6, 12.4  # "the cannon pinion ... carries the minute hand"
MINUTE_WHEEL_AT, RATIO3_AT = 15.6, 17.8
HOUR_WHEEL_AT, RATIO4_AT = 20.8, 23.4
TWELVE_AT, HOUR_HAND_AT = 26.7, 29.0   # 3 x 4 = 12; the hour hand
FRICTION_AT = 34.3                     # "grips the center arbor only by friction"
SET_AT, SET_DURATION = 39.3, 4.4       # setting the hands: the cannon pinion slips
FINAL_HOLD_UNTIL = 46.2                # the last line ends about 44.7 s
FADE_OUT = 1.5

# --- the 3D opening ------------------------------------------------------
Z_ASSEMBLED = {"dial": 0.00, "engine": 0.30, "top": 0.62}
CAM = dict(phi=14, theta=-90, zoom=1.15, center=(0.0, 0.0, 0.0))

# --- the close-up (screen units) --------------------------------------------
SCALE = 2.2                            # close-up size relative to the model
CANNON_XY = (-1.7, 0.1)
MW_ANGLE = -22                         # minute wheel direction from the cannon pinion (as in the model)
RUN_SPEED = -0.35                      # cannon pinion, radians per second (clockwise from the dial side)
FAST_SPEED = -1.6                      # while showing 3 x 4 = 12
SET_SPEED = -2.4                       # while setting
MINUTE_HAND_L, HOUR_HAND_L = 2.75, 1.75

# --- text --------------------------------------------------------------
LAB_X = 2.7                            # left edge of the labels
TITLE = "THE MOTION WORK"
LABELS = {"cannon": ("cannon pinion  ·  12", "on the center arbor:  1 turn / hour"),
          "minute": ("minute wheel  ·  36,  pinion 10", ""),
          "hour": ("hour wheel  ·  40", "carries the hour hand")}
RATIO3, RATIO4 = "36 / 12  =  3", "40 / 10  =  4"
TWELVE = "3 × 4  =  12"
HOUR_TURN = "1 turn / 12 hours"
FRICTION = "friction fit"
SETTING = ("setting the hands:", "the cannon pinion slips,", "the center arbor stays still")
# =====================================================================


def label(s, scale=0.28, color=GREY_B, bold=False):
    return Text(s, font=FONT_SANS, weight=BOLD if bold else NORMAL, color=color).scale(scale)


def ftext(s, scale=0.5, color=WHITE):
    return Text(s, font=FONT_SERIF, slant=ITALIC, color=color).scale(scale)


def hand(length, width, color, tail=0.25):
    pts = [[-tail, 0, 0], [0, width / 2, 0], [length, width * 0.15, 0], [length + 0.08, 0, 0],
           [length, -width * 0.15, 0], [0, -width / 2, 0]]
    return Polygon(*pts).set_fill(color, 1).set_stroke(BG, 1.5)


class Scene08(ThreeDScene):
    def construct(self):
        self.camera.background_color = BG
        self.set_camera_orientation(phi=CAM["phi"] * DEGREES, theta=CAM["theta"] * DEGREES,
                                    zoom=CAM["zoom"], frame_center=np.array(CAM["center"]))
        self.add_fixed_in_frame_mobjects(vignette())

        def wait_until(when):
            d = when - self.renderer.time
            if d > 1e-3:
                self.wait(d)

        # ------------------------------------------------------------ the 3D opening
        mv = Movement()
        explode, dim = attach_driver(self, mv, Z_ASSEMBLED, Z_ASSEMBLED)

        # ------------------------------------------------------------ the close-up
        m_a, m_b = SCALE / ((12 + 36) / 2), SCALE / ((10 + 40) / 2)
        gs = GearSet()
        cannon = gs.gear("cannon", 12, m_a, center=CANNON_XY, kind="pinion")
        minute = gs.gear("minute", 36, m_a, driven_by="cannon", angle=MW_ANGLE, spokes=3, color=STEEL)
        mpin = gs.gear("mpin", 10, m_b, arbor_of="minute", kind="pinion")
        hour = gs.gear("hour", 40, m_b, driven_by="mpin", angle=MW_ANGLE + 180, kind="plain")
        hour.body.set_fill(BRASS, 0.92)
        hour._base = [(m, m.get_fill_opacity(), m.get_stroke_opacity()) for m in hour.family_members_with_points()]
        gs.group.submobjects = [hour, minute, mpin, cannon]
        for n in gs.gears:
            gs.hide(n)
        c0 = cannon.pivot
        arbor = VGroup(Circle(radius=cannon.r * 0.42).set_fill(STEEL_DK, 1).set_stroke(STEEL_HI, 1.5),
                       Line(ORIGIN, RIGHT * cannon.r * 0.38).set_stroke(GLOW, 3)).move_to(c0)
        arbor[1].shift(RIGHT * cannon.r * 0.19)
        friction = Circle(radius=cannon.r * 0.48).move_to(c0).set_stroke(GLOW, 4, 0)
        hands = {"minute": hand(MINUTE_HAND_L, 0.14, WHITE).shift(c0),
                 "hour": hand(HOUR_HAND_L, 0.2, GLOW).shift(c0)}
        state = {"arbor": 0.0, "slip": False, "minute": 0.0, "hour": 0.0}
        # fade the turning hands and arbor through trackers (an .animate would fight the rotation)
        vis = {"minute": ValueTracker(0.0), "hour": ValueTracker(0.0), "arbor": ValueTracker(0.0)}
        shown = {k: None for k in vis}
        turning = {"minute": hands["minute"], "hour": hands["hour"], "arbor": arbor}
        start = {"cannon": cannon._ang, "hour": hour._ang}

        def follow(_):
            ca, ha = cannon._ang - start["cannon"], hour._ang - start["hour"]
            for k, a in (("minute", ca), ("hour", ha)):
                if a != state[k]:
                    hands[k].rotate(a - state[k], about_point=c0)
                    state[k] = a
            if not state["slip"] and ca != state["arbor"]:
                arbor.rotate(ca - state["arbor"], about_point=c0)
                state["arbor"] = ca
            for k, v in vis.items():
                o = v.get_value()
                if o != shown[k]:
                    turning[k].set_opacity(o)
                    shown[k] = o
        follower = Mobject().add_updater(follow)
        hands["minute"].rotate(PI / 2, about_point=c0)            # start at 12 and about 4 o'clock
        hands["hour"].rotate(PI / 2 - TAU * 4 / 12, about_point=c0)

        labels = {}
        for k, (a, b) in LABELS.items():
            rows = [label(a, 0.3, WHITE)] + ([label(b, 0.26, GLOW)] if b else [])
            labels[k] = VGroup(*rows).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        labels["cannon"].move_to([LAB_X, 2.3, 0], aligned_edge=UL)
        labels["minute"].move_to([LAB_X, 1.15, 0], aligned_edge=UL)
        labels["hour"].move_to([LAB_X, 0.25, 0], aligned_edge=UL)
        r3 = ftext(RATIO3, 0.42, GLOW).next_to(labels["minute"], DOWN, aligned_edge=LEFT, buff=0.1)
        r4 = ftext(RATIO4, 0.42, GLOW).next_to(labels["hour"], DOWN, aligned_edge=LEFT, buff=0.1)
        twelve = ftext(TWELVE, 0.62, WHITE).move_to([LAB_X, -1.1, 0], aligned_edge=LEFT)
        hour_turn = label(HOUR_TURN, 0.3, GLOW).next_to(twelve, DOWN, aligned_edge=LEFT, buff=0.2)
        fric_lab = label(FRICTION, 0.3, GLOW).move_to(c0 + np.array([-1.7, 2.35, 0]))
        fric_lead = Line(fric_lab.get_bottom() + DOWN * 0.05,
                         c0 + cannon.r * 0.48 * np.array([-0.6, 0.8, 0])).set_stroke(GLOW, 1.5)
        setting = VGroup(label(SETTING[0], 0.3, WHITE), *[label(t, 0.27, GLOW) for t in SETTING[1:]])
        setting.arrange(DOWN, aligned_edge=LEFT, buff=0.1).move_to([LAB_X, -2.95, 0], aligned_edge=LEFT)
        title = label(TITLE, 0.36, GLOW, True).to_corner(UL, buff=0.45)
        rings = {k: Circle(radius=g.r + 0.12).move_to(g.pivot).set_stroke(GLOW, 4, 0)
                 for k, g in (("cannon", cannon), ("minute", minute), ("hour", hour))}

        curtain = FullScreenRectangle().set_fill(BG, 1).set_stroke(width=0)
        flat = [gs.group, arbor, friction, hands["hour"], hands["minute"], title, r3, r4, twelve, hour_turn,
                fric_lab, fric_lead, setting, *labels.values(), *rings.values()]
        self.add_fixed_in_frame_mobjects(*flat, curtain)
        self.remove(*flat)
        self.add(gs.group)
        gs.attach(self, add=False)
        self.add(follower, *vis.values())

        def pulse(k, run_time=1.2):
            return rings[k].animate(rate_func=there_and_back, run_time=run_time).set_stroke(opacity=0.95)

        # ---------------------------------------------------------- timeline
        self.play(curtain.animate.set_fill(opacity=0), run_time=FADE_IN, rate_func=smooth)
        wait_until(CLEAR_AT)                               # the bridges and train fade away
        self.play(dim["top"].animate.set_value(0), dim["engine"].animate.set_value(0), run_time=CLEAR_DURATION)
        self.remove(mv.tiers["top"], mv.tiers["engine"])
        wait_until(FLIP_AT)                                # dial side up
        self.play(mv.flip.animate.set_value(1.0), run_time=FLIP_DURATION, rate_func=smooth)
        wait_until(MOTION_AT)                              # the motion work, in place
        ring3d = VGroup(*[Circle(radius=r).move_to(mv.world("dial", xy, 0.25)).set_stroke(GLOW, 4)
                          for xy, r in (((0, 0), 0.9), (polar(1.0, -22)[:2], 0.85))])
        self.play(Create(ring3d), FadeIn(title), run_time=1.0)

        wait_until(CLOSEUP_AT)                             # crossfade to the close-up
        self.add(*rings.values(), hands["hour"], hands["minute"], arbor)
        self.play(dim["dial"].animate.set_value(0), FadeOut(ring3d), *gs.show("cannon", "minute", "mpin", "hour"),
                  gs.speed.animate.set_value(RUN_SPEED), run_time=1.0)
        self.remove(mv.tiers["dial"])

        wait_until(CANNON_AT)                              # the cannon pinion on the center arbor
        self.play(FadeIn(labels["cannon"], shift=LEFT * 0.1), pulse("cannon"), vis["arbor"].animate.set_value(1),
                  run_time=1.0)
        wait_until(MINUTE_HAND_AT)
        self.play(vis["minute"].animate.set_value(1), run_time=0.8)

        wait_until(MINUTE_WHEEL_AT)                        # the minute wheel, 3 : 1
        self.play(FadeIn(labels["minute"], shift=LEFT * 0.1), pulse("minute"), run_time=1.0)
        wait_until(RATIO3_AT)
        self.play(FadeIn(r3, shift=UP * 0.1), run_time=0.8)
        wait_until(HOUR_WHEEL_AT)                          # the hour wheel, 4 : 1
        self.play(FadeIn(labels["hour"], shift=LEFT * 0.1), pulse("hour"), run_time=1.0)
        wait_until(RATIO4_AT)
        self.play(FadeIn(r4, shift=UP * 0.1), run_time=0.8)

        wait_until(TWELVE_AT)                              # 3 x 4 = 12
        self.play(Write(twelve), run_time=1.0)
        wait_until(HOUR_HAND_AT)                           # the hour hand: once in twelve hours
        self.play(vis["hour"].animate.set_value(1), FadeIn(hour_turn, shift=UP * 0.1),
                  gs.speed.animate.set_value(FAST_SPEED), run_time=1.0)
        self.wait(2.6)
        self.play(gs.speed.animate.set_value(RUN_SPEED), run_time=1.0)

        wait_until(FRICTION_AT)                            # the friction grip on the center arbor
        self.add(friction)
        self.play(friction.animate.set_stroke(opacity=1), FadeIn(fric_lab), Create(fric_lead), run_time=1.0)

        wait_until(SET_AT)                                 # setting: the cannon pinion slips, the arbor stays still
        state["slip"] = True
        self.play(FadeIn(setting, shift=UP * 0.1), gs.speed.animate.set_value(SET_SPEED), run_time=0.8)
        self.wait(SET_DURATION - 1.6)
        self.play(gs.speed.animate.set_value(0.0), run_time=0.8)

        wait_until(FINAL_HOLD_UNTIL)
        self.remove(curtain)
        self.add_fixed_in_frame_mobjects(curtain)
        self.play(curtain.animate.set_fill(opacity=1), run_time=FADE_OUT)
