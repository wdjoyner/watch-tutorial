"""Film 2, scene 00 - title card over the slowly orbiting mainspring barrel,
opened up along its axis (drum, spring, arbor, cover) and dimmed.

Build:   python build.py 2/scene00_title
No narration file: the title plays over the tick track only. To add a spoken
title, create scene00_title.voice.txt (same format as the other scenes).
"""
from manim import *
from movement import vignette, BG, GLOW, FONT_SANS, FONT_SERIF
from barrel import BarrelModel

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds.
# =====================================================================
KICKER = "LEARNING HOW WATCHES WORK"
TITLE = "The Power Source"
TAGLINE = "the mainspring and barrel of a hand-wound movement"

FADE_IN = 1.6
KICKER_AT, TITLE_AT, TAGLINE_AT = 1.8, 2.8, 4.4
TEXT_FADE = 1.2
HOLD_UNTIL = 8.6            # everything is on screen until here
FADE_OUT = 1.6

TEXT_BACKING = 0.62         # dark panel behind the text
BARREL_DIM = 0.55           # opacity of the dark veil over the barrel (0 = none)
EXPLODE = 0.55              # how far the barrel is opened up (0 closed, 1 fully exploded)
Z0 = -1.35                  # drops the barrel so its opened stack is centered on screen
ORBIT_RATE = 0.06           # radians per second
CAMERA = dict(phi=58, theta=-70, zoom=1.35)
# =====================================================================


def backdrop(scene, theta):
    """The opened barrel, a dark veil over it, and the vignette."""
    scene.set_camera_orientation(phi=CAMERA["phi"] * DEGREES, theta=theta * DEGREES, zoom=CAMERA["zoom"])
    bm = BarrelModel(center=ORIGIN, z0=Z0)
    bm.explode.set_value(EXPLODE)
    scene.add(bm)
    veil = FullScreenRectangle().set_fill(BG, BARREL_DIM).set_stroke(width=0)
    scene.add_fixed_in_frame_mobjects(veil, vignette())
    return bm


def feathered_backing(block):
    return VGroup(*[RoundedRectangle(corner_radius=0.3 + 0.12 * k, width=block.width + 0.6 + 0.25 * k,
                                     height=block.height + 0.3 + 0.25 * k)
                    .set_fill(BG, 1 - (1 - TEXT_BACKING) ** (1 / 8)).set_stroke(width=0)
                    for k in range(8)]).move_to(block)          # darkest in the middle


class Scene00(ThreeDScene):
    def construct(self):
        self.camera.background_color = BG
        backdrop(self, CAMERA["theta"])

        kicker = Text(KICKER, font=FONT_SANS, weight=BOLD, color=GREY_B).scale(0.34)
        title = Text(TITLE, font=FONT_SERIF, color=GLOW).scale(1.05)
        rule = Line(LEFT, RIGHT).set_stroke(GLOW, 2).set_width(title.width * 0.55)
        tagline = Text(TAGLINE, font=FONT_SANS, color=GREY_B).scale(0.3)
        block = VGroup(kicker, title, rule, tagline).arrange(DOWN, buff=0.28)
        block = VGroup(feathered_backing(block), *block)
        curtain = FullScreenRectangle().set_fill(BG, 1).set_stroke(width=0)
        self.add_fixed_in_frame_mobjects(block, curtain)
        self.remove(block)

        # ---------------------------------------------------------- timeline
        self.begin_ambient_camera_rotation(rate=ORBIT_RATE)
        self.play(curtain.animate.set_fill(opacity=0), run_time=FADE_IN, rate_func=smooth)
        t = FADE_IN

        def at(when, *anims, run_time=TEXT_FADE):
            nonlocal t
            if when > t:
                self.wait(when - t)
                t = when
            self.play(*anims, run_time=run_time)
            t += run_time

        at(KICKER_AT, FadeIn(block[0]), FadeIn(kicker, shift=DOWN * 0.15), run_time=0.8)
        at(TITLE_AT, FadeIn(title, scale=0.96), GrowFromCenter(rule))
        at(TAGLINE_AT, FadeIn(tagline, shift=UP * 0.1), run_time=0.8)
        self.wait(max(0, HOLD_UNTIL - t))

        self.remove(curtain)
        self.add_fixed_in_frame_mobjects(curtain)        # re-add so it sits above the text
        self.play(curtain.animate.set_fill(opacity=1), run_time=FADE_OUT)
