"""Film 7, scene 01 - "Where we are": a short recap of the series so far.

The energy chain as three blocks, each tagged with its film: the mainspring
stores it (Film 2), the gear train carries it (Film 3), the escapement and the
balance meter it out (Films 4-6). Then the part you touch: the crown. Old
watches needed two keys, one to wind and one to set the hands; the keyless
works does both with the crown.

Build (render + voice + mux):   python build.py 7/scene01_recap
Render only (quick preview):    PYTHONPATH=.:films/film07_keyless_works manim -ql films/film07_keyless_works/scene01_recap.py Scene01
Narration lines and their start times live in scene01_recap.voice.txt.
"""
from manim import *
import prev  # noqa: F401  (first: earlier films' helpers on the path)
from movement import vignette, BG, GLOW, STEEL, STEEL_HI, STEEL_DK, BRASS, BRASS_HI
from ui import label, heading, curtain, clock

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds.
# Keep the timeline roughly in step with scene01_recap.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 1.0
HEAD_AT = 1.0                  # "Over six films, we followed the energy through a watch."
BLOCK_AT = (5.7, 7.6, 9.6)     # "The mainspring stores it. The gear train carries it. The escapement ..."
TOUCH_AT = 14.4                # "One part is left: the part you touch."
KEYS_AT = 18.0                 # "Old watches needed a key to wind them, and another to set the hands."
SET_KEY_AT = 20.6
KEYLESS_AT = 23.5              # "The keyless works does both, with the crown alone."
FINAL_HOLD_UNTIL = 29.2        # the last line ends about 28.3 s
FADE_OUT = 1.5

# --- layout ----------------------------------------------------------
CHAIN_Y = 1.15
BLOCK_X = (-2.6, 0.9, 4.4)
BLOCK_W, BLOCK_H = 2.9, 1.25
CROWN_XY = (-5.7, CHAIN_Y, 0)
WIND_COLOR, SET_COLOR = "#ffb54a", "#7fe0a0"

# --- on-screen text --------------------------------------------------
TEXT = dict(
    head=("WHERE WE ARE", "six films, one path for the energy"),
    blocks=[("mainspring", "stores the energy", "Film 2"),
            ("gear train", "carries it", "Film 3"),
            ("escapement and balance", "meter it out, one beat at a time", "Films 4, 5, 6")],
    crown="crown", touch="the part you touch",
    key_wind="a key to wind", key_set="a key to set the hands",
    keyless="the keyless works: both, with the crown",
)
# =====================================================================


def key_icon(color, scale=1.0):
    """A watch key, drawn simply: a ring bow, a shaft and a hollow square pipe."""
    bow = Annulus(inner_radius=0.16, outer_radius=0.30).set_fill(color, 1).set_stroke(width=0)
    shaft = Rectangle(width=0.95, height=0.1).set_fill(color, 1).set_stroke(width=0).next_to(bow, RIGHT, buff=-0.04)
    pipe = Rectangle(width=0.24, height=0.24).set_fill(BG, 1).set_stroke(color, 4).next_to(shaft, RIGHT, buff=0)
    return VGroup(bow, shaft, pipe).scale(scale)


def crown_icon(scale=1.0):
    body = RoundedRectangle(width=0.55, height=1.0, corner_radius=0.08).set_fill(STEEL, 1).set_stroke(STEEL_HI, 1.5)
    ridges = VGroup(*[Line([-0.22, y, 0], [0.22, y, 0]).set_stroke(STEEL_DK, 2) for y in np.linspace(-0.38, 0.38, 8)])
    stem = Rectangle(width=0.9, height=0.12).set_fill(STEEL_HI, 1).set_stroke(width=0).next_to(body, RIGHT, buff=0)
    return VGroup(stem, body, ridges).scale(scale)


