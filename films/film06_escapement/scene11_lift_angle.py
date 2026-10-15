"""Film 6, scene 11 - "The lift angle": how a timing machine reads amplitude by ear.
phi(t) = Theta sin(omega t) through one center crossing, with the lift window
|phi| <= 22 deg (ETA's 44 deg lift angle for the 6497). Slowed right down, a tick
is three sounds: unlock, impulse, drop (event timings from Petrangeli's model,
played 150x slower; written to scene11_lift_angle.sfx.txt). The machine times
unlock to drop: about 10.4 ms at 270 deg; a smaller swing (220 deg, dashed)
takes longer. Theta = lift / (2 sin(pi f Delta t)). Enter 52 deg instead of 44 and
the same watch reads 319 deg; the rate is unchanged, since it comes from the
spacing of the ticks.

Build (render + voice + mux):   python build.py 6/scene11_lift_angle
Render only (quick preview):    PYTHONPATH=.:films/film06_escapement manim -ql films/film06_escapement/scene11_lift_angle.py Scene11
Narration lines and their start times live in scene11_lift_angle.voice.txt. Numbers from figures.py.
"""
from manim import *
import prev  # noqa: F401  (first: Film 4 and 5 helpers on the path)
import ui6  # noqa: F401  (extra subscripts)
from ui6 import fmark, write_sfx
import figures as F
from iso import Plot
from movement import vignette, BG, GLOW
from ui import label, heading, tag, curtain, clock, WARM, COOL

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds.
# Keep the timeline roughly in step with scene11_lift_angle.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 1.0
LISTEN_AT = 1.2                       # "How do you measure the amplitude without seeing the balance? Listen."
PLOT_AT = 6.1                         # "The roller jewel touches the fork only while ..."
BAND_AT = 10.0                        # "... a small arc around center, called the lift angle."
ETA_AT = 14.2                         # "ETA gives forty-four degrees for the sixty-four ninety-seven."
PARTS_AT = 19.2                       # "Slowed right down, a tick has three parts ..."
PART_AT = (22.0, 23.1, 24.3)          # "... the unlock, the impulse, and the drop."
DEMO_AT = 25.5                        # the three sounds, slowed (in the 2.5 s gap of the narration)
GAP_AT = 28.0                         # "The machine times the gap from unlock to drop."
DT_AT = 31.2                          # "At two hundred seventy degrees, it's about ten milliseconds."
SMALL_AT = 36.4                       # "A big swing crosses the lift arc quickly, and a small one slowly ..."
FORMULA_AT = 40.6                     # "... so the gap gives the amplitude."
WRONG_AT = 44.1                       # "Enter the wrong lift angle, say fifty-two degrees ..."
WRONG_READ_AT = 47.6                  # "... and the same watch reads three hundred nineteen."
RATE_AT = 50.4                        # "The rate is still right ..."
FINAL_HOLD_UNTIL = 59.2               # the last line ends about 57.2 s
FADE_OUT = 1.5

SLOW = 150                            # slow-motion factor for the sound demo
SOUNDS = (("wood", 1.0), ("click", 0.8), ("bell", 1.0))     # unlock, impulse, drop
T_MS = 100.0                          # plot spans -T_MS .. +T_MS milliseconds around center
LIFT = F.LIFT_6497 / F.DEG            # 44
TEXT = dict(listen="listen", q="amplitude, without seeing the balance?",
            t="time (ms)", phi="balance angle φ", lift="lift window:  ±{:.0f}°".format(LIFT / 2),
            eta="lift angle {:.0f}°: ETA technical communication, 6497".format(LIFT),
            parts=("unlock", "impulse", "drop"),
            slow="slowed {}×:  timings from Petrangeli's model (2017)".format(SLOW),
            dt="Δt ≈ {:.1f} ms at 270°".format(F.DT_6497 * 1e3), big="270°", small="220°",
            formula="Θ = θ<sub>lift</sub> / (2 sin(π f Δt))",
            right="lift entered {:.0f}°:   Θ = {:.0f}°".format(LIFT, F.ROUND_TRIP),
            wrong="lift entered {:.0f}°:   Θ = {:.0f}°".format(F.WRONG_LIFT / F.DEG, F.WRONG_AMP),
            rate="rate unchanged:  it comes from the spacing of the ticks")
# =====================================================================


