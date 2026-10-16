"""Film 6, scene 04 - "Smooth swings and sudden kicks": the hybrid model.
The equation is built term by term (inertia, damping, hairspring, cubic term =
a train of kicks). Below it, the chapter's scaled run (friction and kicks
exaggerated): the angle stays continuous with a small kink at each center
crossing, while the speed jumps by J / I there. Then the kick's energy,
Delta E = J phi'- + J^2 / 2I ~ J phi'-, largest where the balance moves fastest:
a kick halfway out does 87 % as much.

Build (render + voice + mux):   python build.py 6/scene04_kicks
Render only (quick preview):    PYTHONPATH=.:films/film06_escapement manim -ql films/film06_escapement/scene04_kicks.py Scene04
Narration lines and their start times live in scene04_kicks.voice.txt. Numbers from figures.py.
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
# Keep the timeline roughly in step with scene04_kicks.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 1.0
HEAD_AT = 1.2                         # "we treat each impulse as instantaneous"
LHS_AT = (11.0, 12.1, 13.2, 14.4)      # inertia, damping, the hairspring, its small cubic term
RHS_AT = 18.0                         # "a sudden kick, an angular impulse J sub k"
PLOTS_AT = 19.3                       # the angle stays put, the speed jumps (drawn as the line is spoken)
JUMP_AT = 24.0                        # "...and the speed jumps by J over I"
HYBRID_AT = 29.4                      # "mathematicians call this a hybrid system"
ENERGY_AT = 33.6                      # "A kick adds energy J times the speed just before it."
CENTER_AT = 40.0                      # "...where the balance moves fastest, at the center"
HALF_AT = 43.5                        # "Halfway out, it does eighty-seven percent as much."
FINAL_HOLD_UNTIL = 49.0               # the last line ends about 47.0 s
FADE_OUT = 1.5

# --- the run (chapter's scaled example, EXAGGERATED) ---------------------
CYCLES, N = 3, 400
RUN_MU_VIS, RUN_MU_COU = 1 / 6, 0.1     # EXAGGERATED further than the chapter's run (Q 6), so the jumps show
RUN_E_IN = 11.1                       # energy per cycle that holds this run at about 4.24
PLOT_X, PLOT_W, PLOT_H = -6.2, 7.0, 1.3
ANGLE_Y, SPEED_Y = 0.65, -1.15        # vertical centers of the two plots (all above the caption band)
TEXT = dict(lhs=("I φ″", "+ c φ′", "+ κ φ", "+ β φ³"), eq="=", rhs="Σ Jₖ δ(t − tₖ)",
            under=("inertia", "damping", "hairspring", "cubic term", "kicks at times tₖ"),
            angle="angle φ", speed="speed φ′  (the kicks)", time="time", stays="the angle is continuous",
            jumps="the speed jumps by J / I", hybrid="hybrid system: smooth flow + sudden jumps",
            exag="friction and kicks exaggerated", energy="ΔE = J φ′₋ + J² / 2I  ≈  J φ′₋",
            fastest="most energy per kick where it is fastest", center="center", half="halfway out",
            pct="{:.0f}%", sp="speed")
# =====================================================================


class Scene04(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.add(vignette())
        wait_until = clock(self)
        head = heading("SMOOTH SWINGS, SUDDEN KICKS", "the hybrid model").to_corner(UL, buff=0.5)

        # the equation, term by term
        parts = [ftext(s, 0.62) for s in TEXT["lhs"]] + [ftext(TEXT["eq"], 0.62), ftext(TEXT["rhs"], 0.62, GLOW)]
        eq = VGroup(*parts).arrange(RIGHT, buff=0.22).move_to([0.4, 2.55, 0])
        unders = VGroup()
        for p, u, c in zip([*parts[:4], parts[5]], TEXT["under"], (GREY_B,) * 4 + (GLOW,)):
            unders.add(label(u, 0.2, c).next_to(p, DOWN, buff=0.14))

        # the run: angle and speed against time
        th0 = F.theta_star(RUN_E_IN, RUN_MU_COU, RUN_MU_VIS, 1.0)
        path, _ = F.limit_cycle_run(th0, cycles=CYCLES, n=N, e_in=RUN_E_IN, mu_cou=RUN_MU_COU, mu_vis=RUN_MU_VIS)
        T = len(path)
        ts = np.arange(T) / N                                   # in cycles
        amax = 1.12 * max(abs(path[:, 0]).max(), abs(path[:, 1]).max())
        pa = Plot((PLOT_X, ANGLE_Y - PLOT_H / 2), PLOT_W, PLOT_H, (0, CYCLES), (-amax, amax))
        ps = Plot((PLOT_X, SPEED_Y - PLOT_H / 2), PLOT_W, PLOT_H, (0, CYCLES), (-amax, amax))
        zero_a = DashedLine(pa.c2p(0, 0), pa.c2p(CYCLES, 0), stroke_width=1, color=GREY_D)
        zero_s = DashedLine(ps.c2p(0, 0), ps.c2p(CYCLES, 0), stroke_width=1, color=GREY_D)
        ang = VMobject().set_points_as_corners([pa.c2p(t, p) for t, p in zip(ts, path[:, 0])]).set_stroke(COOL, 3)
        spd = VMobject().set_points_as_corners([ps.c2p(t, v) for t, v in zip(ts, path[:, 1])]).set_stroke(WARM, 3)
        kicks = [i for i in range(1, T) if path[i - 1, 0] * path[i, 0] < 0]
        marks = VGroup(*[DashedLine(pa.c2p(ts[i], -amax), ps.c2p(ts[i], amax), stroke_width=1.2, color=GLOW,
                                    dash_length=0.06) for i in kicks])
        jump_dots = VGroup(*[Dot(ps.c2p(ts[i], path[i, 1]), radius=0.05, color=GLOW) for i in kicks])
        labs = VGroup(label(TEXT["angle"], 0.22, COOL).next_to(pa.y_axis, UP, buff=0.06).align_to(pa.y_axis, LEFT),
                      label(TEXT["speed"], 0.22, WARM).next_to(ps.y_axis, UP, buff=0.06).align_to(ps.y_axis, LEFT),
                      label(TEXT["time"], 0.2).next_to(ps.x_axis, DOWN, buff=0.1).align_to(ps.x_axis, RIGHT))
        stays = label(TEXT["stays"], 0.22, COOL).next_to(pa.c2p(CYCLES, 0), RIGHT, buff=0.25)
        jumps = label(TEXT["jumps"], 0.22, WARM).next_to(ps.c2p(CYCLES, 0), RIGHT, buff=0.25)
        exag = tag(TEXT["exag"], GLOW, 0.18).next_to(ps.x_axis, DOWN, buff=0.15).align_to(ps.x_axis, LEFT)
        hybrid = label(TEXT["hybrid"], 0.3, GLOW, bold=True).next_to(eq, DOWN, buff=0.45)
        plots = VGroup(pa, ps, zero_a, zero_s, labs)

        # the kick's energy: speed across the swing, kick at the center and halfway out
        px0 = 1.9
        pe = Plot((px0, -2.15), 4.0, 1.8, (-1.05, 1.05), (0, 1.15))
        prof = pe.curve(lambda u: np.sqrt(max(0.0, 1 - u * u)), -1, 1, color=WARM, width=3)
        e_eq = ftext(TEXT["energy"], 0.5).next_to(pe, UP, buff=0.85).align_to(pe, LEFT)
        e_lbl = label(TEXT["sp"], 0.2, WARM).next_to(pe.y_axis, UP, buff=0.06)
        ax_lbls = VGroup(label("−Θ", 0.2).next_to(pe.c2p(-1, 0), DOWN, buff=0.1),
                         label("0", 0.2).next_to(pe.c2p(0, 0), DOWN, buff=0.1),
                         label("+Θ", 0.2).next_to(pe.c2p(1, 0), DOWN, buff=0.1))
        k_c = Arrow(pe.c2p(0, 0), pe.c2p(0, 1.0), buff=0, stroke_width=5, color=GLOW, tip_length=0.16)
        k_h = Arrow(pe.c2p(0.5, 0), pe.c2p(0.5, F.KICK_AT_HALF), buff=0, stroke_width=5, color=GLOW, tip_length=0.16)
        t_c = label(f'{TEXT["center"]}: 100%', 0.2, GLOW).next_to(k_c, UP, buff=0.06).shift(LEFT * 0.35)
        t_h = label(f'{TEXT["half"]}: ' + TEXT["pct"].format(F.KICK_AT_HALF * 100), 0.2, GLOW).next_to(k_h, RIGHT, buff=0.08)
        fastest = label(TEXT["fastest"], 0.22, GREY_A).next_to(e_eq, DOWN, buff=0.15).align_to(e_eq, LEFT)

        cur = curtain()
        self.add(cur)

        # ---------------------------------------------------------- timeline
        self.play(cur.animate.set_fill(opacity=0), run_time=FADE_IN, rate_func=smooth)
        self.remove(cur)
        wait_until(HEAD_AT)
        self.play(FadeIn(head), run_time=0.8)
        for k, t in enumerate(LHS_AT):
            wait_until(t)
            self.play(FadeIn(parts[k], shift=UP * 0.1), FadeIn(unders[k]), run_time=0.6)
        wait_until(RHS_AT)
        self.play(FadeIn(parts[4]), FadeIn(parts[5], shift=LEFT * 0.1), FadeIn(unders[4]), run_time=0.8)
        wait_until(PLOTS_AT)
        self.play(FadeIn(plots), FadeIn(exag), run_time=0.7)
        self.play(Create(ang), Create(spd), Create(marks), run_time=3.0, rate_func=linear)
        self.play(FadeIn(stays), run_time=0.5)
        wait_until(JUMP_AT)
        self.play(FadeIn(jumps), LaggedStart(*[FadeIn(d, scale=1.6) for d in jump_dots], lag_ratio=0.2), run_time=1.2)
        wait_until(HYBRID_AT)
        self.play(FadeIn(hybrid, shift=UP * 0.1), run_time=0.8)
        wait_until(ENERGY_AT)
        lower = VGroup(plots, ang, spd, marks, jump_dots, stays, jumps, exag)
        self.play(lower.animate.scale(0.74, about_point=[PLOT_X, -2.6, 0]), FadeOut(hybrid), run_time=1.0)
        self.play(Write(e_eq), FadeIn(pe), FadeIn(e_lbl), FadeIn(ax_lbls), Create(prof), run_time=1.4)
        wait_until(CENTER_AT)
        self.play(GrowArrow(k_c), FadeIn(t_c), FadeIn(fastest), run_time=0.8)
        wait_until(HALF_AT)
        self.play(GrowArrow(k_h), FadeIn(t_h), run_time=0.8)

        wait_until(FINAL_HOLD_UNTIL)
        cur.set_fill(opacity=0)
        self.add(cur)
        self.play(cur.animate.set_fill(opacity=1), run_time=FADE_OUT)
