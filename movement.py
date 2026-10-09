"""The watch movement model, shared by every scene in the tutorial.

The model follows the ETA 6497-1 (Unitas), a hand-wound 16 1/2''' movement:
Ø 36.60 mm, 4.50 mm high, 17 jewels, 18,000 vibrations per hour, small seconds
opposite the crown. Part numbers in comments are from ETA's technical
communication for the 6497-1 / 6498-1. The layout is traced from its drawings.

Contents
  * PALETTE / fonts           - colors and typefaces used everywhere
  * kinematics                - tooth counts, per-mesh modules, pivot layout P, state(t)
  * geometry helpers          - shapely shapes -> Manim VMobjects, thickness, finishes
  * Movement                  - builds the three tiers (dial / engine / top)
  * attach_driver()           - one updater that moves, flips and dims the tiers
                                and turns every moving part

Coordinates: the movement lies in the xy-plane, 6 units across (plate radius 3,
so 1 unit = 6.1 mm), center wheel at the origin, stem along +x. +z points up
out of the bridge side. The dial side of the main plate faces -z, so the motion
works and keyless works hang under the plate; `mv.flip` turns the dial tier over
to show them (see attach_driver). Draw order is painter's algorithm, valid while
the camera looks down on the movement (phi < 90 degrees).
"""
import sys
import numpy as np
from manim import *
from shapely.geometry import Polygon as SPoly, Point, LineString, box
from shapely import affinity
from shapely.ops import unary_union

# ============================================================== palette & fonts
BG = "#06070a"
BRASS, BRASS_DK, BRASS_HI = "#c49a43", "#6e5320", "#f1d58e"
GILT = "#d8b25c"
STEEL, STEEL_DK, STEEL_HI = "#8a939d", "#3d434a", "#e3e9ef"
PLATE, PLATE_DK = "#6f7780", "#30353b"
RUBY, RUBY_HI = "#b80f27", "#ff7383"
SCREW, SCREW_HI = "#28489a", "#7fa2ee"
GLOW = "#ffe7b0"

if sys.platform == "darwin":
    FONT_SANS, FONT_SERIF = "Helvetica Neue", "Georgia"
else:
    FONT_SANS, FONT_SERIF = "DejaVu Sans", "DejaVu Serif"


def polar(d, deg):
    a = np.radians(deg)
    return np.array([d * np.cos(a), d * np.sin(a), 0.0])


# ============================================================== kinematics
MOD = 0.03                  # default tooth module for parts outside the going train
BEATS = 5                   # 18,000 vph -> 2.5 Hz balance, 5 beats per second
BAL_HZ = BEATS / 2
BAL_AMPLITUDE = 1.5         # radians; a real balance swings ~4.7 rad, which strobes on video

# Going train. These counts keep real time at 5 beats/s with a 15-tooth escape
# wheel: the seconds (fourth) wheel turns once a minute, the center wheel once an
# hour, the barrel once every 8 hours. ETA does not publish its counts.
TEETH = dict(barrel=80, center_p=10, center=80, third_p=10, third=75,
             fourth_p=10, fourth=70, escape_p=7, escape=15)

# Pivot positions traced from ETA's bridge-side drawing (stem turned to +x).
# Each mesh gets the module that makes the traced center distance exact, so
# wheels and pinions really mesh (watchmakers also use a different module per mesh).
_TRACE = {"barrel": (0.765, 1.362), "third": (-0.992, 0.382), "fourth": (-1.673, 0.0),
          "escape": (-1.709, -0.717), "pallet": (-1.279, -1.087), "balance": (-0.657, -1.625)}


def _d(a, b):
    return float(np.hypot(*(np.array(_TRACE.get(a, (0, 0))) - np.array(_TRACE.get(b, (0, 0))))))


MESH = {"barrel": _d("barrel", "center") / ((TEETH["barrel"] + TEETH["center_p"]) / 2),
        "center": _d("center", "third") / ((TEETH["center"] + TEETH["third_p"]) / 2),
        "third": _d("third", "fourth") / ((TEETH["third"] + TEETH["fourth_p"]) / 2),
        "fourth": _d("fourth", "escape") / ((TEETH["fourth"] + TEETH["escape_p"]) / 2)}
R = {"barrel": MESH["barrel"] * TEETH["barrel"] / 2, "center_p": MESH["barrel"] * TEETH["center_p"] / 2,
     "center": MESH["center"] * TEETH["center"] / 2, "third_p": MESH["center"] * TEETH["third_p"] / 2,
     "third": MESH["third"] * TEETH["third"] / 2, "fourth_p": MESH["third"] * TEETH["fourth_p"] / 2,
     "fourth": MESH["fourth"] * TEETH["fourth"] / 2, "escape_p": MESH["fourth"] * TEETH["escape_p"] / 2,
     "escape": 0.36, "balance": 0.98}


def _toward(a, b):
    v = np.array(_TRACE[b]) - (np.array(_TRACE[a]) if a != "center" else 0)
    return np.degrees(np.arctan2(v[1], v[0]))


P = {"center": np.zeros(3)}
P["barrel"] = polar(R["barrel"] + R["center_p"], _toward("center", "barrel"))
P["third"] = polar(R["center"] + R["third_p"], _toward("center", "third"))
P["fourth"] = P["third"] + polar(R["third"] + R["fourth_p"], _toward("third", "fourth"))
P["escape"] = P["fourth"] + polar(R["fourth"] + R["escape_p"], _toward("fourth", "escape"))
P["pallet"] = P["escape"] + polar(0.57, _toward("escape", "pallet"))
P["balance"] = P["pallet"] + polar(0.82, _toward("pallet", "balance"))
P["seconds"] = P["fourth"]                      # the fourth wheel carries the small seconds

# Winding train (bridge side): winding pinion -> crown wheel 420 -> ratchet wheel 415.
WIND_TEETH = dict(winding_pinion=16, crown_wheel=36, ratchet=60)
R["ratchet"], R["crown_wheel"] = 1.075, 0.67
P["winding_pinion"] = np.array([2.08, 0.0, 0.0])   # on the stem axis, under the plate


