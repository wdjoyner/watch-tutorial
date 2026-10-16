"""Film 7, scene 07 - "Series Epilogue: From the Crown to the Hands".

One slow pass through the running 3D movement (Film 1's model, in real time),
from the crown to the hands, naming the film that covered each stop. The tiers
open (Film 1), the camera visits the keyless works at the crown (Film 7), the
barrel (Film 2), the gear train (Film 3), the escapement (Film 6) and the
balance (Films 4 and 5), then the dial tier turns over to show the motion work
that turns the hands. The camera holds still while each film's card is read.
At the end the seven films are listed in order.

Build (render + voice + mux):   python build.py 7/scene07_crown_to_hands
Render only (quick preview):    PYTHONPATH=.:films/film07_keyless_works manim -ql films/film07_keyless_works/scene07_crown_to_hands.py Scene07
Narration lines and their start times live in scene07_crown_to_hands.voice.txt.
"""
from manim import *
import prev  # noqa: F401  (first: earlier films' helpers on the path)
from movement import Movement, attach_driver, vignette, camera_move, cue, P, BG, GLOW, FONT_SANS
from ui import label, heading, curtain, clock

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds.
# Keep the timeline roughly in step with scene07_crown_to_hands.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 1.4
HEAD_AT = 1.0                  # "This is the last film in the series ..."
TIERS = (7.0, 10.0)            # "Film one laid out its three tiers."
STOPS = [                      # (move start, move end, card time, stop name)
    (10.3, 12.6, 10.8, "crown"),        # "Here at the crown is the keyless works."
    (14.2, 16.6, 15.0, "barrel"),       # "Winding feeds the barrel ...: Film two."
    (20.2, 22.4, 20.8, "train"),        # "The gear train carries it, wheel by wheel: Film three."
    (24.8, 27.2, 25.6, "escapement"),   # "At the end of the train, the escapement ...: Film six."
    (32.5, 34.6, 33.0, "balance"),      # "The balance and hairspring set the pace: Film four."
]
ISO_AT = 36.7                  # "Film five asked why that pace drifts with the size of the swing."
DIAL = (42.1, 45.6)            # "Back under the dial, the motion work turns the hands."
WIDE = (46.4, 50.0)            # "From the crown to the hands, that is how a watch works."
LIST_AT = 47.2
FINAL_HOLD_UNTIL = 53.6        # the last line ends about 49.9 s; the list stays a while
FADE_OUT = 2.0

# --- tiers and camera ------------------------------------------------
Z_ASSEMBLED = {"dial": 0.00, "engine": 0.30, "top": 0.62}
Z_EXPLODED = {"dial": -1.3, "engine": 0.0, "top": 1.3}
CAM0 = dict(phi=48, theta=-62, zoom=0.95)
CAM_STOP = dict(phi=44, theta=-70, zoom=1.9)
CAM_WIDE = dict(phi=50, theta=-62, zoom=0.9)
CAM_DIAL = dict(phi=30, theta=-80, zoom=1.35)
TARGET = dict(crown=(3.6, 0.0, -1.3), barrel=(P["barrel"][0], P["barrel"][1], 0.0),
              train=(P["third"][0], P["third"][1], 0.0), escapement=(P["escape"][0], P["escape"][1], 0.0),
              balance=(P["balance"][0], P["balance"][1], 0.0))
DIM_TRAIN = {"dial": 0.35, "engine": 1.0, "top": 0.18}       # bridges see-through while touring the train
DIM_DIAL = {"dial": 1.0, "engine": 0.12, "top": 0.06}         # the dial tier in full at the end
CARD_POS = (-4.3, -2.15)

# --- on-screen text --------------------------------------------------
FILMS = ["Movement Architecture", "The Power Source", "The Gear Train", "The Regulating Organ", "Isochronism",
         "The Escapement", "The Keyless Works"]
CARDS = dict(tiers=(1,), crown=(7,), barrel=(2,), train=(3,), escapement=(6,), balance=(4,), iso=(5,),
             dial=(3,))
NOTES = dict(tiers="the three tiers", crown="the keyless works", barrel="the mainspring stores the energy",
             train="the gear train carries it", escapement="the escapement locks and releases it",
             balance="the balance and hairspring set the pace", iso="why the pace drifts with the swing",
             dial="the motion work turns the hands")
TEXT = dict(head=("FROM THE CROWN TO THE HANDS", "the series, in one pass"), list_head="Learning How Watches Work")
# =====================================================================


def card(key):
    n = CARDS[key][0]
    t = VGroup(label(f"Film {n}  ·  {FILMS[n - 1]}", 0.32, GLOW, bold=True), label(NOTES[key], 0.24, GREY_B))
    t.arrange(DOWN, aligned_edge=LEFT, buff=0.1)
    back = RoundedRectangle(width=t.width + 0.4, height=t.height + 0.3, corner_radius=0.08)
    back.set_fill(BG, 0.82).set_stroke(GLOW, 1, 0.6)
    return VGroup(back.move_to(t), t).move_to([*CARD_POS, 0], aligned_edge=LEFT)


