"""Film 4 helpers: a flat (2D) balance with a breathing hairspring, and a beat log.

BalanceModel
    bal = BalanceModel(center=(0, 0), radius=1.6)
    bal.attach(scene)                        # one updater swings it from its own clock
    self.play(bal.rate.animate.set_value(0.1))   # slow motion (1 = real time, 2.5 Hz)

    Trackers (animate these, never the balance itself; .animate on it fights the updater):
      rate    clock speed, 1 = real time
      amp     swing amplitude in radians (reduced, like movement.BAL_AMPLITUDE, so it doesn't strobe)
      damp    decay rate of the amplitude, per second of model time (0 = the ideal oscillator)
      drive   1 = swinging on its own, 0 = held at the angle in `manual` (blend between them)
      manual  angle in radians, used where drive < 1
      vis     opacity, 0..1 (fade with this, never FadeIn)
      pins    curb-pin position along the spring, as a fraction of its length (1 = at the stud)

    The hairspring is an Archimedean spiral. Its inner end turns with the staff,
    its outer end is held (at the curb pins, or the stud), and the twist is shared
    evenly along the active length, so the coils open and close as the balance
    swings. Beyond the pins the spring does not move.

    bal.angle(), bal.speed_frac() give the current angle and |angular speed| as a
    fraction of its peak, for energy bars.

BeatLog
    log = BeatLog(scene, lambda: bal.model_t, BEATS) records the video time of each
    beat; log.write(__file__) writes <scene>.ticks.txt, which build.py uses in place
    of its steady tick track, so slow-motion ticks match the picture.
"""
import os
import numpy as np
from manim import *
from movement import vm, disk_g, GILT, BRASS_DK, BRASS_HI, STEEL_HI, STEEL, RUBY, BAL_HZ
from shapely.geometry import LineString

HAIRSPRING = "#9fb6d8"          # blued steel, a touch lighter so it reads on the dark background


class BalanceModel(VGroup):
    def __init__(self, center=(0.0, 0.0), radius=1.6, hz=BAL_HZ, amp=1.2, turns=6, r_in=0.18, r_out=None,
                 spokes=3, stud_deg=-60.0, pins=1.0, show_spring=True, rim_frac=0.84):
        super().__init__()
        self.c = np.array([center[0], center[1], 0.0])
        self.r, self.hz = radius, hz
        self.rate, self.amp, self.damp = ValueTracker(1.0), ValueTracker(amp), ValueTracker(0.0)
        self.drive, self.manual = ValueTracker(1.0), ValueTracker(0.0)
        self.vis, self.pins = ValueTracker(1.0), ValueTracker(pins)
        self.model_t, self.env, self._ang, self._vis = 0.0, 1.0, 0.0, 1.0

        # wheel: a heavy rim on thin arms, hub, staff, impulse jewel
        g = disk_g(radius, n=160).difference(disk_g(radius * rim_frac, n=160))
        for k in range(spokes):
            a = 0.35 + k * TAU / spokes
            g = g.union(LineString([(0, 0), (radius * 0.9 * np.cos(a), radius * 0.9 * np.sin(a))]).buffer(radius * 0.028))
        g = g.union(disk_g(radius * 0.11))
        self.wheel = vm(g, GILT, 1.0, BRASS_HI, 1.0)
        self.staff = Dot(ORIGIN, radius=radius * 0.045, color=STEEL_HI)
        self.jewel = Dot(radius * 0.07 * DOWN, radius=radius * 0.022, color=RUBY)
        self.rotor = VGroup(self.wheel, self.jewel, self.staff)
        self.rotor.shift(self.c)

        # hairspring geometry (in units of the balance radius)
        self.turns, self.r_in = turns, r_in * radius
        self.r_out = (r_out if r_out is not None else 0.58) * radius
        self.stud_a = np.radians(stud_deg)
        self.spring = VMobject().set_stroke(HAIRSPRING, 2.0).set_fill(opacity=0)
        self.collet = Dot(self.c, radius=radius * 0.06, color=STEEL)
        self.stud = Square(radius * 0.09).set_fill(STEEL, 1).set_stroke(STEEL_HI, 1).move_to(self._spring_pt(1.0, 0))
        self.curb = VGroup(Dot(radius=radius * 0.025, color=STEEL_HI), Dot(radius=radius * 0.025, color=STEEL_HI))
        self.curb.set_opacity(0)
        parts = [self.rotor]
        if show_spring:
            parts += [self.spring, self.collet, self.stud, self.curb]
        self.add(*parts)
        self._draw_spring(0.0)                  # before recording opacities, so the spring is faded with the rest
        self._base = [(m, m.get_fill_opacity(), m.get_stroke_opacity()) for m in self.family_members_with_points()]

    # --------------------------------------------------------------- geometry
    def _spring_pt(self, s, phi):
        """Point at fraction s of the spring (0 = collet, 1 = stud) when the staff is at angle phi."""
        p = self.pins.get_value() if hasattr(self, "pins") else 1.0
        twist = phi * max(0.0, 1 - s / p) if p > 1e-6 else 0.0
        r = self.r_in + (self.r_out - self.r_in) * s
        a = self.stud_a - TAU * self.turns * (1 - s) + twist
        return self.c + r * np.array([np.cos(a), np.sin(a), 0.0])

    def _draw_spring(self, phi):
        s = np.linspace(0, 1, int(60 * self.turns))
        self.spring.set_points_smoothly([self._spring_pt(x, phi) for x in s])
        p = self.pins.get_value()
        if p < 0.999:
            q = self._spring_pt(p, phi)
            u = (q - self.c) / np.linalg.norm(q - self.c)
            gap = (self.r_out - self.r_in) / self.turns * 0.45
            self.curb[0].move_to(q + u * gap)
            self.curb[1].move_to(q - u * gap)

    def active_points(self, phi=None):
        """Points of the active length, collet to pins (for highlighting)."""
        phi = self.angle() if phi is None else phi
        s = np.linspace(0, self.pins.get_value(), int(60 * self.turns * self.pins.get_value()) + 2)
        return [self._spring_pt(x, phi) for x in s]

    # --------------------------------------------------------------- motion
    def phase(self):
        return TAU * self.hz * self.model_t

    def angle(self):
        auto = self.amp.get_value() * self.env * np.sin(self.phase())
        d = self.drive.get_value()
        return d * auto + (1 - d) * self.manual.get_value()

    def speed_frac(self):
        """|angular speed| / peak, for the swinging (driven) motion."""
        return abs(np.cos(self.phase()))

    def _apply_vis(self):
        v = self.vis.get_value()
        if abs(v - self._vis) > 1e-4:
            for m, fo, so in self._base:
                m.set_fill(opacity=fo * v, family=False).set_stroke(opacity=so * v, family=False)
            self._vis = v

    def step(self, dt):
        r = self.rate.get_value()
        self.model_t += dt * r
        self.env *= np.exp(-self.damp.get_value() * dt * r)
        a = self.angle()
        if a != self._ang:
            self.rotor.rotate(a - self._ang, about_point=self.c)
            self._ang = a
        self._draw_spring(a)
        if self.pins.get_value() < 0.999:
            self.curb.set_opacity(self.vis.get_value())
        self._apply_vis()

    def attach(self, scene, add=True):
        driver = Mobject()
        driver.add_updater(lambda _, dt: self.step(dt))
        if add:
            scene.add(self)
        scene.add(self.rate, self.amp, self.damp, self.drive, self.manual, self.vis, self.pins, driver)
        return driver


