"""Scene 01 - "The Vertical City": the movement explodes into three tiers.

Build (render + voice + mux):   python build.py scene01_vertical_city
Render only (quick preview):    manim -ql scene01_vertical_city.py Scene01
Narration lines and their start times live in scene01_vertical_city.voice.txt.
"""
from manim import *
from movement import (Movement, attach_driver, vignette, P, BG, GLOW, FONT_SANS)

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds, angles in degrees.
# Keep the timeline roughly in step with the start times in
# scene01_vertical_city.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 1.6              # fade up from black
EXPLODE_AT = 6.0           # when the tiers start to separate
EXPLODE_DURATION = 5.0
SETTLE_CAMERA = 1.2        # camera lift after the explode
TITLE_FADE = 0.8
LABEL_FADE = 0.5           # each of the three labels
GLOW_PULSE = 2.6           # light rays brighten and fade back
TOUR_MOVE = 2.0            # camera travel to each tier
TOUR_HOLD = 1.6            # pause on each tier
TOUR_RETURN = 2.2
FINAL_HOLD = 1.5
FADE_OUT = 1.5

# --- tier heights (scene units; the plate is 6 units across) ---------
Z_ASSEMBLED = {"dial": 0.00, "engine": 0.30, "top": 0.62}
Z_EXPLODED = {"dial": -2.1, "engine": 0.0, "top": 2.1}

# --- camera ----------------------------------------------------------
ORBIT_RATE = 0.085                            # radians per second of slow orbit
CAMERA_START = dict(phi=56, theta=-72, zoom=0.86)
CAMERA_EXPLODED = dict(phi=68, zoom=0.74)
CAMERA_END = dict(phi=66, zoom=0.74)
# tour stops: (tier, height offset above the tier, zoom, phi)
TOUR = [("top", 0.20, 1.08, 52),
        ("engine", 0.15, 1.12, 48),
        ("dial", 0.10, 1.08, 50)]
TOUR_DIM = 0.12            # opacity of the tiers not in focus
FLIP_DIAL = True           # turn the dial tier over at its tour stop to show the dial side
LABEL_DIM = 0.25           # opacity of the labels not in focus

# --- light between the tiers -----------------------------------------
RAY_OPACITY = 0.09
RAY_CORE_OPACITY = 0.32
RAY_PULSE_OPACITY = (0.16, 0.50)   # (glow, core) at the peak of the pulse
MOTE_OPACITY = 0.6

# --- on-screen text --------------------------------------------------
TITLE = "THE VERTICAL CITY"
SUBTITLE = "anatomy of a hand-wound movement"
LABELS = {   # tier: (heading, sub-line, vertical position on screen)
    "top": ("TOP WORKS", "bridges · winding wheels · regulator", 2.3),
    "engine": ("MIDDLE ENGINE", "going train · lever escapement · balance", 0.25),
    "dial": ("DIAL SIDE", "main plate · motion works · keyless works", -1.85),
}
# =====================================================================


