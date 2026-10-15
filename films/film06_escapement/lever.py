"""Film 6 helper: a 2D Swiss lever escapement in close-up, with real contact kinematics.

The outlines come from the planar kinematic model behind the chapter's Swiss-lever
figures (lever_geometry.json, extracted from the .tex). The wheel and lever are not
keyframed: for every balance angle, solve() finds where they must be so that no
two parts overlap (shapely), with the escape wheel always pushing forward:

  lock      the tooth rests on a stone; draw holds the lever on its banking pin
  unlock    the roller jewel pushes the fork; the tooth slides off the locking face,
            and draw makes the wheel recoil slightly
  impulse   the wheel pushes the lever, and the fork pushes the roller jewel
  drop      the tooth leaves the stone; the wheel runs free until the next tooth
            lands on the other stone; the lever runs on to its other banking pin

The result is a table, lever_table.json (rebuild with `python lever.py`), for the
forward vibration (balance counterclockwise, entry stone unlocks) and the return
vibration (clockwise, exit stone unlocks). It reproduces the chapter's four
panels to within about 0.3 deg. The geometry is schematic, not the 6497's: its lift
angle comes out near 40 deg (ETA gives 44 deg for the 6497).

Angles: phi is the roller jewel's polar angle about the balance staff, in degrees;
-90 is the line of centers (the dead point). The balance swing psi = phi + 90.

LeverEscapement(VGroup)
    esc = LeverEscapement(center=(0, -2), scale=1.6)
    esc.attach(scene)
  Trackers (animate these, never the parts):
    rate        model clock speed, 1 = real time (2.5 Hz, 270 deg amplitude)
    lift_rate   extra clock factor while the jewel is inside the lift window (slow it there)
    amp         swing amplitude, degrees
    drive       1 = swinging on its own clock, 0 = held at `manual` (degrees of psi)
    manual      psi in degrees, used where drive < 1
    vis         opacity of everything (fade with this, never FadeIn)
    rim         opacity of the faint balance rim drawn behind (0 hides it)
  esc.anchor(name) gives a part's current screen point, for labels: escape_wheel,
    tooth, entry_stone, exit_stone, pallet_fork, fork, lever_pivot, banking_left,
    banking_right, roller_jewel, roller, staff, guard_pin.
  esc.phase() is "lock", "unlock", "impulse", "drop" or "free" (for live labels).
  esc.events records (video_time, kind) for unlock / impulse / drop / bank, so a
    scene can write sound effects; esc.lift() gives the model's lift angle.
"""
import json, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
GEOM = json.load(open(os.path.join(HERE, "lever_geometry.json")))
TABLE_FILE = os.path.join(HERE, "lever_table.json")
WC, LC, BC = (0.0, 0.0), tuple(GEOM["lever_pivot"]), tuple(GEOM["staff"])
BANK_L, BANK_R = GEOM["banking_deg"]
RJ, RJ_R = GEOM["roller_jewel"]["radius"], GEOM["roller_jewel"]["r"]
PHI_LO, PHI_HI = -150.0, -40.0                   # the sweep: outside it, nothing touches


