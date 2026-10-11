"""Film 3, scene 07 - "The real train": the movement runs on the left with its
bridges off, while a table on the right fills in the 6497's tooth counts, one
mesh at a time: barrel 85 -> 12, center 80 -> 10, third 60 -> 8, fourth 70 -> 7,
escape 15. Each mesh lights up on the movement as its row fills in. The
check at the end: 15 x 2 x 10 x 60 = 18,000 beats an hour.

Build (render + voice + mux):   python build.py 3/scene07_real_train
Render only (quick preview):    PYTHONPATH=.:films/film03_gear_train manim -ql films/film03_gear_train/scene07_real_train.py Scene07
Narration lines and their start times live in scene07_real_train.voice.txt.

Counts: movement.TEETH_6497 (Horological Times, Sept 2006; the barrel's 85/12 is
inferred from the movement's geometry). The camera holds still.
"""
from manim import *
import movement
movement.use_train(movement.TEETH_6497)
from movement import Movement, attach_driver, vignette, P, R, TEETH, BG, GLOW, FONT_SANS, FONT_SERIF

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds.
# Keep the timeline roughly in step with scene07_real_train.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 1.4
TABLE_AT = 1.4                          # "here is the train in this movement"
# per mesh: (wheel count, pinion count, ratio, turns of the driven arbor(s))
MESH_AT = {"barrel": (5.4, 7.2, 8.8, 11.6),
           "center": (24.0, 25.8, 27.4, None),
           "third": (30.0, 31.6, 33.0, 37.8),
           "fourth": (42.8, 44.4, 45.6, 46.6)}
NOT_NEAT_AT, RESERVE_AT = 15.6, 19.4    # "that ratio doesn't need to be neat"; "how long the spring lasts"
SIXTY_AT = 35.0                         # 8 x 7.5 = 60
CHECK_AT = (48.6, 49.8, 51.0, 52.3, 53.6)    # 15, x 2, x 10, x 60, = 18,000
CLOSES_AT = 56.0                        # "the arithmetic closes"
FINAL_HOLD_UNTIL = 62.6                 # the last line ends about 61.2 s
FADE_OUT = 1.5

# --- the movement ------------------------------------------------------
Z_ASSEMBLED = {"dial": 0.00, "engine": 0.30, "top": 0.62}
Z_LIFTED = {"dial": 0.00, "engine": 0.30, "top": 3.6}
# Manim's Cairo 3D camera draws the movement shifted by -2 x frame_center and the
# screen-fixed layer by -frame_center, so frame_center x = 1.65 puts the movement's
# center at about x = -3.3, and the fixed layer is shifted back by FIX_SHIFT below.
CAM = dict(phi=14, theta=-90, zoom=0.98, center=(1.65, 0.0, 0.3))
FIX_SHIFT = np.array([CAM["center"][0], CAM["center"][1], 0.0])

# --- the table (screen coordinates) ---------------------------------------
COL = {"name": 0.35, "wheel": 2.75, "pinion": 3.85, "ratio": 4.75, "turns": 5.55}
ROW0, DROW = 1.85, 0.78                 # first row's y, spacing
HEAD_Y = 2.65
FOOT_Y = -2.55

# --- text --------------------------------------------------------------
ARBORS = ("barrel", "center", "third", "fourth", "escape")
HEADS = {"wheel": "wheel", "pinion": "pinion", "turns": "turns"}
TURNS = {"barrel": "1 per 7 hours", "center": "1 per hour", "third": "8 per hour", "fourth": "1 per minute",
         "escape": "10 per minute"}
RATIOS = {"barrel": "× 7.08", "center": "× 8", "third": "× 7.5", "fourth": "× 10"}
RESERVE = "sets how long the spring lasts, not the time"
SIXTY = "8 × 7.5 = 60"
CHECK = ("15", "× 2", "× 10", "× 60", "=  18,000 beats / hour")
# =====================================================================

