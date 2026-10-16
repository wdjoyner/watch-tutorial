"""Film 7, scene 02 - "The parts": every part named and defined.

The 3D movement's dial-side tier turns over, dial side up (Film 1's model), and
the keyless works and motion work are ringed. The camera comes straight down
and the view crossfades into the flat dial side (dialside.py: the keyless
close-up with the setting train and the motion work, pushed in). Each part
lights up and gets a one-line definition as it is named: crown, stem, winding
pinion, sliding pinion (a clutch), setting lever, yoke and yoke spring, setting
lever jumper, setting wheels, minute wheel, cannon pinion and minute hand, hour
wheel and hour hand. The movement's own clock is stopped (rate 0) in the 3D part.

Build (render + voice + mux):   python build.py 7/scene02_parts
Render only (quick preview):    PYTHONPATH=.:films/film07_keyless_works manim -ql films/film07_keyless_works/scene02_parts.py Scene02
Narration lines and their start times live in scene02_parts.voice.txt.

The flat layer is drawn in the 3D scene with the camera straight down
(phi = 0, theta = -90 degrees, zoom 1, frame center at the origin), where the
3D projection of the z = 0 plane is the identity, so it renders as in a 2D scene.
"""
from manim import *
import prev  # noqa: F401  (first: earlier films' helpers on the path)
from movement import Movement, attach_driver, vignette, BG, GLOW
from ui import label, heading, tag, curtain, clock
from ui6 import callout, callouts
from dialside import DialSide

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds.
# Keep the timeline roughly in step with scene02_parts.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 1.0
FLIP = (1.2, 4.4)              # "Turn the movement over, to the dial side."
RINGS_AT = 4.6                 # "The keyless works sits beside the crown."
FLAT = (6.4, 8.0)              # the camera comes straight down; the flat dial side fades in
CROWN_AT = 7.6                 # "The crown is the knob you turn."
STEM_AT = 9.9                  # "It turns the stem, a steel shaft that can also slide in and out."
STEM_SLIDE = (11.6, 14.2)      # a small pull and back (no contact yet)
WIND_PIN_AT = 15.3             # "On the stem's round part, the winding pinion turns freely."
SLIDING_AT = 20.2              # "On its square part, the sliding pinion slides along the stem ..."
SPIN = (23.0, 27.6)            # the crown turns: the sliding pinion turns with the stem
LEVER_AT = 28.6                # "The setting lever has a pin in a groove on the stem ..."
LEVER_WIGGLE = (31.6, 34.6)
YOKE_AT = 35.3                 # "It moves the yoke, a forked arm that holds the sliding pinion ..."
SPRING_AT = 39.2               # "... and the yoke spring pushes back."
JUMPER_AT = 42.6               # "The setting lever jumper is a spring with notches ..."
SETTING_AT = 49.3              # "The setting wheels lead to the motion work: ..."
MINUTE_AT = 51.9
CANNON_AT = 53.6
HOUR_AT = 56.4
FINAL_HOLD_UNTIL = 60.2        # the last line ends about 59.2 s
FADE_OUT = 1.5

# --- camera and layout ----------------------------------------------
CAM_START = dict(phi=14, theta=-90, zoom=0.86)
RING_KEYLESS = ((2.65, 0.15), 1.25)       # (dial-up model xy, radius), around the keyless works
RING_MOTION = ((-0.55, -0.35), 1.05)      # around the motion work
WIND_COLOR, SET_COLOR = "#ffb54a", "#7fe0a0"

