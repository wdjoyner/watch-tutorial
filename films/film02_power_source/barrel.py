"""Close-up model of the 6497 mainspring barrel, for Film 2.

Built in the movement's units (1 unit = 6.1 mm) and at the movement's barrel
position, so it can stand in for the barrel of `movement.Movement` without a
change of scale. Real 6497 proportions: inside diameter 15.0 mm, arbor core
4.10 mm, mainspring 1.50 mm high, 0.18 mm thick, about 450 mm long; the
ribbon is drawn thicker and with fewer turns than the real spring so it
reads on screen.

    bm = BarrelModel(center=P["barrel"], z0=0.26)
    scene.add(bm)                       # one updater places every part
    bm.explode   ValueTracker 0 -> 1    parts spread out along the axis
    bm.lift      ValueTracker           height of the whole barrel above z0
    bm.drum_turn ValueTracker (rad)     drum angle; the spring's outer end follows
    bm.arbor_turn ValueTracker (rad)    arbor angle; the spring's inner end follows
    bm.show_cover ValueTracker 0..1     cover opacity

Parts are separate groups (bm.drum, bm.spring, bm.arbor_lo, bm.arbor_hi,
bm.cover, bm.wall_hook) so a scene can highlight or label them. Their draw
order is kept correct (painter's algorithm, camera above) as they move.
"""
import numpy as np
from manim import *
from shapely.geometry import LineString, box
from shapely import affinity
from shapely.ops import unary_union
from movement import (vm, disk_g, teeth_g, circ_stripes_g, TEETH, MESH, R, BRASS, BRASS_DK, BRASS_HI,
                      STEEL, STEEL_DK, STEEL_HI, GILT)

MM = 1 / 6.1                         # scene units per millimeter

# ---------------------------------------------------------------- dimensions (mm)
R_IN = 7.5                           # inside radius of the drum wall (15.0 mm inside diameter)
R_ROOT = R["barrel"] / MM - 1.25 * MESH["barrel"] / MM     # tooth root = outside of the wall
FLOOR, WALL_H, FLANGE_H = 0.35, 2.05, 0.65                  # drum floor, total drum height, toothed band
COVER_T, COVER_R, COVER_HOLE = 0.30, R_IN + 0.12, 1.15      # snap-on cover sits in a groove at the top
CORE_R, CORE_H = 2.05, 1.55          # arbor core (4.10 mm), as high as the spring
PIVOT_R, PIVOT_L = 0.55, 1.10        # lower pivot, through the drum floor
SHAFT_R, SHAFT_L, SQUARE = 1.0, 1.55, 1.55                  # upper shaft and the square for the ratchet
FLOOR_HOLE = 0.75
SPRING_H = 1.50
SPRING_T_DRAWN = 0.30                # ribbon thickness as drawn (the real spring is 0.18 mm)
SPRING_TURNS = 7.86                   # whole turns minus a little, so both hooks face the same side
HOOK_IN_DEG = 55.0                   # arbor hook angle (degrees, barrel frame)
HOOK_H = 0.30                        # how far each hook stands proud, mm
EXPLODE_DZ = {"drum": 0.0, "spring": 4.6, "arbor": 9.6, "cover": 16.4}   # mm along the axis

HOOK_OUT_DEG = HOOK_IN_DEG + 360 * SPRING_TURNS


def _mm(g):
    return affinity.scale(g, MM, MM, origin=(0, 0))


# --------------------------------------------------------------- 2D geometry (mm)
def arbor_core_g():
    """Arbor core with its hook: a small tooth the spring's eye catches."""
    a = np.radians(HOOK_IN_DEG)
    t = np.array([np.cos(a), np.sin(a)])
    n = np.array([-np.sin(a), np.cos(a)])
    base = CORE_R - 0.05
    tooth = LineString([tuple(t * base - n * 0.35), tuple(t * (CORE_R + HOOK_H) + n * 0.05),
                        tuple(t * base + n * 0.15)]).convex_hull
    return unary_union([disk_g(CORE_R, n=96), tooth])


def wall_hook_g(turn=0.0):
    """Hook on the inside of the drum wall that the spring's outer end catches."""
    a = np.radians(HOOK_OUT_DEG) + turn
    t = np.array([np.cos(a), np.sin(a)])
    n = np.array([-np.sin(a), np.cos(a)])
    return LineString([tuple(t * (R_IN + 0.05) + n * 0.35), tuple(t * (R_IN - HOOK_H) - n * 0.05),
                       tuple(t * (R_IN + 0.05) - n * 0.15)]).convex_hull


