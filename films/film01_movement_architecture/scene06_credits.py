"""Scene 06 - end credits over the slowly orbiting, dimmed movement.

Build:   python build.py scene06_credits
Edit the CREDITS list below; each entry is (role, name).
"""
from manim import *
from movement import Movement, attach_driver, vignette, BG, GLOW, FONT_SANS, FONT_SERIF

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds.
# =====================================================================
HEADING = "Learning How Watches Work: Movement Architecture"
CREDITS = [
    ("Produced by", "David Joyner"),
    ("Overall design", "Gemini"),
    ("Design and text", "ChatGPT"),
    ("Python code, design, text, and rendering with Manim", "Claude"),
    ("Movement reference", "ETA 6497-1 / 6498-1 Technical Communication (CT 6497-1, 2007)"),
]
TOOLS = "Animated with Manim Community  ·  Narration voiced with Kokoro TTS"
NOTICE = "ETA is a trademark of ETA SA Manufacture Horlogère Suisse. This film is not affiliated with ETA."
NOTICE_COLOR = "#9db4cc"     # muted steel blue, set apart from the credits
NOTICE_SIZE = 0.24

FADE_IN = 1.4
HEADING_FADE = 1.0
CREDIT_FADE = 0.7
CREDIT_GAP = 1.1            # seconds between credits appearing
HOLD = 5.0                  # once everything is on screen
FADE_OUT = 2.0

TEXT_BACKING = 0.62         # dark panel behind the text
MOVEMENT_DIM = 0.22
ORBIT_RATE = 0.06
CAMERA = dict(phi=40, theta=110, zoom=0.92)
Z = {"dial": 0.00, "engine": 0.30, "top": 0.62}
# =====================================================================


class Scene06(ThreeDScene):
    def construct(self):
        self.camera.background_color = BG
        self.set_camera_orientation(phi=CAMERA["phi"] * DEGREES, theta=CAMERA["theta"] * DEGREES, zoom=CAMERA["zoom"])
        mv = Movement()
        _, dim = attach_driver(self, mv, Z, Z)
        for d in dim.values():
            d.set_value(MOVEMENT_DIM)
        self.add_fixed_in_frame_mobjects(vignette())

        heading = Text(HEADING, font=FONT_SERIF, color=GLOW).scale(0.5)
        rule = Line(LEFT, RIGHT).set_stroke(GLOW, 1.5).set_width(heading.width * 0.4)
        entries = []
        for role, name in CREDITS:
            r = Text(role, font=FONT_SANS, color=GREY_B).scale(0.27)
            n = Text(name, font=FONT_SANS, weight=BOLD, color=WHITE).scale(0.46 if len(name) <= 30 else 0.32)
            entries.append(VGroup(r, n).arrange(DOWN, buff=0.08))
        tools = Text(TOOLS, font=FONT_SANS, color=GREY_C).scale(0.24)
        notice = Text(NOTICE, font=FONT_SANS, color=NOTICE_COLOR).scale(NOTICE_SIZE)
        block = VGroup(heading, rule, *entries, tools, notice).arrange(DOWN, buff=0.32)
        rule.shift(UP * 0.12)
        tools.shift(DOWN * 0.15)
        notice.next_to(tools, DOWN, buff=0.16)
        if block.height > config.frame_height - 0.8:
            block.scale_to_fit_height(config.frame_height - 0.8)
        backing = VGroup(*[RoundedRectangle(corner_radius=0.3 + 0.12 * k, width=block.width + 0.6 + 0.25 * k,
                                            height=block.height + 0.3 + 0.25 * k)
                           .set_fill(BG, 1 - (1 - TEXT_BACKING) ** (1 / 8)).set_stroke(width=0)
                           for k in range(8)]).move_to(block)          # feathered: darkest in the middle
        block = VGroup(backing, *block)
        curtain = FullScreenRectangle().set_fill(BG, 1).set_stroke(width=0)
        self.add_fixed_in_frame_mobjects(block, curtain)
        self.remove(block)

        # ---------------------------------------------------------- timeline
        self.begin_ambient_camera_rotation(rate=ORBIT_RATE)
        self.play(curtain.animate.set_fill(opacity=0), run_time=FADE_IN, rate_func=smooth)
        self.play(FadeIn(block[0]), FadeIn(heading, shift=DOWN * 0.1), GrowFromCenter(rule), run_time=HEADING_FADE)
        for e in entries:
            self.play(FadeIn(e, shift=UP * 0.1), run_time=CREDIT_FADE)
            self.wait(CREDIT_GAP - CREDIT_FADE)
        self.play(FadeIn(tools), FadeIn(notice), run_time=CREDIT_FADE)
        self.wait(HOLD)

        self.remove(curtain)
        self.add_fixed_in_frame_mobjects(curtain)        # re-add so it sits above the text
        self.play(curtain.animate.set_fill(opacity=1), run_time=FADE_OUT)
