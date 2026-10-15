"""Film 6, scene 00 - title card over the Swiss lever close-up of lever.py,
running slowed and dimmed, ticking at each drop.

Build:   python build.py 6/scene00_title
No narration file: the title plays over the tick track only. To add a spoken
title, create scene00_title.voice.txt (same format as the other scenes).
The credits (scene12_credits.py) reuse backdrop() and feathered_backing().
"""
from manim import *
import prev  # noqa: F401  (first: Film 4 and 5 helpers on the path)
from lever import LeverEscapement
from ui6 import write_ticks
from movement import vignette, BG, GLOW, FONT_SANS, FONT_SERIF
from ui import tag

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds.
# =====================================================================
KICKER = "LEARNING HOW WATCHES WORK"
TITLE = "The Escapement"
TAGLINE = "how the balance gets its kicks, and what they cost"

FADE_IN = 1.6
KICKER_AT, TITLE_AT, TAGLINE_AT = 1.8, 2.8, 4.4
TEXT_FADE = 1.2
HOLD_UNTIL = 8.6            # everything is on screen until here
FADE_OUT = 1.6

TEXT_BACKING = 0.62         # dark panel behind the text
DIM = 0.5                   # opacity of the escapement behind the text (1 = full)
CENTER, SCALE, RIM_R = (0.0, -1.6), 2.4, 0.95     # the close-up's place and size on screen
RATE = 1 / 4                # slow motion: 4x
SLOW_TAG = "slowed 4×"
# =====================================================================


def backdrop(scene, center=CENTER, scale=SCALE, rate=RATE):
    """The lever escapement, running slowed and dimmed, with the vignette and a slow-motion tag."""
    esc = LeverEscapement(center=center, scale=scale, rim_r=RIM_R)
    esc.rate.set_value(rate)
    esc.lift_rate.set_value(1.0)
    esc.vis.set_value(DIM)
    esc.skipped_drops = True     # at 4x the drop lasts less than a frame
    esc.attach(scene)
    scene.add(vignette())
    scene.add(tag(SLOW_TAG, GLOW, 0.18).set_opacity(0.7).to_corner(DR, buff=0.35))
    return esc


def feathered_backing(block):
    return VGroup(*[RoundedRectangle(corner_radius=0.3 + 0.12 * k, width=block.width + 0.6 + 0.25 * k,
                                     height=block.height + 0.3 + 0.25 * k)
                    .set_fill(BG, 1 - (1 - TEXT_BACKING) ** (1 / 8)).set_stroke(width=0)
                    for k in range(8)]).move_to(block)          # darkest in the middle


class Scene00(Scene):
    def construct(self):
        self.camera.background_color = BG
        esc = backdrop(self)

        kicker = Text(KICKER, font=FONT_SANS, weight=BOLD, color=GREY_B).scale(0.34)
        title = Text(TITLE, font=FONT_SERIF, color=GLOW).scale(1.05)
        rule = Line(LEFT, RIGHT).set_stroke(GLOW, 2).set_width(title.width * 0.55)
        tagline = Text(TAGLINE, font=FONT_SANS, color=GREY_B).scale(0.3)
        block = VGroup(kicker, title, rule, tagline).arrange(DOWN, buff=0.28).move_to(UP * 1.2)
        backing = feathered_backing(block)
        curtain = FullScreenRectangle().set_fill(BG, 1).set_stroke(width=0)
        self.add(curtain)

        # ---------------------------------------------------------- timeline
        self.play(curtain.animate.set_fill(opacity=0), run_time=FADE_IN, rate_func=smooth)
        self.remove(curtain)
        t = FADE_IN

        def at(when, *anims, run_time=TEXT_FADE):
            nonlocal t
            if when > t:
                self.wait(when - t)
                t = when
            self.play(*anims, run_time=run_time)
            t += run_time

        at(KICKER_AT, FadeIn(backing), FadeIn(kicker, shift=DOWN * 0.15), run_time=0.8)
        at(TITLE_AT, FadeIn(title, scale=0.96), GrowFromCenter(rule))
        at(TAGLINE_AT, FadeIn(tagline, shift=UP * 0.1), run_time=0.8)
        self.wait(max(0, HOLD_UNTIL - t))

        curtain.set_fill(opacity=0)
        self.add(curtain)
        self.play(curtain.animate.set_fill(opacity=1), run_time=FADE_OUT)
        write_ticks(__file__, [tt for tt, k in esc.events if k == "drop"])
