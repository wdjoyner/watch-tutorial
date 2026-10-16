"""Film 7 helper: a flat (2D) close-up of the keyless works, seen from the dial side.

    kw = KeylessWorks(origin=(-1.0, 0.6), scale=1.0)
    scene.add(kw)                     # one updater redraws every part from the trackers
    scene.play(kw.pull.animate.set_value(1.0), run_time=4)   # pull the crown out
    scene.play(kw.spin.animate.set_value(TAU), run_time=2)   # turn the crown once

Trackers (animate these, never the parts):
    pull   0 = pushed in (winding), 1 = pulled out (hand setting)
    spin   crown angle in radians (positive = forward, winding)
    vis    overall opacity (0..1)
    glow   {part: ValueTracker 0..1} highlights a part as it is named
Read-outs: kw.anchor(name) gives a point on a part, for callouts; kw.geom(pull)
gives the linkage angles and the sliding pinion's travel.

The linkage is solved, not keyframed. Pulling the stem moves the groove; the
setting lever's pin rides in the groove, so the lever turns about its pivot.
The lever's beak then pushes up on the yoke's pad (found by bisection, contact
only), the yoke turns, and its fork slides the sliding pinion inward along the
square of the stem, off the winding pinion and onto the setting wheel. The yoke
spring pushes back, so with no contact the sliding pinion rests against the
winding pinion. The jumper rides on a knob on the lever's tail; its profile
has a notch for each position and a hump between them.

Turning the crown backward in the winding position: the Breguet teeth ride
over each other, so the sliding pinion is pushed inward by up to one tooth
height (against the yoke spring) and the winding pinion stays still.

Layout follows the usual Swiss keyless works (crown at the right): crown, the
lever's groove, the winding pinion, then the sliding pinion inboard of it, with
the setting wheel beyond. SCHEMATIC: proportions and travels are chosen for
clarity (the stem's real travel is about a millimeter), and the drawing is
labeled so on screen.
"""
from manim import *
from shapely.geometry import Polygon as SPoly, Point, LineString, box
from shapely.ops import unary_union
from movement import vm, teeth_g, disk_g, rounded, STEEL, STEEL_DK, STEEL_HI, BRASS, BRASS_DK, BRASS_HI, GLOW, BG

# ------------------------------------------------------------------ geometry (local units)
STEM_R = 0.075              # stem radius
TRAVEL = 0.50               # stem travel, pushed in -> pulled out
INNER_END = -1.15           # inner end of the stem (pushed in)
CROWN_X = (3.05, 3.70)      # crown, pushed in
CROWN_R = 0.42
GROOVE_X = 2.62             # the setting lever's groove on the stem, pushed in
WP_X = (1.55, 2.25)         # winding pinion: axially fixed, free on the stem
WP_R = 0.30
SP_LEN, SP_R = 0.95, 0.27   # sliding pinion
S_MAX = 0.46                # sliding pinion travel, winding -> setting
BREG_N, BREG_H = 4, 0.13    # Breguet teeth seen across the face, and their height
SET_N, SET_H = 6, 0.07      # straight setting teeth on the sliding pinion's inner face
SW_Z, SW_R = 18, 0.52       # setting wheel (plan view)
SW_C = (WP_X[0] - BREG_H - S_MAX - SP_LEN - SET_H + 0.02 - SW_R, -0.55)   # rim just meets the setting teeth when set

L_PIVOT = np.array([2.87, -2.05])   # setting lever pivot
L_PIN_R = 2.05                      # pivot -> pin (in the groove)
L_BEAK = (-0.98 * PI, 1.30)         # beak arm: angle relative to the pin arm direction, length
L_TAIL = (-0.42 * PI, 1.30)         # tail arm (jumper knob)
Y_PIVOT = np.array([0.55, -2.05])   # yoke pivot
Y_FORK_R = None                     # set below from geometry
Y_PAD = (0.0, 0.80)                 # pad: angle relative to the fork arm + 90 deg, length
J_ANCHOR = np.array([4.80, -2.25])  # jumper's fixed end
YS_ANCHOR = np.array([-0.75, -1.55])  # yoke spring's fixed end

