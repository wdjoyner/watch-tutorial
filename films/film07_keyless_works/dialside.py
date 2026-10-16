"""Film 7 helper: the whole dial side, flat. The keyless close-up (keyless.py)
with its setting wheel replaced by a setting train of Film 3's flat gears:
setting wheel -> intermediate setting wheel -> minute wheel (36, pinion 10) ->
cannon pinion (12) on the center arbor, and the hour wheel (40), with hands and
a mark on the center arbor. Used by scenes 02 and 05.

    ds = DialSide(pull=1.0)
    ds.add_to(scene)
    scene.play(ds.slip.animate.set_value(-1))    # the crown sets the hands

Trackers (animate these, never the parts):
    arbor      center arbor angle in turns (driven by the going train)
    slip       the cannon pinion's turn relative to the arbor (driven from the crown)
    crown      crown turns, used only while the sliding pinion is off the setting wheel
    (the hands start at start_time, 10:10 by default; animate slip by increment_value)
    vis        the gears' opacity; hands_vis, mark_vis for the hands and the arbor's mark
    kw.*       the keyless works' own trackers (pull, glow, vis, ...)
The cannon pinion's angle is arbor + slip. While the sliding pinion is on the
setting wheel, the crown, sliding pinion and setting train all follow it through
the tooth ratios; otherwise the crown turns on its own (from `crown`).
Setting-wheel tooth counts are illustrative (ETA does not publish them); they
cancel out of the ratio anyway.
"""
from manim import *
from movement import BG, GLOW, STEEL, STEEL_HI, STEEL_DK, BRASS
from train import GearSet
from keyless import KeylessWorks, SW_C, SW_R, SW_Z, SET_N

Z_INTER, Z_MINUTE, Z_MPIN, Z_HOUR, Z_CANNON = 26, 36, 10, 40, 12
SET_COLOR = "#7fe0a0"


def hand(length, width, color, tail=0.22):
    pts = [[-tail, 0, 0], [0, width / 2, 0], [length, width * 0.15, 0], [length + 0.07, 0, 0],
           [length, -width * 0.15, 0], [0, -width / 2, 0]]
    return Polygon(*pts).set_fill(color, 1).set_stroke(BG, 1.5)


class DialSide:
    def __init__(self, kw_scale=1.2, sw_screen=(-0.4, 1.5), pull=0.0, angles=(210, 190, 252),
                 minute_hand=1.45, hour_hand=0.95, start_time=(10, 10)):
        inter_a, minute_a, cannon_a = angles
        sw_screen = np.array(sw_screen)
        self.arbor, self.slip, self.crown = ValueTracker(0.0), ValueTracker(0.0), ValueTracker(0.0)
        h, m = start_time                      # the hands start at this time (clockwise = negative turns)
        self.slip.set_value(-(h + m / 60))
        self.vis, self.hands_vis, self.mark_vis = ValueTracker(0.0), ValueTracker(0.0), ValueTracker(0.0)

        m_a = 2 * SW_R * kw_scale / SW_Z
        m_b = m_a * (Z_MINUTE + Z_CANNON) / (Z_MPIN + Z_HOUR)    # the hour wheel coaxial with the cannon pinion
        gs = self.gs = GearSet()
        gs.gear("cannon", Z_CANNON, m_a, center=(0, 0), kind="pinion")
        gs.gear("minute", Z_MINUTE, m_a, driven_by="cannon", angle=cannon_a + 180, spokes=3, color=STEEL)
        gs.gear("mpin", Z_MPIN, m_b, arbor_of="minute", kind="pinion")
        gs.gear("hour", Z_HOUR, m_b, driven_by="mpin", angle=cannon_a, kind="plain")
        gs.gear("inter", Z_INTER, m_a, driven_by="minute", angle=minute_a + 180, spokes=0, color=STEEL)
        gs.gear("setting", SW_Z, m_a, driven_by="inter", angle=inter_a + 180, kind="plain", color=STEEL)
        offset = np.array([*sw_screen, 0]) - gs["setting"].pivot
        for g in gs.gears.values():
            g.shift(offset)
            g.pivot = g.pivot + offset
        gs["hour"].body.set_fill(BRASS, 0.9)
        for g in gs.gears.values():
            g._base = [(m, m.get_fill_opacity(), m.get_stroke_opacity()) for m in g.family_members_with_points()]
        gs.group.submobjects = [gs[n] for n in ("hour", "minute", "mpin", "cannon", "inter", "setting")]
        self.c0 = c0 = gs["cannon"].pivot

        kw_origin = tuple(sw_screen - kw_scale * np.array(SW_C))
        self.kw = kw = KeylessWorks(origin=kw_origin, scale=kw_scale, setting_wheel=False)
        kw.pull.set_value(pull)
        self.spin_per_cannon = -gs["setting"].k * SW_Z / (2 * SET_N)   # the sliding pinion's 12 face teeth

        self.hands = {"hour": hand(hour_hand, 0.17, GLOW), "minute": hand(minute_hand, 0.12, WHITE)}
        self.arbor_mark = VGroup(Circle(radius=0.11).set_fill(STEEL_DK, 1).set_stroke(STEEL_HI, 1.2),
                                 Line(ORIGIN, RIGHT * 0.32).set_stroke(SET_COLOR, 4))
        for m in (*self.hands.values(), self.arbor_mark):
            m.shift(c0)
            m._ang = 0.0

        def turn_to(m, a, v):
            if a != m._ang:
                m.rotate(a - m._ang, about_point=c0)
                m._ang = a
            m.set_fill(opacity=v).set_stroke(opacity=v)
        self.hands["minute"].add_updater(lambda m: turn_to(m, PI / 2 + self.cannon_angle(), self.hands_vis.get_value()))
        self.hands["hour"].add_updater(lambda m: turn_to(m, PI / 2 + gs["hour"]._ang - gs["hour"].c,
                                                         self.hands_vis.get_value()))

        def mark_upd(m):
            a = self.arbor.get_value() * TAU
            if a != m._ang:
                m.rotate(a - m._ang, about_point=c0)
                m._ang = a
            v = self.mark_vis.get_value()
            m[0].set_fill(opacity=v).set_stroke(opacity=v)
            m[1].set_stroke(opacity=v)
        self.arbor_mark.add_updater(mark_upd)

        def drive(m, dt):
            c = self.cannon_angle()
            gs.turn.set_value(c)
            gs.update()
            if kw.engaged_setting():
                kw.spin.set_value(c * self.spin_per_cannon)
            else:
                kw.spin.set_value(self.crown.get_value() * TAU)
            for g in gs.gears.values():
                g.vis.set_value(self.vis.get_value())
        self.driver = Mobject().add_updater(drive)

    def cannon_angle(self):
        return (self.arbor.get_value() + self.slip.get_value()) * TAU

    def add_to(self, scene):
        gs, kw = self.gs, self.kw
        scene.add(gs.group, kw, self.driver, self.arbor, self.slip, self.crown, self.vis, gs.turn, *kw.trackers(),
                  *[g.vis for g in gs.gears.values()], self.hands["hour"], self.hands["minute"], self.arbor_mark,
                  self.hands_vis, self.mark_vis)

    def gp(self, name, ang, f=1.0):
        """A point on a gear's rim (or inside it, f < 1), as a function for callouts."""
        g = self.gs[name]
        return lambda: g.pivot + f * g.r * np.array([np.cos(np.radians(ang)), np.sin(np.radians(ang)), 0])

    def hand_point(self, which, f):
        h = self.hands[which]
        return lambda: self.c0 + f * np.array([np.cos(h._ang), np.sin(h._ang), 0])
