"""The watch movement model, shared by every scene in the tutorial.

Contents
  * PALETTE / fonts           - colors and typefaces used everywhere
  * kinematics                - tooth counts, pitch radii, pivot layout P, state(t)
  * geometry helpers          - shapely shapes -> Manim VMobjects, thickness, finishes
  * build_movement()          - builds the three tiers (dial / engine / top)
  * attach_driver()           - one updater that moves tiers, dims them, spins parts

Coordinates: the movement lies in the xy-plane, 6 units across (plate radius 3),
center wheel at the origin; +z points up out of the movement toward the rotor.
Draw order is painter's algorithm bottom-to-top, valid while the camera looks
down on the movement (phi < 90 degrees).
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

ROTOR_ENGRAVING = "AUTOMATIC  ·  ADJUSTED  ·  28 800 A/h"

# ============================================================== kinematics
# All train wheels share one tooth module so wheels and pinions really mesh.
MOD = 0.03
TEETH = dict(barrel=72, center_p=12, center=60, third_p=8, third=48,
             fourth_p=8, fourth=40, escape_p=7, escape=15)
R = {k: MOD * v / 2 for k, v in TEETH.items()}
R["escape"] = 0.40          # the club-tooth escape wheel is drawn separately
BEATS = 8                   # 28,800 vph -> 4 Hz balance, 8 beats per second
BAL_HZ = BEATS / 2


def polar(d, deg):
    a = np.radians(deg)
    return np.array([d * np.cos(a), d * np.sin(a), 0.0])


# Pivot layout. Each center distance = wheel pitch radius + next pinion's.
# The angles are free layout choices.
P = {"center": np.zeros(3)}
P["barrel"] = P["center"] + polar(R["barrel"] + R["center_p"], 148)
P["third"] = P["center"] + polar(R["center"] + R["third_p"], -38)
P["fourth"] = P["third"] + polar(R["third"] + R["fourth_p"], 28)
P["escape"] = P["fourth"] + polar(R["fourth"] + R["escape_p"], 96)
P["pallet"] = P["escape"] + polar(0.62, 118)
P["balance"] = P["pallet"] + polar(0.95, 128)


def state(t):
    """Angles (radians) of every moving part at time t (seconds).

    The escape wheel steps once per beat; every other train wheel follows
    from tooth ratios, so speeds are physically consistent.
    """
    beats = np.floor(t * BEATS)
    frac = t * BEATS - beats
    step = beats + min(1.0, frac / 0.18)          # snap during first 18% of a beat
    esc = -step * TAU / (2 * TEETH["escape"])
    fourth = -esc * TEETH["escape_p"] / TEETH["fourth"]
    third = -fourth * TEETH["fourth_p"] / TEETH["third"]
    center = -third * TEETH["third_p"] / TEETH["center"]
    barrel_a = -center * TEETH["center_p"] / TEETH["barrel"]
    bal = 1.25 * np.sin(TAU * BAL_HZ * t)
    pal = 0.16 * np.clip(np.sin(TAU * BAL_HZ * t) * 4, -1, 1)
    rotor_a = 0.42 * t + 0.35 * np.sin(0.9 * t)
    return dict(escape=esc, fourth=fourth, third=third, center=center, barrel=barrel_a,
                balance=bal, pallet=pal, rotor=rotor_a)


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
    return VGroup(bot, top)


def lift(m, dz):
    m.shift(OUT * dz)
    return m


def at(m, p):
    m.shift(np.array([p[0], p[1], 0.0]))
    return m


def disk_g(r, c=(0, 0), n=64):
    return Point(c).buffer(r, quad_segs=max(4, n // 4))


def teeth_g(r_pitch, n, addendum=None, dedendum=None):
    a = addendum or MOD * 1.0
    d = dedendum or MOD * 1.25
    pts = []
    for k in range(n):
        a0, da = TAU * k / n, TAU / n
        for frac, rr in ((0.00, r_pitch - d), (0.12, r_pitch - d), (0.22, r_pitch + a * 0.8),
                         (0.30, r_pitch + a), (0.42, r_pitch + a), (0.50, r_pitch + a * 0.8),
                         (0.60, r_pitch - d)):
            ang = a0 + frac * da
            pts.append((rr * np.cos(ang), rr * np.sin(ang)))
    return SPoly(pts)


def wheel_g(r, n, spokes=4, rim=0.16, hub=0.18, spoke_w=0.07, phase=0.3, curved=False):
    g = teeth_g(r, n)
    r_in = r * (1 - rim) - MOD
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


def pinion_g(n):
    return teeth_g(MOD * n / 2, n, MOD * 0.9, MOD * 1.1)


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


# ============================================================== the movement
class Movement:
    """Holds the three tiers and the list of rotating parts.

    tiers : {"dial", "engine", "top"} -> VGroup
    refs  : invisible Dot per tier at its local origin (tracks the tier's height)
    parts : {name -> mobject} for every individually addressable part
    rot   : list of (mobject, pivot_xy, tier, angle_fn(state) -> radians)
    """

    def __init__(self):
        self.parts, self.rot = {}, []
        self.tiers = {"dial": self._dial(), "engine": self._engine(), "top": self._top()}

    def _ref(self):
        return Dot(ORIGIN).set_opacity(0)

    # ---------------------------------------------------------- tier 1: dial side
    def _dial(self):
        plate_g = disk_g(3.0, n=192).difference(box(2.25, -0.18, 3.2, 0.18))   # stem slot
        for k in ("center", "third", "fourth", "escape", "barrel", "balance", "pallet"):
            plate_g = plate_g.difference(disk_g(0.05, P[k][:2]))
        plate = slab(plate_g, PLATE, PLATE_DK, 0.14, stroke=STEEL_HI, sw=1.6)
        perlage = VGroup(*[
            vm(disk_g(0.17, (x, y), 24).difference(disk_g(0.15, (x, y), 24)), STEEL_HI, 0.18, sw=0)
            for x in np.arange(-2.75, 2.8, 0.24) for y in np.arange(-2.75, 2.8, 0.24)
            if x * x + y * y < 2.72 ** 2])
        lift(perlage, 0.004)

        # motion works: cannon pinion, hour wheel, minute (intermediate) wheel
        cannon = slab(pinion_g(14).difference(disk_g(0.03)), STEEL, STEEL_DK, 0.05)
        hour = slab(wheel_g(MOD * 36 / 2 * 1.5, 36, spokes=0, rim=0.5, hub=0.35)
                    .difference(disk_g(0.12)), BRASS, BRASS_DK, 0.04, BRASS_HI)
        minute_p = P["center"] + polar(MOD * 1.5 * (36 / 2 + 10 / 2), 210)
        minute = at(slab(wheel_g(MOD * 1.5 * 30 / 2, 30, spokes=3, rim=0.25, hub=0.25),
                         STEEL, STEEL_DK, 0.04), minute_p)
        lift(hour, 0.05); lift(cannon, 0.10); lift(minute, 0.05)
        self.rot += [(cannon, P["center"], "dial", lambda s: s["center"]),
                     (hour, P["center"], "dial", lambda s: s["center"] / 12),
                     (minute, minute_p, "dial", lambda s: -s["center"] * 14 / 30)]

        # keyless works: stem, crown, winding pinion, sliding pinion, lever, yoke, setting wheel
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
        set_wheel = at(slab(wheel_g(0.22, 22, spokes=0, rim=0.6, hub=0.3), STEEL, STEEL_DK, 0.04, STEEL_HI), (1.85, -0.35))
        keyless = VGroup(*[lift(m, 0.06) for m in (setting_lever, yoke, set_wheel, wind_pin, sliding)],
                         lift(stem, 0.1), lift(crown, 0.18))
        screws = lift(VGroup(*[screw(p) for p in ((1.55, -0.95), (1.85, 1.38), (-2.3, -1.3), (-1.4, 2.2))]), 0.12)
        jewels = lift(VGroup(*[jewel(P[k], 0.06) for k in
                               ("center", "third", "fourth", "escape", "balance", "pallet")]), 0.006)

        self.parts.update(plate=plate, perlage=perlage, cannon_pinion=cannon, hour_wheel=hour,
                          minute_wheel=minute, keyless=keyless, stem=stem, crown=crown,
                          dial_screws=screws, dial_jewels=jewels)
        self.dial_ref = self._ref()
        return VGroup(self.dial_ref, plate, perlage, jewels, hour, minute, cannon, keyless, screws)

    # ---------------------------------------------------------- tier 2: middle engine
    def _engine(self):
        def train_wheel(name, pin_n):
            w = slab(wheel_g(R[name], TEETH[name], spokes=4, curved=True), BRASS, BRASS_DK, 0.045, BRASS_HI, 0.7)
            p = lift(slab(pinion_g(pin_n).difference(disk_g(0.02)), STEEL_HI, STEEL_DK, 0.05, WHITE, 0.4), 0.05)
            return VGroup(w, p)

        # barrel: toothed drum, open so the mainspring shows
        drum_g = teeth_g(R["barrel"], TEETH["barrel"]).difference(disk_g(R["barrel"] * 0.9))
        floor = vm(disk_g(R["barrel"] * 0.9), BRASS_DK, stroke=BRASS, sw=0.6)
        spring_pts = [(0.15 + 0.033 * t) * np.array([np.cos(t), np.sin(t), 0]) for t in np.linspace(0, 23.5, 500)]
        mainspring = VMobject().set_points_smoothly(spring_pts).set_stroke(STEEL_HI, 1.6).set_fill(opacity=0)
        shadow = mainspring.copy().set_stroke("#1a1c20", 3.0).shift(IN * 0.01 + RIGHT * 0.01)
        arbor = vm(disk_g(0.13), STEEL_HI, stroke=WHITE, sw=0.6)
        barrel = at(VGroup(slab(drum_g, BRASS, BRASS_DK, 0.12, BRASS_HI), floor,
                           lift(shadow, 0.02), lift(mainspring, 0.03), lift(arbor, 0.04)), P["barrel"])

        center_w = at(lift(train_wheel("center", TEETH["center_p"]), 0.06), P["center"])
        third_w = at(lift(train_wheel("third", TEETH["third_p"]), 0.10), P["third"])
        fourth_w = at(lift(train_wheel("fourth", TEETH["fourth_p"]), 0.14), P["fourth"])

        # club-tooth escape wheel (steel)
        n, pts = TEETH["escape"], []
        for k in range(n):
            a = TAU * k / n
            for da, rr in ((0.00, 0.62), (0.05, 0.95), (0.13, 1.0), (0.16, 0.93), (0.30, 0.66)):
                pts.append((R["escape"] * rr * np.cos(a + da * TAU / n * 3),
                            R["escape"] * rr * np.sin(a + da * TAU / n * 3)))
        esc_g = SPoly(pts).buffer(0)
        win = disk_g(R["escape"] * 0.5).difference(disk_g(R["escape"] * 0.16))
        for k in range(4):
            a = TAU * k / 4
            win = win.difference(LineString([(0, 0), (np.cos(a), np.sin(a))]).buffer(0.018))
        escape_w = VGroup(slab(esc_g.difference(win), STEEL, STEEL_DK, 0.035, STEEL_HI, 0.6),
                          lift(slab(pinion_g(TEETH["escape_p"]), STEEL_HI, STEEL_DK, 0.04, WHITE, 0.4), 0.04))
        at(lift(escape_w, 0.18), P["escape"])

        # Swiss lever pallet fork with ruby pallet stones
        e, pp, b = P["escape"][:2], P["pallet"][:2], P["balance"][:2]
        u = (b - pp) / np.linalg.norm(b - pp)
        nrm = np.array([-u[1], u[0]])
        entry = e + polar(R["escape"] * 1.02, 118 + 34)[:2]
        exitp = e + polar(R["escape"] * 1.02, 118 - 34)[:2]
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

        # balance wheel, timing weights, hairspring, roller with impulse jewel
        rb = 0.74
        bal_g = disk_g(rb, n=128).difference(disk_g(rb * 0.85, n=128))
        for a in (0.3, 0.3 + PI / 2):
            bal_g = bal_g.union(LineString([(-rb * 0.86 * np.cos(a), -rb * 0.86 * np.sin(a)),
                                            (rb * 0.86 * np.cos(a), rb * 0.86 * np.sin(a))]).buffer(0.035))
        bal_g = bal_g.union(disk_g(0.09))
        weights = VGroup(*[vm(disk_g(0.045, (rb * 0.98 * np.cos(a), rb * 0.98 * np.sin(a)), 16), GILT, stroke=BRASS_HI, sw=0.5)
                           for a in np.linspace(0, TAU, 10, endpoint=False)])
        hs_pts = [(0.1 + 0.042 * t / TAU * 2.4) * np.array([np.cos(t), np.sin(t), 0]) for t in np.linspace(0, 13 * PI, 600)]
        hairspring = VMobject().set_points_smoothly(hs_pts).set_stroke(STEEL_HI, 1.0).set_fill(opacity=0)
        roller = vm(disk_g(0.12), STEEL_HI, stroke=WHITE, sw=0.5)
        impulse = vm(disk_g(0.025, (0.0, -0.1)), RUBY, sw=0)
        balance = VGroup(slab(bal_g, GILT, BRASS_DK, 0.06, BRASS_HI), lift(weights, 0.001),
                         lift(hairspring, 0.03), lift(roller, 0.04), lift(impulse, 0.045))
        at(lift(balance, 0.24), P["balance"])

        for name, mob in (("barrel", barrel), ("center", center_w), ("third", third_w), ("fourth", fourth_w),
                          ("escape", escape_w), ("pallet", pallet), ("balance", balance)):
            self.rot.append((mob, P[name], "engine", lambda s, name=name: s[name]))
        self.parts.update(barrel=barrel, center_wheel=center_w, third_wheel=third_w, fourth_wheel=fourth_w,
                          escape_wheel=escape_w, pallet_fork=pallet, balance=balance, hairspring=hairspring)
        self.engine_ref = self._ref()
        return VGroup(self.engine_ref, barrel, center_w, third_w, fourth_w, escape_w, pallet, balance)

    # ---------------------------------------------------------- tier 3: top modules
    def _top(self):
        def bridge(pts, holes, r=0.14, cotes=True):
            g = rounded(pts, r)
            for h in holes:
                g = g.difference(disk_g(0.11, h[:2]))
            parts = VGroup(slab(g, STEEL, STEEL_DK, 0.12, STEEL_HI, 1.4))
            if cotes:
                parts.add(lift(vm(stripes_g(g.buffer(-0.04)), STEEL_HI, 0.22, sw=0), 0.002))
            parts.add(lift(vm(g.difference(g.buffer(-0.035)), WHITE, 0.55, sw=0), 0.003))   # bevel
            return parts

        barrel_bridge = bridge([(-2.85, 0.15), (-2.55, 1.55), (-1.6, 2.5), (-0.55, 2.2), (-0.3, 1.0), (-0.95, 0.15)],
                               [P["barrel"]])
        train_bridge = bridge([(-0.3, 0.6), (0.5, 0.9), (1.85, 1.15), (2.45, 0.2), (2.0, -1.35), (0.6, -1.55), (-0.25, -0.6)],
                              [P["center"], P["third"], P["fourth"], P["escape"]])
        pallet_cock = bridge([P["pallet"][:2] + d for d in ((-0.25, -0.15), (0.2, -0.3), (0.55, 0.2), (0.1, 0.35))],
                             [P["pallet"]], 0.06, cotes=False)
        bc = P["balance"][:2]
        balance_cock = bridge([(bc[0] - 0.25, bc[1] - 0.15), (bc[0] + 0.22, bc[1] - 0.22),
                               (bc[0] + 1.25, bc[1] - 1.0), (bc[0] + 1.05, bc[1] - 1.45), (bc[0] + 0.35, bc[1] - 1.15)],
                              [P["balance"]], 0.1)
        regulator = lift(slab(unary_union([disk_g(0.12, bc),
                                           LineString([tuple(bc), (bc[0] - 0.75, bc[1] + 0.2)]).buffer(0.03)]),
                              STEEL_HI, STEEL_DK, 0.03, WHITE, 0.5), 0.14)
        shock = lift(VGroup(vm(disk_g(0.14, bc).difference(disk_g(0.11, bc)), GILT, sw=0),
                            vm(LineString([(bc[0] - 0.1, bc[1] - 0.08), (bc[0] + 0.1, bc[1] + 0.08)]).buffer(0.012),
                               GILT, sw=0)), 0.18)

        # winding: ratchet wheel, crown wheel, click
        ratchet = VGroup(slab(teeth_g(0.62, 40, 0.035, 0.035).difference(disk_g(0.08)), STEEL_HI, STEEL_DK, 0.06, WHITE, 0.6),
                         lift(vm(circ_stripes_g(disk_g(0.56).difference(disk_g(0.14)), step=0.05), WHITE, 0.25, sw=0), 0.002),
                         lift(screw((0, 0), 0.1), 0.01))
        at(lift(ratchet, 0.14), P["barrel"])
        crown_wheel_p = P["barrel"] + polar(0.62 + 0.26, 15)
        crown_wheel = VGroup(slab(teeth_g(0.26, 18, 0.03, 0.03).difference(disk_g(0.05)), STEEL_HI, STEEL_DK, 0.05, WHITE, 0.6),
                             lift(screw((0, 0), 0.06, 1.2), 0.01))
        at(lift(crown_wheel, 0.14), crown_wheel_p)
        bx, by = P["barrel"][:2]
        click = lift(slab(rounded([(bx - 0.95, by - 0.15), (bx - 0.6, by - 0.45), (bx - 0.62, by - 0.3)], 0.02),
                          STEEL_HI, STEEL_DK, 0.04, WHITE, 0.5), 0.14)
        self.rot += [(ratchet, P["barrel"], "top", lambda s: -s["rotor"] * 0.15),
                     (crown_wheel, crown_wheel_p, "top", lambda s: s["rotor"] * 0.15 * 0.62 / 0.26)]

        jewels = lift(VGroup(*[jewel(P[k], 0.075) for k in ("center", "third", "fourth", "escape", "pallet")]), 0.004)
        screws = lift(VGroup(*[screw(p, ang=a) for p, a in (
            ((-2.45, 0.45), 0.3), ((-1.55, 2.2), 1.1), ((-0.6, 1.55), 2.0), ((1.6, 0.85), 0.7),
            ((2.05, -0.6), 2.4), ((0.75, -1.25), 1.6), ((-0.05, -0.55), 0.2),
            (tuple(bc + np.array([0.95, -1.15])), 0.9))]), 0.004)

        # automatic rotor: gold segment, Côtes circulaires, bevel, engraving, bearing
        rim_g = disk_g(2.9, n=192).difference(disk_g(2.0, n=192)).intersection(
            SPoly([(0, 0), polar(6, 75)[:2], polar(6, 180)[:2], polar(6, 285)[:2]]))
        web_g = disk_g(2.05, n=128).intersection(SPoly([(0, 0), polar(5, 105)[:2], polar(5, 180)[:2], polar(5, 255)[:2]]))
        web_g = web_g.difference(disk_g(1.35, polar(1.25, 180)[:2])).union(disk_g(0.42))
        rotor_all = unary_union([rim_g, web_g])
        rotor = VGroup(
            slab(rotor_all, GILT, BRASS_DK, 0.10, BRASS_HI, 1.4),
            lift(vm(circ_stripes_g(rotor_all.buffer(-0.05), step=0.075), BRASS_HI, 0.22, sw=0), 0.002),
            lift(vm(rotor_all.difference(rotor_all.buffer(-0.04)), WHITE, 0.5, sw=0), 0.003))
        engraving = VGroup()
        for i, ch in enumerate(ROTOR_ENGRAVING):
            if ch == " ":
                continue
            ang = np.radians(250 - i * 4.0)
            t = Text(ch, font=FONT_SERIF, weight=BOLD).scale(0.17).set_color(BRASS_DK)
            engraving.add(t.rotate(ang - PI / 2).move_to(polar(2.45, np.degrees(ang))))
        rotor.add(lift(engraving, 0.004))
        rotor.add(lift(VGroup(vm(disk_g(0.32), STEEL_HI, stroke=WHITE, sw=1),
                              vm(disk_g(0.25).difference(disk_g(0.18)), STEEL_DK, sw=0),
                              *[screw(polar(0.24, a)[:2], 0.045, a) for a in (30, 150, 270)]), 0.01))
        lift(rotor, 0.34)
        self.rot.append((rotor, P["center"], "top", lambda s: s["rotor"]))

        bridges = lift(VGroup(barrel_bridge, train_bridge, pallet_cock, balance_cock), 0.12)
        self.parts.update(barrel_bridge=barrel_bridge, train_bridge=train_bridge, pallet_cock=pallet_cock,
                          balance_cock=balance_cock, regulator=regulator, shock_protection=shock,
                          ratchet_wheel=ratchet, crown_wheel=crown_wheel, click=click,
                          top_jewels=jewels, top_screws=screws, rotor=rotor)
        self.top_ref = self._ref()
        return VGroup(self.top_ref, bridges, lift(jewels, 0.12), lift(screws, 0.12),
                      regulator, shock, click, ratchet, crown_wheel, rotor)

    @property
    def refs(self):
        return {"dial": self.dial_ref, "engine": self.engine_ref, "top": self.top_ref}

    @property
    def group(self):
        return VGroup(*self.tiers.values())


# ============================================================== driver
def attach_driver(scene, mv, z_assembled, z_exploded):
    """Animate the movement with ONE updater (never .animate a tier: that
    freezes updaters). Returns (explode, dim):

      explode : ValueTracker 0 -> 1 moves tiers from z_assembled to z_exploded
      dim     : {tier: ValueTracker} opacity multiplier per tier (1 = normal)
    """
    tiers, refs = mv.tiers, mv.refs
    for k, t in tiers.items():
        t.shift(OUT * z_assembled[k])
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
            dz = z_assembled[k] + (z_exploded[k] - z_assembled[k]) * e - refs[k].get_center()[2]
            if abs(dz) > 1e-9:
                t.shift(OUT * dz)
            v = dim[k].get_value()
            if abs(v - applied[k]) > 1e-4:
                for m, fo, so in base_op[k]:
                    m.set_fill(opacity=fo * v, family=False)
                    m.set_stroke(opacity=so * v, family=False)
                applied[k] = v
        s = state(clock["t"])
        for mob, pxy, tier, fn in mv.rot:
            target, cur = fn(s), getattr(mob, "_ang", 0.0)
            if target != cur:
                z = refs[tier].get_center()[2]
                mob.rotate(target - cur, axis=OUT, about_point=np.array([pxy[0], pxy[1], z]))
                mob._ang = target

    driver = Mobject()
    driver.add_updater(drive)
    scene.add(mv.group, driver, explode, *dim.values())
    return explode, dim


def vignette():
    h, w = 270, 480
    y, x = np.mgrid[0:h, 0:w]
    d = np.sqrt(((x - w / 2) / (w / 2)) ** 2 + ((y - h / 2) / (h / 2)) ** 2)
    img = np.zeros((h, w, 4), dtype=np.uint8)
    img[..., 3] = (np.clip((d - 0.5) / 0.8, 0, 1) ** 1.5 * 240).astype(np.uint8)
    im = ImageMobject(img)
    return im.stretch_to_fit_width(config.frame_width).stretch_to_fit_height(config.frame_height)