SP_OUT0 = WP_X[0]                   # the Breguet teeth meet here (winding)
SQ_X = (SP_OUT0 - BREG_H - SP_LEN - S_MAX - TRAVEL - 0.06, SP_OUT0 - 0.02)   # the stem's square, pushed in
FORK_X0 = SP_OUT0 - BREG_H - SP_LEN / 2      # fork (groove of the sliding pinion), winding
Y_FORK_R = float(np.hypot(FORK_X0 - Y_PIVOT[0], 0 - Y_PIVOT[1]))
Y_FORK_A0 = float(np.arctan2(0 - Y_PIVOT[1], FORK_X0 - Y_PIVOT[0]))


def _pol(c, a, r):
    return np.array([c[0] + r * np.cos(a), c[1] + r * np.sin(a)])


def lever_angle(pull):
    """Direction of the pivot -> pin arm, with the pin in the groove."""
    xg = GROOVE_X + TRAVEL * pull
    return float(np.arccos(np.clip((xg - L_PIVOT[0]) / L_PIN_R, -1, 1)))


def yoke_angle(s):
    """Fork-arm direction that puts the fork at FORK_X0 - s."""
    x = FORK_X0 - s
    return float(np.arccos(np.clip((x - Y_PIVOT[0]) / Y_FORK_R, -1, 1)))


def beak_point(pull):
    a = lever_angle(pull)
    return _pol(L_PIVOT, a + L_BEAK[0], L_BEAK[1])


PAD_W = 0.09                # half-width of the yoke's pad arm
PAD_LEN = 1.25
BEAK_TIP_R = 0.07


def pad_dir(ya):
    """Direction of the yoke's pad arm (at right angles to the fork arm, pointing right)."""
    return ya - PI / 2 + Y_PAD[0]


def _gap(s, pull):
    """Clearance between the beak tip and the pad's lower face (negative: they overlap).
    The beak sits under the pad; turning the yoke (s up) lifts the pad off it."""
    a = pad_dir(yoke_angle(s))
    nl = np.array([np.sin(a), -np.cos(a)])            # the pad's lower normal
    return float(np.dot(beak_point(pull) - Y_PIVOT, nl)) - PAD_W - BEAK_TIP_R


def solve_s(pull):
    """Sliding pinion travel from the lever (0 with no contact)."""
    if _gap(0.0, pull) >= 0:
        return 0.0
    lo, hi = 0.0, 1.5
    for _ in range(40):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if _gap(mid, pull) < 0 else (lo, mid)
    return hi


PULL_CONTACT = 0.20         # the beak meets the pad after the first fifth of the pull


def _calibrate():
    """Choose the beak arm's angle and length (a grid search) so that the beak first
    touches the pad at PULL_CONTACT and full pull gives S_MAX of travel."""
    global L_BEAK
    us = np.linspace(0, 1, 101)
    best = None
    for ang in np.linspace(0.45 * PI, 0.80 * PI, 71):
        for ln in np.linspace(0.8, 2.0, 61):
            L_BEAK = (ang, ln)
            if _gap(0.0, 0.0) < 0:
                continue                      # touching already when pushed in
            touch = next((u for u in us if _gap(0.0, u) < 0), None)
            if touch is None:
                continue
            err = abs(touch - PULL_CONTACT) * 2 + abs(solve_s(1.0) - S_MAX) / S_MAX
            if best is None or err < best[0]:
                best = (err, (ang, ln))
    L_BEAK = best[1]


# jumper: the knob's position along its arc, in pull units, and the profile it rides
def knob_point(pull):
    return _pol(L_PIVOT, lever_angle(pull) + L_TAIL[0], L_TAIL[1])


J_NOTCH_DEPTH = 0.11


def jumper_lift(u):
    """How far the jumper is pushed out when the knob is at u (0 = winding notch,
    1 = setting notch): zero in each notch, a hump between them."""
    u = float(np.clip(u, -0.15, 1.15))
    return J_NOTCH_DEPTH * np.sin(np.pi * np.clip(u, 0, 1)) ** 2


def snap_rate(u):
    """A rate function for pulls and pushes: slow up the hump, then the jumper snaps
    the lever into the notch (the last third goes quickly)."""
    if u < 0.62:
        return 0.5 * smooth(u / 0.62)
    return 0.5 + 0.5 * rate_functions.ease_out_cubic((u - 0.62) / 0.38)


from movement import SCREW, SCREW_HI


