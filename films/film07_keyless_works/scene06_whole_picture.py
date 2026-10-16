"""Film 7, scene 06 - "The whole picture": the functional diagram, winding and setting only.

The crown turns the stem; the keyless works sends that turning one of two ways.
Pushed in (amber): the winding works winds the mainspring in the barrel, which
drives the gear train. Pulled out (green): the motion work turns the hands. The
gear train also turns the motion work, through the cannon pinion's friction fit
(dashed). Each box lists its parts, so the diagram doubles as the reference
text's table of parts by function. Last, the two things the crown supplies:
energy (amber) and information (green).

Build (render + voice + mux):   python build.py 7/scene06_whole_picture
Render only (quick preview):    PYTHONPATH=.:films/film07_keyless_works manim -ql films/film07_keyless_works/scene06_whole_picture.py Scene06
Narration lines and their start times live in scene06_whole_picture.voice.txt.
"""
from manim import *
import prev  # noqa: F401  (first: earlier films' helpers on the path)
from movement import vignette, BG, GLOW
from ui import label, heading, tag, curtain, clock

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds.
# Keep the timeline roughly in step with scene06_whole_picture.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 1.0
HEAD_AT = 1.0                  # "Put it all together."
INPUT_AT = 3.3                 # "The crown turns the stem, and the keyless works sends that turning one of two ways."
WIND_AT = 9.6                  # "Pushed in, it goes through the winding works to the mainspring."
SET_AT = 14.2                  # "Pulled out, it goes through the motion work to the hands."
TWO_AT = 18.5                  # "So the crown supplies two different things."
ENERGY_AT = 22.0               # "Pushed in, it supplies energy, which the barrel stores and the train spends."
TRAIN_AT = 24.6
INFO_AT = 27.9                 # "Pulled out, it supplies information: the time you want the hands to show."
LAST_AT = 33.4                 # "Sliding the stem picks the destination; turning it drives it."
FINAL_HOLD_UNTIL = 38.6        # the last line ends about 37.7 s
FADE_OUT = 1.5

# --- layout ----------------------------------------------------------
WIND_COLOR, SET_COLOR = "#ffb54a", "#7fe0a0"
TOP_Y, MID_Y, BOT_Y = 1.75, 0.2, -1.35
X = dict(crown=-5.85, keyless=-3.05, winding=0.45, barrel=3.15, train=5.75, motion=0.45, hands=3.15)

# --- on-screen text --------------------------------------------------
TEXT = dict(
    head=("THE WHOLE PICTURE", "winding and setting (the 6497 has no date)"),
    boxes=dict(crown=("crown", "turned by hand"),
               keyless=("keyless works", "stem, winding pinion,\nsliding pinion, setting lever,\nyoke and spring, jumper,\nsetting wheels"),
               winding=("winding works", "crown wheel,\nratchet wheel, click"),
               barrel=("barrel", "arbor, mainspring,\ndrum"),
               train=("gear train", "to the escapement\nand balance"),
               motion=("motion work", "minute wheel,\ncannon pinion,\nhour wheel"),
               hands=("hands", "the time shown")),
    pushed="pushed in", pulled="pulled out", friction="friction fit",
    energy="ENERGY", info="INFORMATION",
    last="sliding the stem picks the destination;  turning it drives it",
)
# =====================================================================


def node(key, color=GREY_B, w=2.05, h=1.25):
    title, parts = TEXT["boxes"][key]
    t = VGroup(label(title, 0.27, WHITE, bold=True), label(parts, 0.19, GREY_B)).arrange(DOWN, buff=0.1)
    box = RoundedRectangle(width=max(w, t.width + 0.3), height=max(h, t.height + 0.3), corner_radius=0.1)
    box.set_stroke(color, 1.4).set_fill(BG, 0.92)
    return VGroup(box, t)


def link(a, b, color, dashed=False, start=None, end=None):
    s = start if start is not None else a[0].get_right()
    e = end if end is not None else b[0].get_left()
    arr = Arrow(s, e, buff=0.08, stroke_width=3.2, tip_length=0.15, color=color)
    if dashed:
        arr = DashedVMobject(arr, num_dashes=14)
    return arr