# --- on-screen text --------------------------------------------------
TEXT = dict(
    head=("THE PARTS", "the dial side"),
    keyless="keyless works", motion="motion work", flat="flat view, schematic",
    crown="crown: the knob you turn",
    stem="stem: a steel shaft that turns,\nand slides in and out",
    winding="winding pinion: turns freely\non the stem's round part",
    sliding="sliding pinion: slides along the square part,\nbut always turns with the stem: a clutch",
    lever="setting lever: its pin sits in\na groove on the stem",
    yoke="yoke: a forked arm that\nholds the sliding pinion",
    spring="yoke spring: pushes back",
    jumper="setting lever jumper: a spring\nwith notches, one per position",
    setting="setting wheels",
    minute="minute wheel",
    cannon="cannon pinion: carries\nthe minute hand",
    hour="hour wheel: carries\nthe hour hand",
)
# short name tags that stay on each part once its definition has faded: (name, screen position)
TAGS = dict(
    crown=("crown", (5.45, 3.3)), stem=("stem", (3.7, 3.3)), winding=("winding pinion", (2.45, 1.65)),
    sliding=("sliding pinion", (0.95, 3.3)), lever=("setting lever", (4.6, 1.45)), yoke=("yoke", (1.95, 0.35)),
    spring=("yoke spring", (-0.45, -0.3)), jumper=("setting lever jumper", (5.55, -1.15)),
)
TAG_SCALE, TAG_COLOR = 0.2, GREY_A
# =====================================================================


