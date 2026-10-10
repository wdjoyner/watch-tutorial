"""Film 2, scene 03 - "Winding": the movement opens into its tiers and the crown
is turned; a glow follows the winding path (crown, stem, winding pinion, crown
wheel, ratchet wheel, arbor) while an inset shows the spring moving from the
drum wall onto the arbor. Close-up on the click, then both power paths:
winding into the arbor, running out of the drum.

Build (render + voice + mux):   python build.py scene03_winding
Render only (quick preview):    PYTHONPATH=.:films/film02_power_source manim -ql films/film02_power_source/scene03_winding.py Scene03
Narration lines and their start times live in scene03_winding.voice.txt.

Click sounds: each time the ratchet wheel advances one tooth (1/16 of a crown
turn: 16-tooth winding pinion, 60-tooth ratchet), the click drops off a tooth.
The scene computes those times from its winding schedule and writes them to
scene03_winding.sfx.txt, which build.py mixes in. That file is generated on
every render; edit WIND_* below, not the file.
"""
import os
from manim import *
from movement import (Movement, attach_driver, vignette, camera_move, cue, polar, P, R, WIND_TEETH,
                      BG, GLOW, FONT_SANS, BRASS, BRASS_DK, BRASS_HI, STEEL, STEEL_HI, RUBY_HI)
from barrel import pack_state_g, arbor_core_g, drum_floor_g, drum_wall_g, development, vm, R_IN, R_ROOT

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds, angles in degrees.
# Keep the timeline roughly in step with scene03_winding.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 1.4
OPEN_AT, OPEN_DURATION = 0.4, 3.4         # the tiers separate; the camera comes around
WIND_START, WIND_END = 4.6, 27.8          # the crown is turned
WIND_TURNS = 14.0                         # crown turns over the winding
PATH_AT, PATH_DURATION = 4.6, 6.6         # the glow travels crown -> arbor
LABEL_TIMES = {"crown": 4.7, "winding_pinion": 5.9, "crown_wheel": 7.4, "ratchet": 9.2, "arbor": 10.9}
INSET_AT = 13.4                           # "The arbor reels the spring in tight"
CLICK_MOVE_AT, CLICK_MOVE = 15.2, 2.6     # push in on the ratchet and click
CLICK_LABEL_AT = 17.9
ONE_WAY_AT = 19.6                         # "one way only"
BLOCKED_AT = 21.8                         # "cannot unwind backward"
WIDE_AT, WIDE_MOVE = 28.0, 2.8            # pull back for the two paths
WINDING_PATH_AT, RUNNING_PATH_AT, MEET_AT = 28.8, 30.8, 32.8
PATH_FLASH = 2.4
FINAL_HOLD = 1.6
FADE_OUT = 1.5

# --- tiers --------------------------------------------------------------
Z_ASSEMBLED = {"dial": 0.00, "engine": 0.30, "top": 0.62}
Z_EXPLODED = {"dial": -1.1, "engine": 0.0, "top": 1.1}
DIM_OPEN = {"dial": 0.45, "engine": 0.55, "top": 0.6}        # see-through while the path is traced
DIM_CLICK = {"dial": 0.25, "engine": 0.3, "top": 1.0}        # the top tier in full for the close-up
DIM_PATHS = {"dial": 0.35, "engine": 0.6, "top": 0.3}        # the two paths, at the end

# --- camera (phi = 0 is straight down) --------------------------------
CAM_START = dict(phi=30, theta=-60, zoom=1.05)
CAM_WIND = dict(phi=64, theta=-62, zoom=1.5)
WIND_TARGET = (1.7, 0.3, 0.0)
CAM_CLICK = dict(phi=38, theta=-72, zoom=3.2)
CAM_WIDE = dict(phi=62, theta=-62, zoom=1.15)
WIDE_TARGET = (0.5, 0.0, 0.0)

# --- colors and inset --------------------------------------------------
WIND_COLOR = "#ffb54a"                    # the winding path (amber, as the lit mainspring in scene 01)
RUN_COLOR = GLOW                          # the running path
INSET_POS = (4.75, 1.85)                  # screen position of the inset's center
INSET_R = 1.25
INSET_START = 0.4                         # arbor turns already wound when the inset appears
SFX_LEVEL = 1.0                           # per-click level written to the .sfx.txt file

