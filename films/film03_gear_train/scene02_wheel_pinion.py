"""Film 3, scene 02 - "Wheel drives pinion": every arbor carries a wheel and a
pinion. On the left, a side view of three arbors (center, third, fourth) shows
the staircase: each wheel meshes with the next arbor's pinion, one level up. On
the right, the same three arbors from above, turning at their true ratios
(80 -> 10 and 60 -> 8), so each one spins faster than the last.

Build (render + voice + mux):   python build.py 3/scene02_wheel_pinion
Render only (quick preview):    PYTHONPATH=.:films/film03_gear_train manim -ql films/film03_gear_train/scene02_wheel_pinion.py Scene02
Narration lines and their start times live in scene02_wheel_pinion.voice.txt.

The gears are flat (train.GearSet). Each mesh has its own module, as in the
movement; the drawing is schematic in size, exact in tooth counts and speeds.
"""
from manim import *
from movement import vignette, BG, GLOW, FONT_SANS, BRASS, BRASS_DK, STEEL, STEEL_HI, PLATE
from train import GearSet, elevation_arbor

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds.
# Keep the timeline roughly in step with scene02_wheel_pinion.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 1.0
ONE_ARBOR_AT = 1.2                    # the third arbor appears, in side view and from above
PART_LABELS_AT = {"wheel": 3.6, "pinion": 5.0, "arbor": 6.4}
DRIVE_AT = 9.0                        # "the wheel on one arbor drives the pinion on the next"
SPIN_UP = 2.0                         # seconds for the train to come up to speed
RATIO1_AT = 14.0                      # "a big gear driving a small one multiplies speed"
ALONG_AT = 24.4                       # "the pinion turns with its wheel"
NEXT_AT = 27.0                        # "... to the next mesh"
FLOW_AT = 30.8                        # "wheel drives pinion, all the way down the train"
FINAL_HOLD_UNTIL = 35.4               # the last line ends about 34.0 s
FADE_OUT = 1.5

# --- speeds --------------------------------------------------------------
CENTER_SPEED = 0.07                   # radians per second for the center wheel (third x8, fourth x60)

# --- side view (scene units) ----------------------------------------------
X_C = -5.4                           # center arbor; the others follow from the radii
PLATE_Y, BRIDGE_Y = -2.45, 2.05       # main plate and bridge, seen edge on
EL = dict(center_w=1.55, third_p=0.2, third_w=1.2, fourth_p=0.17, fourth_w=1.05, center_p=0.19)
LEVEL = {"center": -1.35, "third": -0.15, "fourth": 1.05}       # height of each arbor's wheel
WHEEL_H, PINION_H = 0.08, 0.4

# --- plan view ----------------------------------------------------------------
CENTER_AT = (2.15, 0.65)
M = {"center": 0.0335, "third": 0.035, "fourth": 0.027}         # module of each mesh, scene units
THIRD_ANGLE, FOURTH_ANGLE = -22, 38                             # where each driven arbor sits, degrees

# --- text --------------------------------------------------------------
HEADS = ("SIDE VIEW", "FROM ABOVE")
PART_TEXT = {"wheel": "wheel", "pinion": "pinion", "arbor": "arbor"}
RATIOS = ("center wheel 80  →  third pinion 10      × 8",
          "third wheel 60  →  fourth pinion 8      × 7.5")
FLOW_TEXT = "wheel drives pinion"
# =====================================================================


def label(s, scale=0.3, color=GREY_B, bold=False, t2c=None):
    return Text(s, font=FONT_SANS, weight=BOLD if bold else NORMAL, color=color, t2c=t2c or {}).scale(scale)