class Scene02(ThreeDScene):
    def construct(self):
        self.camera.background_color = BG
        self.set_camera_orientation(phi=CAM_START["phi"] * DEGREES, theta=CAM_START["theta"] * DEGREES,
                                    zoom=CAM_START["zoom"], frame_center=ORIGIN)
        self.add_fixed_in_frame_mobjects(vignette())
        wait_until = clock(self)

        # ---------------------------------------------------------- the 3D dial-side tier
        mv = Movement()
        mv.tiers = {"dial": mv.tiers["dial"]}
        mv.rot = [r for r in mv.rot if r[2] == "dial"]
        frozen = ValueTracker(0.0)
        explode, dim = attach_driver(self, mv, {"dial": 0.0}, {"dial": 0.0}, rate=frozen)

        # ---------------------------------------------------------- the flat dial side (hidden at first)
        ds = DialSide(pull=0.0)
        ds.add_to(self)
        kw = ds.kw
        kw.vis.set_value(0.0)

        head = heading(*TEXT["head"]).to_corner(UL, buff=0.45)
        flat_tag = tag(TEXT["flat"], GREY_B, 0.18).next_to(head, DOWN, buff=0.15, aligned_edge=LEFT)
        self.add_fixed_in_frame_mobjects(head, flat_tag)
        self.remove(head, flat_tag)

        cur = curtain()
        self.add_fixed_in_frame_mobjects(cur)
        self.play(cur.animate.set_fill(opacity=0), run_time=FADE_IN)
        self.remove(cur)
        wait_until(FLIP[0])
        self.play(mv.flip.animate.set_value(1.0), FadeIn(head), run_time=FLIP[1] - FLIP[0], rate_func=smooth)

        # rings around the keyless works and the motion work (screen-fixed, camera still)
        wait_until(RINGS_AT)
        rings = VGroup()
        for (xy, r), txt, col in ((RING_KEYLESS, TEXT["keyless"], WIND_COLOR), (RING_MOTION, TEXT["motion"], SET_COLOR)):
            p = mv.world("dial", xy, 0.1)
            c = np.array([*self.camera.project_point(p)[:2], 0.0])
            ring = Circle(radius=r).move_to(c).set_stroke(col, 3)
            lbl = label(txt, 0.3, col, bold=True).next_to(ring, UP, buff=0.1)
            rings.add(VGroup(ring, lbl))
        self.add_fixed_in_frame_mobjects(rings)
        self.play(FadeIn(rings), run_time=0.8)

        # straight down, then crossfade to the flat view
        wait_until(FLAT[0])
        self.move_camera(phi=0, theta=-90 * DEGREES, zoom=1.0, run_time=FLAT[1] - FLAT[0],
                         added_anims=[dim["dial"].animate.set_value(0.0), FadeOut(rings),
                                      kw.vis.animate.set_value(1.0), ds.vis.animate.set_value(1.0),
                                      ds.hands_vis.animate.set_value(1.0), FadeIn(flat_tag)])
        self.remove(mv.group)

        # ---------------------------------------------------------- the parts, one by one
        shown = []

        def name(text, anchor, at, parts=(), color=WHITE, many=False, keep=1, tag_key=None):
            """Fade out older callouts (keeping `keep`), leaving a short name tag on each part that has one,
            then show this callout and light its parts."""
            c = (callouts if many else callout)(text, anchor, at, color=color, scale=0.24)
            old = shown[:-keep] if keep else shown[:]
            for o in old:
                shown.remove(o)
            anims = [FadeOut(o[0]) for o in old] + [*[kw.glow[p].animate.set_value(0.0) for o in old for p in o[1]]]
            for o in old:
                if o[2]:
                    t, pos = TAGS[o[2]]
                    anims.append(FadeIn(callout(t, o[3], pos, color=TAG_COLOR, scale=TAG_SCALE)))
            anims += [FadeIn(c)] + [kw.glow[p].animate.set_value(1.0) for p in parts]
            shown.append((c, parts, tag_key, anchor))
            self.play(*anims, run_time=0.7)

        wait_until(CROWN_AT)
        name(TEXT["crown"], lambda: kw.anchor("crown"), (5.0, 3.35), ("crown",), tag_key="crown")
        wait_until(STEM_AT)
        name(TEXT["stem"], lambda: kw.anchor("stem"), (2.3, 3.35), ("stem",), tag_key="stem")
        wait_until(STEM_SLIDE[0])
        self.play(kw.pull.animate.set_value(0.15), run_time=1.1, rate_func=smooth)
        self.play(kw.pull.animate.set_value(0.0), run_time=1.1, rate_func=smooth)
        wait_until(WIND_PIN_AT)
        name(TEXT["winding"], lambda: kw.anchor("winding_pinion"), (5.35, 1.35), ("winding_pinion",), keep=0,
             tag_key="winding")
        wait_until(SLIDING_AT)
        name(TEXT["sliding"], lambda: kw.anchor("sliding_pinion"), (0.1, 3.35), ("sliding_pinion",), tag_key="sliding")
        wait_until(SPIN[0])
        self.play(ds.crown.animate.increment_value(0.6), run_time=SPIN[1] - SPIN[0], rate_func=smooth)
        wait_until(LEVER_AT)
        name(TEXT["lever"], lambda: kw.anchor("setting_lever"), (5.3, 1.15), ("setting_lever", "stem"), keep=0,
             tag_key="lever")
        wait_until(LEVER_WIGGLE[0])
        self.play(kw.pull.animate.set_value(0.16), run_time=1.4, rate_func=smooth)
        self.play(kw.pull.animate.set_value(0.0), run_time=1.4, rate_func=smooth)
        wait_until(YOKE_AT)
        name(TEXT["yoke"], lambda: kw.anchor("yoke"), (2.5, -1.35), ("yoke",), keep=0, tag_key="yoke")
        wait_until(SPRING_AT)
        name(TEXT["spring"], lambda: kw.anchor("yoke_spring"), (-0.6, -1.45), ("yoke_spring",), tag_key="spring")
        wait_until(JUMPER_AT)
        name(TEXT["jumper"], lambda: kw.anchor("jumper"), (4.9, -1.5), ("jumper",), keep=0, tag_key="jumper")
        wait_until(SETTING_AT)
        name(TEXT["setting"], [ds.gp("setting", 70), ds.gp("inter", 95)], (-0.3, 2.9), color=SET_COLOR, many=True,
             keep=0)
        wait_until(MINUTE_AT)
        name(TEXT["minute"], ds.gp("minute", 125), (-4.6, 2.2), color=SET_COLOR)
        wait_until(CANNON_AT)
        name(TEXT["cannon"], lambda: ds.c0 + RIGHT * 0.3, (-1.4, -1.55), color=SET_COLOR, keep=2)
        wait_until(HOUR_AT)
        name(TEXT["hour"], ds.gp("hour", 200, 0.95), (-6.1, 0.35), color=SET_COLOR, keep=3)

        wait_until(FINAL_HOLD_UNTIL)
        cur.set_fill(opacity=0)
        self.add_fixed_in_frame_mobjects(cur)
        self.play(cur.animate.set_fill(opacity=1), run_time=FADE_OUT)
