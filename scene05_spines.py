"""Scene 05 - "The Spines": the movement opens into its three tiers and the
camera travels down the center wheel's arbor, from the top bridge, through the
middle tier, through the main plate to the hands; then it pulls back as the
winding stem's path is traced from the crown to the mainspring.

Build (render + voice + mux):   python build.py scene05_spines
Render only (quick preview):    manim -ql scene05_spines.py Scene05

Stylized cross-section: the tiers are dimmed so the arbor reads through them
like an X-ray. The arbor is a scene-local cylinder shaded toward the camera on
every frame; the hands are added below the dial tier. movement.py is unchanged.
"""
from manim import *
from movement import (Movement, attach_driver, vignette, camera_move, cue, state, P, R,
                      BG, GLOW, FONT_SANS, STEEL, STEEL_DK, STEEL_HI)

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds, angles in degrees.
# Keep the timeline roughly in step with scene05_spines.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 1.6
OPEN_AT, OPEN_END = 1.4, 5.0         # tiers separate, dim, arbor appears
DESCEND_END = 10.6                   # camera travels down the arbor (starts at OPEN_END)
PASS_TIMES = {"top": 5.8, "engine": 7.7, "dial": 9.5}   # ring pulse as the camera passes each tier
PULLBACK_END = 13.4                  # camera pulls back to show the winding stem
SNAKE_AT, SNAKE_DURATION = 13.7, 3.6 # glow from the crown to the mainspring
END_HOLD = 2.4
FADE_OUT = 1.5
LABEL_TIMES = {"title": 1.6, "arbor": 6.0, "stem": 10.8}
LABEL_FADE = 0.5
LABEL_BACKING = 0.72

# --- tiers --------------------------------------------------------------
Z_ASSEMBLED = {"dial": 0.00, "engine": 0.30, "top": 0.62}
Z_EXPLODED = {"dial": -1.6, "engine": 0.0, "top": 1.6}
TIER_DIM = 0.42                      # opacity of the tiers once the cross-section opens
PLATE_SEE_THROUGH = 0.22             # dial tier opacity as the camera reaches the hands

# --- camera --------------------------------------------------------------
CAM_START = dict(phi=62, theta=-75, zoom=1.15, center=(0.0, 0.0, 0.3))
CAM_TOP = dict(phi=72, theta=-82, zoom=2.4, target=(0.0, 0.0, 1.85))
CAM_BOTTOM = dict(phi=74, theta=-98, zoom=2.4, target=(0.0, 0.0, -1.85))
CAM_WIDE = dict(phi=70, theta=-62, zoom=1.05, target=(0.9, 0.3, -0.1))

# --- arbor and hands ---------------------------------------------------
ARBOR_TOP, ARBOR_BOTTOM = 1.88, -2.05   # z extent (exploded heights)
ARBOR_R = 0.05
HANDS_Z = -1.98
LIGHT = (0.75, -0.45, 0.5)              # from the side, for depth

# --- dust motes --------------------------------------------------------
MOTES = 70
MOTE_OPACITY = 0.55

# --- on-screen text --------------------------------------------------
TITLE = ("THE SPINES", "what ties the three tiers together")
ITEMS = {
    "arbor": "center wheel arbor  ·  carries the hands",
    "stem": "winding stem  ·  crown to mainspring",
}
# =====================================================================


def _unit(v):
    return v / np.linalg.norm(v)


def cylinder(p0, p1, r, v, light, color=STEEL, bands=18):
    """A shaded cylinder from p0 to p1, as seen from direction v (toward the viewer)."""
    axis = _unit(p1 - p0)
    w = v - np.dot(v, axis) * axis
    w = _unit(w) if np.linalg.norm(w) > 1e-6 else _unit(np.cross(axis, RIGHT))
    m = np.cross(axis, w)
    g = VGroup()
    al = np.linspace(0, PI, bands + 1)
    for a0, a1 in zip(al[:-1], al[1:]):
        am = (a0 + a1) / 2
        n = np.cos(am) * m + np.sin(am) * w
        d = max(0.0, np.dot(n, light))
        spec = max(0.0, np.dot(n, _unit(light + v))) ** 30
        col = interpolate_color(ManimColor(STEEL_DK), ManimColor(color), min(1, 0.25 + 0.9 * d))
        col = interpolate_color(col, ManimColor(WHITE), min(1, spec))
        o0, o1 = r * (np.cos(a0) * m + np.sin(a0) * w), r * (np.cos(a1) * m + np.sin(a1) * w)
        g.add(Polygon(p0 + o0, p1 + o0, p1 + o1, p0 + o1).set_fill(col, 1).set_stroke(col, 0.5))
    return g


