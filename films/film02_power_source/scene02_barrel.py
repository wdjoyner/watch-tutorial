"""Film 2, scene 02 - "Inside the barrel": the barrel lifts out of the movement
and explodes along its axis into drum, mainspring, arbor and cover; insets show
how the spring hooks to the arbor and to the drum wall; then, with the arbor
held, the spring turns the drum, which drives the center pinion.

Build (render + voice + mux):   python build.py scene02_barrel
Render only (quick preview):    PYTHONPATH=.:films/film02_power_source manim -ql films/film02_power_source/scene02_barrel.py Scene02
Narration lines and their start times live in scene02_barrel.voice.txt.
The close-up barrel is the BarrelModel in barrel.py (same folder).
"""
from manim import *
from shapely.geometry import Point
from shapely import affinity
from movement import (Movement, attach_driver, vignette, camera_move, cue, pinion_g, disk_g, P, R, TEETH,
                      MESH, BG, GLOW, FONT_SANS, STEEL, STEEL_DK, STEEL_HI)
from barrel import (BarrelModel, inset_g, extrude, vm, MM, R_IN, R_ROOT, COVER_R, CORE_R, SHAFT_R, FLOOR, WALL_H,
                    SPRING_H, CORE_H, SHAFT_L, HOOK_IN_DEG, HOOK_OUT_DEG)

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds, angles in degrees.
# Keep the timeline roughly in step with scene02_barrel.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 1.2
LIFT_AT, LIFT_DURATION = 0.6, 3.8        # the barrel lifts out; the movement fades away
EXPLODE_AT, EXPLODE_DURATION = 4.4, 1.8  # "The barrel has four parts."
LABEL_TIMES = {"drum": 6.6, "cover": 8.4, "arbor": 10.6, "spring": 14.0, "spring_note": 16.4}
ASSEMBLE_AT, ASSEMBLE_DURATION = 20.2, 2.0   # back together, cover off, camera looks down
INSET_TIMES = {"inner": 22.4, "outer": 24.6}
DRIVE_AT, DRIVE_MOVE = 27.2, 2.2         # pull back; the center pinion appears
HELD_AT = 28.4                           # "Hold the arbor still"
TURN_AT, TURN_DURATION = 29.8, 4.6       # "the spring turns the drum ... teeth drive the gear train"
DRUM_SWEEP = 24                          # degrees the drum turns (demonstration speed)
FINAL_HOLD = 1.6
FADE_OUT = 1.5

# --- the barrel ------------------------------------------------------
Z0 = 0.33                                # barrel base height in the movement
LIFT = 1.2                               # how far it rises out of the movement

# --- camera (phi = 0 is straight down) --------------------------------
CAM_START = dict(phi=24, theta=-60, zoom=1.15)
CAM_EXPLODE = dict(phi=66, theta=-60, zoom=1.45)
CAM_HOOKS = dict(phi=24, theta=-60, zoom=2.3)
CAM_DRIVE = dict(phi=38, theta=-60, zoom=2.0)
DRIVE_FOCUS = 0.6                        # 0 = frame on the barrel, 1 = on the pinion
TEXT_BACKING = 0.75                      # dark panel behind the labels in the last shot
SHIFT_EXPLODE = 1.7                      # barrel sits this far left of center (units), labels on the right
SHIFT_HOOKS = 1.0

# --- on-screen text --------------------------------------------------
LABELS = {
    "cover": ("cover", "182"),
    "arbor": ("arbor", "195"),
    "spring": ("mainspring", "770"),
    "drum": ("drum", "182"),
}
SPRING_NOTE = "about 450 mm long, 0.18 mm thick"
INSETS = {"inner": "inner end on the arbor hook", "outer": "outer end on the drum hook"}
HELD = "arbor held still"
PINION = "center pinion  ·  to the gear train"
LABEL_X = 2.3                            # left edge of the part labels (screen units)
INSET_R = 1.05                           # radius of the magnified insets (screen units)
INSET_FIELD = 1.6                        # radius of the area each inset shows, mm
# =====================================================================

THETA = CAM_EXPLODE["theta"]
SCREEN_RIGHT = np.array([np.cos(np.radians(-(THETA + 90))), -np.sin(np.radians(-(THETA + 90))), 0.0])
RIGHT_DEG = np.degrees(np.arctan2(SCREEN_RIGHT[1], SCREEN_RIGHT[0]))     # barrel-frame angle that faces screen right


