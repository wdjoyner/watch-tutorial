"""Film 6, scene 09 - "Measuring the torque": a short digression on the
torsiometer, the mainspring dynamometer (after Horopedia, "The torsiometer").
A schematic bench, left to right on one shaft: the barrel in its chuck, the
torque sensor (a small element carrying strain gauges; the twist changes their
resistance, giving a voltage proportional to the torque), an encoder counting
turns, and a magnetic hysteresis brake that lets the spring down smoothly.
Plot torque against turns: letting down, then winding, and the gap between the
two curves is energy lost to friction between the coils (SCHEMATIC curve,
shape only). Then a real measurement: Seiko's patent, FIG. 8: 2.65, 2.26 and
1.77 mN m at 0, 20 and 40 hours, about a third less torque.

Build (render + voice + mux):   python build.py 6/scene09_torsiometer
Render only (quick preview):    PYTHONPATH=.:films/film06_escapement manim -ql films/film06_escapement/scene09_torsiometer.py Scene09
Narration lines and their start times live in scene09_torsiometer.voice.txt. Numbers from figures.py.
"""
from manim import *
import prev  # noqa: F401  (first: Film 4 and 5 helpers on the path)
import ui6  # noqa: F401  (extra subscripts)
import figures as F
from iso import Plot
from movement import vignette, BG, GLOW
from ui import ftext, label, heading, tag, curtain, clock, WARM, COOL

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds.
# Keep the timeline roughly in step with scene09_torsiometer.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 1.0
HEAD_AT = 1.2                         # "How do we know a mainspring's torque? ..."
BENCH_AT = 5.0                        # "... a torsiometer: a small dynamometer."
CHUCK_AT = 10.2                       # "The barrel is clamped in a chuck, and lets down slowly against a brake."
BRAKE_AT = 14.6                       # "A magnetic brake gives a smooth, steady resistance ..."
SENSOR_AT = 20.5                      # "Between them sits the torque sensor ..."
TWIST_AT = 26.0                       # "The torque twists it very slightly ..."
VOLT_AT = 31.0                        # "... and out comes a voltage proportional to the torque."
ENCODER_AT = 36.1                     # "An encoder counts the turns."
CURVE_AT = 38.6                       # "Plot torque against turns ..."
WIND_AT = 43.1                        # "Wind it up and let it down ..."
GAP_AT = 48.0                         # "... the gap between them is energy lost to friction."
SEIKO_AT = 53.7                       # "Seiko published one such measurement in a patent ..."
SEIKO_PTS = (57.4, 61.2, 64.4)        # "... two point six five ... two point two six ... one point seven seven"
THIRD_AT = 67.2                       # "A third less torque."
FINAL_HOLD_UNTIL = 70.7               # the last line ends about 68.7 s
FADE_OUT = 1.5

LET_DOWN_RATE = 0.12                  # bench turns per video second (slowed for the eye)
BENCH_Y = 1.25
X = dict(barrel=-5.0, sensor=-2.4, encoder=0.3, brake=3.0)
N_TURNS = 7.0                         # schematic x range of the torque plot
TEXT = dict(q="how do we know the torque?", name="torsiometer:  a mainspring dynamometer",
            src="after Horopedia, “The torsiometer”; drawing schematic",
            barrel="barrel in a chuck", sensor="torque sensor\n(strain gauges)", encoder="encoder:\ncounts turns",
            brake="magnetic brake:\nsmooth, no rubbing", twist="twists very slightly", volt="voltage  ∝  τ",
            x="turns", y="torque τ", down="letting down", up="winding", gap="gap = energy lost\nto coil friction",
            schem="schematic curve: shape only",
            sk_src="Seiko patent US 6,431,746, FIG. 8 (a Seiko wristwatch)", sk_x="hours since full wind",
            sk_y="τ (mN·m)", third="about a third less")
# =====================================================================


def tau_down(n):
    """Schematic letting-down curve over n = 0 .. N_TURNS turns wound (0 = run down)."""
    u = n / N_TURNS
    return 0.25 + 0.55 * (1 - np.exp(-3.5 * u)) + 0.18 * u ** 6