def _link(c1, d1, c2, d2, lower=True):
    """The point at distance d1 from c1 and d2 from c2 (circle intersection)."""
    c1, c2 = np.array(c1[:2], float), np.array(c2[:2], float)
    d = np.linalg.norm(c2 - c1)
    a = (d1 ** 2 - d2 ** 2 + d ** 2) / (2 * d)
    h = np.sqrt(max(0.0, d1 ** 2 - a ** 2))
    m = c1 + a * (c2 - c1) / d
    n = np.array([-(c2 - c1)[1], (c2 - c1)[0]]) / d
    sols = [m + h * n, m - h * n]
    p = min(sols, key=lambda s: s[1]) if lower else max(sols, key=lambda s: s[1])
    return np.array([p[0], p[1], 0.0])


# crown wheel: meshes the ratchet, with its rim over the winding pinion
P["crown_wheel"] = _link(P["barrel"], R["ratchet"] + R["crown_wheel"], P["winding_pinion"], R["crown_wheel"])


def state(t):
    """Angles (radians, about +z, seen from the bridge side) of the going train at time t.

    The escape wheel steps once per beat; every other wheel follows from tooth
    ratios, so speeds are physically consistent.
    """
    beats = np.floor(t * BEATS)
    frac = t * BEATS - beats
    step = beats + min(1.0, frac / 0.18)          # snap during first 18% of a beat
    esc = -step * TAU / (2 * TEETH["escape"])
    fourth = -esc * TEETH["escape_p"] / TEETH["fourth"]
    third = -fourth * TEETH["fourth_p"] / TEETH["third"]
    center = -third * TEETH["third_p"] / TEETH["center"]
    barrel_a = -center * TEETH["center_p"] / TEETH["barrel"]
    swing = np.sin(TAU * BAL_HZ * t)
    return dict(escape=esc, fourth=fourth, third=third, center=center, barrel=barrel_a,
                balance=BAL_AMPLITUDE * swing, pallet=0.16 * np.clip(swing * 4, -1, 1))


def winding_angles(turns):
    """Angles of the winding train after the crown has turned `turns` times."""
    cw = -turns * TAU * WIND_TEETH["winding_pinion"] / WIND_TEETH["crown_wheel"]
    ratchet = -cw * WIND_TEETH["crown_wheel"] / WIND_TEETH["ratchet"]
    return dict(crown_wheel=cw, ratchet=ratchet)


# ============================================================== geometry helpers
def _ring_coords(ring):
    c = np.array(ring.coords)[:-1]
    return [np.array([x, y, 0.0]) for x, y in c]


def vm(geom, color, opacity=1.0, stroke=None, sw=0.8, sop=1.0):
    """Shapely (Multi)Polygon, holes included -> one VMobject."""
    polys = list(geom.geoms) if hasattr(geom, "geoms") else [geom]
    m = VMobject()
    first = True
    for p in polys:
        if p.is_empty or p.geom_type != "Polygon":
            continue
        for i, ring in enumerate([p.exterior] + list(p.interiors)):
            pts = _ring_coords(ring)
            # cairo nonzero winding: exterior CCW, holes CW
            if (i == 0) != ring.is_ccw:
                pts = pts[::-1]
            sub = VMobject().set_points_as_corners(pts + [pts[0]])
            if first:
                m.set_points(sub.points)
                first = False
            else:
                m.append_points(sub.points)
    m.set_fill(color, opacity).set_stroke(stroke or color, sw, sop)
    return m


def slab(geom, color, side, thick, stroke=None, sw=0.8):
    """A part with visible thickness: darker underside copy plus top face."""
    top = vm(geom, color, stroke=stroke, sw=sw)
    bot = vm(geom, side, stroke=side, sw=sw).shift(IN * thick)
    g = VGroup(bot, top)
    g._slab = True                  # lets a flipped tier swap which face is lit
    return g


def lift(m, dz):
    m.shift(OUT * dz)
    return m


def at(m, p):
    m.shift(np.array([p[0], p[1], 0.0]))
    return m