# ======================================================================= the solver
def solve(step=0.1):
    """Quasi-static kinematics over one forward and one return vibration."""
    from shapely.geometry import Polygon, Point
    from shapely import affinity
    wheel = Polygon(GEOM["wheel"][0])
    lever = Polygon(GEOM["lever"][0]).union(Polygon(GEOM["lever"][1]))   # the guard pin sits lower: it never meets the jewel
    stones = Polygon(GEOM["entry_stone"]).union(Polygon(GEOM["exit_stone"]))
    tol = 2e-6

    def wclash(a, b):
        return affinity.rotate(wheel, a, origin=WC).intersection(affinity.rotate(stones, b, origin=LC)).area > tol

    def lclash(b, phi):
        p = Point(BC[0] + RJ * np.cos(np.radians(phi)), BC[1] + RJ * np.sin(np.radians(phi))).buffer(RJ_R, 24)
        return affinity.rotate(lever, b, origin=LC).intersection(p).area > tol

    def slide(clash, x, s, lim):
        """From a feasible x, move in steps of s while still feasible, halving the step on contact."""
        while abs(s) > 1e-3:
            y = min(max(x + s, min(x, lim)), max(x, lim))
            if y != x and not clash(y):
                x = y
            else:
                s /= 2
            if x == lim:
                break
        return x

    def escape(clash, x, s):
        while clash(x):
            x += s
        return x

    def sweep(b, sgn, a_start=0.0):
        """sgn = +1: forward (phi rising, lever heads to BANK_R); -1: return."""
        target = BANK_R if sgn > 0 else BANK_L
        a0 = slide(lambda y: wclash(y, b), a_start, -0.005, a_start - 1.0)   # the locked tooth settles on its stone
        a, mode, rows = a0, "lock", []
        phis = np.arange(PHI_LO, PHI_HI + step / 2, step)
        for phi in (phis if sgn > 0 else phis[::-1]):
            if lclash(b, phi):                                     # the jewel pushes the fork
                b = escape(lambda y: lclash(y, phi), b, -0.01 * sgn)
            if mode != "lock":                                     # the tooth pushes the lever, which leads the jewel
                for _ in range(200):
                    b2 = slide(lambda y: lclash(y, phi) or wclash(a, y), b, -0.02 * sgn, target)
                    a2 = slide(lambda y: wclash(y, b2), a, -0.02, a - 15)
                    if abs(b2 - b) < 1e-4 and abs(a2 - a) < 1e-4:
                        break
                    b, a = b2, a2
            if wclash(a, b):                                       # draw: the wheel recoils
                a = escape(lambda y: wclash(y, b), a, +0.005)
            a = slide(lambda y: wclash(y, b), a, -0.02, a - 15)
            if mode == "lock" and a < a0 - 0.5:
                mode = "impulse"
            rows.append((float(phi), float(b), float(a - a0)))
        rows.sort()
        return rows, b, a

    fwd, b_end, a_end = sweep(BANK_L, +1)
    rev, _, _ = sweep(b_end, -1, a_end)
    return dict(note="phi (deg), lever (deg), wheel advance from the locked pose (deg); built by lever.py solve()",
                forward=fwd, ret=rev)


def build_table():
    global TABLE
    TABLE = solve()
    json.dump(TABLE, open(TABLE_FILE, "w"), separators=(",", ":"))
    return TABLE


TABLE = json.load(open(TABLE_FILE)) if os.path.exists(TABLE_FILE) else None


def _arrays(key):
    r = np.array(TABLE[key])
    return r[:, 0], r[:, 1], r[:, 2]


def events(key="forward"):
    """Balance angles (phi) at which the forward (or return) vibration's events happen."""
    phi, lev, wh = _arrays(key)
    seq = phi if key == "forward" else phi[::-1]
    l = lev if key == "forward" else lev[::-1]
    w = wh if key == "forward" else wh[::-1]
    b0 = l[0]
    unlock = seq[np.argmax(np.abs(l - b0) > 0.05)]
    impulse = seq[np.argmax(w < -0.5)]
    jumps = np.abs(np.diff(w))
    k = np.argmax(jumps * (np.abs(w[1:]) > 6))                     # the drop: the largest late jump in the wheel
    drop = seq[k + 1]
    bank = seq[np.argmax(np.abs(l - l[-1]) < 0.01)]
    return dict(unlock=float(unlock), impulse=float(impulse), drop=float(drop), bank=float(bank),
                wheel_step=float(w[-1]), lever_end=float(l[-1]))


def lift(key="forward"):
    e = events(key)
    return abs(e["bank"] - e["unlock"])


# ======================================================================= the Manim mobject
try:
    from manim import (VGroup, VMobject, Polygon as MPoly, Circle, DashedVMobject, ValueTracker,
                       rotate_vector, WHITE)
    from movement import STEEL, STEEL_DK, STEEL_HI, RUBY, GILT, BRASS_DK
except ImportError:                                                   # `python lever.py` without Manim
    VGroup = object


