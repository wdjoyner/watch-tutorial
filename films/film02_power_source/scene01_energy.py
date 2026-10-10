"""Film 2, scene 01 - "Where the energy lives": the assembled movement; the
bridges lift away, the mainspring barrel lights up, and a glow runs down the
going train to the balance.

Build (render + voice + mux):   python build.py scene01_energy
Render only (quick preview):    PYTHONPATH=. manim -ql films/film02_power_source/scene01_energy.py Scene01
Narration lines and their start times live in scene01_energy.voice.txt.
"""
from manim import *
from movement import Movement, attach_driver, vignette, camera_move, cue, P, R, BG, GLOW, FONT_SANS

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds, angles in degrees.
# Keep the timeline roughly in step with scene01_energy.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 1.6
DRIFT_END = 5.4            # slow drift over the assembled movement ("paid for in advance")
LIFT_DURATION = 3.0        # the bridges lift away ("stored here, in the barrel")
PUSH_END = 11.8            # the camera settles over the barrel
BARREL_GLOW_AT = 6.8       # ring around the barrel
SPRING_GLOW_AT = 8.4       # the mainspring lights up ("a coiled ribbon of spring steel")
PULL_AT = 13.4             # pull back over the train ("everything downstream")
PULL_END = 21.0
FLOW_AT = 14.2             # glow runs barrel -> balance
FLOW_DURATION = 4.4
FINAL_HOLD = 2.4
FADE_OUT = 1.5
LABEL_TIMES = {"title": 2.0, "barrel": 6.8, "train": 15.6, "balance": 17.2}
LABEL_BACKING = 0.72       # opacity of the dark panel behind the labels
SPRING_GLOW = 0.95         # peak opacity of the glowing mainspring
SPRING_COLOR = "#ffb54a"   # warm amber, so the lit spring stands out from the steel
SPRING_HALO = 0.45         # opacity of the soft halo around it
RING_SCALE = 1.0           # glow ring radius / pitch radius (1.0 sits on the teeth)

# --- tier heights ------------------------------------------------------
Z_ASSEMBLED = {"dial": 0.00, "engine": 0.30, "top": 0.62}
Z_LIFTED = {"dial": 0.00, "engine": 0.30, "top": 3.4}    # the bridges rise toward the camera

# --- camera (phi = 0 is straight down) --------------------------------
CAM_START = dict(phi=34, theta=-64, zoom=0.92, center=(0.0, 0.0, 0.3))
CAM_DRIFT = dict(phi=28, theta=-56, zoom=1.0)               # slow drift while the first line plays
CAM_BARREL = dict(phi=24, theta=-48, zoom=2.0)              # close over the barrel
CAM_TRAIN = dict(phi=22, theta=-60, zoom=1.3)               # barrel to balance in one view
TRAIN_TARGET = (-0.75, -0.55, 0.4)                          # center of that view (clear of the label panel)

# --- on-screen text --------------------------------------------------
TITLE = ("THE POWER SOURCE", "where the energy lives")
ITEMS = {
    "barrel": "mainspring barrel  ·  stores the energy",
    "train": "going train  ·  spends it slowly",
    "balance": "balance  ·  sets the pace",
}
# =====================================================================

TRAIN = ["barrel", "center", "third", "fourth", "escape", "pallet", "balance"]
PART = {"barrel": "barrel", "center": "center_wheel", "third": "third_wheel", "fourth": "fourth_wheel",
        "escape": "escape_wheel", "pallet": "pallet_fork", "balance": "balance"}
GLOW_R = {"barrel": R["barrel"], "center": R["center"], "third": R["third"], "fourth": R["fourth"],
          "escape": R["escape"], "pallet": 0.3, "balance": R["balance"]}


