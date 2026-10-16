"""Film 7, scene 00 - title card over the keyless works close-up of keyless.py,
dimmed, with the crown turning slowly to wind (one click per ratchet tooth).

Build:   python build.py 7/scene00_title
No narration file: the title plays over the tick track and the winding clicks
(the scene writes scene00_title.sfx.txt on every render). To add a spoken
title, create scene00_title.voice.txt (same format as the other scenes).
The credits (scene08_credits.py) reuse backdrop() and feathered_backing().
"""
from manim import *
import prev  # noqa: F401  (first: earlier films' helpers on the path)
from keyless import KeylessWorks
from ui6 import write_sfx
from movement import vignette, BG, GLOW, FONT_SANS, FONT_SERIF
import figures

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds.
# =====================================================================
KICKER = "LEARNING HOW WATCHES WORK"
TITLE = "The Keyless Works"
TAGLINE = "one crown to wind the spring and set the hands"

FADE_IN = 1.6
KICKER_AT, TITLE_AT, TAGLINE_AT = 1.8, 2.8, 4.4
TEXT_FADE = 1.2
HOLD_UNTIL = 8.6            # everything is on screen until here
FADE_OUT = 1.6

TEXT_BACKING = 0.62         # dark panel behind the text
DIM = 0.5                   # opacity of the keyless works behind the text (1 = full)
ORIGIN_XY, SCALE = (-1.85, -0.2), 1.3    # the close-up's place and size on screen
CROWN_SPEED = 0.25          # crown turns per second (winding)
CLICKS_PER_TURN = figures.CLICKS_PER_CROWN_TURN    # one click per ratchet tooth, in this model
CLICK_LEVEL = 0.6
# =====================================================================


def backdrop(scene, origin=ORIGIN_XY, scale=SCALE, speed=CROWN_SPEED):
    """The keyless works, dimmed, the crown turning to wind. Returns the list of click times."""
    kw = KeylessWorks(origin=origin, scale=scale)
    kw.vis.set_value(DIM)
    scene.add(kw, *kw.trackers())
    clicks, clock = [], {"t": 0.0, "n": 0}

    def drive(m, dt):
        clock["t"] += dt
        kw.spin.increment_value(speed * TAU * dt)
        n = int(kw.spin.get_value() / TAU * CLICKS_PER_TURN)
        if n > clock["n"]:
            clock["n"] = n
            clicks.append(clock["t"])
    scene.add(Mobject().add_updater(drive))
    scene.add(vignette())
    return clicks


def feathered_backing(block):
    return VGroup(*[RoundedRectangle(corner_radius=0.3 + 0.12 * k, width=block.width + 0.6 + 0.25 * k,
                                     height=block.height + 0.3 + 0.25 * k)
                    .set_fill(BG, 1 - (1 - TEXT_BACKING) ** (1 / 8)).set_stroke(width=0)
                    for k in range(8)]).move_to(block)          # darkest in the middle


class Scene00(Scene):
    def construct(self):
        self.camera.background_color = BG
        clicks = backdrop(self)

        kicker = Text(KICKER, font=FONT_SANS, weight=BOLD, color=GREY_B).scale(0.34)
        title = Text(TITLE, font=FONT_SERIF, color=GLOW).scale(1.05)
        rule = Line(LEFT, RIGHT).set_stroke(GLOW, 2).set_width(title.width * 0.55)
        tagline = Text(TAGLINE, font=FONT_SANS, color=GREY_B).scale(0.3)
        block = VGroup(kicker, title, rule, tagline).arrange(DOWN, buff=0.28).move_to(UP * 1.9)
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
        write_sfx(__file__, [(c, "click", CLICK_LEVEL) for c in clicks])