def _rot(p, c, deg):
    a = np.radians(deg)
    x, y = p[0] - c[0], p[1] - c[1]
    return (c[0] + x * np.cos(a) - y * np.sin(a), c[1] + x * np.sin(a) + y * np.cos(a))


class LeverEscapement(VGroup):
    def __init__(self, center=(0.0, -2.0), scale=1.6, amp=270.0, rim_r=1.15, show_safety=True):
        super().__init__()
        assert TABLE is not None, "run `python lever.py` once to build lever_table.json"
        self.o, self.k = np.array(center, float), scale
        self.rate, self.lift_rate, self.amp = ValueTracker(1.0), ValueTracker(1.0), ValueTracker(amp)
        self.drive, self.manual = ValueTracker(1.0), ValueTracker(-55.0)
        self.vis, self.rim = ValueTracker(1.0), ValueTracker(0.35)
        self.fwd, self.ret = _arrays("forward"), _arrays("ret")
        self.ev_f, self.ev_r = events("forward"), events("ret")
        self.model_t, self.video_t = 0.3, 0.0           # start at the far end of a swing (psi = -amp)
        self.side = "L"                                # L: locked on entry, lever on the left pin; R: on exit
        self.wbase, self.lever_now, self.wheel_now = 0.0, BANK_L, 0.0
        self._phi_prev = None
        self.events = []
        self.skipped_drops = False        # True: also log a drop when one frame jumps impulse -> lock (fast, unslowed runs)

        P = lambda pts: [self.pt(p) for p in pts]
        # parts in their lock-pose outline (geometry units); each is redrawn from its angle
        self.g_wheel = [np.array(r) for r in GEOM["wheel"]]
        self.g_lever = [np.array(r) for r in GEOM["lever"]]
        self.g_stones = [np.array(GEOM["entry_stone"]), np.array(GEOM["exit_stone"])]
        self.g_guard = np.array(GEOM["guard_pin"])
        self.g_safety = np.array(GEOM["safety_roller"])
        j0 = GEOM["roller_jewel"]["angle_deg"]
        self.safety_ref = j0

        self.rim_g = VGroup(Circle(radius=rim_r * self.k, stroke_color=GILT, stroke_width=6),
                            *[VMobject(stroke_color=GILT, stroke_width=4) for _ in range(3)])
        self.wheel_m = VMobject(fill_color=STEEL, fill_opacity=1, stroke_color=STEEL_HI, stroke_width=1.2)
        self.wheel_hub = Circle(radius=GEOM["wheel_hub_r"] * self.k, fill_color=STEEL_DK, fill_opacity=1, stroke_width=0)
        self.lever_m = VMobject(fill_color="#3c5a86", fill_opacity=1, stroke_color="#9fb6d8", stroke_width=1.2)
        self.stones_m = VGroup(*[VMobject(fill_color=RUBY, fill_opacity=1, stroke_color="#ff9aa0", stroke_width=0.8)
                                 for _ in range(2)])
        self.guard_m = VMobject(fill_color=STEEL_HI, fill_opacity=1, stroke_width=0.6, stroke_color=WHITE)
        self.lever_hub = Circle(radius=GEOM["lever_hub_r"] * self.k, fill_color=STEEL_DK, fill_opacity=1, stroke_width=0)
        self.pins = VGroup(*[Circle(radius=c[2] * self.k, fill_color=GILT, fill_opacity=1, stroke_color=BRASS_DK,
                                    stroke_width=1).move_to(self.pt(c[:2])) for c in GEOM["banking_pins"]])
        self.table_m = DashedVMobject(Circle(radius=GEOM["roller_table_r"] * self.k, stroke_color=STEEL_HI,
                                             stroke_width=1.5).move_to(self.pt(BC)), num_dashes=36)
        self.safety_m = VMobject(fill_color=STEEL, fill_opacity=1, stroke_color=STEEL_HI, stroke_width=1)
        self.jewel_m = Circle(radius=RJ_R * self.k, fill_color=RUBY, fill_opacity=1, stroke_color="#ff9aa0",
                              stroke_width=0.8)
        self.staff_m = Circle(radius=GEOM["staff_r"] * self.k, fill_color=STEEL_DK, fill_opacity=1,
                              stroke_width=0).move_to(self.pt(BC))
        self.show_safety = show_safety
        self._filled = None
        self.add(self.rim_g, self.wheel_m, self.wheel_hub.move_to(self.pt(WC)), self.lever_m, self.stones_m,
                 self.guard_m, self.lever_hub.move_to(self.pt(LC)), self.pins, self.table_m, self.safety_m,
                 self.jewel_m, self.staff_m)
        self._draw(-145.0)

    # ------------------------------------------------------------------ geometry
    def pt(self, p):
        return np.array([self.o[0] + self.k * p[0], self.o[1] + self.k * p[1], 0.0])

    def _poly(self, m, rings, c, deg):
        m.clear_points()
        for r in rings:
            pts = [self.pt(_rot(p, c, deg)) for p in r]
            m.start_new_path(pts[0])
            m.add_points_as_corners(pts[1:] + [pts[0]])

    def psi(self):
        """Balance swing angle (degrees from the dead point) for the current frame."""
        swing = self.amp.get_value() * np.sin(2 * np.pi * 2.5 * self.model_t)
        d = self.drive.get_value()
        return d * swing + (1 - d) * self.manual.get_value()

    def _lookup(self, tab, phi):
        p, l, w = tab
        return float(np.interp(phi, p, l)), float(np.interp(phi, p, w))

    def _target(self, phi, rising):
        """Lever and wheel angles for jewel angle phi, given the swing's direction."""
        if self.side == "L":
            if rising or phi > PHI_LO:
                lev, dw = self._lookup(self.fwd, np.clip(phi, PHI_LO, PHI_HI))
                if phi >= PHI_HI and rising:                      # the forward vibration is complete
                    self.side, self.wbase = "R", self.wbase + self.fwd[2][-1]
                    return BANK_R, self.wbase
                return lev, self.wbase + dw
        if self.side == "R":
            lev, dw = self._lookup(self.ret, np.clip(phi, PHI_LO, PHI_HI))
            if phi <= PHI_LO and not rising:
                self.side, self.wbase = "L", self.wbase + self.ret[2][0]
                return BANK_L, self.wbase
            return lev, self.wbase + dw
        return self.lever_now, self.wheel_now

    def _phase_of(self, phi, rising):
        ev = self.ev_f if (self.side == "L") else self.ev_r
        if self.side == "L" and rising:
            seq = [("lock", -999), ("unlock", ev["unlock"]), ("impulse", ev["impulse"]), ("drop", ev["drop"]),
                   ("lock", ev["bank"])]
            name = "lock"
            for n, a in seq:
                if phi >= a:
                    name = n
            return name
        if self.side == "R" and not rising:
            seq = [("lock", 999), ("unlock", ev["unlock"]), ("impulse", ev["impulse"]), ("drop", ev["drop"]),
                   ("lock", ev["bank"])]
            name = "lock"
            for n, a in seq:
                if phi <= a:
                    name = n
            return name
        return "lock"

    def phase(self):
        return getattr(self, "_phase", "lock")

    def lift(self):
        return lift("forward")

    def _draw(self, phi, rising=True, dt_model=0.0):
        lev_t, wh_t = self._target(phi, rising)
        # the drop and the lever's jump at the start of impulse take a little time: cap the speeds
        if dt_model > 0:
            cap_w, cap_l = 2000.0 * dt_model, 6000.0 * dt_model           # deg per model second [GP: 1.5 deg in ~1 ms]
            self.wheel_now += np.clip(wh_t - self.wheel_now, -cap_w, cap_w)
            self.lever_now += np.clip(lev_t - self.lever_now, -cap_l, cap_l)
        else:
            self.wheel_now, self.lever_now = wh_t, lev_t
        self._poly(self.wheel_m, self.g_wheel, WC, self.wheel_now)
        self._poly(self.lever_m, self.g_lever, LC, self.lever_now)
        self._poly(self.guard_m, [self.g_guard], LC, self.lever_now)
        for m, g in zip(self.stones_m, self.g_stones):
            self._poly(m, [g], LC, self.lever_now)
        self._poly(self.safety_m, [self.g_safety], BC, phi - self.safety_ref)
        self.jewel_m.move_to(self.pt((BC[0] + RJ * np.cos(np.radians(phi)), BC[1] + RJ * np.sin(np.radians(phi)))))
        rim, arms = self.rim_g[0], self.rim_g[1:]
        rim.move_to(self.pt(BC))
        r = rim.width / 2
        for i, arm in enumerate(arms):
            a = np.radians(phi + 90 + 120 * i + 30)
            arm.set_points_as_corners([self.pt(BC), self.pt(BC) + r * np.array([np.cos(a), np.sin(a), 0])])
        self._phase = self._phase_of(phi, rising)
        self._apply_vis()

    def _apply_vis(self):
        v = self.vis.get_value()
        if self._filled is None:
            self._filled = {id(m) for m in self.family_members_with_points() if m.get_fill_opacity() > 0}
        for m in self.family_members_with_points():
            m.set_stroke(opacity=v)
            if id(m) in self._filled:
                m.set_fill(opacity=v)
        for m in self.rim_g:
            m.set_stroke(opacity=v * self.rim.get_value())

    def step(self, dt):
        self.video_t += dt
        phi_now = self.psi() - 90.0
        inside = abs(phi_now + 90.0) < 40.0
        dtm = dt * self.rate.get_value() * (self.lift_rate.get_value() if inside else 1.0)
        self.model_t += dtm
        phi = self.psi() - 90.0
        rising = True if self._phi_prev is None else phi >= self._phi_prev
        before = self.phase()
        self._draw(phi, rising, dtm)
        after = self.phase()
        if after != before and after in ("unlock", "impulse", "drop"):
            self.events.append((self.video_t, after))
        if before == "drop" and after == "lock":
            self.events.append((self.video_t, "bank"))
        elif self.skipped_drops and before == "impulse" and after == "lock":
            self.events.append((self.video_t, "drop"))   # a fast frame stepped over the drop (title, credits)
        self._phi_prev = phi

    def attach(self, scene):
        scene.add(self.rate, self.lift_rate, self.amp, self.drive, self.manual, self.vis, self.rim)
        self.add_updater(lambda m, dt: m.step(dt))
        scene.add(self)
        return self

    # ------------------------------------------------------------------ anchors for labels
    def anchor(self, name):
        lev, wh = self.lever_now, self.wheel_now
        phi = self._phi_prev if self._phi_prev is not None else -145.0
        L = lambda p: self.pt(_rot(p, LC, lev))
        if name == "escape_wheel":
            return self.pt(_rot((-0.62, -0.45), WC, wh))
        if name == "tooth":
            return self.pt(_rot((-0.47, 0.83), WC, wh))
        if name == "entry_stone":
            return L(np.mean(self.g_stones[0], axis=0))
        if name == "exit_stone":
            return L(np.mean(self.g_stones[1], axis=0))
        if name == "pallet_fork":
            return L((0.0, 1.24))
        if name == "fork":
            return L((-0.06, 1.70))
        if name == "lever_pivot":
            return self.pt(LC)
        if name in ("banking_left", "banking_right"):
            c = GEOM["banking_pins"][0 if name == "banking_left" else 1]
            return self.pt(c[:2])
        if name == "roller_jewel":
            return self.jewel_m.get_center()
        if name in ("roller", "staff"):
            return self.pt(BC)
        if name == "guard_pin":
            return L(np.mean(self.g_guard, axis=0))
        raise KeyError(name)


if __name__ == "__main__":
    t = build_table()
    for key in ("forward", "ret"):
        e = events(key)
        print(f"{key:8s} " + "  ".join(f"{k} {v:+.1f}" for k, v in e.items()) + f"   lift {lift(key):.1f} deg")