class Scene01(ThreeDScene):
    def construct(self):
        self.camera.background_color = BG
        self.set_camera_orientation(phi=CAMERA_START["phi"] * DEGREES,
                                    theta=CAMERA_START["theta"] * DEGREES, zoom=CAMERA_START["zoom"])
        self.add_fixed_in_frame_mobjects(vignette())

        mv = Movement()
        explode, dim = attach_driver(self, mv, Z_ASSEMBLED, Z_EXPLODED)

        # light rays and dust motes spanning the exploded stack
        ray_pts = [P[k] for k in ("center", "barrel", "balance", "fourth", "escape", "third")] + \
                  [np.array([-2.3, -1.2, 0]), np.array([2.4, -1.2, 0]), np.array([0.3, 2.5, 0])]
        lo, hi = Z_EXPLODED["dial"] + 0.05, Z_EXPLODED["top"] - 0.05
        rays = VGroup(*[Line(p + OUT * lo, p + OUT * hi).set_stroke(GLOW, 9 if i < 6 else 4, 0.0)
                        for i, p in enumerate(ray_pts)])
        cores = VGroup(*[r.copy().set_stroke(WHITE, 1.3, 0.0) for r in rays])
        rng = np.random.default_rng(3)
        motes = VGroup(*[Dot(np.array([x, y, z]), radius=0.012, color=GLOW).set_opacity(0)
                         for x, y, z in rng.uniform([-2.6, -2.6, lo + 0.2], [2.6, 2.6, hi - 0.2], (70, 3))
                         if x * x + y * y < 6.5])

        # screen-fixed text
        def label(heading, sub, y):
            t = Text(heading, font=FONT_SANS, weight=BOLD, color=GLOW).scale(0.40)
            s = Text(sub, font=FONT_SANS, color=GREY_B).scale(0.26)
            g = VGroup(t, s).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
            tick = Line(ORIGIN, RIGHT * 0.45).set_stroke(GLOW, 2)
            return VGroup(tick, g).arrange(RIGHT, buff=0.15, aligned_edge=UP).to_edge(LEFT, buff=0.45).set_y(y)

        lab = {k: label(*v) for k, v in LABELS.items()}
        title = Text(TITLE, font=FONT_SANS, weight=BOLD, color=GLOW).scale(0.48).to_corner(UR, buff=0.5)
        subtitle = Text(SUBTITLE, font=FONT_SANS, color=GREY_B).scale(0.26)
        subtitle.next_to(title, DOWN, buff=0.1, aligned_edge=RIGHT)
        curtain = FullScreenRectangle().set_fill(BG, 1).set_stroke(width=0)

        # ---------------------------------------------------------- timeline
        self.add_fixed_in_frame_mobjects(curtain)
        self.begin_ambient_camera_rotation(rate=ORBIT_RATE)
        self.play(curtain.animate.set_fill(opacity=0), run_time=FADE_IN, rate_func=smooth)
        self.wait(EXPLODE_AT - FADE_IN)

        self.add(rays, cores, motes)
        self.play(explode.animate.set_value(1.0),
                  rays.animate.set_stroke(opacity=RAY_OPACITY),
                  cores.animate.set_stroke(opacity=RAY_CORE_OPACITY),
                  motes.animate.set_opacity(MOTE_OPACITY),
                  run_time=EXPLODE_DURATION, rate_func=rate_functions.ease_in_out_cubic)
        self.move_camera(phi=CAMERA_EXPLODED["phi"] * DEGREES, zoom=CAMERA_EXPLODED["zoom"], run_time=SETTLE_CAMERA)

        self.add_fixed_in_frame_mobjects(title, subtitle, *lab.values())
        self.remove(title, subtitle, *lab.values())
        self.play(FadeIn(title, shift=LEFT * 0.2), FadeIn(subtitle, shift=LEFT * 0.2), run_time=TITLE_FADE)
        for k in ("top", "engine", "dial"):
            self.play(FadeIn(lab[k], shift=RIGHT * 0.2), run_time=LABEL_FADE)
        self.play(rays.animate.set_stroke(opacity=RAY_PULSE_OPACITY[0]),
                  cores.animate.set_stroke(opacity=RAY_PULSE_OPACITY[1]),
                  run_time=GLOW_PULSE, rate_func=there_and_back)

        for tier, dz, zoom, phi in TOUR:
            anims = [lab[o].animate.set_opacity(1.0 if o == tier else LABEL_DIM) for o in lab] + \
                    [dim[o].animate.set_value(1.0 if o == tier else TOUR_DIM) for o in dim]
            if tier == "dial" and FLIP_DIAL:
                anims.append(mv.flip.animate.set_value(1.0))      # dial side up
            self.move_camera(phi=phi * DEGREES, zoom=zoom, frame_center=OUT * (Z_EXPLODED[tier] + dz),
                             added_anims=anims, run_time=TOUR_MOVE, rate_func=smooth)
            self.wait(TOUR_HOLD)

        self.move_camera(phi=CAMERA_END["phi"] * DEGREES, zoom=CAMERA_END["zoom"], frame_center=ORIGIN,
                         added_anims=[l.animate.set_opacity(1) for l in lab.values()] +
                                     [d.animate.set_value(1.0) for d in dim.values()] +
                                     [mv.flip.animate.set_value(0.0)],
                         run_time=TOUR_RETURN)
        self.wait(FINAL_HOLD)
        self.remove(curtain)
        self.add_fixed_in_frame_mobjects(curtain)        # re-add so it sits above the text
        self.play(*[FadeOut(m) for m in (title, subtitle, *lab.values())],
                  curtain.animate.set_fill(opacity=1), run_time=FADE_OUT)
