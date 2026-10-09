"""Scene 04 - "The Top Tier": hovering over the bridges of the hand-wound
movement as it is wound. The crown wheel turns the ratchet wheel, the click
rides over the ratchet teeth, then the camera moves to the balance bridge
where the regulator index is nudged.

Build (render + voice + mux):   python build.py scene04_top_modules
Render only (quick preview):    manim -ql scene04_top_modules.py Scene04
Narration lines and their start times live in scene04_top_modules.voice.txt.

The winding train is driven by mv.wind (crown turns) and the regulator by
mv.regulate (degrees), both trackers on the Movement (see movement.py).
"""
from manim import *
from movement import (Movement, attach_driver, vignette, camera_move, cue, aim, polar, P, R,
                      BG, GLOW, FONT_SANS)

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds, angles in degrees.
# Keep the timeline roughly in step with scene04_top_modules.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 1.6
WIND_START, WIND_END = 5.8, 15.4     # the crown is turned (crown wheel, ratchet, click)
WIND_TURNS = 3.0                     # crown turns over the winding
PAN_START, PAN_END = 15.8, 18.6      # camera moves to the balance bridge
NUDGE_AT = 18.8                      # regulator index nudged (fast <-> slow)
NUDGE = (4.0, -3.0, 0.0)             # regulator positions in degrees, in order
NUDGE_STEP = 0.9                     # seconds per regulator move
END_HOLD = 2.4
FADE_OUT = 1.5
LABEL_TIMES = {"title": 1.6, "winding": 9.4, "click": 14.2, "regulator": 17.6}
LABEL_FADE = 0.5
LABEL_BACKING = 0.72

# --- camera (hovering above the top bridges) ----------------------------
CAM_START = dict(phi=44, theta=-80, zoom=1.7, target=(1.05, 0.55, 0.8))    # over the winding wheels
CAM_REGULATOR = dict(phi=48, theta=-62, zoom=2.4, target=(-0.35, -1.75, 0.8))

# --- on-screen text --------------------------------------------------
TITLE = ("TIER 3  ·  TOP WORKS", "on top of the primary bridges")
ITEMS = {
    "winding": "crown wheel and ratchet wheel  ·  wind the mainspring",
    "click": "click  ·  keeps the mainspring from slipping back",
    "regulator": "regulator  ·  fine-tunes the rate",
}
Z_ASSEMBLED = {"dial": 0.00, "engine": 0.30, "top": 0.62}
# =====================================================================


def start_center(phi, theta, zoom, target):
    """The starting frame_center that puts `target` mid-screen (see movement.aim)."""
    c = np.array(target, dtype=float)
    for _ in range(50):                    # fixed point: aim() with frame_origin = c itself
        c = aim(phi, theta, zoom, target, frame_origin=c)
    return c


class Scene04(ThreeDScene):
    def construct(self):
        self.camera.background_color = BG
        origin = start_center(CAM_START["phi"], CAM_START["theta"], CAM_START["zoom"], CAM_START["target"])
        self.set_camera_orientation(phi=CAM_START["phi"] * DEGREES, theta=CAM_START["theta"] * DEGREES,
                                    zoom=CAM_START["zoom"], frame_center=origin)
        self.add_fixed_in_frame_mobjects(vignette())

        mv = Movement()
        attach_driver(self, mv, Z_ASSEMBLED, Z_ASSEMBLED)

        # rings that pulse when each part is named
        def ring(xy, r, dz=0.22):
            return Circle(radius=r, num_components=64).move_to(mv.world("top", xy, dz)).set_stroke(GLOW, 4, 0)
        rings = {"winding": VGroup(ring(P["barrel"], R["ratchet"] * 1.06), ring(P["crown_wheel"], R["crown_wheel"] * 1.1)),
                 "click": ring(P["barrel"][:2] + polar(R["ratchet"] + 0.15, 155)[:2], 0.34),
                 "regulator": ring(P["balance"], 0.34, 0.3)}
        self.add(*rings.values())

        # screen-fixed text
        head = Text(TITLE[0], font=FONT_SANS, weight=BOLD, color=GLOW).scale(0.40)
        sub = Text(TITLE[1], font=FONT_SANS, color=GREY_B).scale(0.26)
        items = {k: Text(t, font=FONT_SANS, color=GREY_B).scale(0.26) for k, t in ITEMS.items()}
        block = VGroup(head, sub, *items.values()).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        VGroup(*items.values()).shift(DOWN * 0.12)
        bar = Line(ORIGIN, RIGHT * 0.45).set_stroke(GLOW, 2)
        panel = VGroup(bar, block).arrange(RIGHT, buff=0.15, aligned_edge=UP).to_corner(DL, buff=0.5)
        backing = RoundedRectangle(corner_radius=0.12, width=panel.width + 0.5, height=panel.height + 0.4)
        backing.move_to(panel).set_fill(BG, LABEL_BACKING).set_stroke(width=0)
        panel = VGroup(backing, panel)
        curtain = FullScreenRectangle().set_fill(BG, 1).set_stroke(width=0)
        self.add_fixed_in_frame_mobjects(panel, curtain)
        self.remove(panel)

        def fade(*mobs):
            return [FadeIn(m, shift=RIGHT * 0.2) for m in mobs]

        def pulse(k):
            return rings[k].animate(rate_func=there_and_back).set_stroke(opacity=0.9)

        # ---------------------------------------------------------- timeline
        self.play(curtain.animate.set_fill(opacity=0), run_time=FADE_IN, rate_func=smooth)
        t = FADE_IN

        # hover over the barrel bridge while the crown is turned
        seg = dict(start=t, end=PAN_START)
        self.play(cue(LABEL_TIMES["title"], *fade(backing, bar, head, sub), **seg),
                  cue(WIND_START, mv.wind.animate(rate_func=rate_functions.ease_in_out_sine).set_value(WIND_TURNS),
                      run_time=WIND_END - WIND_START, **seg),
                  cue(LABEL_TIMES["winding"], *fade(items["winding"]), pulse("winding"), run_time=1.2, **seg),
                  cue(LABEL_TIMES["click"], *fade(items["click"]), pulse("click"), run_time=1.2, **seg))
        t = PAN_START

        # over to the balance bridge
        seg = dict(start=t, end=PAN_END)
        self.play(*camera_move(self, PAN_END - t, phi=CAM_REGULATOR["phi"], theta=CAM_REGULATOR["theta"],
                               zoom=CAM_REGULATOR["zoom"], target=CAM_REGULATOR["target"], frame_origin=origin),
                  cue(LABEL_TIMES["regulator"], *fade(items["regulator"]), **seg))
        self.remove(self.camera._frame_center)
        t = PAN_END

        self.wait(max(0.0, NUDGE_AT - t))
        self.play(pulse("regulator"), run_time=1.0)
        for deg in NUDGE:
            self.play(mv.regulate.animate.set_value(deg), run_time=NUDGE_STEP, rate_func=smooth)
        self.wait(END_HOLD)
        self.remove(curtain)
        self.add_fixed_in_frame_mobjects(curtain)        # re-add so it sits above the text
        self.play(FadeOut(panel), curtain.animate.set_fill(opacity=1), run_time=FADE_OUT)
