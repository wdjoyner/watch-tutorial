"""Film 4, scene 02 - "Two numbers": the balance's moment of inertia,
I = integral of rho^2 dm, shown as mass dots sized by their weight rho^2 (mass twice
as far out counts four times), so the rim carries most of it; then the
hairspring's stiffness, kappa = E b h^3 / 12 L, the beam formula from Film 2, with
the two springs' cross-sections side by side at the same scale.

Build (render + voice + mux):   python build.py 4/scene02_two_numbers
Render only (quick preview):    PYTHONPATH=.:films/film04_regulating_organ manim -ql films/film04_regulating_organ/scene02_two_numbers.py Scene02
Narration lines and their start times live in scene02_two_numbers.voice.txt.

Numbers come from figures.py: the mainspring is Film 2's (1.50 x 0.18 mm), the
hairspring the chapter's representative 6497-sized one (0.20 x 0.040 mm).
"""
from manim import *
import figures as F
from movement import vignette, BG, GLOW, GILT
from balance import BalanceModel, BeatLog
from ui import ftext, label, tag, heading, curtain, clock, WARM

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds.
# Keep the timeline roughly in step with scene02_two_numbers.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 1.0
I_HEAD_AT = 3.4                       # "moment of inertia, I"
DOTS_AT = 5.6                         # "every bit of its mass"
WEIGHT_AT = 7.6                       # "weighted by the square of its distance"
FORMULA_I_AT = 8.6                    # I = integral rho^2 dm
TWICE_AT = 11.6                       # "mass twice as far out counts four times as much"
RIM_AT = 16.2                         # "a heavy ring on thin arms"
KAPPA_AT = 20.9                       # "the hairspring's stiffness, kappa"
FORMULA_K_AT = 24.4                   # "the beam formula from film two"
SECTIONS_AT = 30.9                    # "only the ribbon is far finer"
CUBED_AT = 33.8                       # "its thickness enters cubed"
RATIO_AT = 35.8                       # "hundreds of times stiffer"
FINAL_HOLD_UNTIL = 40.4               # the last line ends about 38.4 s
FADE_OUT = 1.5

# --- balance -----------------------------------------------------------
BAL_AT, BAL_R = (-3.7, -0.35), 2.35
RATE, AMP = 0.1, 0.45                 # gentle slow-motion swing (radians)
DOT_STEP = 0.16                       # spacing of the mass dots
DOT_R = (0.012, 0.075)                # dot radius at the axis and at the rim (radius ~ rho, so area ~ rho^2)
PAIR = (0.5, 1.0)                     # the two compared dots, as fractions of the rim radius

# --- cross-sections (drawn at the same scale) ----------------------------
MM = 1.6                              # scene units per millimeter
SECTION_AT = {"ms": (1.9, -2.75), "hs": (4.6, -2.75)}
# =====================================================================