def hand(length, width, tail, color):
    """A flat leaf hand pointing along +x, in the xy-plane."""
    pts = [(-tail, 0), (-tail * 0.6, width * 0.7), (length * 0.35, width), (length, 0),
           (length * 0.35, -width), (-tail * 0.6, -width * 0.7)]
    return Polygon(*[np.array([x, y, 0]) for x, y in pts]).set_fill(color, 1).set_stroke(STEEL_DK, 0.8)


class Scene05(ThreeDScene):
    def construct(self):
        self.camera.background_color = BG
        self.set_camera_orientation(phi=CAM_START["phi"] * DEGREES, theta=CAM_START["theta"] * DEGREES,
                                    zoom=CAM_START["zoom"], frame_center=np.array(CAM_START["center"]))
        origin = CAM_START["center"]
        self.add_fixed_in_frame_mobjects(vignette())

        clock = {"t": 0.0}
        ticker = Mobject().add_updater(lambda m, dt: clock.__setitem__("t", clock["t"] + dt))
        self.add(ticker)

        mv = Movement()
        explode, dim = attach_driver(self, mv, Z_ASSEMBLED, Z_EXPLODED)
        light = _unit(np.array(LIGHT))

        # the arbor, redrawn each frame so its shading follows the camera
        show = ValueTracker(0.0)

        def arbor_z(e):
            """Heights along the arbor: bottom end, under the plate, engine, top tier, top end."""
            lerp = lambda k: Z_ASSEMBLED[k] + (Z_EXPLODED[k] - Z_ASSEMBLED[k]) * e
            return [-0.15 + (ARBOR_BOTTOM + 0.15) * e, lerp("dial") - 0.14, lerp("engine") + 0.06,
                    lerp("top") + 0.06, Z_ASSEMBLED["top"] + 0.26 + (ARBOR_TOP - Z_ASSEMBLED["top"] - 0.26) * e]

        def arbor_segment(i):
            def draw():
                v = self.camera.generate_rotation_matrix()[2]
                z = arbor_z(explode.get_value())
                if z[i + 1] - z[i] < 1e-3:
                    return VGroup()
                return cylinder(OUT * z[i], OUT * z[i + 1], ARBOR_R, v, light, STEEL_HI).set_opacity(show.get_value())
            return always_redraw(draw)

        # hands at the lower end of the arbor; the minute hand follows the center wheel
        hands_show = ValueTracker(0.0)

        def hands():
            s = state(clock["t"])
            z = -0.15 + (HANDS_Z + 0.15) * explode.get_value()
            hr = hand(0.85, 0.07, 0.15, STEEL).rotate(PI / 2 + 1.1 + s["center"] / 12, about_point=ORIGIN)
            mn = hand(1.25, 0.05, 0.22, STEEL_HI).rotate(PI / 2 - 0.4 + s["center"], about_point=ORIGIN)
            hub = Circle(radius=0.07).set_fill(STEEL_HI, 1).set_stroke(STEEL_DK, 1)
            g = VGroup(hr, mn.shift(IN * 0.02), hub.shift(IN * 0.03)).shift(OUT * z)
            return g.set_opacity(hands_show.get_value())

        # dust motes drifting through the stack
        rng = np.random.default_rng(5)
        seeds = rng.uniform([-2.8, -2.8, -1.9, 0], [2.8, 2.8, 1.9, TAU], (MOTES, 4))
        seeds = seeds[seeds[:, 0] ** 2 + seeds[:, 1] ** 2 < 7.5]
        motes_show = ValueTracker(0.0)

        def motes():
            t = clock["t"]
            g = VGroup()
            for x, y, z, ph in seeds:
                p = np.array([x + 0.08 * np.sin(0.3 * t + ph), y + 0.08 * np.cos(0.23 * t + ph), z + 0.05 * t % 0.6])
                tw = 0.5 + 0.5 * np.sin(1.7 * t + 3 * ph)
                g.add(Dot(p, radius=0.011, color=GLOW).set_opacity(MOTE_OPACITY * tw * motes_show.get_value()))
            return g

        # rings that pulse as the camera passes each tier's part on the arbor
        ring_spec = {"top": (0.17, Z_EXPLODED["top"] + 0.26), "engine": (R["center"] * 1.04, Z_EXPLODED["engine"] + 0.12),
                     "dial": (0.3, Z_EXPLODED["dial"] + 0.12)}
        rings = {k: Circle(radius=r, num_components=48).move_to(OUT * z).set_stroke(GLOW, 4, 0)
                 for k, (r, z) in ring_spec.items()}

        # the winding path: crown -> stem -> winding pinion -> crown wheel -> ratchet -> barrel
        zd, ze, zt = Z_EXPLODED["dial"], Z_EXPLODED["engine"], Z_EXPLODED["top"]
        cwp = P["barrel"] + np.array([0.88 * np.cos(np.radians(15)), 0.88 * np.sin(np.radians(15)), 0])
        snake_pts = [np.array([3.95, 0, zd + 0.18]), np.array([2.1, 0, zd + 0.12]),
                     np.array([1.6, 0.25, ze - 0.4]), np.array([cwp[0], cwp[1], zt + 0.2]),
                     np.array([P["barrel"][0], P["barrel"][1], zt + 0.22]),
                     np.array([P["barrel"][0], P["barrel"][1], ze + 0.15])]
        snake = VMobject().set_points_smoothly(snake_pts).set_stroke(GLOW, 7, 0.95)
        snake_trace = snake.copy().set_stroke(GLOW, 1.5, 0)

        # draw order, bottom to top: hands, arbor below the plate, dial tier, arbor, engine, arbor, top, arbor
        group = next(m for m in self.mobjects if isinstance(m, VGroup) and mv.tiers["dial"] in m.submobjects)
        i = self.mobjects.index(group)
        segs = [arbor_segment(k) for k in range(4)]
        ordered = [always_redraw(hands), segs[0], mv.tiers["dial"], segs[1], mv.tiers["engine"], segs[2],
                   mv.tiers["top"], segs[3]]
        self.mobjects[i:i + 1] = ordered
        self.add(always_redraw(motes), *rings.values(), snake_trace, show, hands_show, motes_show)

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

        def pulse(k):
            return rings[k].animate(rate_func=there_and_back).set_stroke(opacity=0.9)

        # ---------------------------------------------------------- timeline
        self.play(curtain.animate.set_fill(opacity=0), run_time=FADE_IN, rate_func=smooth)
        t = FADE_IN

        # the tiers separate and dim; the arbor appears; the camera settles at its top
        seg = dict(start=t, end=OPEN_END)
        self.play(*camera_move(self, OPEN_END - t, phi=CAM_TOP["phi"], theta=CAM_TOP["theta"], zoom=CAM_TOP["zoom"],
                               target=CAM_TOP["target"], frame_origin=origin),
                  explode.animate(run_time=OPEN_END - t, rate_func=rate_functions.ease_in_out_cubic).set_value(1.0),
                  *[d.animate(run_time=OPEN_END - t).set_value(TIER_DIM) for d in dim.values()],
                  show.animate(run_time=OPEN_END - t).set_value(1.0),
                  motes_show.animate(run_time=OPEN_END - t).set_value(1.0),
                  cue(LABEL_TIMES["title"], *fade(backing, bar, head, sub), **seg))
        self.remove(self.camera._frame_center)
        t = OPEN_END

        # down the arbor: top bridge, center wheel, main plate, hands
        seg = dict(start=t, end=DESCEND_END)
        flash = Line(OUT * ARBOR_TOP, OUT * ARBOR_BOTTOM).set_stroke(GLOW, 8)
        self.play(*camera_move(self, DESCEND_END - t, rate_func=rate_functions.ease_in_out_sine,
                               phi=CAM_BOTTOM["phi"], theta=CAM_BOTTOM["theta"], zoom=CAM_BOTTOM["zoom"],
                               target=CAM_BOTTOM["target"], frame_origin=origin),
                  cue(t + 0.3, ShowPassingFlash(flash, time_width=0.3), run_time=DESCEND_END - t - 0.6, **seg),
                  *[cue(PASS_TIMES[k], pulse(k), run_time=1.2, **seg) for k in ("top", "engine", "dial")],
                  cue(PASS_TIMES["dial"] - 0.4, hands_show.animate.set_value(1.0), run_time=0.8, **seg),
                  cue(PASS_TIMES["dial"] - 0.6, dim["dial"].animate.set_value(PLATE_SEE_THROUGH), run_time=1.0, **seg),
                  cue(LABEL_TIMES["arbor"], *fade(items["arbor"]), **seg))
        self.remove(self.camera._frame_center)
        t = DESCEND_END

        # pull back to show the winding stem, then trace it to the mainspring
        seg = dict(start=t, end=SNAKE_AT + SNAKE_DURATION)
        self.play(*camera_move(self, PULLBACK_END - t, phi=CAM_WIDE["phi"], theta=CAM_WIDE["theta"],
                               zoom=CAM_WIDE["zoom"], target=CAM_WIDE["target"], frame_origin=origin),
                  cue(LABEL_TIMES["stem"], *fade(items["stem"]), **seg),
                  cue(SNAKE_AT, snake_trace.animate.set_stroke(opacity=0.45), run_time=SNAKE_DURATION, **seg),
                  cue(SNAKE_AT, ShowPassingFlash(snake, time_width=0.4), run_time=SNAKE_DURATION, **seg))
        self.remove(self.camera._frame_center)

        self.wait(END_HOLD)
        self.remove(curtain)
        self.add_fixed_in_frame_mobjects(curtain)        # re-add so it sits above the text
        self.play(FadeOut(panel), curtain.animate.set_fill(opacity=1), run_time=FADE_OUT)
