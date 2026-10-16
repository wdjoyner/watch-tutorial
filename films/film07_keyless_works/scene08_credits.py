"""Film 7, scene 08 - end credits over the same dimmed keyless works as the
title card, the crown still winding. The last film of the series.

Build:   python build.py 7/scene08_credits
Edit the CREDITS list below; each entry is (role, name).
"""
from manim import *
import prev  # noqa: F401  (first: earlier films' helpers on the path)
from ui6 import write_sfx
from movement import BG, GLOW, FONT_SANS, FONT_SERIF
from scene00_title import backdrop, feathered_backing, CLICK_LEVEL

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds.
# =====================================================================
HEADING = "Learning How Watches Work: The Keyless Works"
CREDITS = [
    ("Produced by", "David Joyner"),
    ("Python code, design, text, and rendering with Manim", "Claude"),
    ("Mathematical reference", "The Mathematics of the Automatic Mechanical Watch (AI and W. David Joyner, 2026)"),
    ("Movement reference, keyless parts, and their order on the stem",
     "ETA 6497-1 Technical Communication (CT 6497-1)"),
    ("Winding wheel tooth counts (16, 36, 60) and setting wheel tooth counts",
     "this series' model; ETA does not publish them"),
    ("Mainspring development (about 8 barrel turns)", "Film 2 of this series, The Power Source"),
]
CLOSING = "Thank you for watching the series."
TOOLS = "Animated with Manim Community  ·  Narration voiced with Kokoro TTS"
NOTICE = ("ETA is a trademark of ETA SA Manufacture Horlogère Suisse.",
          "This film is not affiliated with ETA.")         # one centered line each
NOTICE_COLOR = "#9db4cc"     # muted steel blue, set apart from the credits
NOTICE_SIZE = 0.24

FADE_IN = 1.4
HEADING_FADE = 1.0
CREDIT_FADE = 0.7
CREDIT_GAP = 1.2            # seconds between credits appearing
HOLD = 6.0                  # once everything is on screen
FADE_OUT = 2.0
ORIGIN_XY, SCALE = (-1.3, -0.4), 1.45     # the keyless works sits a little lower and larger than on the title card
# =====================================================================


class Scene08(Scene):
    def construct(self):
        self.camera.background_color = BG
        clicks = backdrop(self, origin=ORIGIN_XY, scale=SCALE)

        heading = Text(HEADING, font=FONT_SERIF, color=GLOW).scale(0.5)
        rule = Line(LEFT, RIGHT).set_stroke(GLOW, 1.5).set_width(heading.width * 0.4)
        entries = []
        for i, (role, name) in enumerate(CREDITS):
            r = Text(role, font=FONT_SANS, color=GREY_B).scale(0.27)
            n = Text(name, font=FONT_SANS, weight=BOLD, color=WHITE).scale(0.46 if i < 2 else 0.32)
            entries.append(VGroup(r, n).arrange(DOWN, buff=0.08))
        closing = Text(CLOSING, font=FONT_SERIF, slant=ITALIC, color=GLOW).scale(0.4)
        tools = Text(TOOLS, font=FONT_SANS, color=GREY_C).scale(0.24)
        notice = VGroup(*[Text(s, font=FONT_SANS, color=NOTICE_COLOR).scale(NOTICE_SIZE) for s in NOTICE])
        notice.arrange(DOWN, buff=0.08)
        block = VGroup(heading, rule, *entries, closing, tools, notice).arrange(DOWN, buff=0.26)
        rule.shift(UP * 0.12)
        tools.shift(DOWN * 0.1)
        notice.next_to(tools, DOWN, buff=0.16)
        if block.height > config.frame_height - 0.8:
            block.scale_to_fit_height(config.frame_height - 0.8)
        if block.width > config.frame_width - 0.9:
            block.scale_to_fit_width(config.frame_width - 0.9)
        block.move_to(ORIGIN)
        backing = feathered_backing(block)
        curtain = FullScreenRectangle().set_fill(BG, 1).set_stroke(width=0)
        self.add(curtain)

        # ---------------------------------------------------------- timeline
        self.play(curtain.animate.set_fill(opacity=0), run_time=FADE_IN, rate_func=smooth)
        self.remove(curtain)
        self.play(FadeIn(backing), FadeIn(heading, shift=DOWN * 0.1), GrowFromCenter(rule), run_time=HEADING_FADE)
        for e in entries:
            self.play(FadeIn(e, shift=UP * 0.1), run_time=CREDIT_FADE)
            self.wait(CREDIT_GAP - CREDIT_FADE)
        self.play(FadeIn(closing, shift=UP * 0.1), run_time=1.0)
        self.wait(0.6)
        self.play(FadeIn(tools), FadeIn(notice), run_time=CREDIT_FADE)
        self.wait(HOLD)

        curtain.set_fill(opacity=0)
        self.add(curtain)
        self.play(curtain.animate.set_fill(opacity=1), run_time=FADE_OUT)
        write_sfx(__file__, [(c, "click", CLICK_LEVEL) for c in clicks])
