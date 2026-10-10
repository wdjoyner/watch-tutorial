"""Scene 02 - "The Dial Side": a low tracking shot over the dial side of the
main plate, past the motion works, to the sliding clutch snapping into the
winding pinion.

Build (render + voice + mux):   python build.py scene02_dial_side
Render only (quick preview):    manim -ql scene02_dial_side.py Scene02
Narration lines and their start times live in scene02_dial_side.voice.txt.

The model's keyless works are flat top-view shapes. At this camera height the
parts that turn on the stem axis (stem, winding pinion, sliding clutch, crown)
need to read as cylinders, so this scene swaps them for cylinders that are
shaded toward the camera on every frame. Their teeth scroll as they turn, and
the Breguet (ratchet) teeth on the facing ends of the clutch and the winding
pinion interlock when the clutch snaps in.
"""
from manim import *
from movement import (Movement, attach_driver, vignette, camera_move, cue, BG, GLOW, FONT_SANS,
                      STEEL, STEEL_DK, STEEL_HI)

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds, angles in degrees.
# Keep the timeline roughly in step with scene02_dial_side.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 1.6
GLIDE = 9.0                # tracking move from the motion works to the clutch
PUSH_AT = 9.2              # crown pushed in (setting -> winding position)
PUSH_DURATION = 0.5
SNAP_DURATION = 0.14       # the clutch snaps onto the winding pinion
FLASH = 0.5                # glow at the moment of contact
WIND = 7.5                 # crown turns, winding pinion follows
WIND_TURNS = 2.2           # crown turns during WIND
FINAL_HOLD = 1.2
FADE_OUT = 1.5
LABEL_TIMES = {"title": 1.4, "keyless": 9.4, "motion": 12.6, "calendar": 15.6}
LABEL_FADE = 0.5

# --- camera (phi near 90 = low, grazing the plate) --------------------
CAM_START = dict(phi=75, theta=-104, zoom=3.9, center=(-0.95, -0.5, 0.08))   # on the minute wheel
CAM_CLUTCH = dict(phi=72, theta=-84, zoom=3.9, center=(2.5, 0.0, 0.14))
CAM_PUSH_IN = dict(phi=70, theta=-77, zoom=4.7, center=(2.36, 0.0, 0.14))

# --- keyless works on the stem axis (scene units) ---------------------
AXIS_Z = 0.14              # height of the stem axis above the plate
PULL_OUT = 0.12            # how far the crown sits out in setting position
CLUTCH_TRAVEL = 0.16       # clutch travel between setting and winding
YOKE_SWING = 8.0           # degrees the yoke swings over the clutch travel
LEVER_SWING = -3.5         # degrees the setting lever swings with the stem
LIGHT = (-0.45, -0.55, 0.75)

# --- on-screen text --------------------------------------------------
TITLE = ("TIER 1  ·  DIAL SIDE", "the interface layer, under the dial")
ITEMS = {
    "keyless": "keyless works  ·  winding and setting",
    "motion": "motion works  ·  drives the hands",
    "calendar": "dial-side complications  ·  calendar",
}
# =====================================================================

AXIS = np.array([1.0, 0.0, 0.0])


def _unit(v):
    return v / np.linalg.norm(v)


