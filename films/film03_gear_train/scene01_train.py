"""Film 3, scene 01 - "The train in order": the bridges lift away from the
running movement, and the five wheels of the going train are named and numbered
in order (barrel, center, third, fourth, escape). The "second wheel" is the
center wheel; a pulse of light shows power flowing down the train to the
escapement; and each wheel's period appears beside its name.

Build (render + voice + mux):   python build.py 3/scene01_train
Render only (quick preview):    PYTHONPATH=.:films/film03_gear_train manim -ql films/film03_gear_train/scene01_train.py Scene01
Narration lines and their start times live in scene01_train.voice.txt.

The camera holds still so the screen-fixed labels stay on their wheels (they
are placed with the camera's own projection). The train uses the documented
6497 tooth counts (movement.TEETH_6497), so the third wheel shows 60 teeth.
"""
from manim import *
import movement
movement.use_train(movement.TEETH_6497)
from movement import Movement, attach_driver, vignette, P, R, BG, GLOW, FONT_SANS

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds, angles in degrees.
# Keep the timeline roughly in step with scene01_train.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 1.2
LIFT_AT, LIFT_DURATION = 1.6, 3.4     # the bridges lift away toward the camera
TRAIN_AT = 5.6                        # "called the going train": a sweep along the train
NAME_AT = {"barrel": 8.2, "center": 9.9, "third": 13.5, "fourth": 15.0, "escape": 18.3}
NUMBERS_AT = 21.2                     # "watchmakers number them in that order"
SECOND_AT = 23.9                      # "the 'second wheel' is the center wheel"
NOT_SECONDS_AT = 26.4                 # "not the wheel that carries the seconds"
FLOW_AT, FLOW_DURATION = 29.4, 3.0    # "power flows down the train"
ESCAPE_AT = 33.0                      # "the escapement lets it out one tooth at a time"
SPEEDS_AT, SPEEDS_LAG = 37.0, 0.55    # "each wheel turns faster than the one before it"
FINAL_HOLD_UNTIL = 44.6               # the last line ends about 43.2 s
FADE_OUT = 1.5

# --- tier heights ------------------------------------------------------
Z_ASSEMBLED = {"dial": 0.00, "engine": 0.30, "top": 0.62}
Z_LIFTED = {"dial": 0.00, "engine": 0.30, "top": 3.6}

# --- camera (held still; phi = 0 is straight down) ---------------------
CAM = dict(phi=14, theta=-90, zoom=1.22, center=(-0.35, 0.05, 0.3))

# --- labels: screen position of each label's left edge ------------------
TRAIN = ["barrel", "center", "third", "fourth", "escape"]
LABEL_AT = {"barrel": (3.75, 2.55), "center": (4.55, -1.45), "third": (-6.6, 2.55),
            "fourth": (-6.6, 0.55), "escape": (-6.6, -1.35)}
NAMES = {"barrel": "barrel", "center": "center wheel", "third": "third wheel",
         "fourth": "fourth wheel", "escape": "escape wheel"}
CARRIES = {"center": "carries the minute hand", "fourth": "carries the seconds hand"}
SPEEDS = {"barrel": "1 turn in about 7 hours", "center": "1 turn an hour", "third": "1 turn in 7½ minutes",
          "fourth": "1 turn a minute", "escape": "1 turn in 6 seconds"}
SECOND_TAG = "the “second wheel”"
TITLE = ("THE GOING TRAIN", "barrel to escapement")
WARN = "#ff8a6a"                      # the fourth wheel's "seconds" pulse
# =====================================================================

RING_R = {"barrel": R["barrel"], "center": R["center"], "third": R["third"], "fourth": R["fourth"],
          "escape": R["escape"], "pallet": 0.3, "balance": R["balance"]}
FLOW = TRAIN + ["pallet", "balance"]
Z_RING = Z_ASSEMBLED["engine"] + 0.32


