"""Film 4, scene 01 - "The timekeeper": the bridges lift off the running
movement and the camera moves in over the balance. Its wheel, staff and
hairspring are named; then the movement slows ten times so the swing can be
seen, and the two numbers that set its pace are named: I and kappa.

Build (render + voice + mux):   python build.py 4/scene01_timekeeper
Render only (quick preview):    PYTHONPATH=.:films/film04_regulating_organ manim -ql films/film04_regulating_organ/scene01_timekeeper.py Scene01
Narration lines and their start times live in scene01_timekeeper.voice.txt.

The scene starts with frame_center at the origin, so neither the picture nor the
screen-fixed layer is offset (see CLAUDE.md); the camera moves with camera_move(target=...)
and then holds still while labels are pinned with the camera's own projection.
On every render the scene writes scene01_timekeeper.ticks.txt (the movement's
beats, slowed with the picture), which build.py uses for the tick track.
"""
from manim import *
from movement import Movement, attach_driver, camera_move, vignette, P, R, BG, GLOW, FONT_SANS, FONT_SERIF
from balance import BeatLog
from ui import heading, tag, label, curtain, clock

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds, angles in degrees.
# Keep the timeline roughly in step with scene01_timekeeper.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 1.2
LIFT_AT, LIFT_DURATION = 2.0, 3.0     # the bridges lift away
PUSH_AT, PUSH_DURATION = 5.4, 3.6     # the camera moves in over the balance
BALANCE_AT = 8.4                      # "...where it ends up: the balance"
NAME_AT = {"wheel": 11.0, "staff": 12.4, "spring": 14.6}
SLOW_AT, SLOW_DURATION = 20.0, 1.6    # "...keep it swinging": slow down ten times
NUMBERS_AT = {"I": 28.4, "kappa": 30.6}   # "how hard the wheel is to turn", "how stiff the spring is"
FINAL_HOLD_UNTIL = 34.4               # the last line ends about 32.3 s
FADE_OUT = 1.5

# --- motion ------------------------------------------------------------
SLOW = 0.1                            # clock rate after SLOW_AT (0.1 = ten times slower)

# --- tier heights ------------------------------------------------------
Z_ASSEMBLED = {"dial": 0.00, "engine": 0.30, "top": 0.62}
Z_LIFTED = {"dial": 0.00, "engine": 0.30, "top": 3.6}

# --- camera (phi = 0 is straight down) ---------------------------------
CAM_START = dict(phi=14, theta=-90, zoom=1.0)
CAM_CLOSE = dict(phi=12, theta=-90, zoom=2.7)
TARGET_OFFSET = (0.55, -0.2)           # aim a little right of the balance, leaving room for labels on the left

# --- text --------------------------------------------------------------
TITLE = ("THE BALANCE", "the watch's timekeeper")
NAMES = {"wheel": "balance wheel", "staff": "staff", "spring": "hairspring"}
NAME_AT_SCREEN = {"wheel": (-6.5, 2.4), "staff": (-6.5, 0.9), "spring": (-6.5, -0.6)}
SLOW_TAG = "slowed 10×"
NUMBERS = {"I": ("I", "how hard the wheel is to turn"), "kappa": ("κ", "how stiff the spring is")}
# =====================================================================

Z_BAL = Z_ASSEMBLED["engine"] + 0.32          # height of the balance's top face, for labels