class StemPart:
    """A part that turns on the stem axis, drawn as a shaded cylinder.

    x0, x1     : axial extent (before any slide offset)
    r          : radius
    teeth      : number of lengthwise teeth or knurl ridges (0 = smooth)
    teeth_span : (a, b) fraction of the length carrying the teeth
    dog_lo/hi  : number of Breguet ratchet teeth on the low-x / high-x end face
    groove     : (fraction, width) of a dark ring, e.g. where the yoke engages
    """

    def __init__(self, x0, x1, r, teeth=0, teeth_span=(0, 1), dog_lo=0, dog_hi=0,
                 groove=None, color=STEEL, bands=36):
        self.x0, self.x1, self.r = x0, x1, r
        self.teeth, self.span, self.dog_lo, self.dog_hi = teeth, teeth_span, dog_lo, dog_hi
        self.groove, self.color, self.bands = groove, color, bands

    def draw(self, rot, dx, v, light):
        """rot: angle about the axis; dx: axial slide; v: unit vector toward the viewer."""
        w = _unit(v - np.dot(v, AXIS) * AXIS)        # surface normal facing the camera
        m = np.cross(AXIS, w)                        # silhouette direction
        c = np.array([0.0, 0.0, AXIS_Z])
        x0, x1, r = self.x0 + dx, self.x1 + dx, self.r
        dog_h = 0.35 * r

        def end_x(alpha, x, n, sign):
            if n == 0:
                return x
            u = ((alpha + rot) * n / TAU) % 1.0
            saw = u / 0.8 if u < 0.8 else (1.0 - u) / 0.2   # ratchet profile
            return x + sign * dog_h * saw

        def pt(x, alpha):
            return c + AXIS * x + r * (np.cos(alpha) * m + np.sin(alpha) * w)

        def shade(n):
            d = max(0.0, np.dot(n, light))
            spec = max(0.0, np.dot(n, _unit(light + v))) ** 24
            return 0.18 + 0.62 * d, spec

        g = VGroup()
        alphas = np.linspace(0, PI, self.bands + 1)
        for a0, a1 in zip(alphas[:-1], alphas[1:]):
            am = (a0 + a1) / 2
            b, spec = shade(np.cos(am) * m + np.sin(am) * w)
            col = interpolate_color(ManimColor(STEEL_DK), ManimColor(self.color), min(1, b * 1.3))
            col = interpolate_color(col, ManimColor(WHITE), min(1, spec * 0.9))
            lo0, lo1 = end_x(a0, x0, self.dog_lo, -1), end_x(a1, x0, self.dog_lo, -1)
            hi0, hi1 = end_x(a0, x1, self.dog_hi, +1), end_x(a1, x1, self.dog_hi, +1)
            q = Polygon(pt(lo0, a0), pt(hi0, a0), pt(hi1, a1), pt(lo1, a1))
            g.add(q.set_fill(col, 1).set_stroke(col, 0.6))

        if self.groove:
            f, gw = self.groove
            xm = x0 + f * (x1 - x0)
            ring = VGroup(*[Polygon(pt(xm - gw / 2, a0), pt(xm + gw / 2, a0), pt(xm + gw / 2, a1),
                                    pt(xm - gw / 2, a1)) for a0, a1 in zip(alphas[:-1], alphas[1:])])
            g.add(ring.set_fill(STEEL_DK, 1).set_stroke(STEEL_DK, 0.6))

        if self.teeth:
            xa = x0 + self.span[0] * (x1 - x0)
            xb = x0 + self.span[1] * (x1 - x0)
            for k in range(self.teeth):
                a = (rot + TAU * k / self.teeth) % TAU
                if 0.08 < a < PI - 0.08:
                    s = np.sin(a)
                    g.add(Line(pt(xa, a), pt(xb, a)).set_stroke("#15181c", 1.6, 0.35 + 0.55 * s))
                    a2 = a + PI / self.teeth
                    if a2 < PI - 0.08:
                        b, spec = shade(np.cos(a2) * m + np.sin(a2) * w)
                        g.add(Line(pt(xa, a2), pt(xb, a2)).set_stroke(STEEL_HI, 1.0, min(1, 0.25 + spec + 0.4 * b)))

        # the end cap that faces the camera
        side = np.dot(v, AXIS)
        if abs(side) > 0.02:
            xe = x1 if side > 0 else x0
            cap = Polygon(*[pt(xe, a) for a in np.linspace(0, TAU, 40, endpoint=False)])
            g.add(cap.set_fill(STEEL_DK, 1).set_stroke(self.color, 0.8))
        return g