def disk_g(r, c=(0, 0), n=64):
    return Point(c[0], c[1]).buffer(r, quad_segs=max(4, n // 4))


def teeth_g(r_pitch, n, addendum=None, dedendum=None, m=None):
    m = m or MOD
    a = addendum or m * 1.0
    d = dedendum or m * 1.25
    pts = []
    for k in range(n):
        a0, da = TAU * k / n, TAU / n
        for frac, rr in ((0.00, r_pitch - d), (0.12, r_pitch - d), (0.22, r_pitch + a * 0.8),
                         (0.30, r_pitch + a), (0.42, r_pitch + a), (0.50, r_pitch + a * 0.8),
                         (0.60, r_pitch - d)):
            ang = a0 + frac * da
            pts.append((rr * np.cos(ang), rr * np.sin(ang)))
    return SPoly(pts)


def ratchet_teeth_g(r, n, depth):
    """Sawtooth (ratchet) teeth: a steep face the click catches, then a slope."""
    pts = []
    for k in range(n):
        a = TAU * k / n
        pts += [((r - depth) * np.cos(a), (r - depth) * np.sin(a)),
                (r * np.cos(a + 0.12 * TAU / n), r * np.sin(a + 0.12 * TAU / n))]
    return SPoly(pts)


def wheel_g(r, n, spokes=4, rim=0.16, hub=0.18, spoke_w=0.07, phase=0.3, curved=False, m=None):
    m = m or MOD
    g = teeth_g(r, n, m=m)
    r_in = r * (1 - rim) - m
    window = disk_g(r_in).difference(disk_g(r * hub))
    for k in range(spokes):
        a = phase + TAU * k / spokes
        if curved:
            pts = [(rr * np.cos(a + 0.6 * (rr / r) ** 2), rr * np.sin(a + 0.6 * (rr / r) ** 2))
                   for rr in np.linspace(r * hub * 0.5, r_in * 1.02, 12)]
            sp = LineString(pts).buffer(r * spoke_w / 2)
        else:
            sp = LineString([(0, 0), (r_in * 1.05 * np.cos(a), r_in * 1.05 * np.sin(a))]).buffer(r * spoke_w)
        window = window.difference(sp)
    return g.difference(window).difference(disk_g(0.025))


def pinion_g(n, m=None):
    m = m or MOD
    return teeth_g(m * n / 2, n, m * 0.9, m * 1.1, m=m)


def stripes_g(region, width=0.11, angle=62, gap_ratio=0.5):
    """Côtes de Genève bands clipped to region."""
    minx, miny, maxx, maxy = region.bounds
    L = 2 * max(maxx - minx, maxy - miny) + 2
    bands, x = [], -L
    while x < L:
        bands.append(box(x, -L, x + width * gap_ratio, L))
        x += width
    return affinity.rotate(unary_union(bands), angle, origin=(0, 0)).intersection(region)


def circ_stripes_g(region, center=(0, 0), step=0.09):
    """Côtes circulaires (concentric graining) clipped to region."""
    rings, r = [], step
    while r < 4:
        rings.append(disk_g(r + step * 0.45, center).difference(disk_g(r, center)))
        r += step
    return unary_union(rings).intersection(region)


def rounded(pts, r=0.12):
    return SPoly(pts).buffer(-r, join_style=1).buffer(2 * r, join_style=1).buffer(-r, join_style=1)


def arc_pts(r, a0, a1, n=40):
    """Points on a circle of radius r from angle a0 to a1 (degrees, counterclockwise)."""
    return [tuple(polar(r, a)[:2]) for a in np.linspace(a0, a1, n)]


def jewel(p, r=0.07, chaton=True):
    g = VGroup()
    if chaton:
        g.add(vm(disk_g(r * 1.75, p), GILT, stroke=BRASS_HI, sw=0.6))
    g.add(vm(disk_g(r, p), RUBY, stroke=RUBY_HI, sw=0.7))
    g.add(vm(disk_g(r * 0.32, (p[0] - r * 0.3, p[1] + r * 0.32)), RUBY_HI, sw=0))
    g.add(vm(disk_g(r * 0.22, p), "#3a0008", sw=0))
    return g


def screw(p, r=0.085, ang=0.4):
    head = vm(disk_g(r, p), SCREW, stroke=SCREW_HI, sw=0.8)
    slot = vm(affinity.rotate(box(-r, -r * 0.16, r, r * 0.16), ang, use_radians=True)
              .intersection(disk_g(r * 0.9)), "#0c1222", sw=0)
    return VGroup(head, at(slot, p))


def dv(p):
    """A bridge-side xy position as seen in the dial tier's own (dial-up) frame."""
    return (float(p[0]), -float(p[1]))


def _swap_faces(g):
    """Exchange the styles of a slab's two faces (the lit face is drawn last)."""
    a, b = g.submobjects
    sa = (a.get_fill_color(), a.get_fill_opacity(), a.get_stroke_color(), a.get_stroke_width(), a.get_stroke_opacity())
    sb = (b.get_fill_color(), b.get_fill_opacity(), b.get_stroke_color(), b.get_stroke_width(), b.get_stroke_opacity())
    for m, (fc, fo, sc, sw, so) in ((a, sb), (b, sa)):
        m.set_fill(fc, fo, family=False).set_stroke(sc, sw, so, family=False)


def reverse_draw_order(m):
    """Reverse painter's order through the whole family (for a tier turned over)."""
    if getattr(m, "_slab", False):
        _swap_faces(m)
    m.submobjects.reverse()
    for s in m.submobjects:
        reverse_draw_order(s)


# ============================================================== the movement
DIAL_AXIS_Z = -0.07         # the dial tier turns over about this line (mid-plate, along x)


class Movement:
    """Holds the three tiers and the list of moving parts.

    tiers : {"dial", "engine", "top"} -> VGroup
    refs  : invisible Dot per tier on its reference point (tracks the tier's height)
    parts : {name -> mobject} for every individually addressable part
    rot   : list of (mobject, pivot_xy, tier, angle_fn(state) -> radians). Dial-tier
            pivots and angles are in the dial tier's own dial-up frame.
    wind  : ValueTracker, crown turns; drives crown wheel, ratchet and click
    regulate : ValueTracker, regulator index angle in degrees
    flip  : ValueTracker, 0 = dial side down (as fitted), 1 = dial side up

    Movement(dial_up=True) starts with the dial tier turned dial side up.
    """

    def __init__(self, dial_up=False):
        self.parts, self.rot = {}, []
        self.wind, self.regulate = ValueTracker(0.0), ValueTracker(0.0)
        self.flip = ValueTracker(1.0 if dial_up else 0.0)
        self.tiers = {"dial": self._dial(), "engine": self._engine(), "top": self._top()}
        self.dial_alpha = 0.0                     # current turn of the dial tier about the x-axis
        if not dial_up:
            self.tiers["dial"].rotate(PI, axis=RIGHT, about_point=np.array([0, 0, DIAL_AXIS_Z]))
            reverse_draw_order(self.tiers["dial"])
            self.dial_alpha = PI

    def _ref(self, z=0.0):
        return Dot(OUT * z).set_opacity(0)

    # ---------------------------------------------------------- tier 1: dial side
    # Built dial side up (as on ETA's page 5): z = 0 is the dial face of the plate,
    # the plate's bridge face is at z = -0.14, and positions are mirrored with dv().
    def _dial(self):
        plate_g = disk_g(3.0, n=192).difference(box(2.25, -0.18, 3.2, 0.18))   # stem slot
        for k in ("center", "third", "fourth", "escape", "barrel", "balance", "pallet"):
            plate_g = plate_g.difference(disk_g(0.05, dv(P[k])))
        plate = slab(plate_g, PLATE, PLATE_DK, 0.14, stroke=STEEL_HI, sw=1.6)

        def perlage(z):
            return lift(VGroup(*[
                vm(disk_g(0.17, (x, y), 24).difference(disk_g(0.15, (x, y), 24)), STEEL_HI, 0.18, sw=0)
                for x in np.arange(-2.75, 2.8, 0.24) for y in np.arange(-2.75, 2.8, 0.24)
                if x * x + y * y < 2.72 ** 2]), z)

        train = ("center", "third", "fourth", "escape", "balance", "pallet")
        bridge_face = VGroup(perlage(-0.144),
                             lift(VGroup(*[jewel(dv(P[k]), 0.06) for k in train]), -0.146))
        dial_face = VGroup(perlage(0.004),
                           lift(VGroup(*[jewel(dv(P[k]), 0.045, chaton=False) for k in train if k != "balance"]), 0.006),
                           lift(VGroup(vm(disk_g(0.15, dv(P["balance"])).difference(disk_g(0.11, dv(P["balance"]))),
                                          GILT, sw=0),                                        # lower shock setting 3025
                                       jewel(dv(P["balance"]), 0.06, chaton=False)), 0.006),
                           lift(VGroup(vm(disk_g(0.07, dv(P["seconds"])), STEEL_HI, stroke=WHITE, sw=0.5)), 0.03))   # seconds pivot 224

        # motion works: driver cannon pinion 240 (12), minute wheel 260 (36, pinion 10), hour wheel 250 (40)
        mw_p = polar(1.0, -22)
        m_a, m_b = 1.0 / ((12 + 36) / 2), 1.0 / ((10 + 40) / 2)
        cannon = slab(pinion_g(12, m_a).difference(disk_g(0.05)), STEEL, STEEL_DK, 0.05, STEEL_HI)
        hour = slab(wheel_g(m_b * 20, 40, spokes=0, rim=0.5, hub=0.35, m=m_b).difference(disk_g(0.14)),
                    BRASS, BRASS_DK, 0.04, BRASS_HI)
        minute = at(VGroup(slab(wheel_g(m_a * 18, 36, spokes=3, rim=0.25, hub=0.25, m=m_a), STEEL, STEEL_DK, 0.04),
                           lift(slab(pinion_g(10, m_b), STEEL_HI, STEEL_DK, 0.04, WHITE, 0.4), 0.04)), mw_p)
        lift(hour, 0.05); lift(cannon, 0.10); lift(minute, 0.05)
        self.rot += [(cannon, (0, 0), "dial", lambda s: -s["center"]),
                     (minute, mw_p, "dial", lambda s: s["center"] * 12 / 36),
                     (hour, (0, 0), "dial", lambda s: -s["center"] / 12)]

        # keyless works: setting lever 443, yoke 435, setting wheel 450, winding pinion 410,
        # sliding pinion 407, stem 401, crown (order kept: scene02 indexes this group)
        stem = VGroup(Line([2.15, 0, 0], [3.65, 0, 0]).set_stroke(STEEL_HI, 7),
                      Line([2.15, 0, 0], [3.65, 0, 0]).set_stroke(STEEL_DK, 2))
        crown_g = box(3.65, -0.28, 3.95, 0.28)
        for y in np.linspace(-0.26, 0.26, 9):
            crown_g = crown_g.difference(box(3.9, y - 0.012, 3.96, y + 0.012))
        crown = slab(crown_g, STEEL, STEEL_DK, 0.18, STEEL_HI)
        sliding = slab(box(2.45, -0.11, 2.75, 0.11), STEEL_HI, STEEL_DK, 0.06)
        wind_pin = at(slab(teeth_g(0.13, 14).difference(disk_g(0.04)), STEEL, STEEL_DK, 0.05, STEEL_HI), (2.1, 0.0))
        setting_lever = slab(rounded([(2.0, -0.35), (2.7, -0.25), (2.75, -0.55), (1.6, -1.15), (1.35, -0.95)], 0.08),
                             STEEL, STEEL_DK, 0.05, STEEL_HI)
        yoke = slab(rounded([(2.55, 0.2), (2.75, 0.3), (2.3, 1.35), (1.75, 1.55), (1.7, 1.35), (2.15, 1.15)], 0.07),
                    STEEL, STEEL_DK, 0.05, STEEL_HI)
        set_p = (2.36, -0.36)
        set_wheel = at(slab(wheel_g(0.2, 20, spokes=0, rim=0.6, hub=0.3), STEEL, STEEL_DK, 0.04, STEEL_HI), set_p)
        keyless = VGroup(*[lift(m, 0.06) for m in (setting_lever, yoke, set_wheel, wind_pin, sliding)],
                         lift(stem, 0.1), lift(crown, 0.18))

        # setting train continues: intermediate setting wheel 453 between 450 and the minute wheel
        mid_p = _link(set_p, 0.2 + 0.27, mw_p, m_a * 18 + 0.27, lower=True)
        intermediate = lift(at(slab(wheel_g(0.27, 26, spokes=0, rim=0.55, hub=0.3), STEEL, STEEL_DK, 0.04, STEEL_HI),
                               mid_p), 0.07)
        # yoke spring 440 (a wire) and setting lever jumper 445 (a cover plate over the yoke pivot)
        spring_pts = [np.array([x, y, 0]) for x, y in ((1.35, 1.75), (1.6, 1.3), (1.95, 1.0), (2.35, 0.62), (2.6, 0.36))]
        yoke_spring = lift(VMobject().set_points_smoothly(spring_pts).set_stroke(STEEL_HI, 2.2).set_fill(opacity=0), 0.08)
        jumper_g = rounded([(1.2, 1.15), (1.65, 0.85), (2.05, 1.05), (2.2, 1.6), (1.85, 2.05), (1.3, 1.9)], 0.1)
        jumper = lift(slab(jumper_g.difference(disk_g(0.05, (1.85, 1.38))), STEEL, STEEL_DK, 0.04, STEEL_HI, 1.0), 0.13)
        screws = lift(VGroup(*[screw(p) for p in ((1.55, -0.95), (1.85, 1.38), (-2.3, -1.3), (-1.4, 2.2))]), 0.18)

        works = VGroup(hour, minute, cannon, keyless, intermediate, yoke_spring, jumper, screws)
        self.parts.update(plate=plate, cannon_pinion=cannon, hour_wheel=hour, minute_wheel=minute,
                          keyless=keyless, stem=stem, crown=crown, setting_wheel=set_wheel,
                          intermediate_setting_wheel=intermediate, yoke_spring=yoke_spring,
                          setting_lever_jumper=jumper, dial_screws=screws, dial_works=works,
                          dial_face=dial_face, bridge_face=bridge_face)
        self.dial_ref = self._ref(DIAL_AXIS_Z)
        return VGroup(self.dial_ref, bridge_face, plate, dial_face, works)

    # ---------------------------------------------------------- tier 2: middle engine
    def _engine(self):
        def train_wheel(name, pin, spokes=5):
            mesh_w = {"center": "center", "third": "third", "fourth": "fourth"}[name]
            mesh_p = {"center": "barrel", "third": "center", "fourth": "third"}[name]
            w = slab(wheel_g(R[name], TEETH[name], spokes=spokes, curved=True, m=MESH[mesh_w]),
                     BRASS, BRASS_DK, 0.045, BRASS_HI, 0.7)
            p = lift(slab(pinion_g(TEETH[pin], MESH[mesh_p]).difference(disk_g(0.02)), STEEL_HI, STEEL_DK, 0.05,
                          WHITE, 0.4), 0.05)
            return VGroup(w, p)

        # movement barrel 180/1: toothed drum, open so the mainspring 770 shows
        rb = R["barrel"]
        drum_g = teeth_g(rb, TEETH["barrel"], m=MESH["barrel"]).difference(disk_g(rb * 0.9))
        floor = vm(disk_g(rb * 0.9), BRASS_DK, stroke=BRASS, sw=0.6)
        spring_pts = [(0.2 + 0.042 * t) * np.array([np.cos(t), np.sin(t), 0]) for t in np.linspace(0, 25, 560)]
        mainspring = VMobject().set_points_smoothly(spring_pts).set_stroke(STEEL_HI, 1.6).set_fill(opacity=0)
        shadow = mainspring.copy().set_stroke("#1a1c20", 3.0).shift(IN * 0.01 + RIGHT * 0.01)
        arbor = vm(disk_g(0.17), STEEL_HI, stroke=WHITE, sw=0.6)
        barrel = at(VGroup(slab(drum_g, BRASS, BRASS_DK, 0.12, BRASS_HI), floor,
                           lift(shadow, 0.02), lift(mainspring, 0.03), lift(arbor, 0.04)), P["barrel"])

        # each arbor: its wheel, and the pinion driven by the previous wheel
        center_w = at(lift(train_wheel("center", "center_p"), 0.06), P["center"])     # 201
        third_w = at(lift(train_wheel("third", "third_p"), 0.10), P["third"])         # 210
        fourth_w = at(lift(train_wheel("fourth", "fourth_p"), 0.14), P["fourth"])     # 220/224, small seconds

        # club-tooth escape wheel 705 (steel)
        n, pts, re = TEETH["escape"], [], R["escape"]
        for k in range(n):
            a = TAU * k / n
            for da, rr in ((0.00, 0.62), (0.05, 0.95), (0.13, 1.0), (0.16, 0.93), (0.30, 0.66)):
                pts.append((re * rr * np.cos(a + da * TAU / n * 3), re * rr * np.sin(a + da * TAU / n * 3)))
        esc_g = SPoly(pts).buffer(0)
        win = disk_g(re * 0.5).difference(disk_g(re * 0.16))
        for k in range(4):
            a = TAU * k / 4
            win = win.difference(LineString([(0, 0), (np.cos(a), np.sin(a))]).buffer(0.018))
        escape_w = VGroup(slab(esc_g.difference(win), STEEL, STEEL_DK, 0.035, STEEL_HI, 0.6),
                          lift(slab(pinion_g(TEETH["escape_p"], MESH["fourth"]), STEEL_HI, STEEL_DK, 0.04, WHITE, 0.4),
                               0.04))
        at(lift(escape_w, 0.18), P["escape"])

        # pallet fork 710 with ruby pallet stones; the lever points at the balance
        e, pp, b = P["escape"][:2], P["pallet"][:2], P["balance"][:2]
        u = (b - pp) / np.linalg.norm(b - pp)
        nrm = np.array([-u[1], u[0]])
        to_pallet = np.degrees(np.arctan2(*(pp - e)[::-1]))
        entry = e + polar(re * 1.02, to_pallet + 34)[:2]
        exitp = e + polar(re * 1.02, to_pallet - 34)[:2]
        tip = pp + u * 0.62
        fork_g = unary_union([
            LineString([tuple(pp), tuple(entry)]).buffer(0.035),
            LineString([tuple(pp), tuple(exitp)]).buffer(0.035),
            LineString([tuple(pp), tuple(tip)]).buffer(0.03),
            LineString([tuple(tip), tuple(tip + u * 0.1 + nrm * 0.08)]).buffer(0.022),
            LineString([tuple(tip), tuple(tip + u * 0.1 - nrm * 0.08)]).buffer(0.022),
            Point(tuple(pp)).buffer(0.07)])
        stones = VGroup(*[vm(Point(tuple(q)).buffer(0.035), RUBY, stroke=RUBY_HI, sw=0.5) for q in (entry, exitp)])
        pallet = lift(VGroup(slab(fork_g, STEEL_HI, STEEL_DK, 0.03, WHITE, 0.5), lift(stones, 0.002)), 0.22)

        # timed annular balance 721: plain ring, three arms, hairspring, double roller 730
        rb = R["balance"]
        bal_g = disk_g(rb, n=128).difference(disk_g(rb * 0.9, n=128))
        for a in (0.3, 0.3 + TAU / 3, 0.3 + 2 * TAU / 3):
            bal_g = bal_g.union(LineString([(0, 0), (rb * 0.92 * np.cos(a), rb * 0.92 * np.sin(a))]).buffer(0.032))
        bal_g = bal_g.union(disk_g(0.09))
        wheel = slab(bal_g, GILT, BRASS_DK, 0.06, BRASS_HI)
        hs_pts = [(0.14 + 0.075 * t / TAU) * np.array([np.cos(t), np.sin(t), 0]) for t in np.linspace(0, 7 * TAU, 600)]
        hairspring = VMobject().set_points_smoothly(hs_pts).set_stroke(STEEL_HI, 1.0).set_fill(opacity=0)
        roller = vm(disk_g(0.12), STEEL_HI, stroke=WHITE, sw=0.5)
        impulse = vm(disk_g(0.025, (0.0, -0.1)), RUBY, sw=0)
        balance = VGroup(wheel, lift(hairspring, 0.03), lift(roller, 0.04), lift(impulse, 0.045))
        at(lift(balance, 0.24), P["balance"])

        for name, mob in (("barrel", barrel), ("center", center_w), ("third", third_w), ("fourth", fourth_w),
                          ("escape", escape_w), ("pallet", pallet), ("balance", balance)):
            self.rot.append((mob, P[name], "engine", lambda s, name=name: s[name]))
        self.parts.update(barrel=barrel, center_wheel=center_w, third_wheel=third_w, fourth_wheel=fourth_w,
                          seconds_wheel=fourth_w, escape_wheel=escape_w, pallet_fork=pallet, balance=balance,
                          balance_wheel=wheel, hairspring=hairspring)
        self.engine_ref = self._ref()
        return VGroup(self.engine_ref, barrel, center_w, third_w, fourth_w, escape_w, pallet, balance)

    # ---------------------------------------------------------- tier 3: top modules
    def _top(self):
        clear_bal = disk_g(R["balance"] + 0.06, P["balance"][:2])

        def bridge(g, holes, cotes=True):
            for h in holes:
                g = g.difference(disk_g(0.11, h[:2]))
            parts = VGroup(slab(g, STEEL, STEEL_DK, 0.12, STEEL_HI, 1.4))
            if cotes:
                parts.add(lift(vm(stripes_g(g.buffer(-0.04)), STEEL_HI, 0.22, sw=0), 0.002))
            parts.add(lift(vm(g.difference(g.buffer(-0.035)), WHITE, 0.55, sw=0), 0.003))   # bevel
            return parts

        # bridge outlines traced from ETA's drawing (edge arcs in degrees, stem at 0)
        seam = (-0.394, 0.681), (-0.394, -0.275)
        barrel_g = rounded(arc_pts(2.95, -35.8, 135.2) +
                           [(-2.067, 2.055), seam[0], seam[1], (1.040, -1.769), (2.387, -1.734)], 0.1)
        train_g = rounded(arc_pts(2.95, 135.2, 222.9) +
                          [(-2.163, -2.008), (-1.589, -1.171), seam[1], seam[0], (-2.067, 2.055)], 0.1)
        barrel_g = barrel_g.buffer(-0.025).difference(clear_bal)
        train_g = train_g.buffer(-0.025).difference(clear_bal)
        barrel_bridge = bridge(barrel_g, [P["barrel"], P["center"]])                 # 105
        train_bridge = bridge(train_g, [P["third"], P["fourth"], P["escape"]])       # 110

        e, pp = P["escape"][:2], P["pallet"][:2]
        u = (pp - e) / np.linalg.norm(pp - e)
        n = np.array([-u[1], u[0]])
        c = pp - u * 0.12
        pallet_g = rounded([tuple(c + u * a + n * b) for a, b in ((-0.45, -0.3), (0.3, -0.3), (0.3, 0.3), (-0.45, 0.3))], 0.12)
        pallet_bridge = bridge(pallet_g, [P["pallet"]], cotes=False)                  # 125

        bc = P["balance"][:2]
        cock_screw = bc + np.array([1.18, -0.9])
        cock_g = unary_union([disk_g(0.34, bc), disk_g(0.3, cock_screw),
                              LineString([tuple(bc), tuple(cock_screw)]).buffer(0.26)])
        balance_cock = bridge(cock_g, [P["balance"]])                                 # 121/3

        # two-piece regulator 303/5 with long pointer, stud support 375, shock absorber 3024
        reg_dir = polar(1.0, -11.7)[:2]
        regulator = lift(VGroup(
            slab(unary_union([disk_g(0.15, bc).difference(disk_g(0.1, bc)),
                              LineString([tuple(bc), tuple(bc + reg_dir * 1.3)]).buffer(0.028),
                              disk_g(0.05, tuple(bc + reg_dir * 1.3))]), STEEL_HI, STEEL_DK, 0.03, WHITE, 0.5),
            lift(slab(unary_union([LineString([tuple(bc), tuple(bc + polar(0.5, 100)[:2])]).buffer(0.035),
                                   disk_g(0.07, tuple(bc + polar(0.5, 100)[:2]))]), STEEL, STEEL_DK, 0.03, STEEL_HI, 0.5),
                 0.01)), 0.14)
        shock = lift(VGroup(vm(disk_g(0.14, bc).difference(disk_g(0.11, bc)), GILT, sw=0),
                            vm(LineString([(bc[0] - 0.1, bc[1] - 0.08), (bc[0] + 0.1, bc[1] + 0.08)]).buffer(0.012),
                               GILT, sw=0), jewel(bc, 0.05, chaton=False)), 0.18)
        self.rot.append((regulator, bc, "top", lambda s: self.regulate.get_value() * DEGREES))

        # winding: ratchet wheel 415, crown wheel 420 with ring 422, click 425, click spring 430
        br = P["barrel"][:2]
        ratchet = VGroup(slab(ratchet_teeth_g(R["ratchet"], WIND_TEETH["ratchet"], 0.05).difference(disk_g(0.1)),
                              STEEL_HI, STEEL_DK, 0.06, WHITE, 0.6),
                         lift(vm(circ_stripes_g(disk_g(R["ratchet"] - 0.08).difference(disk_g(0.16)), step=0.05),
                                 WHITE, 0.25, sw=0), 0.002),
                         lift(screw((0, 0), 0.12), 0.01))
        at(lift(ratchet, 0.14), br)
        cwp = P["crown_wheel"][:2]
        crown_wheel = VGroup(slab(teeth_g(R["crown_wheel"], WIND_TEETH["crown_wheel"], 0.03, 0.035)
                                  .difference(disk_g(0.08)), STEEL_HI, STEEL_DK, 0.05, WHITE, 0.6),
                             lift(vm(circ_stripes_g(disk_g(R["crown_wheel"] - 0.07).difference(disk_g(0.16)), step=0.05),
                                     WHITE, 0.25, sw=0), 0.002),
                             lift(vm(disk_g(0.17).difference(disk_g(0.1)), STEEL, stroke=STEEL_HI, sw=0.5), 0.01),
                             lift(screw((0, 0), 0.09, 1.2), 0.015))
        at(lift(crown_wheel, 0.14), cwp)
        click_pivot = br + polar(R["ratchet"] + 0.32, 163)[:2]
        click_tip = br + polar(R["ratchet"] - 0.02, 147)[:2]
        click = lift(VGroup(slab(unary_union([disk_g(0.11, click_pivot),
                                              LineString([tuple(click_pivot), tuple(click_tip)]).buffer(0.06)]),
                                 STEEL_HI, STEEL_DK, 0.04, WHITE, 0.5),
                            lift(screw(click_pivot, 0.07, 0.8), 0.005)), 0.14)
        cs_pts = [np.array([*(br + polar(R["ratchet"] + r, a)[:2]), 0]) for r, a in ((0.3, 186), (0.42, 176), (0.4, 160))]
        click_spring = lift(VMobject().set_points_smoothly(cs_pts).set_stroke(STEEL_HI, 2.0).set_fill(opacity=0), 0.15)
        tooth = TAU / WIND_TEETH["ratchet"]

        def click_angle(s):
            ph = (winding_angles(self.wind.get_value())["ratchet"] % tooth) / tooth
            return 0.12 * ph                       # rides up a tooth, drops off its face
        self.rot += [(ratchet, br, "top", lambda s: winding_angles(self.wind.get_value())["ratchet"]),
                     (crown_wheel, cwp, "top", lambda s: winding_angles(self.wind.get_value())["crown_wheel"]),
                     (click, click_pivot, "top", click_angle)]

        jewels = lift(VGroup(*[jewel(P[k], 0.075) for k in ("center", "third", "fourth", "escape", "pallet")]), 0.004)
        screws = lift(VGroup(*[screw(p, ang=a) for p, a in (
            ((2.390, 1.099), 0.3), ((1.876, -1.374), 1.1), ((-1.291, 1.912), 2.0),          # 5105 (3x)
            ((-2.067, 1.374), 0.7), ((-2.366, -1.171), 2.4),                                # 5110 (2x)
            (tuple(cock_screw), 0.9),                                                       # 5121
            (tuple(pp + n * 0.2 - u * 0.35), 1.6), (tuple(pp - n * 0.2 - u * 0.35), 0.2))]),  # 5125 (2x)
                      0.004)

        bridges = lift(VGroup(barrel_bridge, train_bridge, pallet_bridge, balance_cock), 0.12)
        self.parts.update(barrel_bridge=barrel_bridge, train_bridge=train_bridge, pallet_bridge=pallet_bridge,
                          pallet_cock=pallet_bridge, balance_cock=balance_cock, balance_bridge=balance_cock,
                          regulator=regulator, shock_protection=shock, ratchet_wheel=ratchet,
                          crown_wheel=crown_wheel, click=click, click_spring=click_spring,
                          top_jewels=jewels, top_screws=screws)
        self.top_ref = self._ref()
        return VGroup(self.top_ref, bridges, lift(jewels, 0.12), lift(screws, 0.12),
                      regulator, shock, ratchet, crown_wheel, click, click_spring)

    @property
    def refs(self):
        return {"dial": self.dial_ref, "engine": self.engine_ref, "top": self.top_ref}

    @property
    def group(self):
        return VGroup(*self.tiers.values())

    def world(self, tier, xy, z_local=0.0):
        """World position of a point given in a tier's own frame (dial tier: dial-up frame)."""
        ref = self.refs[tier].get_center()
        if tier != "dial":
            return np.array([xy[0], xy[1], ref[2] + z_local])
        a = self.dial_alpha
        rx = np.array([[1, 0, 0], [0, np.cos(a), -np.sin(a)], [0, np.sin(a), np.cos(a)]])
        return ref + rx @ np.array([xy[0], xy[1], z_local - DIAL_AXIS_Z])


# ============================================================== driver
TIER_REF_OFFSET = {"dial": DIAL_AXIS_Z, "engine": 0.0, "top": 0.0}


def attach_driver(scene, mv, z_assembled, z_exploded):
    """Animate the movement with ONE updater (never .animate a tier: that
    freezes updaters). z values are the height of each tier's base: for the
    dial tier, the bridge face of the main plate. Returns (explode, dim):

      explode : ValueTracker 0 -> 1 moves tiers from z_assembled to z_exploded
      dim     : {tier: ValueTracker} opacity multiplier per tier (1 = normal)

    Also animatable, on the Movement: mv.flip (0 -> 1 turns the dial tier dial
    side up, about the stem axis), mv.wind (crown turns), mv.regulate (degrees).
    """
    tiers, refs = mv.tiers, mv.refs
    for k, t in tiers.items():
        t.shift(OUT * (z_assembled[k] + TIER_REF_OFFSET[k] - refs[k].get_center()[2]))
    clock = {"t": 0.0}
    explode = ValueTracker(0.0)
    dim = {k: ValueTracker(1.0) for k in tiers}
    base_op = {k: [(m, m.get_fill_opacity(), m.get_stroke_opacity()) for m in t.family_members_with_points()
                   if isinstance(m, VMobject)] for k, t in tiers.items()}
    applied = {k: 1.0 for k in tiers}

    def drive(_, dt):
        clock["t"] += dt
        e = explode.get_value()
        for k, t in tiers.items():
            zt = z_assembled[k] + (z_exploded[k] - z_assembled[k]) * e + TIER_REF_OFFSET[k]
            dz = zt - refs[k].get_center()[2]
            if abs(dz) > 1e-9:
                t.shift(OUT * dz)
            v = dim[k].get_value()
            if abs(v - applied[k]) > 1e-4:
                for m, fo, so in base_op[k]:
                    m.set_fill(opacity=fo * v, family=False)
                    m.set_stroke(opacity=so * v, family=False)
                applied[k] = v
        if "dial" in tiers:                               # turn the dial tier over
            target = PI * (1 - mv.flip.get_value())
            d = target - mv.dial_alpha
            if abs(d) > 1e-9:
                face_down = np.cos(mv.dial_alpha) < 0
                tiers["dial"].rotate(d, axis=RIGHT, about_point=refs["dial"].get_center())
                mv.dial_alpha = target
                if (np.cos(target) < 0) != face_down:
                    reverse_draw_order(tiers["dial"])
        s = state(clock["t"])
        ca, sa = np.cos(mv.dial_alpha), np.sin(mv.dial_alpha)
        for mob, pxy, tier, fn in mv.rot:
            target, cur = fn(s), getattr(mob, "_ang", 0.0)
            if target != cur:
                if tier == "dial":
                    axis, pivot = np.array([0.0, -sa, ca]), mv.world("dial", pxy)
                else:
                    axis, pivot = OUT, np.array([pxy[0], pxy[1], refs[tier].get_center()[2]])
                mob.rotate(target - cur, axis=axis, about_point=pivot)
                mob._ang = target

    driver = Mobject()
    driver.add_updater(drive)
    scene.add(mv.group, driver, explode, *dim.values(), mv.flip, mv.wind, mv.regulate)
    return explode, dim


def aim(phi, theta, zoom, target, frame_origin=ORIGIN):
    """frame_center that puts `target` at the middle of the screen.

    Manim's Cairo ThreeDCamera subtracts frame_center before the 3D rotation,
    and its cached cairo context also shifts the picture by -frame_center.xy as
    it was on the FIRST rendered frame. So a point passed as frame_center lands
    off-center by -frame_origin.xy, where frame_origin is the frame_center the
    scene started with. This solves for the frame_center that cancels that.
    Angles in degrees.
    """
    a = -(theta + 90) * DEGREES
    rz = np.array([[np.cos(a), -np.sin(a), 0], [np.sin(a), np.cos(a), 0], [0, 0, 1]])
    b = -phi * DEGREES
    rx = np.array([[1, 0, 0], [0, np.cos(b), -np.sin(b)], [0, np.sin(b), np.cos(b)]])
    mxy = (rx @ rz)[:2, :2]
    p, c0 = np.array(target, dtype=float), np.array(frame_origin, dtype=float)
    cxy = p[:2] - np.linalg.solve(zoom * mxy, c0[:2])
    return np.array([cxy[0], cxy[1], p[2]])


def camera_move(scene, run_time, rate_func=smooth, phi=None, theta=None, zoom=None, frame_center=None,
                target=None, frame_origin=ORIGIN):
    """Camera animations for scene.play(), each carrying its own run_time and rate_func.

    Use this instead of move_camera(added_anims=...) when other animations in the
    same play() have their own timing: move_camera passes its run_time and
    rate_func to every added animation, which stretches and eases timed cues.
    Angles in degrees. `target` (needs phi, theta, zoom) centers that 3D point on
    screen; pass the scene's starting frame_center as `frame_origin` (see aim()).
    `frame_center` is passed through as is. After the play(), call
    scene.remove(scene.camera._frame_center) (Manim does this to avoid redrawing
    every frame).
    """
    if target is not None:
        frame_center = aim(phi, theta, zoom, target, frame_origin)
    cam, kw, anims = scene.camera, dict(run_time=run_time, rate_func=rate_func), []
    for value, tracker in ((phi, cam.phi_tracker), (theta, cam.theta_tracker), (zoom, cam.zoom_tracker)):
        if value is not None:
            anims.append(tracker.animate(**kw).set_value(value * (DEGREES if tracker is not cam.zoom_tracker else 1)))
    if frame_center is not None:
        anims.append(cam._frame_center.animate(**kw).move_to(np.array(frame_center, dtype=float)))
    return anims


def cue(when, *anims, start, end, run_time=0.5):
    """Play anims at absolute time `when` inside a segment [start, end].

    Returns one animation lasting exactly end - start, so play() never
    stretches it. Pass it alongside camera_move() animations.
    """
    lead = max(0.0, when - start)
    dur = min(run_time, max(0.01, end - start - lead))
    parts = ([Wait(lead)] if lead > 1e-3 else []) + [AnimationGroup(*anims, run_time=dur)]
    tail = end - start - lead - dur
    if tail > 1e-3:
        parts.append(Wait(tail))
    return Succession(*parts)


def vignette():
    h, w = 270, 480
    y, x = np.mgrid[0:h, 0:w]
    d = np.sqrt(((x - w / 2) / (w / 2)) ** 2 + ((y - h / 2) / (h / 2)) ** 2)
    img = np.zeros((h, w, 4), dtype=np.uint8)
    img[..., 3] = (np.clip((d - 0.5) / 0.8, 0, 1) ** 1.5 * 240).astype(np.uint8)
    im = ImageMobject(img)
    return im.stretch_to_fit_width(config.frame_width).stretch_to_fit_height(config.frame_height)