class BeatLog:
    """Record the video time of each beat of a model clock; write <scene>.ticks.txt."""

    def __init__(self, scene, model_time=None, beats_per_s=5, active=lambda: True, rate=None):
        """model_time: a function giving the model clock; or pass rate= (the
        ValueTracker given to attach_driver) and the log integrates it the same way."""
        self.times, self.t, self.last, self.mt = [], 0.0, None, 0.0
        self.model_time = model_time if model_time is not None else (lambda: self.mt)
        self.bps, self.active, self.rate = beats_per_s, active, rate

        def rec(_, dt):
            self.t += dt
            if rate is not None:
                self.mt += dt * rate.get_value()
            k = int(np.floor(self.model_time() * self.bps))
            if self.last is not None and k != self.last and self.active():
                self.times.append(self.t)
            self.last = k
        self.mob = Mobject()
        self.mob.add_updater(rec)
        scene.add(self.mob)

    def write(self, scene_file):
        path = os.path.splitext(scene_file)[0] + ".ticks.txt"
        with open(path, "w") as f:
            f.write("# Written by the scene on every render: video time of each beat, for build.py's tick track.\n")
            for t in self.times:
                f.write(f"{t:.3f}\n")


def escape_wheel_g(radius, n=15):
    """Shapely outline of a club-tooth escape wheel (the same tooth form as movement.py's)."""
    from shapely.geometry import Polygon as SPoly
    pts = []
    for k in range(n):
        a = TAU * k / n
        for da, rr in ((0.00, 0.62), (0.05, 0.95), (0.13, 1.0), (0.16, 0.93), (0.30, 0.66)):
            pts.append((radius * rr * np.cos(a + da * TAU / n * 3), radius * rr * np.sin(a + da * TAU / n * 3)))
    g = SPoly(pts).buffer(0)
    win = disk_g(radius * 0.5).difference(disk_g(radius * 0.16))
    for k in range(4):
        a = TAU * k / 4
        win = win.difference(LineString([(0, 0), (np.cos(a) * radius, np.sin(a) * radius)]).buffer(radius * 0.05))
    return g.difference(win)