class Scene01(ThreeDScene):
    def construct(self):
        self.camera.background_color = BG
        self.set_camera_orientation(phi=CAM["phi"] * DEGREES, theta=CAM["theta"] * DEGREES,
                                    zoom=CAM["zoom"], frame_center=np.array(CAM["center"]))
        self.add_fixed_in_frame_mobjects(vignette())

        def wait_until(when):
            d = when - self.renderer.time
            if d > 1e-3:
                self.wait(d)

        mv = Movement()
        mv.tiers["dial"].remove(mv.parts["dial_works"])       # under the plate, out of sight
        mv.rot = [r for r in mv.rot if r[2] != "dial"]
        explode, dim = attach_driver(self, mv, Z_ASSEMBLED, Z_LIFTED)

        # rings over the wheels, for highlights and the power flow
        rings = {k: Circle(radius=RING_R[k] * 1.08, num_components=64).move_to(P[k] + OUT * Z_RING)
                 .set_stroke(GLOW, 4, 0) for k in FLOW}
        self.add(*rings.values())
        path = VMobject().set_points_as_corners([P[k] + OUT * Z_RING for k in FLOW]).set_stroke(GLOW, 7, 0.9)

        # screen-fixed labels with leader lines to the wheels
        def screen(k):
            return self.camera.project_point(P[k] + OUT * Z_RING)

        labels, leaders, subs, speeds, nums = {}, {}, {}, {}, {}
        for i, k in enumerate(TRAIN, 1):
            num = Text(str(i), font=FONT_SANS, weight=BOLD, color=GLOW).scale(0.42)
            name = Text(NAMES[k], font=FONT_SANS, color=WHITE).scale(0.34)
            head = VGroup(num, name).arrange(RIGHT, buff=0.16)
            rows = [head]
            if k in CARRIES:
                subs[k] = Text(CARRIES[k], font=FONT_SANS, color=GREY_B).scale(0.25)
                rows.append(subs[k])
            speeds[k] = Text(SPEEDS[k], font=FONT_SANS, color=GLOW).scale(0.25)
            rows.append(speeds[k])
            block = VGroup(*rows).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
            name.align_to(num, DOWN)
            x, y = LABEL_AT[k]
            block.move_to(np.array([x, y, 0]), aligned_edge=UL)
            labels[k], nums[k] = block, num
            target = screen(k)
            near = head.get_left() + LEFT * 0.12 if x > 0 else head.get_right() + RIGHT * 0.12
            leaders[k] = VGroup(Line(near, target).set_stroke(GREY_B, 1.4, 0.8),
                                Dot(target, radius=0.045, color=GLOW))
        second_tag = Text(SECOND_TAG, font=FONT_SANS, slant=ITALIC, color=GLOW).scale(0.3)
        second_tag.next_to(labels["center"], UP, buff=0.14, aligned_edge=LEFT)

        head = Text(TITLE[0], font=FONT_SANS, weight=BOLD, color=GLOW).scale(0.40)
        sub = Text(TITLE[1], font=FONT_SANS, color=GREY_B).scale(0.26)
        title = VGroup(head, sub).arrange(DOWN, aligned_edge=LEFT, buff=0.1).to_corner(DL, buff=0.5)

        curtain = FullScreenRectangle().set_fill(BG, 1).set_stroke(width=0)
        fixed = [title, second_tag] + list(leaders.values()) + list(labels.values())
        self.add_fixed_in_frame_mobjects(*fixed, curtain)
        self.remove(*fixed)
        # the speed lines appear last; hide them inside their blocks for now
        for k in TRAIN:
            speeds[k].set_opacity(0)

        def pulse(k, run_time=1.2, width=4):
            return rings[k].animate(rate_func=there_and_back, run_time=run_time).set_stroke(GLOW, width, 0.95)

        # ---------------------------------------------------------- timeline
        self.play(curtain.animate.set_fill(opacity=0), run_time=FADE_IN, rate_func=smooth)
        wait_until(LIFT_AT)
        self.play(explode.animate(run_time=LIFT_DURATION, rate_func=rate_functions.ease_in_cubic).set_value(1.0),
                  dim["top"].animate(run_time=LIFT_DURATION, rate_func=rate_functions.ease_in_quad).set_value(0.0),
                  FadeIn(title, shift=RIGHT * 0.2, run_time=1.0, rate_func=smooth))
        self.remove(mv.tiers["top"])                      # invisible now; stop drawing it

        wait_until(TRAIN_AT)
        self.play(ShowPassingFlash(VMobject().set_points_as_corners([P[k] + OUT * Z_RING for k in TRAIN])
                                   .set_stroke(GLOW, 6, 0.9), time_width=0.4, run_time=1.8))

        for k in TRAIN:                                   # name the wheels in order
            wait_until(NAME_AT[k])
            self.play(FadeIn(labels[k], shift=RIGHT * 0.15 if LABEL_AT[k][0] < 0 else LEFT * 0.15),
                      Create(leaders[k]), pulse(k), run_time=0.9)

        wait_until(NUMBERS_AT)                            # numbered in order
        self.play(LaggedStart(*[Indicate(nums[k], color=GLOW, scale_factor=1.5) for k in TRAIN],
                              lag_ratio=0.35, run_time=2.2))
        wait_until(SECOND_AT)                             # the second wheel is the center wheel
        self.play(FadeIn(second_tag, shift=UP * 0.1), Indicate(nums["center"], color=GLOW, scale_factor=1.6),
                  pulse("center", 1.4, 6), run_time=1.0)
        wait_until(NOT_SECONDS_AT)                        # ... not the wheel with the seconds hand
        self.play(Indicate(subs["fourth"], color=WARN, scale_factor=1.15), pulse("fourth", 1.2, 6), run_time=1.2)

        wait_until(FLOW_AT)                               # power flows down the train
        self.play(ShowPassingFlash(path.copy(), time_width=0.35, run_time=FLOW_DURATION),
                  LaggedStart(*[pulse(k, 0.9) for k in FLOW], lag_ratio=0.55, run_time=FLOW_DURATION))
        wait_until(ESCAPE_AT)                             # one tooth at a time
        self.play(Succession(*[AnimationGroup(pulse("escape", 0.4, 5), pulse("balance", 0.4, 5))
                               for _ in range(4)]), run_time=1.6)

        wait_until(SPEEDS_AT)                             # each wheel faster than the last
        self.play(LaggedStart(*[speeds[k].animate.set_opacity(1) for k in TRAIN],
                              lag_ratio=SPEEDS_LAG, run_time=SPEEDS_LAG * 4 + 0.6))

        wait_until(FINAL_HOLD_UNTIL)
        self.remove(curtain)
        self.add_fixed_in_frame_mobjects(curtain)         # re-add so it sits above the text
        self.play(curtain.animate.set_fill(opacity=1), run_time=FADE_OUT)