def tau_up(n):
    return tau_down(n) * 1.12 + 0.03 * (n > 0.05)


class Scene09(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.add(vignette())
        wait_until = clock(self)
        head = heading("MEASURING THE TORQUE", "a digression: the torsiometer").to_corner(UL, buff=0.5)
        q = label(TEXT["q"], 0.3, GLOW).to_edge(UP, buff=0.55).shift(RIGHT * 2.4)
        name = label(TEXT["name"], 0.3, WHITE, bold=True).move_to(q)
        src = tag(TEXT["src"], GREY_B, 0.17).to_corner(UR, buff=0.4).shift(DOWN * 0.55)

        # ---------------- the bench (one shaft, left to right)
        turns = ValueTracker(0.0)          # turns let down so far
        rate = ValueTracker(0.0)           # turns per second
        tau = ValueTracker(0.0)            # 0 .. 1, load on the sensor (drives the twist and the meter)
        driver = Mobject()
        driver.add_updater(lambda m, dt: turns.increment_value(dt * rate.get_value()))

        y = BENCH_Y
        shaft = Line([X["barrel"], y, 0], [X["brake"] + 0.6, y, 0]).set_stroke(GREY_B, 5)
        base = Line([X["barrel"] - 1.0, y - 0.95, 0], [X["brake"] + 1.2, y - 0.95, 0]).set_stroke(GREY_D, 6)

        def spinner(r, col, spokes=3):
            g = VGroup(Circle(radius=r).set_stroke(col, 3).set_fill(BG, 1),
                       *[Line(ORIGIN, r * 0.9 * np.array([np.cos(a), np.sin(a), 0])).set_stroke(col, 2)
                         for a in np.arange(spokes) * TAU / spokes])
            return g

        def spin(m, x, ratio=1.0):
            ref = m.copy()
            m.add_updater(lambda mm: mm.become(ref.copy().rotate(-TAU * ratio * turns.get_value()).move_to([x, y, 0])))
            return m

        barrel = spin(spinner(0.62, GLOW, 1).move_to([X["barrel"], y, 0]), X["barrel"])
        jaws = VGroup(*[Polygon([-0.12, 0.72, 0], [0.12, 0.72, 0], [0.08, 0.58, 0], [-0.08, 0.58, 0])
                        .rotate(a, about_point=ORIGIN).set_stroke(GREY_A, 1.5).set_fill(GREY_C, 1)
                        for a in (0, TAU / 3, 2 * TAU / 3)])
        jaws = spin(jaws.move_to([X["barrel"], y, 0]), X["barrel"])

        sw, sh = 1.3, 0.42
        s_body = Rectangle(width=sw, height=sh).set_stroke(GREY_A, 2).set_fill(GREY_E, 1).move_to([X["sensor"], y, 0])
        zig = [[X["sensor"] - 0.3 + 0.075 * i, y + (0.09 if i % 2 else -0.09), 0] for i in range(9)]
        gauge = VMobject().set_points_as_corners(zig).set_stroke(COOL, 2.2)
        gauge.add_updater(lambda m: m.set_stroke(interpolate_color(ManimColor(COOL), ManimColor(GLOW), tau.get_value())))
        twist = Line([X["sensor"] - sw / 2, y - sh / 2, 0], [X["sensor"] + sw / 2, y + sh / 2, 0]).set_stroke(WARM, 2)
        twist.set_stroke(opacity=0)
        tw_ref = Line([X["sensor"], y - sh / 2, 0], [X["sensor"], y + sh / 2, 0])

        def tw_upd(m):
            k = tau.get_value()
            d = 0.35 * k
            m.put_start_and_end_on([X["sensor"] - d, y - sh / 2, 0], [X["sensor"] + d, y + sh / 2, 0])
        twist.add_updater(tw_upd)
        sensor = VGroup(s_body, gauge, twist)

        enc = spin(spinner(0.5, COOL, 12).move_to([X["encoder"], y, 0]), X["encoder"])
        brake = spin(spinner(0.62, WARM, 2).move_to([X["brake"], y, 0]), X["brake"])
        mags = VGroup(*[Rectangle(width=0.22, height=0.32).set_stroke(GREY_A, 1).set_fill(c, 1)
                        .move_to([X["brake"] + dx, y + 0.78, 0]) for dx, c in ((-0.15, RED_D), (0.15, BLUE_D))])
        mags.add(*[m.copy().move_to([m.get_x(), y - 0.78, 0]) for m in mags])

        l_barrel = label(TEXT["barrel"], 0.22, GLOW).move_to([X["barrel"], y - 1.25, 0])
        l_sensor = label(TEXT["sensor"], 0.22, COOL).move_to([X["sensor"], y - 1.3, 0])
        l_enc = label(TEXT["encoder"], 0.22, COOL).move_to([X["encoder"], y - 1.3, 0])
        l_brake = label(TEXT["brake"], 0.22, WARM).move_to([X["brake"], y - 1.3, 0])
        l_twist = label(TEXT["twist"], 0.2, WARM).next_to(s_body, UP, buff=0.18).shift(LEFT * 0.6)

        # meter: a bar proportional to tau, with its label
        m_frame = Rectangle(width=1.1, height=0.2).set_stroke(GREY_B, 1.2).move_to([X["sensor"] + 1.25, y + 0.85, 0])
        m_bar = Rectangle(width=1.1, height=0.2).set_stroke(width=0).set_fill(GLOW, 0.9)
        m_bar.add_updater(lambda m: m.stretch_to_fit_width(max(1e-3, 1.1 * tau.get_value()))
                          .move_to(m_frame.get_left(), aligned_edge=LEFT))
        m_lbl = ftext(TEXT["volt"], 0.4, GLOW).next_to(m_frame, RIGHT, buff=0.15)
        wire = DashedLine(s_body.get_top(), m_frame.get_left(), stroke_width=1.4, color=GREY_B, dash_length=0.05)
        meter = VGroup(wire, m_frame, m_bar, m_lbl)

        bench = VGroup(base, shaft, barrel, jaws, sensor, enc, brake, mags)

        # ---------------- torque vs turns (schematic)
        p = Plot((-6.2, -3.55), 5.6, 2.6, (0, N_TURNS), (0, 1.1))
        pl = VGroup(p.xlabel(TEXT["x"], 0.22), p.ylabel(TEXT["y"], 0.22))
        pl[0].next_to(p.x_axis, DOWN, buff=0.12).align_to(p.x_axis, RIGHT)
        c_down = p.curve(tau_down, N_TURNS, 0, color=COOL, width=3)
        c_up = p.curve(tau_up, 0, N_TURNS, color=WARM, width=3)
        gap = Polygon(*p.pts(tau_up, 0, N_TURNS), *p.pts(tau_down, N_TURNS, 0)).set_stroke(width=0).set_fill(GREY_B, 0.3)
        l_down = label(TEXT["down"], 0.2, COOL).next_to(p.c2p(4.6, tau_down(4.6)), DOWN, buff=0.12)
        l_up = label(TEXT["up"], 0.2, WARM).next_to(p.c2p(2.4, tau_up(2.4)), UP, buff=0.1)
        l_gap = label(TEXT["gap"], 0.2, GREY_A).next_to(p, RIGHT, buff=0.1).shift(UP * 0.4)
        schem = tag(TEXT["schem"], GLOW, 0.17).next_to(p.x_axis, DOWN, buff=0.12).align_to(p.x_axis, LEFT)

        # ---------------- Seiko's measurement
        sk = Plot((1.6, -3.1), 4.4, 2.1, (0, 45), (0, 3.4))
        sk_t = VGroup(*[sk.xtick(h, f"{h}", 0.2) for h in F.SKO_HOURS], *[sk.ytick(v, f"{v}", 0.2) for v in (1, 2, 3)])
        sk_l = VGroup(label(TEXT["sk_x"], 0.2).next_to(sk.x_axis, DOWN, buff=0.34).align_to(sk.x_axis, RIGHT),
                      label(TEXT["sk_y"], 0.2).next_to(sk.y_axis, UP, buff=0.08).align_to(sk.y_axis, LEFT))
        sk_src = tag(TEXT["sk_src"], GREY_B, 0.16).next_to(sk, UP, buff=0.3).align_to(sk.y_axis, LEFT)
        pts = [sk.c2p(h, t) for h, t in zip(F.SKO_HOURS, F.SKO_MNM)]
        dots = VGroup(*[Dot(pt, radius=0.07, color=GLOW) for pt in pts])
        vals = VGroup(*[label(f"{t:.2f}", 0.22, GLOW).next_to(pt, UR, buff=0.06) for t, pt in zip(F.SKO_MNM, pts)])
        joins = VGroup(*[DashedLine(a, b, stroke_width=1.6, color=GLOW, dash_length=0.06) for a, b in zip(pts, pts[1:])])
        third = label(TEXT["third"] + f"  (−{F.SKO_DROP_PCT:.0f}%)", 0.24, WARM, bold=True)
        third.next_to(pts[-1], DOWN, buff=0.3).shift(LEFT * 0.4)

        cur = curtain()
        self.add(cur, driver)

        # ---------------------------------------------------------- timeline
        self.play(cur.animate.set_fill(opacity=0), run_time=FADE_IN, rate_func=smooth)
        self.remove(cur)
        wait_until(HEAD_AT)
        self.play(FadeIn(head), FadeIn(q), run_time=0.8)
        wait_until(BENCH_AT)
        self.play(FadeOut(q), FadeIn(name), FadeIn(src), FadeIn(bench), run_time=1.0)
        wait_until(CHUCK_AT)
        self.play(FadeIn(l_barrel), Indicate(jaws, color=WHITE, scale_factor=1.1), run_time=1.0)
        self.play(rate.animate.set_value(LET_DOWN_RATE), tau.animate.set_value(0.75), run_time=1.5)
        wait_until(BRAKE_AT)
        self.play(FadeIn(l_brake), Indicate(mags, color=WHITE, scale_factor=1.1), run_time=1.0)
        wait_until(SENSOR_AT)
        self.play(FadeIn(l_sensor), Indicate(s_body, color=WHITE, scale_factor=1.15), run_time=1.0)
        wait_until(TWIST_AT)
        twist.set_stroke(opacity=1)
        self.play(FadeIn(l_twist), tau.animate.set_value(0.95), run_time=1.0)
        self.play(tau.animate.set_value(0.75), run_time=1.0)
        wait_until(VOLT_AT)
        self.play(FadeIn(meter), run_time=0.8)
        wait_until(ENCODER_AT)
        self.play(FadeIn(l_enc), Indicate(enc, color=WHITE, scale_factor=1.1), run_time=1.0)
        wait_until(CURVE_AT)
        self.play(FadeIn(p), FadeIn(pl), FadeIn(schem), run_time=0.7)
        self.play(Create(c_down), FadeIn(l_down), tau.animate.set_value(0.25), run_time=3.0, rate_func=linear)
        wait_until(WIND_AT)
        self.play(Create(c_up), FadeIn(l_up), run_time=2.5, rate_func=linear)
        wait_until(GAP_AT)
        self.play(FadeIn(gap), FadeIn(l_gap), run_time=0.9)
        wait_until(SEIKO_AT)
        self.play(rate.animate.set_value(0.0), FadeIn(sk), FadeIn(sk_t), FadeIn(sk_l), FadeIn(sk_src), run_time=1.0)
        for i, t in enumerate(SEIKO_PTS):
            wait_until(t)
            anims = [FadeIn(dots[i], scale=1.6), FadeIn(vals[i])]
            if i:
                anims.append(Create(joins[i - 1]))
            self.play(*anims, run_time=0.6)
        wait_until(THIRD_AT)
        self.play(FadeIn(third, shift=UP * 0.1), run_time=0.6)

        wait_until(FINAL_HOLD_UNTIL)
        cur.set_fill(opacity=0)
        self.add(cur)
        self.play(cur.animate.set_fill(opacity=1), run_time=FADE_OUT)