class Scene01(ThreeDScene):
    def construct(self):
        self.camera.background_color = BG
        origin = np.array(CAM_START["center"])
        self.set_camera_orientation(phi=CAM_START["phi"] * DEGREES, theta=CAM_START["theta"] * DEGREES,
                                    zoom=CAM_START["zoom"], frame_center=origin)
        self.add_fixed_in_frame_mobjects(vignette())

        mv = Movement()
        # the motion works and keyless works sit under the plate, out of sight
        mv.tiers["dial"].remove(mv.parts["dial_works"])
        mv.rot = [r for r in mv.rot if r[2] != "dial"]
        explode, dim = attach_driver(self, mv, Z_ASSEMBLED, Z_LIFTED)

        # glowing copy of the mainspring, laid over the real one (the barrel turns
        # once in 8 hours, so it barely moves during the shot); a wide faint stroke
        # underneath gives it a soft halo
        spring = mv.parts["barrel"][3]
        halo = spring.copy().set_stroke(SPRING_COLOR, 9, 0)
        core = spring.copy().set_stroke(SPRING_COLOR, 2.4, 0)
        self.add(halo, core)

        # power flow: a glow along the train, and a ring on each wheel as it passes,
        # each drawn just above the top of its own part so it sits centered on it
        top = {k: P[k][:2].tolist() + [mv.parts[PART[k]].get_zenith()[2] + 0.01] for k in TRAIN}
        path = VMobject().set_points_as_corners([np.array(top[k]) for k in TRAIN]).set_stroke(GLOW, 7, 0.9)
        rings = VGroup(*[Circle(radius=GLOW_R[k] * RING_SCALE, num_components=48).move_to(np.array(top[k]))
                         .set_stroke(GLOW, 4, 0) for k in TRAIN])
        self.add(rings)

        # screen-fixed text
        head = Text(TITLE[0], font=FONT_SANS, weight=BOLD, color=GLOW).scale(0.40)
        sub = Text(TITLE[1], font=FONT_SANS, color=GREY_B).scale(0.26)
        items = {k: Text(t, font=FONT_SANS, color=GREY_B).scale(0.26) for k, t in ITEMS.items()}
        block = VGroup(head, sub, *items.values()).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        VGroup(*items.values()).shift(DOWN * 0.12)
        bar = Line(ORIGIN, RIGHT * 0.45).set_stroke(GLOW, 2)
        panel = VGroup(bar, block).arrange(RIGHT, buff=0.15, aligned_edge=UP).to_corner(DL, buff=0.5)
        backing = RoundedRectangle(corner_radius=0.12, width=panel.width + 0.5, height=panel.height + 0.4)
        backing.move_to(panel).set_fill(BG, LABEL_BACKING).set_stroke(width=0)
        panel = VGroup(backing, panel)
        curtain = FullScreenRectangle().set_fill(BG, 1).set_stroke(width=0)
        self.add_fixed_in_frame_mobjects(panel, curtain)
        self.remove(panel)

        def fade(*mobs):
            return [FadeIn(m, shift=RIGHT * 0.2) for m in mobs]

        def ring(k, opacity, run_time, rate_func=smooth):
            return rings[TRAIN.index(k)].animate(run_time=run_time, rate_func=rate_func).set_stroke(opacity=opacity)

        # ---------------------------------------------------------- timeline
        # fade up on the assembled movement, drifting slowly
        t = 0.0
        self.play(*camera_move(self, DRIFT_END, rate_func=rate_functions.ease_in_out_sine, **CAM_DRIFT),
                  cue(0.0, curtain.animate.set_fill(opacity=0), start=t, end=DRIFT_END, run_time=FADE_IN),
                  cue(LABEL_TIMES["title"], *fade(backing, bar, head, sub), start=t, end=DRIFT_END))
        t = DRIFT_END

        # the bridges lift away; push in over the barrel, which lights up
        seg = dict(start=t, end=PUSH_END)
        self.play(*camera_move(self, PUSH_END - t, rate_func=rate_functions.ease_in_out_sine,
                               target=P["barrel"] + OUT * 0.6, frame_origin=origin, **CAM_BARREL),
                  explode.animate(run_time=LIFT_DURATION, rate_func=rate_functions.ease_in_cubic).set_value(1.0),
                  dim["top"].animate(run_time=LIFT_DURATION, rate_func=rate_functions.ease_in_quad).set_value(0.0),
                  cue(BARREL_GLOW_AT, ring("barrel", 0.9, 1.0), run_time=1.0, **seg),
                  cue(LABEL_TIMES["barrel"], *fade(items["barrel"]), **seg),
                  cue(SPRING_GLOW_AT, halo.animate.set_stroke(opacity=SPRING_HALO), core.animate.set_stroke(opacity=SPRING_GLOW),
                      run_time=1.6, **seg))
        self.remove(self.camera._frame_center)
        self.remove(mv.tiers["top"])                       # invisible now; stop drawing it
        self.wait(PULL_AT - PUSH_END)
        t = PULL_AT

        # pull back over the whole train while the glow runs down it to the balance
        flow = AnimationGroup(
            ShowPassingFlash(path.copy(), time_width=0.35, run_time=FLOW_DURATION),
            LaggedStart(*[ring(k, 0.9, 1.0, there_and_back) for k in TRAIN[1:]], lag_ratio=0.55,
                        run_time=FLOW_DURATION),
            ring("barrel", 0.35, 1.5))
        seg = dict(start=t, end=PULL_END)
        self.play(*camera_move(self, PULL_END - t, rate_func=rate_functions.ease_in_out_sine,
                               target=np.array(TRAIN_TARGET), frame_origin=origin, **CAM_TRAIN),
                  cue(FLOW_AT, flow, run_time=FLOW_DURATION, **seg),
                  cue(LABEL_TIMES["train"], *fade(items["train"]), **seg),
                  cue(LABEL_TIMES["balance"], *fade(items["balance"]), **seg))
        self.remove(self.camera._frame_center)

        self.wait(FINAL_HOLD)
        self.remove(curtain)
        self.add_fixed_in_frame_mobjects(curtain)        # re-add so it sits above the text
        self.play(FadeOut(panel), curtain.animate.set_fill(opacity=1), run_time=FADE_OUT)