def spring_path(twist=0.0, inner_turn=0.0, n=900):
    """Centerline of the ribbon: an Archimedean spiral from the arbor to the wall.
    twist = drum angle - arbor angle; it is spread evenly along the spring."""
    s = np.linspace(0, 1, n)
    r0, r1 = CORE_R + SPRING_T_DRAWN / 2 + 0.02, R_IN - SPRING_T_DRAWN / 2 - 0.02
    ang = np.radians(HOOK_IN_DEG) + inner_turn + s * TAU * SPRING_TURNS + s * twist
    r = r0 + (r1 - r0) * s ** 0.9
    return np.column_stack([r * np.cos(ang), r * np.sin(ang)])


def spring_g(twist=0.0, inner_turn=0.0):
    pts = spring_path(twist, inner_turn)
    rib = LineString(pts).buffer(SPRING_T_DRAWN / 2, cap_style=2, join_style=2)
    # a slot near each end, where the hooks go through
    for p, q in ((pts[6], pts[0]), (pts[-7], pts[-1])):
        d = (q - p) / np.linalg.norm(q - p)
        c = (p + q) / 2
        slot = affinity.rotate(box(-0.22, -0.06, 0.22, 0.06), np.degrees(np.arctan2(d[1], d[0])), origin=(0, 0))
        rib = rib.difference(affinity.translate(slot, c[0], c[1]))
    return rib


def drum_floor_g():
    return disk_g(R_IN + 0.02, n=128).difference(disk_g(FLOOR_HOLE))


def drum_wall_g():
    return disk_g(R_ROOT, n=160).difference(disk_g(R_IN, n=160))


def drum_teeth_g():
    return teeth_g(R["barrel"] / MM, TEETH["barrel"], m=MESH["barrel"] / MM).difference(disk_g(R_IN, n=160))


def cover_g():
    g = disk_g(COVER_R, n=160).difference(disk_g(COVER_HOLE))
    a = np.radians(-25)
    notch = disk_g(0.45, (COVER_R * np.cos(a), COVER_R * np.sin(a)))    # pry notch on the edge
    return g.difference(notch)


def square_g():
    return box(-SQUARE / 2, -SQUARE / 2, SQUARE / 2, SQUARE / 2)


# ------------------------------------------------------------ extruded mobjects
def extrude(geom_mm, color, side, h_mm, layers=6, stroke=None, sw=0.6, z_mm=0.0):
    """A solid of height h: stacked darker copies of the outline, then the lit top
    face. Built in the barrel frame (units), base at z_mm."""
    g = _mm(geom_mm)
    out = VGroup()
    for k in range(layers):
        z = (z_mm + h_mm * k / layers) * MM
        out.add(vm(g, side, stroke=side, sw=sw).shift(OUT * z))
    out.add(vm(g, color, stroke=stroke or color, sw=sw).shift(OUT * (z_mm + h_mm) * MM))
    return out


