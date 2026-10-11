"""Film 3 helpers: flat (2D) gears that mesh in phase, and side elevations of arbors.

GearSet
    gs = GearSet()
    a = gs.gear("a", z=40, m=0.06, center=(-2, 0))              # the driving gear
    b = gs.gear("b", z=10, m=0.06, driven_by="a", angle=0)      # placed on a's pitch circle, meshed
    c = gs.gear("c", z=60, m=0.04, arbor_of="b", kind="wheel")  # same arbor as b (turns with it)
    gs.attach(scene)                       # one updater turns every gear from gs.turn
    self.play(gs.turn.animate.set_value(TAU))                   # a turns once, the rest follow

    gs.turn is the driving gear's angle in radians; gs.speed (a ValueTracker,
    radians per second) turns it continuously while gs.attach's updater runs.
    Fade gears with gs.show(...) / gear.vis, not FadeIn (that fights the rotation). Each gear's angle is
    c + k * turn, with k from the tooth ratios, so speeds stay exact; a driven
    gear starts with a tooth gap facing its driver's tooth, so teeth interleave.

Shapes come from movement.py (teeth_g, wheel_g, pinion_g, vm), so the flat gears
match the 3D model's tooth form.
"""
from manim import *
from movement import teeth_g, wheel_g, pinion_g, disk_g, vm, BRASS, BRASS_DK, BRASS_HI, STEEL, STEEL_DK, STEEL_HI

TOOTH_MID = 0.36        # a tooth's center, as a fraction of the pitch angle (see teeth_g)
GAP_MID = 0.86          # a gap's center


def gear_shape(z, m, kind="wheel", spokes=4):
    """Shapely outline of a gear with z teeth of module m, centered at the origin."""
    r = m * z / 2
    if kind == "pinion":
        return pinion_g(z, m).difference(disk_g(min(0.04, r * 0.3)))
    if kind == "plain":
        return teeth_g(r, z, m=m).difference(disk_g(min(0.05, r * 0.15)))
    return wheel_g(r, z, spokes=spokes, curved=True, m=m)


class Gear(VGroup):
    """A flat gear. Rotate it only through its GearSet (angle = c + k * turn)."""

    def __init__(self, z, m, kind="wheel", color=None, spokes=4, stroke=None, opacity=1.0):
        super().__init__()
        self.z, self.m, self.kind = z, m, kind
        self.r = m * z / 2
        steel = kind == "pinion"
        color = color or (STEEL_HI if steel else BRASS)
        stroke = stroke or (WHITE if steel else BRASS_HI)
        self.body = vm(gear_shape(z, m, kind, spokes), color, opacity, stroke, 0.9)
        self.hub = Dot(ORIGIN, radius=min(0.05, self.r * 0.2), color=STEEL_HI if not steel else STEEL_DK)
        self.add(self.body, self.hub)
        self.c, self.k, self._ang = 0.0, 1.0, 0.0
        self.pivot = ORIGIN.copy()
        # fade a gear with gear.vis (0..1), never FadeIn/FadeOut: those fight the rotation
        self.vis, self._vis = ValueTracker(1.0), 1.0
        self._base = [(m, m.get_fill_opacity(), m.get_stroke_opacity()) for m in self.family_members_with_points()]

    def apply_vis(self):
        v = self.vis.get_value()
        if abs(v - self._vis) > 1e-4:
            for m, fo, so in self._base:
                m.set_fill(opacity=fo * v, family=False).set_stroke(opacity=so * v, family=False)
            self._vis = v

    def place(self, center):
        p = np.array([center[0], center[1], 0.0])
        self.shift(p - self.pivot)
        self.pivot = p
        return self

    def set_angle(self, a):
        if a != self._ang:
            self.rotate(a - self._ang, about_point=self.pivot)
            self._ang = a


class GearSet:
    def __init__(self):
        self.gears = {}
        self.turn = ValueTracker(0.0)
        self.speed = ValueTracker(0.0)      # radians per second the updater adds to turn (animatable)
        self.group = VGroup()

    def gear(self, name, z, m, center=None, driven_by=None, angle=0.0, arbor_of=None,
             kind="wheel", color=None, spokes=4, phase=0.0, opacity=1.0):
        """Add a gear. Give center (the driving gear), or driven_by (placed at
        `angle` degrees around that gear, at the meshing distance), or arbor_of
        (coaxial with that gear and turning with it)."""
        g = Gear(z, m, kind, color, spokes, opacity=opacity)
        if arbor_of is not None:
            a = self.gears[arbor_of]
            g.place(a.pivot)
            g.c, g.k = a.c + phase, a.k
        elif driven_by is not None:
            d = self.gears[driven_by]
            psi = np.radians(angle)
            g.place(d.pivot + (d.r + g.r) * np.array([np.cos(psi), np.sin(psi), 0.0]))
            ratio = d.z / g.z
            th_d = psi - TOOTH_MID * TAU / d.z                # driver angle with a tooth facing g
            th_g = psi + PI - GAP_MID * TAU / g.z             # g angle with a gap facing the driver
            g.c = th_g - ratio * (d.c - th_d)
            g.k = -ratio * d.k
        else:
            g.place(center)
            g.c, g.k = phase, 1.0
        g.set_angle(g.c)
        self.gears[name] = g
        self.group.add(g)
        return g

    def hide(self, *names):
        for n in names:
            self.gears[n].vis.set_value(0.0)
            self.gears[n].apply_vis()

    def show(self, *names, run_time=0.8):
        """Animations that fade gears in (their rotation keeps running)."""
        return [self.gears[n].vis.animate(run_time=run_time).set_value(1.0) for n in names]

    def __getitem__(self, name):
        return self.gears[name]

    def update(self):
        t = self.turn.get_value()
        for g in self.gears.values():
            g.set_angle(g.c + g.k * t)
            g.apply_vis()

    def attach(self, scene, add=True):
        """Add the gears and one updater that turns them; returns the driver mobject."""
        driver = Mobject()

        def drive(_, dt):
            v = self.speed.get_value()
            if v:
                self.turn.increment_value(v * dt)
            self.update()
        driver.add_updater(drive)
        if add:
            scene.add(self.group)
        scene.add(self.turn, self.speed, driver, *[g.vis for g in self.gears.values()])
        return driver


# ---------------------------------------------------------------- side elevation
def elevation_arbor(x, y0, y1, parts, axle=STEEL_HI):
    """Side view of an arbor at x from y0 to y1. parts: list of (y, r, h, kind)
    with kind "wheel" (thin brass disk seen edge on) or "pinion" (steel, with leaf lines)."""
    g = VGroup(Line([x, y0, 0], [x, y1, 0]).set_stroke(axle, 3))
    for y, r, h, kind in parts:
        if kind == "wheel":
            g.add(Rectangle(width=2 * r, height=h).move_to([x, y, 0]).set_fill(BRASS, 1).set_stroke(BRASS_HI, 1))
        else:
            body = Rectangle(width=2 * r, height=h).move_to([x, y, 0]).set_fill(STEEL, 1).set_stroke(WHITE, 1)
            leaves = VGroup(*[Line([x + u * r, y - h / 2, 0], [x + u * r, y + h / 2, 0]).set_stroke(STEEL_DK, 1.2)
                              for u in (-0.6, -0.2, 0.2, 0.6)])
            g.add(body, leaves)
    return g