PINION = {"center": "center_p", "third": "third_p", "fourth": "fourth_p", "escape": "escape_p"}
NEXT = {"barrel": "center", "center": "third", "third": "fourth", "fourth": "escape"}
Z_RING = Z_ASSEMBLED["engine"] + 0.32


def label(s, scale=0.28, color=GREY_B, bold=False):
    return Text(s, font=FONT_SANS, weight=BOLD if bold else NORMAL, color=color).scale(scale)


def ftext(s, scale=0.5, color=WHITE):
    return Text(s, font=FONT_SERIF, slant=ITALIC, color=color).scale(scale)


class Scene07(ThreeDScene):
    def construct(self):
        self.camera.background_color = BG
        self.set_camera_orientation(phi=CAM["phi"] * DEGREES, theta=CAM["theta"] * DEGREES,
                                    zoom=CAM["zoom"], frame_center=np.array(CAM["center"]))
        self.add_fixed_in_frame_mobjects(vignette().shift(FIX_SHIFT))

        def wait_until(when):
            d = when - self.renderer.time
            if d > 1e-3:
                self.wait(d)

        mv = Movement()
        mv.tiers["dial"].remove(mv.parts["dial_works"])
        mv.rot = [r for r in mv.rot if r[2] != "dial"]
        explode, dim = attach_driver(self, mv, Z_ASSEMBLED, Z_LIFTED)
        explode.set_value(1.0)
        dim["top"].set_value(0.0)
        self.remove(mv.tiers["top"])

        rings = {k: Circle(radius=R[k] * 1.08, num_components=64).move_to(P[k] + OUT * Z_RING).set_stroke(GLOW, 4, 0)
                 for k in ARBORS}
        self.add(*rings.values())

        def pulse(k, run_time=1.2):
            return rings[k].animate(rate_func=there_and_back, run_time=run_time).set_stroke(GLOW, 5, 0.95)

        # ------------------------------------------------------------ the table
        def row_y(i):
            return ROW0 - i * DROW
        heads = VGroup(*[label(t, 0.26, GREY_B).move_to([COL[k] + (0.55 if k == "turns" else 0), HEAD_Y, 0])
                         for k, t in HEADS.items()])
        names = {k: label(k, 0.3, WHITE).move_to([COL["name"], row_y(i), 0], aligned_edge=LEFT)
                 for i, k in enumerate(ARBORS)}
        wheels = {k: label(str(TEETH[k]), 0.34, WHITE, True).move_to([COL["wheel"], row_y(i), 0])
                  for i, k in enumerate(ARBORS)}
        pinions = {k: label(str(TEETH[PINION[k]]), 0.34, WHITE, True).move_to([COL["pinion"], row_y(i), 0])
                   for i, k in enumerate(ARBORS) if k in PINION}
        dash = label("—", 0.3).move_to([COL["pinion"], row_y(0), 0])
        turns = {k: label(TURNS[k], 0.26, GLOW).move_to([COL["turns"], row_y(i), 0], aligned_edge=LEFT)
                 for i, k in enumerate(ARBORS)}
        links, ratios = {}, {}
        for i, k in enumerate(ARBORS[:-1]):
            a = wheels[k].get_right() + RIGHT * 0.08
            b = pinions[NEXT[k]].get_left() + LEFT * 0.08
            links[k] = Arrow(a, b, buff=0, stroke_width=2.5, tip_length=0.13, color=GLOW)
            ratios[k] = label(RATIOS[k], 0.3, GLOW, True).move_to([COL["ratio"], (row_y(i) + row_y(i + 1)) / 2, 0])
        reserve = label(RESERVE, 0.26, GREY_B).move_to([3.5, FOOT_Y, 0])
        sixty = label(SIXTY, 0.3, WHITE).move_to([3.5, FOOT_Y - 0.5, 0])
        check = VGroup(*[ftext(c, 0.4, WHITE if i < 4 else GLOW) for i, c in enumerate(CHECK)]).arrange(RIGHT, buff=0.16)
        check.move_to([3.5, FOOT_Y, 0])
        box = SurroundingRectangle(check, buff=0.18, corner_radius=0.08).set_stroke(GLOW, 2.5)

        curtain = FullScreenRectangle().set_fill(BG, 1).set_stroke(width=0).scale(1.5)
        fixed = [heads, dash, reserve, sixty, check, box, *names.values(), *wheels.values(), *pinions.values(),
                 *turns.values(), *links.values(), *ratios.values()]
        for m in fixed + [curtain]:
            m.shift(FIX_SHIFT)
        self.add_fixed_in_frame_mobjects(*fixed, curtain)
        self.remove(*fixed)

        def pop(m):
            return FadeIn(m, scale=1.3)

        # ---------------------------------------------------------- timeline
        self.play(curtain.animate.set_fill(opacity=0), run_time=FADE_IN, rate_func=smooth)
        wait_until(TABLE_AT)                               # the table's frame
        self.play(FadeIn(heads), LaggedStart(*[FadeIn(names[k], shift=RIGHT * 0.1) for k in ARBORS], lag_ratio=0.2),
                  FadeIn(dash), run_time=1.4)

        for k in ("barrel", "center", "third", "fourth"):  # one mesh at a time
            t_w, t_p, t_r, t_t = MESH_AT[k]
            nxt = NEXT[k]
            wait_until(t_w)
            self.play(pop(wheels[k]), pulse(k), run_time=0.8)
            wait_until(t_p)
            self.play(pop(pinions[nxt]), pulse(nxt), run_time=0.8)
            wait_until(t_r)
            self.play(GrowArrow(links[k]), FadeIn(ratios[k], shift=LEFT * 0.1), run_time=0.8)
            if k == "barrel":
                wait_until(t_t)
                self.play(FadeIn(turns["barrel"], shift=LEFT * 0.1), run_time=0.6)
                wait_until(NOT_NEAT_AT)                    # not a neat ratio, and it needn't be
                self.play(Indicate(ratios["barrel"], color=WHITE), run_time=1.0)
                wait_until(RESERVE_AT)
                self.play(FadeIn(reserve, shift=UP * 0.1), run_time=0.8)
            if k == "third":
                wait_until(SIXTY_AT)                       # 8 x 7.5 = 60
                self.play(FadeIn(sixty, shift=UP * 0.1), Indicate(ratios["center"], color=WHITE),
                          Indicate(ratios["third"], color=WHITE), run_time=1.0)
                wait_until(t_t)                            # the center wheel once an hour, the fourth once a minute
                self.play(FadeIn(turns["center"], shift=LEFT * 0.1), FadeIn(turns["third"], shift=LEFT * 0.1),
                          pulse("center"), run_time=0.8)
                self.play(FadeIn(turns["fourth"], shift=LEFT * 0.1), pulse("fourth"), run_time=0.8)
            if k == "fourth":
                wait_until(t_t)
                self.play(FadeIn(turns["escape"], shift=LEFT * 0.1), pop(wheels["escape"]), run_time=0.8)

        wait_until(CHECK_AT[0] - 0.6)                      # 15 x 2 x 10 x 60
        self.play(FadeOut(reserve), FadeOut(sixty), run_time=0.5)
        for i, t in enumerate(CHECK_AT):
            wait_until(t)
            extra = {0: [Indicate(wheels["escape"])], 2: [Indicate(turns["escape"])]}.get(i, [])
            self.play(FadeIn(check[i], shift=LEFT * 0.1), *extra, run_time=0.6)
        wait_until(CLOSES_AT)                              # the arithmetic closes
        self.play(Create(box), *[pulse(k, 1.4) for k in ARBORS], run_time=1.4)

        wait_until(FINAL_HOLD_UNTIL)
        self.remove(curtain)
        self.add_fixed_in_frame_mobjects(curtain)
        self.play(curtain.animate.set_fill(opacity=1), run_time=FADE_OUT)