class BarrelModel(VGroup):
    def __init__(self, center=ORIGIN, z0=0.0, **kw):
        super().__init__(**kw)
        self.c = np.array([center[0], center[1], 0.0])
        self.z0 = z0
        self.explode, self.lift = ValueTracker(0.0), ValueTracker(0.0)
        self.drum_turn, self.arbor_turn = ValueTracker(0.0), ValueTracker(0.0)
        self.show_cover = ValueTracker(1.0)

        teeth = extrude(drum_teeth_g(), BRASS, BRASS_DK, FLANGE_H, 3, BRASS_HI)
        floor = extrude(drum_floor_g(), BRASS_DK, BRASS_DK, FLOOR, 1, BRASS)
        wall = extrude(drum_wall_g(), BRASS, BRASS_DK, WALL_H, 8, BRASS_HI)
        self.drum = VGroup(teeth, floor, wall)
        self.wall_hook = extrude(wall_hook_g(), BRASS, BRASS_DK, SPRING_H, 3, BRASS_HI, z_mm=FLOOR)
        self.arbor_lo = VGroup(extrude(disk_g(PIVOT_R), STEEL, STEEL_DK, PIVOT_L, 4, STEEL_HI, z_mm=FLOOR - PIVOT_L),
                               extrude(arbor_core_g(), STEEL, STEEL_DK, CORE_H, 6, STEEL_HI, z_mm=FLOOR))
        top = FLOOR + CORE_H
        self.arbor_hi = VGroup(extrude(disk_g(SHAFT_R), STEEL, STEEL_DK, SHAFT_L, 5, STEEL_HI, z_mm=top),
                               extrude(square_g(), STEEL, STEEL_DK, 0.7, 3, STEEL_HI, z_mm=top + SHAFT_L))
        cz = WALL_H - COVER_T
        grain = vm(_mm(circ_stripes_g(cover_g(), step=0.5)), BRASS_HI, opacity=0.18, sw=0)
        self.cover = VGroup(extrude(cover_g(), BRASS, BRASS_DK, COVER_T, 2, BRASS_HI, z_mm=cz),
                            grain.shift(OUT * (WALL_H + 0.01) * MM))
        self.spring = self._spring_mob(0.0, 0.0)

        self._parts = {"drum": self.drum, "wall_hook": self.wall_hook, "spring": self.spring,
                       "arbor_lo": self.arbor_lo, "arbor_hi": self.arbor_hi, "cover": self.cover}
        self._group = {"drum": "drum", "wall_hook": "drum", "spring": "spring", "arbor_lo": "arbor",
                       "arbor_hi": "arbor", "cover": "cover"}
        self._top_mm = {"arbor_hi": top + SHAFT_L + 0.7, "cover": WALL_H}
        self._dz = {k: 0.0 for k in self._parts}
        self._ang = {k: 0.0 for k in self._parts}
        self._cover_op = 1.0
        self._spring_key = (0.0, 0.0)
        for m in self._parts.values():
            m.shift(self.c + OUT * z0)
        self.add(*self._order())
        self.add_updater(lambda m, dt: m._update())

    # -- helpers
    def _spring_mob(self, twist, inner):
        return extrude(spring_g(twist, inner), STEEL_HI, STEEL_DK, SPRING_H, 7, WHITE, sw=0.5, z_mm=FLOOR)

    def offset(self, key):
        """Current height of a part above its assembled position (units)."""
        return self.lift.get_value() + self.explode.get_value() * EXPLODE_DZ[self._group[key]] * MM

    def anchor(self, key, r_mm=None, deg=0.0, z_mm=None):
        """A world point on a part: at radius r_mm, angle deg (barrel frame), height z_mm."""
        a = np.radians(deg)
        r = (r_mm or 0.0) * MM
        z = self.z0 + self.offset(key) + (z_mm if z_mm is not None else 0.0) * MM
        return self.c + np.array([r * np.cos(a), r * np.sin(a), 0.0]) + OUT * z

    def _order(self):
        e = self.explode.get_value()
        order = ["drum"] + (["wall_hook"] if e > 0.5 else []) + ["spring"] + \
                (["wall_hook"] if e <= 0.5 else []) + ["arbor_lo"]
        hi = sorted(["cover", "arbor_hi"], key=lambda k: self._top_mm[k] * MM + self.offset(k))
        return [self._parts[k] for k in order + hi]

    def _update(self):
        turn = {"drum": self.drum_turn.get_value(), "wall_hook": self.drum_turn.get_value(),
                "arbor_lo": self.arbor_turn.get_value(), "arbor_hi": self.arbor_turn.get_value(),
                "cover": self.drum_turn.get_value(), "spring": 0.0}
        # the spring is redrawn when its ends move relative to each other
        key = (round(turn["drum"] - turn["arbor_lo"], 4), round(turn["arbor_lo"], 4))
        if key != self._spring_key:
            new = self._spring_mob(key[0], key[1])
            new.shift(self.c + OUT * (self.z0 + self._dz["spring"]))
            self.spring.become(new)
            self._spring_key = key
        axis_pt = lambda k: self.c + OUT * (self.z0 + self._dz[k])
        for k, m in self._parts.items():
            dz = self.offset(k) - self._dz[k]
            if abs(dz) > 1e-9:
                m.shift(OUT * dz)
                self._dz[k] += dz
            if k != "spring":
                da = turn[k] - self._ang[k]
                if abs(da) > 1e-9:
                    m.rotate(da, axis=OUT, about_point=axis_pt(k))
                    self._ang[k] += da
        op = self.show_cover.get_value()
        if abs(op - self._cover_op) > 1e-4:
            for sub in self.cover.family_members_with_points():
                base = getattr(sub, "_base_op", None)
                if base is None:
                    base = sub._base_op = (sub.get_fill_opacity(), sub.get_stroke_opacity())
                sub.set_fill(opacity=base[0] * op, family=False).set_stroke(opacity=base[1] * op, family=False)
            self._cover_op = op
        self.submobjects = self._order()


# ------------------------------------------------------------------ insets
def inset_g(which, twist=0.0):
    """Top-face geometry (mm, barrel frame) near one hook, as [(geom, color, stroke)]
    for a magnified 2D inset, and the hook's position."""
    if which == "inner":
        a = np.radians(HOOK_IN_DEG)
        p = np.array([np.cos(a), np.sin(a)]) * CORE_R
        items = [(drum_floor_g(), BRASS_DK, BRASS), (spring_g(twist), STEEL_HI, WHITE), (arbor_core_g(), STEEL, STEEL_HI)]
    else:
        a = np.radians(HOOK_OUT_DEG)
        p = np.array([np.cos(a), np.sin(a)]) * R_IN
        items = [(drum_floor_g(), BRASS_DK, BRASS), (drum_wall_g(), BRASS, BRASS_HI), (spring_g(twist), STEEL_HI, WHITE),
                 (wall_hook_g(), BRASS, BRASS_HI)]
    return items, p
