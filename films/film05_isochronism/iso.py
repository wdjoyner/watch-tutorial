"""Film 5 helpers, built on Film 4's balance.py and ui.py (reached through f4.py).

IsoBalance(BalanceModel)
    A flat balance whose frequency depends on its amplitude, as the Duffing
    correction says: f(Theta) = f0 (1 + 3 beta Theta^2 / 8 kappa). Extra trackers:
      beta    beta / kappa, per rad^2 (0 = a perfectly linear spring)
      offset  rest angle of the staff relative to the hairspring, radians: the
              collet turned on the staff, for beat error (0 = in beat)
    `amp` is the drawn swing (reduced, so it doesn't strobe). real_amp() maps it
    to the amplitude it stands for: amp == amp_full is drawn for real_full (270 deg).
    The phase is integrated, so the frequency can change while it runs.

    bal.beats() is the number of times the staff has crossed the line of
    centers (angle 0). With offset = 0 that is 2 per cycle, evenly spaced; with
    an offset, the crossings alternate long and short intervals. Pass
    `lambda: bal.beats()` to BeatLog with beats_per_s=1.

Plot
    A plain 2D plot frame (Lines and Text only: no Axes numbers, which need LaTeX).
    p = Plot(origin, w, h, xr, yr); p.c2p(x, y); p.curve(f, x0, x1); p.frame(...)
"""
import f4  # noqa: F401  (puts Film 4's folder on sys.path)
import numpy as np
from manim import *
from balance import BalanceModel
from ui import label

DEG = np.pi / 180


class IsoBalance(BalanceModel):
    def __init__(self, *args, beta=0.0, offset=0.0, amp_full=1.2, real_full=270 * DEG, **kw):
        super().__init__(*args, **kw)
        self.beta, self.offset = ValueTracker(beta), ValueTracker(offset)
        self.amp_full, self.real_full = amp_full, real_full
        self._ph = 0.0

    def real_amp(self):
        return self.amp.get_value() * self.env / self.amp_full * self.real_full

    def hz_now(self):
        return self.hz * (1 + 3 * self.beta.get_value() * self.real_amp() ** 2 / 8)

    def phase(self):
        return self._ph

    def swing(self):
        return super().angle()

    def angle(self):
        return self.offset.get_value() + super().angle()

    def _draw_spring(self, phi):
        # the spring is relaxed at the collet's own zero: subtract the staff's offset
        off = self.offset.get_value() if hasattr(self, "offset") else 0.0
        super()._draw_spring(phi - off)

    def step(self, dt):
        self._ph += TAU * self.hz_now() * dt * self.rate.get_value()
        super().step(dt)

    def beats(self):
        """Crossings of the line of centers (staff angle 0) so far."""
        a = self.amp.get_value() * self.env
        if a <= 1e-9:
            return 0
        s = np.clip(-self.offset.get_value() / a, -1, 1)
        th0 = np.arcsin(s)                       # crossings at phase th0 and pi - th0 (mod 2 pi)
        ph = self._ph
        n = np.floor((ph - th0) / TAU) + 1 if ph >= th0 else 0
        m = np.floor((ph - (np.pi - th0)) / TAU) + 1 if ph >= np.pi - th0 else 0
        return int(n + m)

    def attach(self, scene, add=True):
        d = super().attach(scene, add)
        scene.add(self.beta, self.offset)
        return d