class Scene02(ThreeDScene):
    def construct(self):
        self.camera.background_color = BG
        origin = ORIGIN          # the starting frame_center; screen position = project_point(p)[:2]
        self.set_camera_orientation(phi=CAM_START["phi"] * DEGREES, theta=CAM_START["theta"] * DEGREES,
                                    zoom=CAM_START["zoom"], frame_center=origin)
        self.add_fixed_in_frame_mobjects(vignette())

        # the movement, bridges off as at the end of scene 01, with its barrel replaced by the close-up model
        mv = Movement()
        mv.tiers["dial"].remove(mv.parts["dial_works"])
        mv.tiers["engine"].remove(mv.parts["barrel"])
        mv.rot = [r for r in mv.rot if r[2] != "dial" and r[0] is not mv.parts["barrel"]]
        z = {"dial": 0.00, "engine": 0.30, "top": 0.62}
        _, dim = attach_driver(self, mv, z, z)
        dim["top"].set_value(0.0)
        self.remove(mv.tiers["top"])

        c = P["barrel"]
        bm = BarrelModel(center=c, z0=Z0)
        self.add(bm)

        # center pinion (shown at the end): meshes with the drum's teeth, turns 8 times as fast
        pin_g = affinity.scale(pinion_g(TEETH["center_p"], MESH["barrel"]), 1 / MM, 1 / MM, origin=(0, 0))
        pinion = VGroup(extrude(pin_g, STEEL, STEEL_DK, 1.0, 4, STEEL_HI),
                        extrude(disk_g(0.55), STEEL, STEEL_DK, 4.0, 5, STEEL_HI, z_mm=1.0))
        pinion.shift(P["center"] + OUT * Z0)
        pinion.set_opacity(0)
        pin_turn = {"a": 0.0}

        def drive_pinion(m):
            target = -bm.drum_turn.get_value() * TEETH["barrel"] / TEETH["center_p"]
            m.rotate(target - pin_turn["a"], axis=OUT, about_point=P["center"] + OUT * Z0)
            pin_turn["a"] = target
        pinion.add_updater(drive_pinion)

        def screen(p):
            return self.camera.project_point(p)[:2]

        def wait_until(when):                               # wait to an absolute scene time
            d = when - self.renderer.time
            if d > 1e-3:
                self.wait(d)

        curtain = FullScreenRectangle().set_fill(BG, 1).set_stroke(width=0)
        self.add_fixed_in_frame_mobjects(curtain)

        # ---------------------------------------------------------- timeline
        # fade up; the barrel lifts out and the movement fades away; the camera comes around to the side
        t = 0.0
        seg = dict(start=t, end=LIFT_AT + LIFT_DURATION)
        cam = dict(CAM_EXPLODE)
        target = c + OUT * (Z0 + LIFT + 1.2) + SCREEN_RIGHT * SHIFT_EXPLODE      # middle of the exploded stack
        self.play(cue(0.0, curtain.animate.set_fill(opacity=0), run_time=FADE_IN, **seg),
                  cue(LIFT_AT, bm.lift.animate(rate_func=smooth).set_value(LIFT),
                      dim["engine"].animate(rate_func=rate_functions.ease_in_quad).set_value(0.0),
                      dim["dial"].animate(rate_func=rate_functions.ease_in_quad).set_value(0.0),
                      run_time=LIFT_DURATION, **seg),
                  cue(LIFT_AT, *camera_move(self, LIFT_DURATION, rate_func=rate_functions.ease_in_out_sine,
                                            target=target, frame_origin=origin, **cam),
                      run_time=LIFT_DURATION, **seg))
        self.remove(self.camera._frame_center)
        self.remove(mv.tiers["dial"], mv.tiers["engine"])
        t = LIFT_AT + LIFT_DURATION

        # explode along the axis
        wait_until(EXPLODE_AT)
        self.play(bm.explode.animate.set_value(1.0), run_time=EXPLODE_DURATION, rate_func=smooth)
        t = EXPLODE_AT + EXPLODE_DURATION

        # part labels, with leader lines to points facing the right side of the screen
        anchors = {
            "cover": bm.anchor("cover", COVER_R, RIGHT_DEG, WALL_H),
            "arbor": bm.anchor("arbor_hi", SHAFT_R, RIGHT_DEG, FLOOR + CORE_H + SHAFT_L * 0.6),
            "spring": bm.anchor("spring", R_IN - 0.2, RIGHT_DEG, FLOOR + SPRING_H * 0.6),
            "drum": bm.anchor("drum", R_ROOT, RIGHT_DEG, WALL_H * 0.5),
        }
        labels, ys = {}, []
        for k in ("cover", "arbor", "spring", "drum"):                 # top to bottom on screen
            a = screen(anchors[k])
            y = a[1] if not ys else min(a[1], ys[-1] - 0.55)
            ys.append(y)
            name = Text(LABELS[k][0], font=FONT_SANS, weight=BOLD, color=GLOW).scale(0.36)
            num = Text(LABELS[k][1], font=FONT_SANS, color=GREY_B).scale(0.30)
            txt = VGroup(name, num).arrange(RIGHT, buff=0.16, aligned_edge=DOWN)
            txt.move_to([LABEL_X, y, 0], aligned_edge=LEFT)
            dot = Dot([a[0], a[1], 0], radius=0.035, color=GLOW)
            lead = Line([a[0], a[1], 0], [LABEL_X - 0.12, y, 0]).set_stroke(GLOW, 1.4, 0.8)
            labels[k] = VGroup(lead, dot, txt)
        note = Text(SPRING_NOTE, font=FONT_SANS, color=GREY_B).scale(0.24)
        note.next_to(labels["spring"][2], DOWN, aligned_edge=LEFT, buff=0.1)
        self.add_fixed_in_frame_mobjects(*labels.values(), note)
        self.remove(*labels.values(), note)

        def show(m):
            return AnimationGroup(Create(m[0]), FadeIn(m[1]), FadeIn(m[2], shift=RIGHT * 0.15), run_time=0.7)

        for k in ("drum", "cover", "arbor", "spring"):
            wait_until(LABEL_TIMES[k])
            self.play(show(labels[k]))
            t = LABEL_TIMES[k] + 0.7
        wait_until(LABEL_TIMES["spring_note"])
        self.play(FadeIn(note, shift=UP * 0.1), run_time=0.6)
        t = LABEL_TIMES["spring_note"] + 0.6

        # back together without the cover; look down on the coil
        wait_until(ASSEMBLE_AT)
        t = ASSEMBLE_AT
        cam = dict(CAM_HOOKS)
        hook_target = c + OUT * (Z0 + LIFT) + SCREEN_RIGHT * SHIFT_HOOKS
        self.play(*camera_move(self, ASSEMBLE_DURATION + 0.2, rate_func=rate_functions.ease_in_out_sine,
                               target=hook_target, frame_origin=origin, **cam),
                  bm.explode.animate(run_time=ASSEMBLE_DURATION, rate_func=smooth).set_value(0.0),
                  bm.show_cover.animate(run_time=1.0).set_value(0.0),
                  FadeOut(VGroup(*labels.values(), note), run_time=0.6))
        self.remove(self.camera._frame_center)
        t = ASSEMBLE_AT + ASSEMBLE_DURATION + 0.2

        # insets: magnified top views of the two hooks
        rot = -(THETA + 90)                                    # barrel frame -> screen orientation
        z_top = FLOOR + SPRING_H
        hooks = {"inner": bm.anchor("spring", CORE_R + 0.1, HOOK_IN_DEG, z_top),
                 "outer": bm.anchor("spring", R_IN - 0.1, HOOK_OUT_DEG, z_top)}
        inset_pos = {"inner": np.array([4.2, 1.55, 0]), "outer": np.array([4.2, -1.55, 0])}
        insets = {}
        for k in ("inner", "outer"):
            items, p = inset_g(k)
            field = Point(p[0], p[1]).buffer(INSET_FIELD, quad_segs=24)
            s = INSET_R / INSET_FIELD
            g = VGroup(Circle(radius=INSET_R).set_fill(BG, 1).set_stroke(width=0))
            for geom, col, stroke in items:
                clip = geom.intersection(field)
                if clip.is_empty:
                    continue
                clip = affinity.translate(clip, -p[0], -p[1])
                clip = affinity.scale(affinity.rotate(clip, rot, origin=(0, 0)), s, s, origin=(0, 0))
                g.add(vm(clip, col, stroke=stroke, sw=1.0))
            g.add(Circle(radius=INSET_R).set_stroke(GLOW, 2))
            g.move_to(inset_pos[k])
            cap = Text(INSETS[k], font=FONT_SANS, color=GREY_B).scale(0.26).next_to(g, DOWN, buff=0.12)
            h = screen(hooks[k])
            ring = Circle(radius=0.11).set_stroke(GLOW, 2.5).move_to([h[0], h[1], 0])
            edge = inset_pos[k] + normalize(np.array([h[0], h[1], 0]) - inset_pos[k]) * INSET_R
            lead = Line([h[0], h[1], 0], edge).set_stroke(GLOW, 1.4, 0.8)
            insets[k] = VGroup(ring, lead, g, cap)
            self.add_fixed_in_frame_mobjects(insets[k])
            self.remove(insets[k])
        for k in ("inner", "outer"):
            wait_until(INSET_TIMES[k])
            ring, lead, g, cap = insets[k]
            self.play(Create(ring), Create(lead), FadeIn(g, scale=0.8), FadeIn(cap), run_time=0.8)
            t = INSET_TIMES[k] + 0.8

        # pull back; the barrel drops back to the movement's plane and the center pinion appears;
        # the arbor is held, so the spring turns the drum, and the drum turns the pinion
        wait_until(DRIVE_AT)
        t = DRIVE_AT
        self.add(pinion)
        mid = c + (P["center"] - c) * DRIVE_FOCUS + OUT * Z0
        self.play(*camera_move(self, DRIVE_MOVE, rate_func=rate_functions.ease_in_out_sine, target=mid,
                               frame_origin=origin, **CAM_DRIVE),
                  bm.lift.animate(run_time=DRIVE_MOVE, rate_func=smooth).set_value(0.0),
                  FadeOut(VGroup(*insets.values()), run_time=0.6),
                  pinion.animate(run_time=DRIVE_MOVE, rate_func=rate_functions.ease_in_quad).set_opacity(1))
        self.remove(self.camera._frame_center)
        t = DRIVE_AT + DRIVE_MOVE

        # "held" and pinion labels
        top_arbor = bm.anchor("arbor_hi", 0, 0, FLOOR + CORE_H + SHAFT_L + 0.7)
        ha = screen(top_arbor)
        def backed(txt):
            back = RoundedRectangle(corner_radius=0.08, width=txt.width + 0.3, height=txt.height + 0.22)
            return VGroup(back.move_to(txt).set_fill(BG, TEXT_BACKING).set_stroke(width=0), txt)

        held_ring = Circle(radius=0.16).set_stroke(GLOW, 3).move_to([ha[0], ha[1], 0])
        held = backed(Text(HELD, font=FONT_SANS, weight=BOLD, color=GLOW).scale(0.30))
        held.move_to([ha[0] + 1.9, ha[1] + 1.5, 0], aligned_edge=LEFT)
        held = VGroup(Line(held_ring.point_at_angle(PI / 4), held[0].get_left()).set_stroke(GLOW, 1.4, 0.8), held)
        pa = screen(P["center"] + OUT * (Z0 + 2.0 * MM))
        pin_txt = backed(Text(PINION, font=FONT_SANS, color=GREY_B).scale(0.28))
        pin_txt.move_to([pa[0] - 0.6, pa[1] - 1.5, 0], aligned_edge=RIGHT)
        pin_lead = Line([pa[0], pa[1] - 0.12, 0], pin_txt[0].get_top()).set_stroke(GLOW, 1.4, 0.8)
        self.add_fixed_in_frame_mobjects(held_ring, held, pin_lead, pin_txt)
        self.remove(held_ring, held, pin_lead, pin_txt)
        wait_until(HELD_AT)
        self.play(Create(held_ring), Create(held[0]), FadeIn(held[1]), run_time=0.7)
        t = max(t, HELD_AT) + 0.7
        wait_until(TURN_AT)
        self.play(bm.drum_turn.animate.set_value(-DRUM_SWEEP * DEGREES),
                  cue(TURN_AT + 1.6, Create(pin_lead), FadeIn(pin_txt), start=TURN_AT, end=TURN_AT + TURN_DURATION,
                      run_time=0.7),
                  run_time=TURN_DURATION, rate_func=rate_functions.ease_in_out_sine)

        self.wait(FINAL_HOLD)
        self.remove(curtain)
        self.add_fixed_in_frame_mobjects(curtain)
        self.play(FadeOut(VGroup(held_ring, held, pin_lead, pin_txt)), curtain.animate.set_fill(opacity=1),
                  run_time=FADE_OUT)
