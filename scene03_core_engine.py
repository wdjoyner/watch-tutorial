"""Scene 03 - "The Core Engine": the bridges lift away and the camera pushes in
over the going train, from the mainspring barrel to the balance wheel.

Build (render + voice + mux):   python build.py scene03_core_engine
Render only (quick preview):    manim -ql scene03_core_engine.py Scene03
Narration lines and their start times live in scene03_core_engine.voice.txt.

Every wheel turns at its true speed (from state()), so the barrel and center
wheel barely move in a 20-second shot. A glow travels along the train to show
the flow of power. The hairspring is redrawn each frame so it breathes as the
balance swings, and faint trailing copies of the balance give it a motion blur.
"""
from manim import *
from movement import (Movement, attach_driver, vignette, state, P, R, BG, GLOW, FONT_SANS, STEEL_HI)

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds, angles in degrees.
# Keep the timeline roughly in step with scene03_core_engine.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 1.6
LIFT_AT = 1.8              # the bridges and rotor lift away
LIFT_DURATION = 3.2
POWER_AT = 7.4             # glow on the barrel ("tightly coiled mainspring")
POWER_FLOW = 4.2           # glow travels barrel -> balance ("through the going train")
PUSH_END = 18.0            # the slow forward push ends here
FINAL_HOLD = 2.3
FADE_OUT = 1.5
LABEL_TIMES = {"title": 3.4, "barrel": 7.4, "train": 10.2, "balance": 14.4}
LABEL_FADE = 0.5
LABEL_BACKING = 0.72       # opacity of the dark panel behind the labels

# --- tier heights ------------------------------------------------------
Z_ASSEMBLED = {"dial": 0.00, "engine": 0.30, "top": 0.62}
Z_LIFTED = {"dial": 0.00, "engine": 0.30, "top": 3.4}    # top tier rises toward the camera

# --- camera (phi = 0 is straight down) --------------------------------
CAM_START = dict(phi=16, theta=-58, zoom=0.95, center=(0.0, 0.2, 0.3))
CAM_TRAIN = dict(phi=20, theta=-62, zoom=1.35, center=(0.15, 0.45, 0.3))
CAM_END = dict(phi=22, theta=-66, zoom=2.3, center=(0.8, 1.75, 0.55))   # on the escapement and balance

# --- balance and hairspring --------------------------------------------
BLUR_COPIES = 4            # trailing copies of the balance
BLUR_STEP = 1 / 120        # seconds between copies
BLUR_OPACITY = 0.22
HS_TURNS = 7
HS_INNER, HS_PITCH = 0.14, 0.075     # inner radius, growth per turn
HS_BREATH = 0.05           # relative radius change at full amplitude

# --- on-screen text --------------------------------------------------
TITLE = ("TIER 2  ·  CORE ENGINE", "between the main plate and the bridges")
ITEMS = {
    "barrel": "mainspring barrel  ·  stores the energy",
    "train": "going train  ·  gears it down",
    "balance": "balance and escapement  ·  keep the beat",
}
# =====================================================================

TRAIN = ["barrel", "center", "third", "fourth", "escape", "pallet", "balance"]
GLOW_R = {"barrel": R["barrel"], "center": R["center"], "third": R["third"], "fourth": R["fourth"],
          "escape": R["escape"], "pallet": 0.3, "balance": 0.78}