class Scene02(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.add(vignette())
        wait_until = clock(self)

        bal = BalanceModel(center=BAL_AT, radius=BAL_R, amp=AMP)
        bal.rate.set_value(RATE)
        bal.attach(self)
        log = BeatLog(self, lambda: bal.model_t, 2 * bal.hz)

        # mass dots on the rim and arms, carried by the wheel; radius grows with rho
        c = np.array([*BAL_AT, 0.0])
        rim_in = BAL_R * 0.84
        pts = []
        for x in np.arange(-BAL_R, BAL_R + 1e-9, DOT_STEP):
            for y in np.arange(-BAL_R, BAL_R + 1e-9, DOT_STEP):
                p = np.array([x, y])
                r = np.hypot(x, y)
                on_rim = rim_in + 0.03 < r < BAL_R - 0.03
                on_arm = any(abs(np.cos(0.35 + k * TAU / 3) * p[1] - np.sin(0.35 + k * TAU / 3) * p[0]) < 0.05
                             and np.dot([np.cos(0.35 + k * TAU / 3), np.sin(0.35 + k * TAU / 3)], p) > 0.2
                             and r < rim_in for k in range(3))
                if on_rim or on_arm:
                    pts.append((p, r))
        small = VGroup(*[Dot(c + [*p, 0], radius=DOT_R[0] * 2.2, color=WHITE).set_opacity(0) for p, _ in pts])
        big = VGroup(*[Dot(c + [*p, 0], radius=DOT_R[0] + (DOT_R[1] - DOT_R[0]) * r / BAL_R, color=WARM).set_opacity(0)
                       for p, r in pts])
        bal.rotor.add(small, big)                          # the dots turn with the wheel
        # their opacity follows trackers (never .animate them: that fights the swing updater)
        small_op, big_op = ValueTracker(0.0), ValueTracker(0.0)
        small.add_updater(lambda m: m.set_opacity(small_op.get_value()))
        big.add_updater(lambda m: m.set_opacity(big_op.get_value()))
        self.add(small_op, big_op)

        # the compared pair, on one arm direction (screen-fixed; shown while the swing is small)
        a = 0.35                                           # the arm pointing right, toward the open space
        u = np.array([np.cos(a), np.sin(a), 0.0])
        pair = VGroup()
        for f, txt, dy in zip(PAIR, ("ρ   counts ×1", "2ρ  counts ×4"), (-0.55, 0.55)):
            p = c + u * BAL_R * f * (0.92 if f == 1 else 1)
            t = label(txt, 0.3, GLOW).move_to([-0.2, p[1] + dy, 0], aligned_edge=LEFT)
            pair.add(VGroup(Circle(radius=0.16).move_to(p).set_stroke(GLOW, 3),
                            Line(p + (t.get_left() - p) / np.linalg.norm(t.get_left() - p) * 0.18,
                                 t.get_left() + LEFT * 0.08).set_stroke(GLOW, 1.4, 0.8), t))

        title_i = heading("MOMENT OF INERTIA,  I", "how hard the wheel is to turn").to_corner(UR, buff=0.6).shift(LEFT * 2.6)
        formula_i = ftext("I  =  ∫ ρ² dm", 0.75).move_to([3.2, 2.55, 0])
        legend_i = label("ρ  distance of each bit of mass  dm  from the axis", 0.25).next_to(formula_i, DOWN, buff=0.22)
        block_i = VGroup(title_i, formula_i, legend_i)

        formula_k = ftext("κ  =  E b h³ / 12 L", 0.75).move_to([3.2, 0.95, 0])
        legend_k = label("E  modulus      b  height      h  thickness      L  length", 0.25)
        legend_k.next_to(formula_k, DOWN, buff=0.22)
        film2 = label("the beam formula from Film 2", 0.25, GLOW).next_to(legend_k, DOWN, buff=0.14)
        title_k = heading("STIFFNESS,  κ", "how stiff the hairspring is").move_to(title_i, aligned_edge=UL)

        # cross-sections at the same scale: height b up, thickness h across
        def section(b_mm, h_mm, name, dims, key):
            r = Rectangle(width=h_mm * MM, height=b_mm * MM).set_fill(GILT if key == "ms" else "#9fb6d8", 1)
            r.set_stroke(WHITE, 0.8).move_to([*SECTION_AT[key], 0], aligned_edge=DOWN)
            t = VGroup(label(name, 0.27, WHITE), label(dims, 0.22)).arrange(DOWN, buff=0.06)
            t.next_to(r, DOWN, buff=0.16)
            return VGroup(r, t)
        ms = section(F.MS_B * 1e3, F.MS_H * 1e3, "mainspring", f"{F.MS_H * 1e3:.2f} × {F.MS_B * 1e3:.2f} mm", "ms")
        hs = section(F.B_HS_6497 * 1e3, F.H_HS_6497 * 1e3, "hairspring", f"{F.H_HS_6497 * 1e3:.3f} × {F.B_HS_6497 * 1e3:.2f} mm", "hs")
        repr_tag = tag("representative", scale=0.2).next_to(hs, DOWN, buff=0.1)
        sections = VGroup(ms, hs, repr_tag)
        cubed = ftext(f"h³:  ({F.MS_H * 1e3:.2f} / {F.H_HS_6497 * 1e3:.3f})³  ≈  {F.THICKNESS_CUBED_RATIO:.0f}", 0.42)
        cubed.move_to([3.4, 0.75, 0])
        ratio = ftext(f"κ mainspring  ≈  {round(F.STIFFNESS_RATIO, -1):.0f} × κ hairspring", 0.42, GLOW)
        ratio.next_to(cubed, DOWN, buff=0.2)

        cur = curtain()
        self.add(cur)

        # ---------------------------------------------------------- timeline
        self.play(cur.animate.set_fill(opacity=0), run_time=FADE_IN, rate_func=smooth)
        self.remove(cur)
        wait_until(I_HEAD_AT)
        self.play(FadeIn(title_i, shift=DOWN * 0.1), run_time=0.8)
        wait_until(DOTS_AT)                                # every bit of mass
        self.play(small_op.animate.set_value(0.85), run_time=1.0)
        wait_until(WEIGHT_AT)                              # weighted by rho^2
        self.play(small_op.animate.set_value(0.0), big_op.animate.set_value(0.95), run_time=1.2)
        wait_until(FORMULA_I_AT)
        self.play(Write(formula_i), run_time=1.4)
        self.play(FadeIn(legend_i, shift=UP * 0.1), run_time=0.7)

        wait_until(TWICE_AT)                               # twice as far, four times
        self.play(bal.amp.animate.set_value(0.0), run_time=0.8)   # hold the wheel still for the comparison
        self.play(LaggedStart(*[FadeIn(p) for p in pair], lag_ratio=0.6), run_time=1.6)
        wait_until(RIM_AT)                                 # heavy ring, thin arms
        self.play(FadeOut(pair), Indicate(bal.wheel, color=GLOW, scale_factor=1.0), run_time=1.2)
        self.play(bal.amp.animate.set_value(AMP), run_time=1.0)

        wait_until(KAPPA_AT)                               # kappa
        bal.spring.set_stroke(GLOW, 3.4)                   # set directly: the updater redraws the spring each frame
        self.play(big_op.animate.set_value(0.0),
                  FadeOut(title_i), FadeIn(title_k), formula_i.animate.set_opacity(0.35),
                  legend_i.animate.set_opacity(0.35), run_time=1.0)
        wait_until(FORMULA_K_AT)
        self.play(Write(formula_k), run_time=1.4)
        self.play(FadeIn(legend_k, shift=UP * 0.1), FadeIn(film2, shift=UP * 0.1), run_time=0.8)

        wait_until(SECTIONS_AT)                            # far finer
        self.play(FadeOut(VGroup(formula_i, legend_i)), VGroup(formula_k, legend_k, film2).animate.shift(UP * 1.5),
                  FadeIn(sections, shift=UP * 0.2), run_time=1.2)
        wait_until(CUBED_AT)                               # thickness cubed
        self.play(FadeIn(cubed, shift=UP * 0.1), run_time=0.9)
        wait_until(RATIO_AT)                               # hundreds of times stiffer
        self.play(FadeIn(ratio, shift=UP * 0.1), run_time=0.9)

        wait_until(FINAL_HOLD_UNTIL)
        cur.set_fill(opacity=0)
        self.add(cur)
        self.play(cur.animate.set_fill(opacity=1), run_time=FADE_OUT)
        log.write(__file__)