class Scene01(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.add(vignette())
        wait_until = clock(self)

        head = heading(*TEXT["head"]).to_corner(UL, buff=0.45)
        blocks = VGroup()
        for x, (name, job, film) in zip(BLOCK_X, TEXT["blocks"]):
            box = RoundedRectangle(width=BLOCK_W, height=BLOCK_H, corner_radius=0.12).set_stroke(GREY_B, 1.4)
            box.set_fill(BG, 0.9)
            t = VGroup(label(name, 0.27, WHITE, bold=True), label(job, 0.21, GREY_B)).arrange(DOWN, buff=0.12)
            f = label(film, 0.22, GLOW).next_to(box, DOWN, buff=0.14)
            blocks.add(VGroup(box, t, f).move_to([x, CHAIN_Y - 0.1, 0]))
        arrows = VGroup(*[Arrow(blocks[i][0].get_right(), blocks[i + 1][0].get_left(), buff=0.06, stroke_width=3,
                                tip_length=0.14, color=WIND_COLOR) for i in range(2)])

        crown = crown_icon(1.1).move_to(CROWN_XY)
        crown_lbl = label(TEXT["crown"], 0.28, WHITE, bold=True).next_to(crown, UP, buff=0.2)
        touch = label(TEXT["touch"], 0.24, GLOW).next_to(crown, DOWN, buff=0.25)
        c_arrow = Arrow(crown.get_right(), blocks[0][0].get_left(), buff=0.12, stroke_width=3, tip_length=0.14,
                        color=WIND_COLOR)

        k_wind = VGroup(key_icon(WIND_COLOR), label(TEXT["key_wind"], 0.24, WIND_COLOR))
        k_wind[1].next_to(k_wind[0], RIGHT, buff=0.3)
        k_set = VGroup(key_icon(SET_COLOR), label(TEXT["key_set"], 0.24, SET_COLOR))
        k_set[1].next_to(k_set[0], RIGHT, buff=0.3)
        keys = VGroup(k_wind, k_set).arrange(DOWN, aligned_edge=LEFT, buff=0.35).move_to([-2.4, -1.25, 0])
        cross = VGroup(Line(keys.get_corner(UL), keys.get_corner(DR)), Line(keys.get_corner(DL), keys.get_corner(UR)))
        cross.set_stroke(GREY_B, 2, 0.7)
        keyless = label(TEXT["keyless"], 0.32, GLOW, bold=True).move_to([2.9, -1.25, 0])
        k_arrow = Arrow(keys.get_right() + RIGHT * 0.15, keyless.get_left(), buff=0.15, stroke_width=3, tip_length=0.14,
                        color=GLOW)

        cur = curtain()
        self.add(cur)
        self.play(cur.animate.set_fill(opacity=0), run_time=FADE_IN)
        self.remove(cur)
        wait_until(HEAD_AT)
        self.play(FadeIn(head), run_time=0.8)
        for i, t in enumerate(BLOCK_AT):
            wait_until(t)
            anims = [FadeIn(blocks[i], shift=RIGHT * 0.15)]
            if i:
                anims.append(GrowArrow(arrows[i - 1]))
            self.play(*anims, run_time=0.8)

        wait_until(TOUCH_AT)
        self.play(FadeIn(crown, shift=RIGHT * 0.2), FadeIn(crown_lbl), run_time=0.8)
        self.play(GrowArrow(c_arrow), FadeIn(touch), run_time=0.7)

        wait_until(KEYS_AT)
        self.play(FadeIn(k_wind, shift=UP * 0.1), run_time=0.7)
        wait_until(SET_KEY_AT)
        self.play(FadeIn(k_set, shift=UP * 0.1), run_time=0.7)
        wait_until(KEYLESS_AT)
        self.play(Create(cross), run_time=0.6)
        self.play(GrowArrow(k_arrow), FadeIn(keyless, shift=RIGHT * 0.1),
                  crown[1].animate.set_stroke(GLOW, 3), run_time=0.9)

        wait_until(FINAL_HOLD_UNTIL)
        cur.set_fill(opacity=0)
        self.add(cur)
        self.play(cur.animate.set_fill(opacity=1), run_time=FADE_OUT)