class Scene06(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.add(vignette())
        wait_until = clock(self)

        head = heading(*TEXT["head"]).to_corner(UL, buff=0.45)
        n = {k: node(k) for k in X}
        n["keyless"] = node("keyless", GLOW, w=2.6, h=2.2)
        for k, x in X.items():
            y = {"crown": MID_Y, "keyless": MID_Y, "winding": TOP_Y, "barrel": TOP_Y, "train": TOP_Y,
                 "motion": BOT_Y, "hands": BOT_Y}[k]
            n[k].move_to([x, y, 0])
        a_in = link(n["crown"], n["keyless"], GLOW)
        a_wind = link(n["keyless"], n["winding"], WIND_COLOR, start=n["keyless"][0].get_right() + UP * 0.45)
        a_bar = link(n["winding"], n["barrel"], WIND_COLOR)
        a_train = link(n["barrel"], n["train"], WIND_COLOR)
        a_set = link(n["keyless"], n["motion"], SET_COLOR, start=n["keyless"][0].get_right() + DOWN * 0.45)
        a_hands = link(n["motion"], n["hands"], SET_COLOR)
        a_fric = link(n["train"], n["motion"], GREY_B, dashed=True, start=n["train"][0].get_bottom(),
                      end=n["motion"][0].get_right() + UP * 0.25)
        fric = label(TEXT["friction"], 0.2, GREY_B).next_to(a_fric.get_center(), RIGHT, buff=0.12)
        pushed = label(TEXT["pushed"], 0.22, WIND_COLOR).next_to(a_wind.get_center(), UL, buff=0.04)
        pulled = label(TEXT["pulled"], 0.22, SET_COLOR).next_to(a_set.get_center(), DL, buff=0.04)
        energy = tag(TEXT["energy"], WIND_COLOR, 0.28).next_to(n["barrel"], UP, buff=0.2)
        info = tag(TEXT["info"], SET_COLOR, 0.28).next_to(n["hands"], RIGHT, buff=0.35)
        last = label(TEXT["last"], 0.3, GLOW, bold=True).move_to([0, -2.4, 0])

        cur = curtain()
        self.add(cur)
        self.play(cur.animate.set_fill(opacity=0), run_time=FADE_IN)
        self.remove(cur)
        wait_until(HEAD_AT)
        self.play(FadeIn(head), run_time=0.8)
        wait_until(INPUT_AT)
        self.play(FadeIn(n["crown"], shift=RIGHT * 0.15), run_time=0.7)
        self.play(GrowArrow(a_in), FadeIn(n["keyless"], shift=RIGHT * 0.15), run_time=0.9)
        wait_until(WIND_AT)
        self.play(GrowArrow(a_wind), FadeIn(pushed), FadeIn(n["winding"], shift=RIGHT * 0.1), run_time=0.9)
        self.play(GrowArrow(a_bar), FadeIn(n["barrel"], shift=RIGHT * 0.1), run_time=0.8)
        wait_until(SET_AT)
        self.play(GrowArrow(a_set), FadeIn(pulled), FadeIn(n["motion"], shift=RIGHT * 0.1), run_time=0.9)
        self.play(GrowArrow(a_hands), FadeIn(n["hands"], shift=RIGHT * 0.1), run_time=0.8)
        wait_until(TWO_AT)
        self.play(n["crown"][0].animate.set_stroke(GLOW, 3), run_time=0.6)
        wait_until(ENERGY_AT)
        self.play(FadeIn(energy, shift=DOWN * 0.1),
                  *[m[0].animate.set_stroke(WIND_COLOR, 2.4) for m in (n["winding"], n["barrel"])], run_time=0.8)
        wait_until(TRAIN_AT)
        self.play(GrowArrow(a_train), FadeIn(n["train"], shift=RIGHT * 0.1), run_time=0.8)
        self.play(Create(a_fric), FadeIn(fric), run_time=0.9)
        wait_until(INFO_AT)
        self.play(FadeIn(info, shift=LEFT * 0.1),
                  *[m[0].animate.set_stroke(SET_COLOR, 2.4) for m in (n["motion"], n["hands"])], run_time=0.8)
        wait_until(LAST_AT)
        self.play(FadeIn(last, shift=UP * 0.1), run_time=0.9)

        wait_until(FINAL_HOLD_UNTIL)
        cur.set_fill(opacity=0)
        self.add(cur)
        self.play(cur.animate.set_fill(opacity=1), run_time=FADE_OUT)