class Scene02(ThreeDScene):
    def construct(self):
        self.camera.background_color = BG
        self.set_camera_orientation(phi=CAM_START["phi"] * DEGREES, theta=CAM_START["theta"] * DEGREES,
                                    zoom=CAM_START["zoom"], frame_center=np.array(CAM_START["center"]))
        self.add_fixed_in_frame_mobjects(vignette())

        # dial tier only, turned dial side up; the flat stem-axis parts are replaced below
        mv = Movement(dial_up=True)
        keyless = mv.parts["keyless"]
        setting_lever, yoke = keyless[0], keyless[1]
        keyless.remove(*keyless[3:])                  # winding pinion, sliding pinion, stem, crown
        mv.tiers = {"dial": mv.tiers["dial"]}
        mv.rot = [r for r in mv.rot if r[2] == "dial"]
        attach_driver(self, mv, {"dial": 0.0}, {"dial": 0.0})

        # stem-axis parts (positions are the winding position)
        stem = StemPart(1.80, 3.70, 0.035, color=STEEL_HI, bands=8)
        pinion = StemPart(1.94, 2.22, 0.11, teeth=14, teeth_span=(0, 0.75), dog_hi=9)
        clutch = StemPart(2.22, 2.50, 0.10, teeth=12, teeth_span=(0.78, 1.0), dog_lo=9,
                          groove=(0.5, 0.05), color=STEEL_HI)
        crown = StemPart(3.65, 3.95, 0.28, teeth=26, teeth_span=(0.12, 1.0))

        push = ValueTracker(0.0)      # 0 = crown pulled (setting), 1 = pushed in (winding)
        engage = ValueTracker(0.0)    # 0 = clutch out, 1 = locked onto the winding pinion
        spin = ValueTracker(0.0)      # crown angle; the clutch and pinion turn with it once engaged
        flash = ValueTracker(0.0)
        light = _unit(np.array(LIGHT))

        def stem_axis():
            v = self.camera.generate_rotation_matrix()[2]
            out = (1 - push.get_value()) * PULL_OUT
            gap = (1 - engage.get_value()) * CLUTCH_TRAVEL
            a = spin.get_value()
            g = VGroup(stem.draw(a, out, v, light),
                       pinion.draw(a, 0.0, v, light),
                       clutch.draw(a, gap, v, light),
                       crown.draw(a, out, v, light))
            f = flash.get_value()
            if f > 0.01:
                ring = Circle(radius=0.17, num_components=24).rotate(PI / 2, UP).move_to([2.22, 0, AXIS_Z])
                g.add(ring.set_stroke(GLOW, 6 * f, 0.7 * f), ring.copy().set_stroke(WHITE, 1.5, f))
            return g

        live = always_redraw(stem_axis)

        # the yoke and setting lever swing with the clutch and stem
        pivots = {id(yoke): np.array([1.85, 1.38, 0]), id(setting_lever): np.array([1.55, -0.95, 0])}
        swings = {id(yoke): lambda: YOKE_SWING * (1 - engage.get_value()),
                  id(setting_lever): lambda: LEVER_SWING * (1 - push.get_value())}

        def swing(m):
            target = swings[id(m)]() * DEGREES
            cur = getattr(m, "_swing", 0.0)
            if abs(target - cur) > 1e-6:
                m.rotate(target - cur, axis=OUT, about_point=pivots[id(m)])
                m._swing = target
        for m in (yoke, setting_lever):
            swing(m)
            m.add_updater(swing)

        self.add(live, push, engage, spin, flash)

        # screen-fixed text
        def item(text):
            return Text(text, font=FONT_SANS, color=GREY_B).scale(0.26)

        head = Text(TITLE[0], font=FONT_SANS, weight=BOLD, color=GLOW).scale(0.40)
        sub = Text(TITLE[1], font=FONT_SANS, color=GREY_B).scale(0.26)
        items = {k: item(t) for k, t in ITEMS.items()}
        block = VGroup(head, sub, *items.values()).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        items_g = VGroup(*items.values()).shift(DOWN * 0.12)
        tick = Line(ORIGIN, RIGHT * 0.45).set_stroke(GLOW, 2)
        panel = VGroup(tick, block).arrange(RIGHT, buff=0.15, aligned_edge=UP).to_corner(DL, buff=0.5)
        curtain = FullScreenRectangle().set_fill(BG, 1).set_stroke(width=0)
        self.add_fixed_in_frame_mobjects(panel, curtain)
        self.remove(panel)

        # ---------------------------------------------------------- timeline
        t = 0.0

        def at_time(when):
            nonlocal t
            if when > t:
                self.wait(when - t)
                t = when

        def play(*anims, run_time, **kw):
            nonlocal t
            self.play(*anims, run_time=run_time, **kw)
            t += run_time

        # fade up while the glide starts; the glide carries the title on the way
        self.play(curtain.animate.set_fill(opacity=0), run_time=FADE_IN, rate_func=smooth)
        t = FADE_IN
        title_in = [FadeIn(tick, shift=RIGHT * 0.2), FadeIn(head, shift=RIGHT * 0.2), FadeIn(sub, shift=RIGHT * 0.2)]
        self.play(*camera_move(self, GLIDE - FADE_IN, phi=CAM_CLUTCH["phi"], theta=CAM_CLUTCH["theta"],
                               zoom=CAM_CLUTCH["zoom"], frame_center=CAM_CLUTCH["center"]),
                  cue(LABEL_TIMES["title"], *title_in, start=FADE_IN, end=GLIDE, run_time=LABEL_FADE * 1.6))
        self.remove(self.camera._frame_center)
        t = GLIDE

        # crown pushed in; the yoke releases the clutch and it snaps onto the winding pinion
        at_time(PUSH_AT)
        play(push.animate.set_value(1.0), run_time=PUSH_DURATION, rate_func=smooth)
        play(engage.animate.set_value(1.0), FadeIn(items["keyless"], shift=RIGHT * 0.2),
             run_time=SNAP_DURATION, rate_func=rate_functions.ease_in_quad)
        play(flash.animate.set_value(1.0), run_time=FLASH, rate_func=there_and_back)

        # winding: crown turns, the clutch drives the winding pinion; slow push-in
        seg = dict(start=t, end=t + WIND)
        self.play(*camera_move(self, WIND, phi=CAM_PUSH_IN["phi"], theta=CAM_PUSH_IN["theta"],
                               zoom=CAM_PUSH_IN["zoom"], frame_center=CAM_PUSH_IN["center"]),
                  spin.animate(run_time=WIND, rate_func=rate_functions.ease_in_out_sine).set_value(-WIND_TURNS * TAU),
                  cue(LABEL_TIMES["motion"], FadeIn(items["motion"], shift=RIGHT * 0.2), **seg),
                  cue(LABEL_TIMES["calendar"], FadeIn(items["calendar"], shift=RIGHT * 0.2), **seg))
        self.remove(self.camera._frame_center)
        t += WIND

        self.wait(FINAL_HOLD)
        self.remove(curtain)
        self.add_fixed_in_frame_mobjects(curtain)        # re-add so it sits above the text
        self.play(FadeOut(panel), curtain.animate.set_fill(opacity=1), run_time=FADE_OUT)