# --- on-screen text --------------------------------------------------
LABELS = {"crown": "crown", "winding_pinion": "winding pinion", "crown_wheel": "crown wheel",
          "ratchet": "ratchet wheel", "arbor": "arbor"}
INSET_CAPTION = "the spring, from above"
CLICK_TEXT = "click"
PATH_TEXT = {"winding": "winding  ·  turns the arbor", "running": "running  ·  turns the drum"}
# =====================================================================

WIND_RATE = rate_functions.ease_in_out_sine


def crown_turns(t):
    if t <= WIND_START:
        return 0.0
    if t >= WIND_END:
        return WIND_TURNS
    return WIND_TURNS * WIND_RATE((t - WIND_START) / (WIND_END - WIND_START))


def click_times():
    """Times at which the ratchet passes a tooth (one per 1/16 crown turn)."""
    per_tooth = 1 / WIND_TEETH["winding_pinion"]
    ts = np.linspace(WIND_START, WIND_END, 20000)
    turns = np.array([crown_turns(t) for t in ts])
    k = np.arange(1, int(WIND_TURNS / per_tooth) + 1) * per_tooth
    return np.interp(k, turns, ts)


def write_sfx():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scene03_winding.sfx.txt")
    with open(path, "w") as f:
        f.write("# Generated by scene03_winding.py on every render; edit its WIND_* settings instead.\n")
        f.write("# time_in_seconds | sound | level\n")
        for t in click_times():
            f.write(f"{t:.3f} | click | {SFX_LEVEL}\n")


