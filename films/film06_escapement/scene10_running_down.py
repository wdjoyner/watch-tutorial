"""Film 6, scene 10 - "Running down": scene 07's balance sheet, with the
escapement's energy per cycle E_in following the mainspring torque. ETA does
not publish the 6497's torque curve, so the scene borrows the measured curve
of Seiko's patent (FIG. 8, a Seiko wristwatch): 27, 23 and 18 g cm at 0, 20 and
40 hours. Applied to our REPRESENTATIVE balance, the crossing slides from
270 deg to about 242 and 205 deg. A lower amplitude changes the rate (Film 5).
Then old oil: the viscous loss grows (ILLUSTRATIVE factor, tagged), the loss
curve steepens, and the amplitude sinks at full wind.

Build (render + voice + mux):   python build.py 6/scene10_running_down
Render only (quick preview):    PYTHONPATH=.:films/film06_escapement manim -ql films/film06_escapement/scene10_running_down.py Scene10
Narration lines and their start times live in scene10_running_down.voice.txt. Numbers from figures.py.
"""
from manim import *
import prev  # noqa: F401  (first: Film 4 and 5 helpers on the path)
from ui6 import fmark
import figures as F
from iso import Plot
from movement import vignette, BG, GLOW
from ui import label, heading, tag, curtain, clock, WARM, COOL

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds.
# Keep the timeline roughly in step with scene10_running_down.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 1.0
PLOT_AT = 1.2                         # "ETA doesn't publish ... so let's borrow Seiko's."
TAG_AT = 4.5
DROP_AT = 13.0                        # "... as the mainspring runs down, the flat line drops."
SLIDE_AT = 16.9                       # "The crossing slides left."
H20_AT = 23.6                         # "... to about two hundred forty after twenty hours ..."
H40_AT = 27.6                         # "... and two hundred five after forty."
CHAIN_AT = 31.2                       # "A lower amplitude means a different rate ..."
FILM5_AT = 37.3                       # "That closes the chain from Film five."
OIL_AT = 40.9                         # "Old oil does the same from the other side ..."
STEEP_AT = 44.0                       # "... the loss curve steepens, and the amplitude sinks."
TIMER_AT = 47.6                       # "A watchmaker sees it on the timing machine ..."
FINAL_HOLD_UNTIL = 54.4               # the last line ends about 52.4 s
FADE_OUT = 1.5

THETA_MAX, Y_MAX = 360.0, 0.40        # axes: degrees, microjoules (as in scene 07)
OLD_OIL = 1.6                         # ILLUSTRATIVE: viscous losses multiplied by this for old oil
TEXT = dict(x="amplitude Θ", y="energy per cycle (μJ)", loss="lost:  W<sub>loss</sub>(Θ)",
            ein="E<sub>in</sub>  ∝  mainspring torque", src="torque curve: Seiko patent US 6,431,746, FIG. 8 "
            "(a Seiko wristwatch);  balance representative",
            no_eta="ETA does not publish the 6497's torque curve",
            hours=("full wind", "after 20 h", "after 40 h"),
            chain=("lower amplitude", "isochronism + escapement error", "a different rate"),
            film5="the chain from Film 5", oil="old oil:  viscous losses × {:.1f}  (illustrative)",
            timer="seen on the timing machine first")
# =====================================================================