class Scene07(ThreeDScene):
    def construct(self):
        self.camera.background_color = BG
        self.set_camera_orientation(phi=CAM0["phi"] * DEGREES, theta=CAM0["theta"] * DEGREES, zoom=CAM0["zoom"],
                                    frame_center=ORIGIN)
        # no vignette here: a screen-fixed image is displaced when the camera's frame center moves
        wait_until = clock(self)

        mv = Movement()
        explode, dim = attach_driver(self, mv, Z_ASSEMBLED, Z_EXPLODED)

        head = heading(*TEXT["head"]).to_corner(UL, buff=0.45)
        self.add_fixed_in_frame_mobjects(head)
        self.remove(head)
        cur = curtain()
        self.add_fixed_in_frame_mobjects(cur)
        self.play(cur.animate.set_fill(opacity=0), run_time=FADE_IN)
        self.remove(cur)
        wait_until(HEAD_AT)
        self.play(FadeIn(head), run_time=0.8)

        shown = {"card": None}

        def show_card(key):
            c = card(key)
            self.add_fixed_in_frame_mobjects(c)
            self.remove(c)
            anims = [FadeIn(c, shift=UP * 0.1)]
            if shown["card"] is not None:
                anims.append(FadeOut(shown["card"]))
            shown["card"] = c
            return anims

        # the tiers open (Film 1)
        wait_until(TIERS[0])
        self.play(explode.animate.set_value(1.0), *show_card("tiers"), run_time=TIERS[1] - TIERS[0], rate_func=smooth)

        # the stops, each with its film's card; the camera holds still while it is read
        for i, (t0, t1, tc, key) in enumerate(STOPS):
            wait_until(t0)
            extra = []
            if key == "barrel":
                extra = [dim[k].animate(run_time=t1 - t0).set_value(v) for k, v in DIM_TRAIN.items()]
            self.play(*camera_move(self, t1 - t0, target=np.array(TARGET[key]), frame_origin=ORIGIN, **CAM_STOP),
                      cue(tc, *show_card(key), start=t0, end=t1, run_time=0.8), *extra)
            self.remove(self.camera._frame_center)
        wait_until(ISO_AT)
        self.play(*show_card("iso"), run_time=0.8)

        # back under the dial: the dial tier turns over
        wait_until(DIAL[0])
        self.play(*camera_move(self, DIAL[1] - DIAL[0], target=np.array([0.0, 0.0, Z_EXPLODED["dial"]]),
                               frame_origin=ORIGIN, **CAM_DIAL),
                  mv.flip.animate(run_time=DIAL[1] - DIAL[0]).set_value(1.0),
                  *[dim[k].animate(run_time=DIAL[1] - DIAL[0]).set_value(v) for k, v in DIM_DIAL.items()],
                  cue(DIAL[0] + 0.8, *show_card("dial"), start=DIAL[0], end=DIAL[1], run_time=0.8))
        self.remove(self.camera._frame_center)

        # wide, and the seven films in order
        wait_until(WIDE[0])
        rows = VGroup(*[label(f"{i + 1}.  {t}", 0.27, WHITE if i < 6 else GLOW, bold=(i == 6))
                        for i, t in enumerate(FILMS)]).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        lh = label(TEXT["list_head"], 0.28, GREY_B, bold=True)
        films = VGroup(lh, rows).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        back = RoundedRectangle(width=films.width + 0.5, height=films.height + 0.4, corner_radius=0.1)
        back.set_fill(BG, 0.8).set_stroke(GREY_B, 1, 0.6)
        film_list = VGroup(back.move_to(films), films).to_edge(LEFT, buff=0.5).shift(DOWN * 0.15)
        self.add_fixed_in_frame_mobjects(film_list)
        self.remove(film_list)
        seg = dict(start=WIDE[0], end=WIDE[1])
        self.play(*camera_move(self, WIDE[1] - WIDE[0], target=np.array([0.8, 0.0, 0.0]), frame_origin=ORIGIN,
                               **CAM_WIDE),
                  *[dim[k].animate(run_time=WIDE[1] - WIDE[0]).set_value(v) for k, v in
                    {"dial": 1.0, "engine": 1.0, "top": 1.0}.items()],
                  explode.animate(run_time=WIDE[1] - WIDE[0]).set_value(0.55),
                  cue(WIDE[0], FadeOut(shown["card"]), **seg, run_time=0.6),
                  cue(LIST_AT, FadeIn(film_list, shift=RIGHT * 0.15), **seg, run_time=1.0))
        self.remove(self.camera._frame_center)

        wait_until(FINAL_HOLD_UNTIL)
        cur.set_fill(opacity=0)
        self.add_fixed_in_frame_mobjects(cur)
        self.play(cur.animate.set_fill(opacity=1), run_time=FADE_OUT)