class Scene03(ThreeDScene):
    def construct(self):
        write_sfx()
        self.camera.background_color = BG
        origin = ORIGIN                           # screen position of a 3D point = project_point(p)[:2]
        self.set_camera_orientation(phi=CAM_START["phi"] * DEGREES, theta=CAM_START["theta"] * DEGREES,
                                    zoom=CAM_START["zoom"], frame_center=origin)
        self.add_fixed_in_frame_mobjects(vignette())

        mv = Movement()
        explode, dim = attach_driver(self, mv, Z_ASSEMBLED, Z_EXPLODED)
        clock = {"t": 0.0}
        tick = Mobject()
        tick.add_updater(lambda m, dt: clock.__setitem__("t", clock["t"] + dt))
        self.add(tick)

        def wait_until(when):
            d = when - self.renderer.time
            if d > 1e-3:
                self.wait(d)

        def screen(p):
            return np.array([*self.camera.project_point(p)[:2], 0.0])

        curtain = FullScreenRectangle().set_fill(BG, 1).set_stroke(width=0)
        self.add_fixed_in_frame_mobjects(curtain)

        # ---------------------------------------------------------- open the tiers
        seg = dict(start=0.0, end=OPEN_AT + OPEN_DURATION)
        self.play(cue(0.0, curtain.animate.set_fill(opacity=0), run_time=FADE_IN, **seg),
                  cue(OPEN_AT, explode.animate.set_value(1.0),
                      *[dim[k].animate.set_value(v) for k, v in DIM_OPEN.items()],
                      *camera_move(self, OPEN_DURATION, target=np.array(WIND_TARGET), frame_origin=origin, **CAM_WIND),
                      run_time=OPEN_DURATION, **seg))
        self.remove(self.camera._frame_center)

        # now that the tiers have settled: points along the winding path, in world coordinates
        pts = {"crown": mv.parts["crown"].get_center(),
               "winding_pinion": np.array([P["winding_pinion"][0], 0.0, mv.parts["stem"].get_center()[2]]),
               "crown_wheel": mv.parts["crown_wheel"].get_center() + OUT * 0.05,
               "ratchet": mv.parts["ratchet_wheel"].get_center() + OUT * 0.05,
               "arbor": mv.parts["barrel"].get_center() + OUT * 0.1}
        wind_pts = [pts["crown"], pts["winding_pinion"], pts["winding_pinion"] + OUT * 0.5,
                    pts["crown_wheel"] - OUT * 0.3, pts["crown_wheel"], pts["ratchet"], pts["arbor"]]
        wind_path = VMobject().set_points_smoothly(wind_pts).set_stroke(WIND_COLOR, 7, 0.95)
        wind_trace = wind_path.copy().set_stroke(WIND_COLOR, 2.0, 0.5)
        train = ["barrel", "center_wheel", "third_wheel", "fourth_wheel", "escape_wheel", "pallet_fork", "balance"]
        run_pts = [mv.parts[k].get_center() + OUT * 0.06 for k in train]
        run_path = VMobject().set_points_as_corners(run_pts).set_stroke(RUN_COLOR, 8, 1.0)
        ring_r = {"crown": 0.34, "winding_pinion": 0.2, "crown_wheel": R["crown_wheel"] * 1.05,
                  "ratchet": R["ratchet"] * 1.05, "arbor": 0.22}
        rings = {k: Circle(radius=ring_r[k], num_components=48).move_to(pts[k]).set_stroke(GLOW, 4, 0)
                 for k in pts}
        self.add(*rings.values())

        # turning arrow around the stem, at the crown
        cz = pts["crown"]
        arc = Arc(radius=0.42, start_angle=-0.4 * PI, angle=1.5 * PI, stroke_width=4, color=WIND_COLOR)
        arc.add_tip(tip_length=0.14, tip_width=0.14)
        arc.rotate(PI / 2, axis=UP).move_to(cz + RIGHT * 0.25)

        # labels with leader lines, placed from the settled camera
        labels = {}
        offsets = {"crown": (0.9, -1.0), "winding_pinion": (-1.3, -1.25), "crown_wheel": (0.9, 0.7),
                   "ratchet": (-2.0, 0.35), "arbor": (-1.7, -0.6)}
        for k, (dx, dy) in offsets.items():
            a = screen(pts[k])
            txt = Text(LABELS[k], font=FONT_SANS, weight=BOLD, color=GLOW).scale(0.32)
            spot = a + np.array([dx, dy, 0])
            txt.move_to(spot, aligned_edge=LEFT if dx > 0 else RIGHT)
            back = RoundedRectangle(corner_radius=0.06, width=txt.width + 0.24, height=txt.height + 0.18)
            back.move_to(txt).set_fill(BG, 0.7).set_stroke(width=0)
            lead = Line(a, txt.get_left() + LEFT * 0.1 if dx > 0 else txt.get_right() + RIGHT * 0.1)
            lead.set_stroke(GLOW, 1.4, 0.8)
            labels[k] = VGroup(lead, back, txt)
        self.add_fixed_in_frame_mobjects(*labels.values())
        self.remove(*labels.values())

        # ---------------------------------------------------------- the inset
        s_in = INSET_R / (R_ROOT + 0.4)                           # mm -> screen units
        frame_in = VGroup(Circle(radius=INSET_R).set_fill(BG, 1).set_stroke(width=0),
                          vm(affinity_scale(drum_floor_g(), s_in), BRASS_DK, stroke=BRASS_DK, sw=0),
                          vm(affinity_scale(drum_wall_g(), s_in), BRASS, stroke=BRASS_HI, sw=0.8))
        border = Circle(radius=INSET_R).set_stroke(GLOW, 2)
        cap = Text(INSET_CAPTION, font=FONT_SANS, color=GREY_B).scale(0.26)
        dev = development()
        show_inset = ValueTracker(0.0)

        def inset():
            ratchet_turns = crown_turns(clock["t"]) * WIND_TEETH["winding_pinion"] / WIND_TEETH["ratchet"]
            a_turns = min(dev, INSET_START + ratchet_turns)
            inner, outer, free, arbor_deg, w = pack_state_g(a_turns, outer_deg=200.0)
            op = show_inset.get_value()
            core = shapely_rotate(arbor_core_g(), arbor_deg - 55.0)       # its hook follows the inner end
            g = VGroup(frame_in.copy(),
                       vm(affinity_scale(outer, s_in), STEEL_HI, stroke=WHITE, sw=0.4),
                       vm(affinity_scale(inner, s_in), STEEL_HI, stroke=WHITE, sw=0.4),
                       vm(affinity_scale(free, s_in), STEEL_HI, stroke=WHITE, sw=0.4),
                       vm(affinity_scale(core, s_in), STEEL, stroke=STEEL_HI, sw=0.6),
                       border.copy())
            g.move_to(np.array([*INSET_POS, 0]))
            for m in g.family_members_with_points():        # fade each part, keeping its own opacities
                m.set_fill(opacity=m.get_fill_opacity() * op, family=False)
                m.set_stroke(opacity=m.get_stroke_opacity() * op, family=False)
            return g

        inset_mob = always_redraw(inset)
        cap.next_to(np.array([INSET_POS[0], INSET_POS[1] - INSET_R, 0]), DOWN, buff=0.14)
        cap_back = RoundedRectangle(corner_radius=0.06, width=cap.width + 0.26, height=cap.height + 0.18)
        cap = VGroup(cap_back.move_to(cap).set_fill(BG, 0.75).set_stroke(width=0), cap)
        self.add_fixed_in_frame_mobjects(inset_mob, cap)
        cap.set_opacity(0)

        # ---------------------------------------------------------- click close-up pieces
        br = P["barrel"][:2]
        z_top = mv.parts["ratchet_wheel"].get_center()[2] + 0.06
        click_pt = np.array([*(br + polar(R["ratchet"] + 0.16, 156)[:2]), z_top])
        click_target = np.array([*(br + polar(R["ratchet"] * 0.55, 150)[:2]), z_top])
        bc = np.array([br[0], br[1], z_top])

        def rim_arc(r, a0, a1, color, width=3.5):
            m = Arc(radius=r, start_angle=a0 * DEGREES, angle=(a1 - a0) * DEGREES, arc_center=bc,
                    stroke_width=width, color=color)
            return m.add_tip(tip_length=0.07, tip_width=0.07)

        allowed = rim_arc(R["ratchet"] + 0.22, 172, 206, WIND_COLOR)
        blocked = rim_arc(R["ratchet"] + 0.42, 206, 172, RUBY_HI)
        mid = bc + polar(R["ratchet"] + 0.42, 189)
        cross = VGroup(Line(mid + (UP + LEFT) * 0.09, mid + (DOWN + RIGHT) * 0.09),
                       Line(mid + (UP + RIGHT) * 0.09, mid + (DOWN + LEFT) * 0.09)).set_stroke(RUBY_HI, 4)

        # ---------------------------------------------------------- winding schedule helpers
        def wind_to(t_end):
            """Animate mv.wind from its value now to its value at t_end, following crown_turns()."""
            t_a = self.renderer.time
            v_a, v_b = crown_turns(t_a), crown_turns(t_end)
            span = max(v_b - v_a, 1e-9)
            rf = lambda u: (crown_turns(t_a + u * (t_end - t_a)) - v_a) / span
            return mv.wind.animate(rate_func=rf, run_time=t_end - t_a).set_value(v_b)

        def pulse(k, run_time=1.0):
            return rings[k].animate(rate_func=there_and_back, run_time=run_time).set_stroke(opacity=0.9)

        def show(k):
            lead, back, txt = labels[k]
            return AnimationGroup(Create(lead), FadeIn(back), FadeIn(txt), pulse(k), run_time=0.8)

        # ---------------------------------------------------------- 1. turn the crown; trace the winding path
        t = self.renderer.time
        seg = dict(start=t, end=INSET_AT)
        self.play(wind_to(INSET_AT),
                  cue(WIND_START, FadeIn(arc), run_time=0.6, **seg),
                  cue(PATH_AT, ShowPassingFlash(wind_path.copy(), time_width=0.25), Create(wind_trace),
                      run_time=PATH_DURATION, **seg),
                  *[cue(LABEL_TIMES[k], show(k), run_time=0.8, **seg) for k in LABELS],
                  cue(INSET_AT - 0.9, *[FadeOut(m) for m in labels.values()], run_time=0.8, **seg))

        # ---------------------------------------------------------- 2. the inset; push in on the click
        click_label = Text(CLICK_TEXT, font=FONT_SANS, weight=BOLD, color=GLOW).scale(0.34)
        seg = dict(start=INSET_AT, end=CLICK_MOVE_AT + CLICK_MOVE)
        self.play(wind_to(CLICK_MOVE_AT + CLICK_MOVE),
                  cue(INSET_AT, show_inset.animate.set_value(1.0), cap[0].animate.set_fill(opacity=0.75), cap[1].animate.set_opacity(1), run_time=0.8, **seg),
                  cue(CLICK_MOVE_AT, *camera_move(self, CLICK_MOVE, target=click_target, frame_origin=origin, **CAM_CLICK),
                      *[dim[k].animate.set_value(v) for k, v in DIM_CLICK.items()],
                      FadeOut(arc), wind_trace.animate.set_stroke(opacity=0),
                      run_time=CLICK_MOVE, **seg))
        self.remove(self.camera._frame_center)

        # ---------------------------------------------------------- 3. the click: one way only
        cp = screen(click_pt)
        click_label.move_to(cp + np.array([-1.6, 1.0, 0]), aligned_edge=RIGHT)
        click_lead = Line(cp, click_label.get_right() + RIGHT * 0.1).set_stroke(GLOW, 1.4, 0.8)
        self.add_fixed_in_frame_mobjects(click_lead, click_label)
        self.remove(click_lead, click_label)
        t = self.renderer.time
        seg = dict(start=t, end=WIND_END)
        self.play(wind_to(WIND_END),
                  cue(CLICK_LABEL_AT, Create(click_lead), FadeIn(click_label), run_time=0.7, **seg),
                  cue(ONE_WAY_AT, Create(allowed), run_time=0.7, **seg),
                  cue(BLOCKED_AT, Create(blocked), FadeIn(cross), run_time=0.7, **seg))

        # ---------------------------------------------------------- 4. two paths meet in one spring
        wait_until(WIDE_AT)
        run_trace = run_path.copy().set_stroke(RUN_COLOR, 3.0, 0.75)
        barrel_ring = Circle(radius=R["barrel"] * 1.06, num_components=64).move_to(pts["arbor"] - OUT * 0.04)
        barrel_ring.set_stroke(GLOW, 5, 0)
        self.add(barrel_ring)
        legend = VGroup()
        for k, col in (("winding", WIND_COLOR), ("running", RUN_COLOR)):
            dash = Line(ORIGIN, RIGHT * 0.45).set_stroke(col, 4)
            txt = Text(PATH_TEXT[k], font=FONT_SANS, color=GREY_B).scale(0.28)
            legend.add(VGroup(dash, txt).arrange(RIGHT, buff=0.15))
        legend.arrange(DOWN, aligned_edge=LEFT, buff=0.16).to_corner(DL, buff=0.55)
        backing = RoundedRectangle(corner_radius=0.12, width=legend.width + 0.5, height=legend.height + 0.4)
        backing.move_to(legend).set_fill(BG, 0.72).set_stroke(width=0)
        self.add_fixed_in_frame_mobjects(backing, legend)
        self.remove(backing, legend)
        t = WIDE_AT
        seg = dict(start=t, end=MEET_AT + PATH_FLASH)
        self.play(cue(t, *camera_move(self, WIDE_MOVE, target=np.array(WIDE_TARGET), frame_origin=origin, **CAM_WIDE),
                      *[dim[k].animate.set_value(v) for k, v in DIM_PATHS.items()],
                      *[FadeOut(m) for m in (click_lead, click_label, cap)], show_inset.animate.set_value(0),
                      FadeOut(allowed), FadeOut(blocked), FadeOut(cross),
                      run_time=WIDE_MOVE, **seg),
                  cue(WINDING_PATH_AT, ShowPassingFlash(wind_path.copy(), time_width=0.35),
                      wind_trace.animate.set_stroke(width=3.0, opacity=0.8), FadeIn(backing), FadeIn(legend[0]),
                      run_time=PATH_FLASH, **seg),
                  cue(RUNNING_PATH_AT, ShowPassingFlash(run_path.copy(), time_width=0.35), Create(run_trace),
                      FadeIn(legend[1]), run_time=PATH_FLASH, **seg),
                  cue(MEET_AT, barrel_ring.animate(rate_func=there_and_back_with_pause).set_stroke(opacity=0.9),
                      run_time=PATH_FLASH, **seg))
        self.remove(self.camera._frame_center)

        self.wait(FINAL_HOLD)
        self.remove(curtain)
        self.add_fixed_in_frame_mobjects(curtain)
        self.play(FadeOut(VGroup(backing, legend)), curtain.animate.set_fill(opacity=1), run_time=FADE_OUT)


def affinity_scale(g, s):
    from shapely import affinity
    return affinity.scale(g, s, s, origin=(0, 0))


def shapely_rotate(g, deg):
    from shapely import affinity
    return affinity.rotate(g, deg, origin=(0, 0))