class Scene10(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.add(vignette())
        wait_until = clock(self)
        head = heading("RUNNING DOWN", "the amplitude follows the mainspring").to_corner(UL, buff=0.5)

        uj, D = 1e6, F.DEG
        frac = ValueTracker(1.0)          # E_in as a fraction of its full-wind value
        oil = ValueTracker(1.0)           # multiplier on the viscous loss

        def loss(d, k=1.0):
            return (4 * F.MU_COU * d * D + k * np.pi * F.MU_VIS * F.OMEGA0 * (d * D) ** 2) * uj

        def star():
            return F.theta_star(frac.get_value() * F.E_IN, F.MU_COU, oil.get_value() * F.MU_VIS, F.OMEGA0) / D

        p = Plot((-5.6, -3.2), 8.2, 5.0, (0, THETA_MAX), (0, Y_MAX))
        ticks = VGroup(*[p.xtick(d, f"{d:.0f}°", 0.2) for d in (90, 180, 270, 360)],
                       *[p.ytick(y, f"{y:.1f}", 0.2) for y in (0.1, 0.2, 0.3, 0.4)])
        axl = VGroup(p.xlabel(TEXT["x"], 0.24), p.ylabel(TEXT["y"], 0.24))
        def x_end():                      # stop the loss curve at the top of the plot
            d = np.linspace(0, THETA_MAX, 721)
            return d[loss(d, oil.get_value()) <= Y_MAX][-1]

        c_loss = p.curve(loss, 0, THETA_MAX, color=WARM, width=4)
        c_loss.add_updater(lambda m: m.become(p.curve(lambda d: loss(d, oil.get_value()), 0, x_end(), color=WARM, width=4)))
        l_loss = fmark(TEXT["loss"], 0.42, WARM).next_to(p.c2p(THETA_MAX, loss(THETA_MAX)), RIGHT, buff=0.1)
        l_loss.add_updater(lambda m: m.next_to(p.c2p(x_end(), loss(x_end(), oil.get_value())), RIGHT, buff=0.1))
        c_in = always_redraw(lambda: Line(p.c2p(0, frac.get_value() * F.E_IN * uj),
                                          p.c2p(THETA_MAX, frac.get_value() * F.E_IN * uj)).set_stroke(GLOW, 4))
        l_in = fmark(TEXT["ein"], 0.38, GLOW)
        l_in.add_updater(lambda m: m.next_to(p.c2p(THETA_MAX, frac.get_value() * F.E_IN * uj), RIGHT, buff=0.1))
        ghost = DashedLine(p.c2p(0, F.E_IN * uj), p.c2p(THETA_MAX, F.E_IN * uj), stroke_width=1.5, color=GLOW)
        ghost.set_stroke(opacity=0.45)

        dot = always_redraw(lambda: Dot(p.c2p(star(), frac.get_value() * F.E_IN * uj), radius=0.1, color=WHITE))
        drop = always_redraw(lambda: DashedLine(p.c2p(star(), frac.get_value() * F.E_IN * uj), p.c2p(star(), 0),
                                                stroke_width=1.5, color=WHITE))
        readout = always_redraw(lambda: label(f"Θ* ≈ {star():.0f}°", 0.3, WHITE, bold=True)
                                .next_to(p.c2p(star(), 0), UP, buff=0.12).shift(LEFT * 0.62))
        hour = label(TEXT["hours"][0], 0.26, GLOW, bold=True).move_to(p.c2p(70, 0.33))

        no_eta = label(TEXT["no_eta"], 0.24, GREY_A).next_to(head, DOWN, buff=0.3, aligned_edge=LEFT)
        src = tag(TEXT["src"], GREY_B, 0.17).to_corner(UR, buff=0.4)

        chain = VGroup(*[label(t, 0.24, c) for t, c in zip(TEXT["chain"], (WHITE, GREY_A, WARM))])
        chain.arrange(RIGHT, buff=0.55)
        arrows = VGroup(*[Arrow(a.get_right(), b.get_left(), buff=0.08, stroke_width=2.5, tip_length=0.12, color=GREY_B)
                          for a, b in zip(chain, chain[1:])])
        chain_g = VGroup(chain, arrows).move_to([0.0, 2.1, 0])
        chain_box = SurroundingRectangle(chain_g, buff=0.18, corner_radius=0.1).set_stroke(GREY_B, 1.2).set_fill(BG, 0.9)
        f5 = tag(TEXT["film5"], WARM, 0.2).next_to(chain_box, DOWN, buff=0.15)
        oil_t = tag(TEXT["oil"].format(OLD_OIL), GLOW, 0.2).next_to(src, DOWN, buff=0.15).align_to(src, RIGHT)
        timer = label(TEXT["timer"], 0.26, GREY_A).move_to(p.c2p(80, 0.33)).shift(DOWN * 0.45)

        cur = curtain()
        self.add(cur)

        # ---------------------------------------------------------- timeline
        self.play(cur.animate.set_fill(opacity=0), run_time=FADE_IN, rate_func=smooth)
        self.remove(cur)
        wait_until(PLOT_AT)
        self.play(FadeIn(head), FadeIn(no_eta), FadeIn(p), FadeIn(ticks), FadeIn(axl),
                  FadeIn(c_loss), FadeIn(l_loss), FadeIn(c_in), FadeIn(l_in), run_time=1.0)
        wait_until(TAG_AT)
        self.play(FadeIn(src), FadeIn(dot), FadeIn(drop), FadeIn(readout), FadeIn(hour), run_time=0.8)
        wait_until(DROP_AT)
        self.add(ghost)
        self.play(Indicate(l_in, color=WHITE), run_time=1.0)
        wait_until(SLIDE_AT)
        self.play(FadeOut(no_eta), run_time=0.5)
        wait_until(H20_AT - 1.6)
        h1 = label(TEXT["hours"][1], 0.26, GLOW, bold=True).move_to(hour)
        self.play(frac.animate.set_value(F.SKO_FRAC[1]), Transform(hour, h1), run_time=1.6)
        wait_until(H40_AT - 1.4)
        h2 = label(TEXT["hours"][2], 0.26, GLOW, bold=True).move_to(hour)
        self.play(frac.animate.set_value(F.SKO_FRAC[2]), Transform(hour, h2), run_time=1.6)
        wait_until(CHAIN_AT)
        self.play(FadeIn(chain_box), FadeIn(chain[0]), run_time=0.6)
        self.play(GrowArrow(arrows[0]), FadeIn(chain[1]), run_time=0.6)
        self.play(GrowArrow(arrows[1]), FadeIn(chain[2]), run_time=0.6)
        wait_until(FILM5_AT)
        self.play(FadeIn(f5), run_time=0.6)

        wait_until(OIL_AT)
        h0 = label(TEXT["hours"][0], 0.26, GLOW, bold=True).move_to(hour)
        self.play(FadeOut(VGroup(chain_box, chain, arrows, f5)), frac.animate.set_value(1.0), Transform(hour, h0),
                  run_time=1.2)
        self.play(FadeIn(oil_t), run_time=0.6)
        wait_until(STEEP_AT)
        self.play(oil.animate.set_value(OLD_OIL), run_time=2.0)
        wait_until(TIMER_AT)
        self.play(FadeIn(timer), run_time=0.7)

        wait_until(FINAL_HOLD_UNTIL)
        cur.set_fill(opacity=0)
        self.add(cur)
        self.play(cur.animate.set_fill(opacity=1), run_time=FADE_OUT)