class Scene11(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.add(vignette())
        wait_until = clock(self)
        head = heading("THE LIFT ANGLE", "how a timing machine reads amplitude").to_corner(UL, buff=0.5)

        # ear: three arcs and a question
        arcs = VGroup(*[Arc(radius=r, start_angle=-0.6, angle=1.2).set_stroke(GLOW, 3) for r in (0.18, 0.32, 0.46)])
        listen = VGroup(arcs, label(TEXT["listen"], 0.34, GLOW, bold=True).next_to(arcs, RIGHT, buff=0.15))
        q = label(TEXT["q"], 0.28, GREY_A)
        ear = VGroup(listen, q).arrange(DOWN, buff=0.2).move_to([3.6, 2.3, 0])

        # phi(t) through one center crossing
        w = TAU * F.F_6497
        phi = lambda amp: (lambda tm: amp * np.sin(w * tm / 1000.0))
        a_big, a_small = F.AMP / F.DEG, F.AMP_LOW / F.DEG
        p = Plot((-6.3, -3.0), 7.0, 4.6, (-T_MS, T_MS), (-300, 300))
        zero = DashedLine(p.c2p(-T_MS, 0), p.c2p(T_MS, 0), stroke_width=1, color=GREY_D)
        ticks = VGroup(*[p.xtick(x, f"{x:.0f}", 0.2) for x in (-100, -50, 0, 50, 100)],
                       *[p.ytick(y, f"{y:+.0f}°".replace("+0", "0"), 0.2) for y in (-270, 0, 270)])
        axl = VGroup(label(TEXT["t"], 0.22).next_to(p.x_axis, DOWN, buff=0.38).align_to(p.x_axis, RIGHT),
                     label(TEXT["phi"], 0.22).next_to(p.y_axis, UP, buff=0.08).align_to(p.y_axis, LEFT))
        c_big = p.curve(phi(a_big), -T_MS, T_MS, color=COOL, width=3)
        c_small = DashedVMobject(p.curve(phi(a_small), -T_MS, T_MS, color=WARM, width=2.5), num_dashes=50)
        l_big = label(TEXT["big"], 0.22, COOL).next_to(p.c2p(60, phi(a_big)(60)), UL, buff=0.06)
        l_small = label(TEXT["small"], 0.22, WARM).next_to(p.c2p(60, phi(a_small)(60)), DR, buff=0.06)
        band = Rectangle(width=p.c2p(T_MS, 0)[0] - p.c2p(-T_MS, 0)[0],
                         height=p.c2p(0, LIFT / 2)[1] - p.c2p(0, -LIFT / 2)[1])
        band.set_stroke(GLOW, 1).set_fill(GLOW, 0.22).move_to(p.c2p(0, 0))
        l_band = label(TEXT["lift"], 0.22, GLOW).next_to(band, UP, buff=0.06).align_to(band, LEFT).shift(RIGHT * 0.1)
        eta = tag(TEXT["eta"], GREY_B, 0.17).next_to(l_band, UP, buff=0.12).align_to(l_band, LEFT)

        # the gap at 270 (and at 220)
        def gap_marks(dt_s, col, y):
            h = dt_s * 1000 / 2
            a, b = p.c2p(-h, y), p.c2p(h, y)
            return VGroup(DashedLine(p.c2p(-h, -LIFT / 2), a, stroke_width=1.2, color=col, dash_length=0.04),
                          DashedLine(p.c2p(h, LIFT / 2), b, stroke_width=1.2, color=col, dash_length=0.04),
                          DoubleArrow(a, b, buff=0, stroke_width=2.5, tip_length=0.1, color=col))
        g_big = gap_marks(F.DT_6497, COOL, -60)
        l_dt = label(TEXT["dt"], 0.24, COOL, bold=True).next_to(g_big[2], RIGHT, buff=0.15)
        g_small = gap_marks(F.DT_6497_LOW, WARM, -150)

        # the slowed tick: three parts on a bar, lit as the sounds play
        names = list(F.GP_PHASES)
        bw = 4.2
        x0 = 1.7
        segs, starts, t_acc = VGroup(), {}, 0.0
        cols = dict(unlock=COOL, **{"impulse I": WARM, "impulse II": WARM}, drop=GLOW)
        for nm in names:
            dw = bw * F.GP_PHASES[nm] / F.GP_ACTIVE
            seg = Rectangle(width=dw, height=0.32).set_stroke(BG, 1.5).set_fill(cols[nm], 0.25)
            seg.move_to([x0 + bw * t_acc / F.GP_ACTIVE + dw / 2, 0.9, 0])
            segs.add(seg)
            starts[nm] = t_acc
            t_acc += F.GP_PHASES[nm]
        part_lbls = VGroup(label(TEXT["parts"][0], 0.22, COOL).next_to(segs[0], DOWN, buff=0.12),
                           label(TEXT["parts"][1], 0.22, WARM).next_to(VGroup(segs[1], segs[2]), DOWN, buff=0.12),
                           label(TEXT["parts"][2], 0.22, GLOW).next_to(segs[3], DOWN, buff=0.12))
        slow = tag(TEXT["slow"], GLOW, 0.17).next_to(segs, UP, buff=0.2).align_to(segs, LEFT)
        cursor = Line(UP * 0.25, DOWN * 0.25).set_stroke(WHITE, 3).move_to(segs.get_left())
        # sound times (video): unlock begins, impulse begins, drop (end of impulse II)
        snd_ms = (0.0, starts["impulse I"], starts["drop"])
        snd_t = [DEMO_AT + s * SLOW for s in snd_ms]
        write_sfx(__file__, [(t, snd, lvl) for t, (snd, lvl) in zip(snd_t, SOUNDS)])

        # formula and readouts, right column
        formula = fmark(TEXT["formula"], 0.5).move_to([3.85, -0.4, 0])
        right = label(TEXT["right"], 0.26, COOL).move_to([3.85, -1.3, 0])
        wrong = label(TEXT["wrong"], 0.26, WARM, bold=True).next_to(right, DOWN, buff=0.25).align_to(right, LEFT)
        rate = label(TEXT["rate"], 0.22, WHITE).next_to(wrong, DOWN, buff=0.4).align_to(right, LEFT)

        cur = curtain()
        self.add(cur)

        # ---------------------------------------------------------- timeline
        self.play(cur.animate.set_fill(opacity=0), run_time=FADE_IN, rate_func=smooth)
        self.remove(cur)
        wait_until(LISTEN_AT)
        self.play(FadeIn(head), FadeIn(q), run_time=0.8)
        wait_until(LISTEN_AT + 3.4)
        self.play(LaggedStart(*[Create(a) for a in arcs], lag_ratio=0.3), FadeIn(listen[1]), run_time=0.8)
        wait_until(PLOT_AT)
        self.play(FadeIn(p), FadeIn(zero), FadeIn(ticks), FadeIn(axl), run_time=0.8)
        self.play(Create(c_big), FadeIn(l_big), run_time=1.5)
        wait_until(BAND_AT)
        self.play(FadeIn(band), FadeIn(l_band), run_time=0.8)
        wait_until(ETA_AT)
        self.play(FadeIn(eta), run_time=0.7)

        wait_until(PARTS_AT)
        self.play(FadeOut(ear), FadeIn(segs), FadeIn(slow), run_time=0.8)
        for i, t in enumerate(PART_AT):
            wait_until(t)
            group = (segs[0],) if i == 0 else ((segs[1], segs[2]) if i == 1 else (segs[3],))
            self.play(*[s.animate.set_fill(opacity=0.85) for s in group], FadeIn(part_lbls[i]), run_time=0.5)
        wait_until(DEMO_AT - 0.4)
        self.play(*[s.animate.set_fill(opacity=0.25) for s in segs], FadeIn(cursor), run_time=0.4)
        lit = [VGroup(segs[0]), VGroup(segs[1], segs[2]), VGroup(segs[3])]
        for i, t in enumerate(snd_t):
            wait_until(t)
            x_to = segs.get_left()[0] + bw * (snd_ms[i + 1] if i < 2 else F.GP_ACTIVE) / F.GP_ACTIVE
            dur = (snd_t[i + 1] - t) if i < 2 else F.GP_PHASES["drop"] * SLOW
            self.play(cursor.animate.set_x(x_to), lit[i].animate.set_fill(opacity=0.85),
                      run_time=dur, rate_func=linear)

        wait_until(GAP_AT)
        self.play(Create(g_big), run_time=0.8)
        wait_until(DT_AT)
        self.play(FadeIn(l_dt), run_time=0.6)
        wait_until(SMALL_AT)
        self.play(Create(c_small), FadeIn(l_small), run_time=1.2)
        self.play(Create(g_small), run_time=0.8)
        wait_until(FORMULA_AT)
        self.play(FadeIn(formula, shift=UP * 0.1), run_time=0.8)
        wait_until(WRONG_AT)
        self.play(FadeIn(right), run_time=0.6)
        wait_until(WRONG_READ_AT)
        self.play(FadeIn(wrong, shift=UP * 0.1), run_time=0.6)
        wait_until(RATE_AT)
        self.play(FadeIn(rate), run_time=0.6)

        wait_until(FINAL_HOLD_UNTIL)
        cur.set_fill(opacity=0)
        self.add(cur)
        self.play(cur.animate.set_fill(opacity=1), run_time=FADE_OUT)