class Scene02(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.add(vignette())

        def wait_until(when):
            d = when - self.renderer.time
            if d > 1e-3:
                self.wait(d)

        # ------------------------------------------------------------ side view
        x_t = X_C + EL["center_w"] + EL["third_p"]
        x_f = x_t + EL["third_w"] + EL["fourth_p"]
        frame_lines = VGroup(*[Line([X_C - 1.5, y, 0], [x_f + 1.2, y, 0]).set_stroke(PLATE, 5)
                               for y in (PLATE_Y, BRIDGE_Y)])
        y0, y1 = PLATE_Y + 0.04, BRIDGE_Y - 0.04
        arbor_c = elevation_arbor(X_C, y0, y1, [(LEVEL["center"] - 0.55, EL["center_p"], PINION_H, "pinion"),
                                                (LEVEL["center"], EL["center_w"], WHEEL_H, "wheel")])
        arbor_t = elevation_arbor(x_t, y0, y1, [(LEVEL["center"], EL["third_p"], PINION_H, "pinion"),
                                                (LEVEL["third"], EL["third_w"], WHEEL_H, "wheel")])
        arbor_f = elevation_arbor(x_f, y0, y1, [(LEVEL["third"], EL["fourth_p"], PINION_H, "pinion"),
                                                (LEVEL["fourth"], EL["fourth_w"], WHEEL_H, "wheel")])
        contact1 = Circle(radius=0.2).move_to([x_t - EL["third_p"], LEVEL["center"], 0]).set_stroke(GLOW, 3, 0)
        contact2 = Circle(radius=0.2).move_to([x_f - EL["fourth_p"], LEVEL["third"], 0]).set_stroke(GLOW, 3, 0)

        # part labels on the third arbor
        def callout(text, point, offset):
            t = label(text, 0.28, WHITE)
            t.move_to(point + offset)
            return VGroup(Line(t.get_edge_center(-np.sign(offset[0]) * RIGHT) if offset[0] else t.get_bottom(),
                               point).set_stroke(GREY_B, 1.2), t)
        parts = {"wheel": callout(PART_TEXT["wheel"], np.array([x_t + 0.6, LEVEL["third"] + 0.04, 0]),
                                  np.array([0.0, 0.75, 0])),
                 "pinion": callout(PART_TEXT["pinion"], np.array([x_t + EL["third_p"], LEVEL["center"], 0]),
                                   np.array([1.15, 0.0, 0])),
                 "arbor": callout(PART_TEXT["arbor"], np.array([x_t, LEVEL["third"] + 1.3, 0]),
                                  np.array([-0.85, 0.0, 0]))}

        # ------------------------------------------------------------ plan view
        gs = GearSet()
        gs.gear("center", 80, M["center"], center=CENTER_AT, spokes=4)
        gs.gear("third_p", 10, M["center"], driven_by="center", angle=THIRD_ANGLE, kind="pinion")
        gs.gear("third", 60, M["third"], arbor_of="third_p", spokes=4)
        gs.gear("fourth_p", 8, M["third"], driven_by="third", angle=FOURTH_ANGLE, kind="pinion")
        gs.gear("fourth", 70, M["fourth"], arbor_of="fourth_p", spokes=4)
        # draw order: each driven wheel under its driver, pinions on top
        for n, c in (("third", "#a98336"), ("fourth", "#8d6d2c")):
            gs[n].body.set_fill(c)
            gs[n]._base = [(m, m.get_fill_opacity(), m.get_stroke_opacity()) for m in gs[n].family_members_with_points()]
        gs.group.submobjects = [gs[n] for n in ("fourth", "third", "center", "third_p", "fourth_p")]
        gs.hide("center", "fourth_p", "fourth")
        gs.attach(self)

        heads = VGroup(label(HEADS[0], 0.3, GLOW, True).move_to([(X_C + x_f) / 2 + 0.1, 3.3, 0]),
                       label(HEADS[1], 0.3, GLOW, True).move_to([CENTER_AT[0] + 1.3, 3.3, 0]))
        ratios = VGroup(*[label(r, 0.27, WHITE, t2c={r[r.index("×"):]: GLOW}) for r in RATIOS])
        ratios.arrange(DOWN, aligned_edge=LEFT, buff=0.16).move_to([CENTER_AT[0] + 1.25, -2.75, 0])
        ring_t = Circle(radius=0.32).move_to(gs["third_p"].pivot).set_stroke(GLOW, 4, 0)

        flow_path = VMobject().set_points_as_corners([
            [X_C, LEVEL["center"], 0], [x_t, LEVEL["center"], 0], [x_t, LEVEL["third"], 0],
            [x_f, LEVEL["third"], 0], [x_f, LEVEL["fourth"], 0], [x_f + EL["fourth_w"] + 0.5, LEVEL["fourth"], 0]])
        flow_path.set_stroke(GLOW, 6)
        flow_text = label(FLOW_TEXT, 0.3, GLOW).move_to([(X_C + x_f) / 2, -3.1, 0])

        curtain = FullScreenRectangle().set_fill(BG, 1).set_stroke(width=0)
        self.add(curtain)

        def flash(c):
            return c.animate(rate_func=there_and_back, run_time=1.2).set_stroke(opacity=1)

        # ---------------------------------------------------------- timeline
        self.add(frame_lines, heads)
        self.bring_to_front(curtain)
        self.play(curtain.animate.set_fill(opacity=0), run_time=FADE_IN, rate_func=smooth)
        self.remove(curtain)
        wait_until(ONE_ARBOR_AT)                          # one arbor: a wheel and a pinion
        self.play(FadeIn(arbor_t, shift=UP * 0.2), run_time=1.0)
        for k in ("wheel", "pinion", "arbor"):
            wait_until(PART_LABELS_AT[k])
            self.play(FadeIn(parts[k]), run_time=0.6)

        wait_until(DRIVE_AT)                              # the wheel on one arbor drives the next pinion
        self.play(FadeIn(arbor_c, shift=UP * 0.2), *gs.show("center"), run_time=1.0)
        self.add(contact1, ring_t)
        self.play(flash(contact1), gs.speed.animate(run_time=SPIN_UP, rate_func=smooth).set_value(CENTER_SPEED))

        wait_until(RATIO1_AT)                             # a big gear driving a small one: x8
        self.play(FadeIn(ratios[0], shift=UP * 0.1), flash(ring_t),
                  run_time=1.2)

        wait_until(ALONG_AT)                              # the speed passes along the arbor
        self.play(Indicate(arbor_t, color=GLOW, scale_factor=1.04), FadeOut(parts["wheel"]),
                  FadeOut(parts["pinion"]), FadeOut(parts["arbor"]), run_time=1.4)
        wait_until(NEXT_AT)                               # ... to the next mesh: x7.5
        self.add(contact2)
        self.play(FadeIn(arbor_f, shift=UP * 0.2), *gs.show("fourth_p", "fourth"), FadeIn(ratios[1], shift=UP * 0.1),
                  run_time=1.0)
        self.play(flash(contact2))

        wait_until(FLOW_AT)                               # all the way down the train
        self.play(ShowPassingFlash(flow_path, time_width=0.4, run_time=2.4), FadeIn(flow_text, run_time=1.0))

        wait_until(FINAL_HOLD_UNTIL)
        curtain.set_fill(opacity=0)
        self.add(curtain)
        self.play(curtain.animate.set_fill(opacity=1), run_time=FADE_OUT)