class Plot(VGroup):
    """A plain plot frame: x along w, y along h, value ranges xr, yr."""

    def __init__(self, origin, w, h, xr, yr, color=GREY_B):
        super().__init__()
        self.o, self.w, self.h, self.xr, self.yr = np.array([*origin, 0.0]), w, h, xr, yr
        self.x_axis = Line(self.o, self.o + RIGHT * w).set_stroke(color, 1.4)
        self.y_axis = Line(self.o, self.o + UP * h).set_stroke(color, 1.4)
        self.add(self.x_axis, self.y_axis)

    def c2p(self, x, y):
        fx = (x - self.xr[0]) / (self.xr[1] - self.xr[0])
        fy = (y - self.yr[0]) / (self.yr[1] - self.yr[0])
        return self.o + np.array([fx * self.w, fy * self.h, 0.0])

    def pts(self, f, x0, x1, n=120):
        return [self.c2p(x, f(x)) for x in np.linspace(x0, x1, n)]

    def curve(self, f, x0=None, x1=None, color=WHITE, width=3.0, n=120):
        x0 = self.xr[0] if x0 is None else x0
        x1 = self.xr[1] if x1 is None else x1
        return VMobject().set_points_smoothly(self.pts(f, x0, x1, n)).set_stroke(color, width).set_fill(opacity=0)

    def xtick(self, x, text, scale=0.22):
        p = self.c2p(x, self.yr[0])
        return VGroup(Line(p, p + DOWN * 0.08).set_stroke(GREY_B, 1.2), label(text, scale).next_to(p, DOWN, buff=0.14))

    def ytick(self, y, text, scale=0.22):
        p = self.c2p(self.xr[0], y)
        return VGroup(Line(p, p + LEFT * 0.08).set_stroke(GREY_B, 1.2), label(text, scale).next_to(p, LEFT, buff=0.14))

    def xlabel(self, text, scale=0.24):
        return label(text, scale).next_to(self.x_axis, DOWN, buff=0.45).align_to(self.x_axis, RIGHT)

    def ylabel(self, text, scale=0.24):
        return label(text, scale).next_to(self.y_axis, UP, buff=0.1).align_to(self.y_axis, LEFT)


def spring_cg(points):
    """Center of gravity of a uniform wire through the given points (arclength-weighted)."""
    P = np.asarray(points)[:, :2]
    d = np.linalg.norm(np.diff(P, axis=0), axis=1)
    mid = (P[1:] + P[:-1]) / 2
    return (mid * d[:, None]).sum(0) / d.sum()


class FlatSpring(VMobject):
    """A flat spiral hairspring, schematic: its inner end turns with the staff by
    phi, its outer end is pinned at the stud, and the coils both turn and open or
    close (breathe) as it winds. Not a balance: no wheel, just the spring, a
    collet and a stud. spring.cg(phi) is the spring's center of gravity.

    Drive it with an updater: spring.add_updater(lambda m: m.draw(phi_now())).
    """

    def __init__(self, center=(0, 0), r_in=0.18, r_out=1.0, turns=7, stud_deg=-60.0, breathe=0.18,
                 color="#9fb6d8", width=2.0):
        super().__init__()
        self.c = np.array([center[0], center[1], 0.0])
        self.r_in, self.r_out, self.turns, self.breathe = r_in, r_out, turns, breathe
        self.stud_a = np.radians(stud_deg)
        self.set_stroke(color, width).set_fill(opacity=0)
        self.draw(0.0)

    def pts(self, phi, n=None):
        s = np.linspace(0, 1, n or int(70 * self.turns))
        r = (self.r_in + (self.r_out - self.r_in) * s) * (1 - self.breathe * phi * (1 - s))
        a = self.stud_a - TAU * self.turns * (1 - s) + phi * (1 - s)
        return self.c + np.c_[r * np.cos(a), r * np.sin(a), np.zeros_like(s)]

    def draw(self, phi):
        self.set_points_smoothly(self.pts(phi))
        return self

    def cg(self, phi):
        g = spring_cg(self.pts(phi, 1200))
        return np.array([g[0], g[1], 0.0])

    def stud_pt(self):
        return self.pts(0.0, 2)[-1]


class CrossLog:
    """Record the video time each time the staff crosses the line of centers
    (bal.angle() changes sign), interpolated between frames, and write
    <scene>.ticks.txt for build.py. Unlike BeatLog it needs no model clock, so a
    beat-error offset or a change of rate never skips or doubles a tick."""

    def __init__(self, scene, bal, active=lambda: True):
        self.times, self.t, self.prev = [], 0.0, None
        self.bal, self.active = bal, active

        def rec(_, dt):
            a = self.bal.angle()
            if self.prev is not None and dt > 0 and (a > 0) != (self.prev > 0) and self.active():
                frac = abs(self.prev) / (abs(self.prev) + abs(a)) if a != self.prev else 1.0
                self.times.append(self.t + dt * frac)
            self.t += dt
            self.prev = a
        self.mob = Mobject()
        self.mob.add_updater(rec)
        scene.add(self.mob)

    def write(self, scene_file):
        import os
        path = os.path.splitext(scene_file)[0] + ".ticks.txt"
        with open(path, "w") as f:
            f.write("# Written by the scene on every render: video time of each beat, for build.py's tick track.\n")
            for t in self.times:
                f.write(f"{t:.3f}\n")