class Scene03(ThreeDScene):
    def construct(self):
        self.camera.background_color = BG
        self.set_camera_orientation(phi=CAM_START["phi"] * DEGREES, theta=CAM_START["theta"] * DEGREES,
                                    zoom=CAM_START["zoom"], frame_center=np.array(CAM_START["center"]))
        self.add_fixed_in_frame_mobjects(vignette())

        mv = Movement()
        # the motion works and keyless works sit on the far (dial) face; leave only the plate
        dial = mv.tiers["dial"]
        hidden = [mv.parts[k] for k in ("hour_wheel", "minute_wheel", "cannon_pinion", "keyless")]
        dial.remove(*hidden)
        mv.rot = [r for r in mv.rot if not any(r[0] is h for h in hidden)]
        # the hairspring is redrawn below so it can breathe
        balance = mv.parts["balance"]
        balance.remove(mv.parts["hairspring"])
        explode, dim = attach_driver(self, mv, Z_ASSEMBLED, Z_LIFTED)

        # a clock in step with the driver's
        clock = {"t": 0.0}
        tick = Mobject()
        tick.add_updater(lambda m, dt: clock.__setitem__("t", clock["t"] + dt))
        self.add(tick)

        bxy = P["balance"][:2]
        z_bal = lambda: mv.engine_ref.get_center()[2] + 0.24

        # motion blur: faint copies of the rim, arms and weights at earlier angles
        ghosts = []
        for k in range(1, BLUR_COPIES + 1):
            g = VGroup(balance[0][1].copy(), balance[1].copy())
            g.set_fill(opacity=BLUR_OPACITY * (1 - k / (BLUR_COPIES + 1))).set_stroke(opacity=0)
            g._ang, g._lag = 0.0, k * BLUR_STEP

            def follow(m):
                target = state(max(0.0, clock["t"] - m._lag))["balance"]
                m.rotate(target - m._ang, axis=OUT, about_point=np.array([bxy[0], bxy[1], z_bal()]))
                m._ang = target
            g.add_updater(follow)
            ghosts.append(g)

        # breathing hairspring: the inner end turns with the balance, the outer end stays at the stud
        def hairspring():
            phi = state(clock["t"])["balance"]
            U = HS_TURNS * TAU
            u = np.linspace(0, U, 420)
            f = u / U
            r = (HS_INNER + HS_PITCH * u / TAU) * (1 + HS_BREATH * (phi / 1.25) * f)
            a = 0.6 + u + phi * (1 - f)
            z = z_bal() + 0.03
            pts = np.column_stack([bxy[0] + r * np.cos(a), bxy[1] + r * np.sin(a), np.full_like(u, z)])
            spring = VMobject().set_points_smoothly(pts).set_stroke(STEEL_HI, 1.1).set_fill(opacity=0)
            stud = Dot(pts[-1], radius=0.03, color=STEEL_HI)
            return VGroup(spring, stud)

        self.add(*ghosts, always_redraw(hairspring))

        # power flow: a glow along the train, and a ring on each wheel as it passes
        z_train = lambda: mv.engine_ref.get_center()[2] + 0.32
        path = VMobject().set_points_as_corners([P[k] + OUT * Z_ASSEMBLED["engine"] + OUT * 0.32 for k in TRAIN])
        path.set_stroke(GLOW, 7, 0.9)
        rings = VGroup(*[Circle(radius=GLOW_R[k] * 1.08, num_components=48).move_to(P[k] + OUT * (Z_ASSEMBLED["engine"] + 0.32))
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

        def label_at(when, *mobs, now):
            return Succession(Wait(max(0, when - now)),
                              AnimationGroup(*[FadeIn(m, shift=RIGHT * 0.2) for m in mobs], run_time=LABEL_FADE))

        # ---------------------------------------------------------- timeline
        # fade up; the bridges and rotor lift off toward the camera and fade away
        self.play(curtain.animate.set_fill(opacity=0), run_time=FADE_IN, rate_func=smooth)
        self.wait(LIFT_AT - FADE_IN)
        t = LIFT_AT
        self.move_camera(phi=CAM_TRAIN["phi"] * DEGREES, theta=CAM_TRAIN["theta"] * DEGREES,
                         zoom=CAM_TRAIN["zoom"], frame_center=np.array(CAM_TRAIN["center"]),
                         added_anims=[explode.animate(rate_func=rate_functions.ease_in_cubic).set_value(1.0),
                                      dim["top"].animate(rate_func=rate_functions.ease_in_quad).set_value(0.0),
                                      label_at(LABEL_TIMES["title"], backing, bar, head, sub, now=t)],
                         run_time=LIFT_DURATION, rate_func=smooth)
        t += LIFT_DURATION
        self.remove(mv.tiers["top"])                       # invisible now; stop drawing it

        # slow forward push toward the balance, with the power flow along the way
        def ring_pulse(k, run_time):
            return rings[TRAIN.index(k)].animate(rate_func=there_and_back, run_time=run_time).set_stroke(opacity=0.9)

        flow = Succession(
            Wait(max(0, POWER_AT - t)),
            ring_pulse("barrel", 1.4),
            AnimationGroup(ShowPassingFlash(path.copy(), time_width=0.35, run_time=POWER_FLOW),
                           LaggedStart(*[ring_pulse(k, 1.0) for k in TRAIN[1:]], lag_ratio=0.55,
                                       run_time=POWER_FLOW)))
        self.move_camera(phi=CAM_END["phi"] * DEGREES, theta=CAM_END["theta"] * DEGREES,
                         zoom=CAM_END["zoom"], frame_center=np.array(CAM_END["center"]),
                         added_anims=[flow,
                                      label_at(LABEL_TIMES["barrel"], items["barrel"], now=t),
                                      label_at(LABEL_TIMES["train"], items["train"], now=t),
                                      label_at(LABEL_TIMES["balance"], items["balance"], now=t)],
                         run_time=PUSH_END - t, rate_func=rate_functions.ease_in_out_sine)

        self.wait(FINAL_HOLD)
        self.remove(curtain)
        self.add_fixed_in_frame_mobjects(curtain)        # re-add so it sits above the text
        self.play(FadeOut(panel), curtain.animate.set_fill(opacity=1), run_time=FADE_OUT)
