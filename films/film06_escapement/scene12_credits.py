"""Film 6, scene 12 - end credits over the same slowed, dimmed lever escapement
as the title card.

Build:   python build.py 6/scene12_credits
Edit the CREDITS list below; each entry is (role, name).
"""
from manim import *
import prev  # noqa: F401  (first: Film 4 and 5 helpers on the path)
from ui6 import write_ticks
from movement import BG, GLOW, FONT_SANS, FONT_SERIF
from scene00_title import backdrop, feathered_backing

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds.
# =====================================================================
HEADING = "Learning How Watches Work: The Escapement"
CREDITS = [
    ("Produced by", "David Joyner"),
    ("Python code, design, text, and rendering with Manim", "Claude"),
    ("Mathematical reference", "The Mathematics of the Automatic Mechanical Watch (AI and W. David Joyner, 2026)"),
    ("Escapement model, timings, and energy audit", "G. Petrangeli, Mathematics of a Watch Escapement (2017)"),
    ("Airy's theorem", "G. B. Airy, Trans. Cambridge Phil. Soc. 3 (1830, read 1826)"),
    ("Mainspring torque curve", "Seiko Epson, US Patent 6,431,746 B1 (2002), FIG. 8"),
    ("The torsiometer", "Horopedia, “The torsiometer”"),
    ("Movement reference and lift angle", "ETA 6497-1 Technical Communication (CT 6497-1)"),
    ("Normal lift angles", "WOSTEP, The Theory of Horology"),
    ("Balance losses, amplitudes, and Q", "representative values from the chapter; ETA does not publish them"),
]
TOOLS = "Animated with Manim Community  ·  Narration voiced with Kokoro TTS"
NOTICE = ("ETA is a trademark of ETA SA Manufacture Horlogère Suisse; Seiko is a trademark of its owner.",
          "This film is not affiliated with either.")         # one centered line each
NOTICE_COLOR = "#9db4cc"     # muted steel blue, set apart from the credits
NOTICE_SIZE = 0.24

FADE_IN = 1.4
HEADING_FADE = 1.0
CREDIT_FADE = 0.7
CREDIT_GAP = 1.1            # seconds between credits appearing
HOLD = 6.0                  # once everything is on screen
FADE_OUT = 2.0
CENTER, SCALE = (0.0, -2.2), 2.6     # the escapement sits a little lower and larger than on the title card
# =====================================================================


class Scene12(Scene):
    def construct(self):
        self.camera.background_color = BG
        esc = backdrop(self, center=CENTER, scale=SCALE)

        heading = Text(HEADING, font=FONT_SERIF, color=GLOW).scale(0.5)
        rule = Line(LEFT, RIGHT).set_stroke(GLOW, 1.5).set_width(heading.width * 0.4)
        entries = []
        for i, (role, name) in enumerate(CREDITS):
            r = Text(role, font=FONT_SANS, color=GREY_B).scale(0.27)
            n = Text(name, font=FONT_SANS, weight=BOLD, color=WHITE).scale(0.46 if i < 2 else 0.32)
            entries.append(VGroup(r, n).arrange(DOWN, buff=0.08))
        tools = Text(TOOLS, font=FONT_SANS, color=GREY_C).scale(0.24)
        notice = VGroup(*[Text(s, font=FONT_SANS, color=NOTICE_COLOR).scale(NOTICE_SIZE) for s in NOTICE])
        notice.arrange(DOWN, buff=0.08)
        block = VGroup(heading, rule, *entries, tools, notice).arrange(DOWN, buff=0.26)
        rule.shift(UP * 0.12)
        tools.shift(DOWN * 0.15)
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
        self.play(FadeIn(tools), FadeIn(notice), run_time=CREDIT_FADE)
        self.wait(HOLD)

        curtain.set_fill(opacity=0)
        self.add(curtain)
        self.play(curtain.animate.set_fill(opacity=1), run_time=FADE_OUT)
        write_ticks(__file__, [t for t, k in esc.events if k == "drop"])