class KeylessWorks(VGroup):
    PARTS = ("crown", "stem", "winding_pinion", "sliding_pinion", "setting_lever", "jumper", "yoke",
             "yoke_spring", "setting_wheel")

    def __init__(self, origin=(0.0, 0.0), scale=1.0, setting_wheel=True, window=None, parts=None, follow=None):
        super().__init__()
        # origin and scale are trackers, so a scene can zoom in on the clutch and back
        self.ox, self.oy, self.kt = ValueTracker(origin[0]), ValueTracker(origin[1]), ValueTracker(scale)
        self.draw_sw = setting_wheel
        self.window = box(*window) if window else None     # local (x0, y0, x1, y1): draw only inside
        self.only = set(parts) if parts else None           # draw only these parts
        self.follow = follow                                # another KeylessWorks whose trackers drive this one
        self.pull = ValueTracker(0.0)
        self.spin = ValueTracker(0.0)
        self.vis = ValueTracker(1.0)
        self.glow = {p: ValueTracker(0.0) for p in self.PARTS}
        self.inset_vis = ValueTracker(1.0)   # an inset's own fade (times its main view's vis)
        self._wp_ang = 0.0          # the winding pinion only turns when driven
        self._sp_ang = 0.0
        self._last_spin = 0.0
        self.ride = 0.0             # axial push-back from Breguet teeth riding over
        self.add_updater(lambda m, dt: m._redraw())
        self._redraw()

    # ------------------------------------------------------------ coordinates
    @property
    def o(self):
        return np.array([self.ox.get_value(), self.oy.get_value()])

    @property
    def k(self):
        return self.kt.get_value()

    def zoom_to(self, local_xy, screen_xy, scale):
        """Animations that put local point local_xy at screen_xy at the given scale."""
        return [self.kt.animate.set_value(scale),
                self.ox.animate.set_value(screen_xy[0] - scale * local_xy[0]),
                self.oy.animate.set_value(screen_xy[1] - scale * local_xy[1])]

    def P(self, xy):
        return np.array([self.o[0] + self.k * xy[0], self.o[1] + self.k * xy[1], 0.0])

    def _vm(self, geom, color, op=1.0, stroke=None, sw=0.9):
        from shapely import affinity
        g = affinity.scale(geom, self.k, self.k, origin=(0, 0))
        if self.window is not None:
            geom = geom.intersection(self.window)
            g = affinity.translate(affinity.scale(geom, self.k, self.k, origin=(0, 0)), self.o[0], self.o[1])
        else:
            g = affinity.translate(g, self.o[0], self.o[1])
        v = self.vis.get_value()
        return vm(g, color, op * v, stroke, sw, sop=v)

    def trackers(self):
        return [self.pull, self.spin, self.vis, self.inset_vis, self.ox, self.oy, self.kt, *self.glow.values()]

    # ------------------------------------------------------------ state
    def geom(self, pull=None):
        p = self.pull.get_value() if pull is None else pull
        s_lev = solve_s(p)
        s = max(s_lev, self.ride)
        return dict(pull=p, dx=TRAVEL * p, lever=lever_angle(p), s=s, s_lever=s_lev, yoke=yoke_angle(s),
                    beak=beak_point(p), knob=knob_point(p))

    def engaged_winding(self):
        return self.geom()["s"] < 0.02

    def engaged_setting(self):
        return self.geom()["s_lever"] > S_MAX - 0.03

    def anchor(self, name):
        g = self.geom()
        dx, s = g["dx"], g["s"]
        pts = {
            "crown": (CROWN_X[0] + dx + 0.35, CROWN_R * 0.95),
            "stem": (2.85 + dx, STEM_R),
            "groove": (GROOVE_X + dx, 0.0),
            "winding_pinion": ((WP_X[0] + WP_X[1]) / 2, WP_R),
            "breguet": (SP_OUT0 - BREG_H / 2 - s, SP_R * 0.6),
            "sliding_pinion": (SP_OUT0 - BREG_H - s - SP_LEN * 0.3, SP_R),
            "setting_teeth": (SP_OUT0 - BREG_H - s - SP_LEN - SET_H / 2, -SP_R * 0.6),
            "setting_wheel": (SW_C[0] - SW_R * 0.3, SW_C[1] - SW_R * 0.8),
            "setting_lever": tuple(_pol(L_PIVOT, g["lever"], L_PIN_R * 0.55)),
            "lever_pin": tuple(_pol(L_PIVOT, g["lever"], L_PIN_R)),
            "beak": tuple(g["beak"]),
            "yoke": tuple(_pol(Y_PIVOT, g["yoke"], Y_FORK_R * 0.5)),
            "fork": (SP_OUT0 - BREG_H - s - SP_LEN / 2, -SP_R),
            "yoke_spring": tuple((YS_ANCHOR + self._spring_end(g)) / 2),
            "jumper": tuple(J_ANCHOR + (self._jumper_tip(g) - J_ANCHOR) * 0.5),
            "knob": tuple(g["knob"]),
        }
        return self.P(pts[name])

    # ------------------------------------------------------------ helpers
    def _spring_end(self, g):
        return _pol(Y_PIVOT, g["yoke"], Y_FORK_R * 0.42) + np.array([-0.06, 0])

    def _jumper_tip(self, g):
        return getattr(self, "_jtip", knob_point(0.5))

    def _hl(self, part, color):
        """Blend a part's color toward GLOW by its glow tracker."""
        v = self.glow[part].get_value()
        return interpolate_color(ManimColor(color), ManimColor(GLOW), 0.65 * v) if v > 0 else color

    def _hl_stroke(self, part, base):
        v = self.glow[part].get_value()
        return GLOW if v > 0.3 else base

    # ------------------------------------------------------------ drawing
    def _redraw(self):
        if self.follow is not None:                     # an inset mirrors its main view
            f = self.follow
            self.pull.set_value(f.pull.get_value())
            self.vis.set_value(f.vis.get_value() * self.inset_vis.get_value())
            for p in self.PARTS:
                self.glow[p].set_value(f.glow[p].get_value())
            self.ride, self._wp_ang, self._sp_ang = f.ride, f._wp_ang, f._sp_ang
            self._sw_a = getattr(f, "_sw_a", 0.0)
            spin = f.spin.get_value()
        else:
            spin = self.spin.get_value()
            d_spin = spin - self._last_spin
            self._last_spin = spin
            s_lev = solve_s(self.pull.get_value())
            # the sliding pinion turns with the stem; the winding pinion only when driven forward
            self._sp_ang = spin
            if s_lev < 1e-6 and d_spin < 0:
                # turned backward while pushed in: the Breguet teeth ride over each other, pushing
                # the sliding pinion inward against the yoke spring; the winding pinion stays still
                v = ((self._wp_ang - self._sp_ang) * BREG_N / TAU) % 1.0
                self.ride = BREG_H * (v / 0.75 if v < 0.75 else (1 - v) / 0.25)
            elif d_spin > 0:
                self.ride = 0.0
                if s_lev < 0.02:                        # engaged: drive the winding pinion
                    lag = round((self._sp_ang - self._wp_ang) * BREG_N / TAU) * TAU / BREG_N
                    self._wp_ang = self._sp_ang - lag
            self._sw_angle(spin)
        g = self.geom()
        dx, s = g["dx"], g["s"]
        out = VGroup()
        show = (lambda p: True) if self.only is None else (lambda p: p in self.only)

        # setting wheel (in the plate, under the stem)
        if self.draw_sw and show("setting_wheel"):
            sw_turn = 0.0
            if self.engaged_setting():
                sw_turn = spin
            gear = teeth_g(SW_R, SW_Z).difference(disk_g(0.05))
            from shapely import affinity
            gear = affinity.rotate(gear, -getattr(self, '_sw_a', 0.0), origin=(0, 0), use_radians=True)
            gear = affinity.translate(gear, *SW_C)
            out.add(self._vm(gear, self._hl("setting_wheel", STEEL), 1.0, self._hl_stroke("setting_wheel", STEEL_HI)))
            out.add(self._vm(disk_g(0.06, SW_C), STEEL_DK, 1.0, STEEL_HI))

        under, over = VGroup(), VGroup()   # parts off the stem axis (left out of an inset)
        # yoke spring (a wire from its anchor to the yoke's fork arm)
        e = self._spring_end(g)
        mid = (YS_ANCHOR + e) / 2 + np.array([0.18, -0.10])
        spring = VMobject().set_points_smoothly([self.P(YS_ANCHOR), self.P(mid), self.P(e)])
        under.add(spring.set_stroke(self._hl_stroke("yoke_spring", STEEL_HI), 2.6 * self.k, self.vis.get_value())
                .set_fill(opacity=0))
        under.add(self._vm(disk_g(0.06, YS_ANCHOR), STEEL_DK, 1.0, STEEL_HI))

        # yoke: pivot boss, fork arm up to the sliding pinion's groove, pad arm to the right
        ya = g["yoke"]
        tip = _pol(Y_PIVOT, ya, Y_FORK_R - 0.06)
        pd = pad_dir(ya)
        pad_end = _pol(Y_PIVOT, pd, PAD_LEN)
        arm = LineString([tuple(Y_PIVOT), tuple(tip)]).buffer(0.085)
        pad = LineString([tuple(Y_PIVOT), tuple(pad_end)]).buffer(PAD_W, cap_style=2)
        u = np.array([np.cos(ya), np.sin(ya)])
        n = np.array([-u[1], u[0]])
        fork_c = tip
        fork = SPoly([tuple(fork_c - n * 0.16 - u * 0.12), tuple(fork_c + n * 0.16 - u * 0.12),
                      tuple(fork_c + n * 0.16 + u * 0.10), tuple(fork_c + n * 0.06 + u * 0.10),
                      tuple(fork_c + n * 0.06 - u * 0.02), tuple(fork_c - n * 0.06 - u * 0.02),
                      tuple(fork_c - n * 0.06 + u * 0.10), tuple(fork_c - n * 0.16 + u * 0.10)])
        yoke = unary_union([arm, pad, fork, disk_g(0.16, Y_PIVOT)]).difference(disk_g(0.05, Y_PIVOT))
        under.add(self._vm(yoke, self._hl("yoke", STEEL), 1.0, self._hl_stroke("yoke", STEEL_HI)))

        # stem (slides): round, with a square section under the sliding pinion, and the groove
        x0, x1 = INNER_END + dx, CROWN_X[0] + dx
        stem = box(x0, -STEM_R, x1, STEM_R)
        groove = box(GROOVE_X + dx - 0.05, -STEM_R, GROOVE_X + dx + 0.05, STEM_R)
        sq = box(SQ_X[0] + dx, -STEM_R * 1.25, SQ_X[1] + dx, STEM_R * 1.25)
        stem_c = self._hl("stem", STEEL_HI)
        out.add(self._vm(stem.difference(groove), stem_c, 1.0, self._hl_stroke("stem", WHITE), 0.6))
        out.add(self._vm(groove, STEEL_DK, 1.0))
        out.add(self._vm(sq.intersection(box(x0, -1, x1, 1)), self._hl("stem", STEEL), 1.0,
                         self._hl_stroke("stem", STEEL_HI), 0.6))

        # winding pinion: fixed axially; Breguet teeth on its inner face
        out.add(self._cylinder(WP_X[0], WP_X[1], WP_R, self._wp_ang, 12, "winding_pinion",
                               lo_teeth=("breguet_m", -1, self._wp_ang)))
        # sliding pinion: Breguet teeth outward, straight setting teeth inward, groove for the fork
        a0, a1 = SP_OUT0 - BREG_H - s - SP_LEN, SP_OUT0 - BREG_H - s
        out.add(self._cylinder(a0, a1, SP_R, self._sp_ang, 10, "sliding_pinion",
                               hi_teeth=("breguet", +1, self._sp_ang), lo_teeth=("straight", -1, self._sp_ang),
                               groove=((a0 + a1) / 2, 0.08)))
        # the yoke's fork, sitting in the sliding pinion's groove
        gx = (a0 + a1) / 2
        over.add(self._vm(box(gx - 0.035, -SP_R - 0.02, gx + 0.035, -SP_R + 0.07), self._hl("yoke", STEEL_HI), 1.0,
                         self._hl_stroke("yoke", WHITE), 0.6))

        # crown (knurled)
        cx0, cx1 = CROWN_X[0] + dx, CROWN_X[1] + dx
        crown = box(cx0, -CROWN_R, cx1, CROWN_R)
        for y in np.linspace(-CROWN_R + 0.04, CROWN_R - 0.04, 9):
            yy = y + 0.05 * np.sin(spin * 2)
            crown = crown.difference(box(cx1 - 0.05, yy - 0.012, cx1 + 0.01, yy + 0.012))
        over.add(self._vm(rounded(list(crown.exterior.coords)[:-1], 0.05), self._hl("crown", STEEL), 1.0,
                         self._hl_stroke("crown", STEEL_HI)))
        over.add(self._knurl(cx0, cx1, spin))

        # setting lever: pin arm up to the groove, beak arm to the left, tail to the jumper
        la = g["lever"]
        pin = _pol(L_PIVOT, la, L_PIN_R)
        beak = g["beak"]
        knob = g["knob"]
        lever = unary_union([LineString([tuple(L_PIVOT), tuple(pin)]).buffer(0.09),
                             LineString([tuple(L_PIVOT), tuple(beak)]).buffer(0.08),
                             LineString([tuple(L_PIVOT), tuple(knob)]).buffer(0.08),
                             disk_g(0.19, L_PIVOT), disk_g(BEAK_TIP_R + 0.02, beak)])
        lever = lever.difference(disk_g(0.05, L_PIVOT))
        over.add(self._vm(lever, self._hl("setting_lever", STEEL), 1.0, self._hl_stroke("setting_lever", STEEL_HI)))
        over.add(self._vm(disk_g(0.065, pin), STEEL_HI, 1.0, WHITE, 0.6))          # pin in the groove

        # jumper: a leaf spring whose tip has two notches, pushed out by the knob
        over.add(self._jumper(g))
        over.add(self._vm(disk_g(0.075, knob), STEEL_HI, 1.0, WHITE, 0.6))         # knob for the jumper

        for c in (L_PIVOT, Y_PIVOT, J_ANCHOR):
            over.add(self._vm(disk_g(0.075, c), SCREW, 1.0, SCREW_HI, 0.6))
            over.add(Line(self.P(c + np.array([-0.06, 0.02])), self.P(c + np.array([0.06, -0.02])))
                    .set_stroke(BG, 2 * self.k, self.vis.get_value()))
        if self.only is None:
            out.submobjects.insert(1 if self.draw_sw else 0, under)
            out.add(over)
        self.become(out)
        return self

    def _sw_angle(self, spin):
        """Setting wheel angle: follows the sliding pinion's setting teeth only while engaged."""
        if not hasattr(self, "_sw_a"):
            self._sw_a, self._sw_spin = 0.0, spin
        if self.engaged_setting():
            self._sw_a += (spin - self._sw_spin) * SET_N * 2 / SW_Z
        self._sw_spin = spin
        return self._sw_a

    def _cylinder(self, x0, x1, r, ang, n_lines, part, lo_teeth=None, hi_teeth=None, groove=None):
        """A part on the stem axis, in plan view: a rectangle with lengthwise tooth
        lines that scroll as it turns, and teeth drawn on its end faces."""
        col = self._hl(part, STEEL)
        v = self.vis.get_value()
        body = box(x0, -r, x1, r)
        if groove:
            gx, gw = groove
            body = body.difference(box(gx - gw / 2, -r - 0.01, gx + gw / 2, -r + 0.05)).difference(
                box(gx - gw / 2, r - 0.05, gx + gw / 2, r + 0.01))
        g = VGroup(self._vm(body, col, 1.0, self._hl_stroke(part, STEEL_HI)))
        for k in range(n_lines):
            a = (ang + TAU * k / n_lines) % TAU
            if 0.15 < a < PI - 0.15:
                y = -r * np.cos(a)
                xa, xb = x0 + 0.05, x1 - 0.05
                if groove:
                    gx, gw = groove
                    g.add(Line(self.P((xa, y)), self.P((gx - gw / 2, y))).set_stroke(STEEL_DK, 1.4, 0.8 * v * np.sin(a)))
                    g.add(Line(self.P((gx + gw / 2, y)), self.P((xb, y))).set_stroke(STEEL_DK, 1.4, 0.8 * v * np.sin(a)))
                else:
                    g.add(Line(self.P((xa, y)), self.P((xb, y))).set_stroke(STEEL_DK, 1.4, 0.8 * v * np.sin(a)))
        for spec, x in ((lo_teeth, x0), (hi_teeth, x1)):
            if spec:
                kind, side, a = spec
                g.add(self._face_teeth(x, r, side, a, kind, part))
        return g

    def _face_teeth(self, x, r, side, ang, kind, part):
        """Teeth on an end face, seen from the side as a profile across the face."""
        n = SET_N if kind == "straight" else BREG_N
        h = SET_H if kind == "straight" else BREG_H
        ys = np.linspace(-r, r, 241)
        pts = []
        for y in ys:
            u = ((np.arccos(np.clip(-y / r, -1, 1)) + ang) * n / TAU) % 1.0
            if kind in ("breguet", "breguet_m"):
                prof = u / 0.75 if u < 0.75 else (1 - u) / 0.25        # ratchet: long slope, steep face
                if kind == "breguet_m":
                    prof = 1 - prof                                    # the mating face
            else:
                prof = 1.0 if 0.25 < u < 0.75 else 0.0                  # straight (square) teeth
            pts.append((x + side * h * prof, y))
        poly = SPoly([(x, -r)] + pts + [(x, r)])
        return self._vm(poly.buffer(0), self._hl(part, STEEL_HI), 1.0, self._hl_stroke(part, WHITE), 0.6)

    def _knurl(self, x0, x1, spin):
        v = self.vis.get_value()
        g = VGroup()
        for k in range(14):
            a = (spin + TAU * k / 14) % TAU
            if 0.12 < a < PI - 0.12:
                y = -CROWN_R * np.cos(a)
                g.add(Line(self.P((x0 + 0.06, y)), self.P((x1 - 0.08, y))).set_stroke(STEEL_DK, 1.6, 0.7 * v))
        return g

    def _jumper(self, g):
        """Leaf spring with a W-shaped tip: a notch for each position and a hump between.
        The knob always touches the profile, so the leaf is pushed out by jumper_lift(u)."""
        knob = g["knob"]
        k0, k1 = knob_point(0.0), knob_point(1.0)
        span = float(np.linalg.norm(k1 - k0))
        along = (k1 - k0) / span
        normal = np.array([-along[1], along[0]])
        if np.dot(normal, J_ANCHOR - (k0 + k1) / 2) < 0:
            normal = -normal                       # from the knob's path toward the jumper
        u = float(np.dot(knob - k0, along) / span)
        lift = jumper_lift(u)
        kr = 0.075                                 # knob radius

        def surface(t):                            # recess depth measured outward
            if t < 0:
                return J_NOTCH_DEPTH * max(0.0, 1 + t / 0.14)
            if t > 1:
                return J_NOTCH_DEPTH * max(0.0, 1 - (t - 1) / 0.14)
            return J_NOTCH_DEPTH * (1 - np.sin(np.pi * t) ** 2)

        prof = [k0 + along * (t * span) + normal * (kr + lift + surface(t) - J_NOTCH_DEPTH)
                for t in np.linspace(-0.45, 1.45, 77)]
        back = [p + normal * 0.24 for p in reversed(prof)]
        tip_poly = SPoly([tuple(p) for p in prof + back]).buffer(0)
        far = prof[-1] + normal * 0.14
        leaf = LineString([tuple(J_ANCHOR), tuple(far)]).buffer(0.065)
        shape = unary_union([tip_poly, leaf, disk_g(0.15, J_ANCHOR)]).difference(disk_g(0.05, J_ANCHOR))
        self._jtip = (prof[len(prof) // 2] + normal * 0.08)
        return self._vm(shape, self._hl("jumper", STEEL), 1.0, self._hl_stroke("jumper", STEEL_HI))


class Spinner(VGroup):
    """A flat part turned about its own center by an angle function (radians, read each frame)."""

    def __init__(self, mob, center, angle_fn):
        super().__init__(mob)
        self.c = np.array([center[0], center[1], 0.0])
        self.fn, self._a = angle_fn, 0.0
        self.add_updater(lambda m: m._turn())

    def _turn(self):
        a = self.fn()
        if a != self._a:
            self.rotate(a - self._a, about_point=self.c)
            self._a = a


_calibrate()


if __name__ == "__main__":
    for p in np.linspace(0, 1, 11):
        print(f"pull {p:.1f}  lever {np.degrees(lever_angle(p)):6.2f}  s {solve_s(p):.3f}  "
              f"yoke {np.degrees(yoke_angle(solve_s(p))):6.2f}")
    print("pad", Y_PAD, "beak", L_BEAK)