class Scene01(ThreeDScene):
    def construct(self):
        self.camera.background_color = BG
        self.set_camera_orientation(phi=CAM_START["phi"] * DEGREES, theta=CAM_START["theta"] * DEGREES,
                                    zoom=CAM_START["zoom"], frame_center=ORIGIN)
        self.add_fixed_in_frame_mobjects(vignette())
        wait_until = clock(self)

        mv = Movement()
        mv.tiers["dial"].remove(mv.parts["dial_works"])       # under the plate, out of sight
        mv.rot = [r for r in mv.rot if r[2] != "dial"]
        rate = ValueTracker(1.0)
        explode, dim = attach_driver(self, mv, Z_ASSEMBLED, Z_LIFTED, rate=rate)
        log = BeatLog(self, rate=rate)

        bc = P["balance"]
        ring = Circle(radius=R["balance"] * 1.1, num_components=64).move_to(bc + OUT * Z_BAL).set_stroke(GLOW, 5, 0)
        self.add(ring)

        title = heading(*TITLE).to_corner(UL, buff=0.5)
        title = VGroup(SurroundingRectangle(title, buff=0.15, corner_radius=0.08).set_fill(BG, 0.85).set_stroke(width=0), title)
        slow_tag = tag(SLOW_TAG).to_corner(UR, buff=0.5)
        rows = []
        for k in ("I", "kappa"):
            sym, text = NUMBERS[k]
            rows.append(VGroup(Text(sym, font=FONT_SERIF, slant=ITALIC, color=GLOW).scale(0.6),
                               label(text, 0.3, WHITE)).arrange(RIGHT, buff=0.3))
        numbers = VGroup(*rows).arrange(DOWN, aligned_edge=LEFT, buff=0.25).to_corner(DL, buff=0.6)
        cur = curtain()
        self.add_fixed_in_frame_mobjects(title, slow_tag, numbers, cur)
        self.remove(title, slow_tag, numbers)

        # ---------------------------------------------------------- timeline
        self.play(cur.animate.set_fill(opacity=0), run_time=FADE_IN, rate_func=smooth)
        wait_until(LIFT_AT)
        self.play(explode.animate(run_time=LIFT_DURATION, rate_func=rate_functions.ease_in_cubic).set_value(1.0),
                  dim["top"].animate(run_time=LIFT_DURATION, rate_func=rate_functions.ease_in_quad).set_value(0.0))
        self.remove(mv.tiers["top"])
        wait_until(PUSH_AT)
        target = bc + np.array([TARGET_OFFSET[0], TARGET_OFFSET[1], Z_BAL])
        self.play(*camera_move(self, PUSH_DURATION, rate_func=rate_functions.ease_in_out_sine, target=target,
                               frame_origin=ORIGIN, **CAM_CLOSE))
        self.remove(self.camera._frame_center)

        wait_until(BALANCE_AT)                              # "the balance"
        self.play(FadeIn(title, shift=RIGHT * 0.2),
                  ring.animate(rate_func=there_and_back).set_stroke(GLOW, 6, 0.95), run_time=1.4)

        # labels pinned to the parts with the camera's own projection (the camera is still from here on)
        def screen(p):
            return self.camera.project_point(p)
        anchors = {"wheel": bc + R["balance"] * 0.95 * np.array([np.cos(2.5), np.sin(2.5), 0]) + OUT * Z_BAL,
                   "staff": bc + OUT * (Z_BAL + 0.02),
                   "spring": bc + 0.47 * np.array([np.cos(3.75), np.sin(3.75), 0]) + OUT * Z_BAL}
        for k in ("wheel", "staff", "spring"):
            wait_until(NAME_AT[k])
            name = label(NAMES[k], 0.34, WHITE)
            name.move_to(np.array([*NAME_AT_SCREEN[k], 0]), aligned_edge=LEFT)
            tip = screen(anchors[k])
            lead = VGroup(Line(name.get_right() + RIGHT * 0.12, tip).set_stroke(GREY_A, 2.0, 0.9),
                          Dot(tip, radius=0.06, color=GLOW))
            self.add_fixed_in_frame_mobjects(name, lead)
            self.remove(name, lead)
            self.play(FadeIn(name, shift=RIGHT * 0.15), Create(lead), run_time=0.9)

        wait_until(SLOW_AT)                                 # slow motion
        self.play(rate.animate.set_value(SLOW), FadeIn(slow_tag, shift=DOWN * 0.1), run_time=SLOW_DURATION)

        for k in ("I", "kappa"):                            # the two numbers
            wait_until(NUMBERS_AT[k])
            self.play(FadeIn(numbers[0 if k == "I" else 1], shift=UP * 0.1), run_time=0.9)

        wait_until(FINAL_HOLD_UNTIL)
        self.remove(cur)
        self.add_fixed_in_frame_mobjects(cur)               # re-add so it sits above the text
        self.play(cur.animate.set_fill(opacity=1), run_time=FADE_OUT)
        log.write(__file__)
