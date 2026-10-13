"""Film 5, scene 06 - "The overcoil": a flat spiral breathing, its center of
gravity (offset magnified) wandering and loading the pivots: an amplitude-
dependent rate and a positional error. Breguet (1795) raised the outer end and
curved it back over the coils. Phillips (1860): the terminal curve's center of
gravity G must lie on the radius at right angles to OC, at OG = rho0^2 / l.
The drawn terminal curve is computed in figures.py to meet both conditions
(l = 3.745 rho0, OG = 0.2670 rho0, angle GOC = 90 degrees). The overcoil's
breathing is schematic. Silicon springs: uneven coils, etched.

Build (render + voice + mux):   python build.py 5/scene06_overcoil
Render only (quick preview):    PYTHONPATH=.:films/film05_isochronism manim -ql films/film05_isochronism/scene06_overcoil.py Scene06
Narration lines and their start times live in scene06_overcoil.voice.txt. Numbers from figures.py.
No balance on screen: the steady tick track plays.
"""
from manim import *
import iso  # noqa: F401  (first: puts Film 4's helpers on the path)
import figures as F
from iso import FlatSpring
from movement import vignette, BG, GLOW, STEEL, STEEL_HI
from ui import ftext, label, heading, tag, curtain, clock, WARM, COOL

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds.
# Keep the timeline roughly in step with scene06_overcoil.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 1.0
HEAD_AT = 1.2                         # "A flat spiral has a flaw"
CG_AT = 3.6                           # "its center of gravity wanders off the axis"
PUSH_AT = 8.0                         # "and pushes sideways on the pivots"
RATE_AT = 11.7                        # "That adds an amplitude-dependent rate"
POS_AT = 14.6                         # "and a positional error: dial up and crown down"
BREGUET_AT = 19.8                     # "In 1795, Breguet raised the outer end..."
SIDE_AT = 22.6                        # "...and curved it back over the coils"
PHILLIPS_AT = 28.3                    # "In 1860, Edouard Phillips found the shape that works"
PERP_AT = 34.3                        # "the center of gravity of the end curve must lie on the radius at right angles"
DIST_AT = 39.6                        # "at a distance rho nought squared over its length"
CHECK_AT = 42.4                       # the computed curve's numbers
CONC_AT = 45.1                        # "Then the coils breathe concentrically"
SILICON_AT = 48.9                     # "Today's silicon springs..."
FINAL_HOLD_UNTIL = 55.8               # the last line ends about 54.2 s
FADE_OUT = 1.5

# --- pictures ------------------------------------------------------------
LEFT_C, RIGHT_C, RHO0 = (-3.7, 0.35), (3.6, 0.65), 1.55
SWING_HZ = 0.35                       # slowed, schematic breathing
CG_MAG = 14.0                         # magnification of the flat spiral's center-of-gravity offset (tagged)
LOAD_MAG = 1.0                        # length of the pivot-load arrow, per unit of magnified offset
# =====================================================================


class Scene06(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.add(vignette())
        wait_until = clock(self)
        clk = ValueTracker(0.0).add_updater(lambda m, dt: m.increment_value(dt))
        swing = lambda: 1.1 * np.sin(TAU * SWING_HZ * clk.get_value())
        vflat, vover = ValueTracker(0.0), ValueTracker(0.0)

        # --- left: the flat spiral, its center of gravity wandering
        lc = np.array([*LEFT_C, 0.0])
        flat = FlatSpring(center=LEFT_C, r_in=0.14, r_out=RHO0, turns=8, stud_deg=-40, breathe=0.16)
        flat.add_updater(lambda m: m.draw(swing()).set_stroke(opacity=vflat.get_value()))
        f_stud = Square(0.16).set_fill(STEEL, 1).set_stroke(STEEL_HI, 1).move_to(flat.stud_pt())
        f_axis = VGroup(Line(lc + LEFT * 0.2, lc + RIGHT * 0.2), Line(lc + DOWN * 0.2, lc + UP * 0.2)).set_stroke(WHITE, 1.5)
        cg_pos = lambda: lc + CG_MAG * (flat.cg(swing()) - lc)
        cg_vis = ValueTracker(0.0)
        f_cg = Dot(radius=0.09, color=WARM).add_updater(lambda m: m.move_to(cg_pos()).set_opacity(cg_vis.get_value()))
        trail = TracedPath(lambda: cg_pos(), stroke_color=WARM, stroke_width=1.5, dissipating_time=2.5)
        load_vis = ValueTracker(0.0)
        load = Line(lc, lc + RIGHT).set_stroke(GLOW, 4)
        load.add_updater(lambda m: m.put_start_and_end_on(lc, lc + LOAD_MAG * (cg_pos() - lc) + 1e-4 * RIGHT)
                         .set_stroke(opacity=load_vis.get_value()))
        f_title = label("flat spiral", 0.28, COOL, bold=True).move_to(lc + UP * (RHO0 + 0.45))
        cg_tag = tag(f"center of gravity (dot): offset ×{CG_MAG:.0f}", WARM, 0.2).next_to(lc + DOWN * RHO0, DOWN, buff=0.2)
        load_lbl = label("sideways push\non the pivots", 0.22, GLOW).move_to(lc + LEFT * 2.35 + DOWN * 0.6)
        effects = VGroup(label("amplitude-dependent rate", 0.26, WARM),
                         label("positional error:  dial up  ≠  crown down", 0.26, WARM)).arrange(DOWN, buff=0.14, aligned_edge=LEFT)
        effects.move_to([LEFT_C[0], -2.85, 0])
        f_static = VGroup(f_stud, f_axis, f_title, cg_tag, load_lbl)

        # --- right: the Breguet overcoil (plan view), its terminal curve computed to meet Phillips' conditions
        rc = np.array([*RIGHT_C, 0.0])
        body = FlatSpring(center=RIGHT_C, r_in=0.14, r_out=RHO0 * 0.97, turns=8, stud_deg=90, breathe=0.0)
        body.add_updater(lambda m: m.draw(0.0).scale(1 - 0.035 * swing(), about_point=rc).set_stroke(opacity=0.8 * vover.get_value()))
        tc = np.c_[F.PH_CURVE * RHO0, np.zeros(len(F.PH_CURVE))] + rc
        term = VMobject().set_points_smoothly(tc[::6]).set_stroke(WARM, 3.5)
        o_stud = Square(0.16).set_fill(STEEL, 1).set_stroke(STEEL_HI, 1).move_to(tc[-1])
        o_g = Dot(rc, radius=0.09, color=GLOW)
        o_title = label("Breguet overcoil, 1795", 0.28, WARM, bold=True).move_to(rc + UP * (RHO0 + 0.45))
        o_g_lbl = label("spring's G stays on the axis", 0.22, GLOW).next_to(rc + DOWN * RHO0, DOWN, buff=0.2)
        sch = tag("breathing schematic", GLOW, 0.2).next_to(o_g_lbl, DOWN, buff=0.12)

        # side view: the outer end raised and brought back over the coils
        sv = np.array([RIGHT_C[0], -2.75, 0])
        side = VGroup(Line(sv + LEFT * RHO0, sv + RIGHT * RHO0).set_stroke(COOL, 4),
                      VMobject().set_points_smoothly([sv + RIGHT * RHO0, sv + RIGHT * (RHO0 + 0.12) + UP * 0.18,
                                                      sv + RIGHT * (RHO0 - 0.2) + UP * 0.36, sv + LEFT * 0.4 + UP * 0.36])
                      .set_stroke(WARM, 3.5))
        side_lbl = label("side view: the end raised and curved back", 0.22).next_to(side, DOWN, buff=0.15)

        # --- left, after the flat spiral: Phillips' conditions on the computed curve
        pc = lc
        coils = VGroup(*[Circle(radius=RHO0 * k).move_to(pc).set_stroke(GREY_D, 1.2) for k in (1.0, 0.86, 0.72, 0.58)])
        ptc = np.c_[F.PH_CURVE * RHO0, np.zeros(len(F.PH_CURVE))] + pc
        p_term = VMobject().set_points_smoothly(ptc[::6]).set_stroke(WARM, 3.5)
        O, C = pc, pc + UP * RHO0
        G = pc + np.array([F.PH_G[0], F.PH_G[1], 0.0]) * RHO0
        oc = Line(O, C).set_stroke(WHITE, 2)
        og = Line(O, G).set_stroke(GLOW, 4)
        square = VMobject().set_points_as_corners([O + UP * 0.18, O + UP * 0.18 + LEFT * 0.18, O + LEFT * 0.18]).set_stroke(WHITE, 1.5)
        dots = VGroup(*[Dot(p, radius=0.07, color=c) for p, c in ((O, WHITE), (C, WHITE), (G, GLOW))])
        names = VGroup(label("O", 0.3).next_to(O, DOWN + RIGHT, buff=0.06), label("C", 0.3).next_to(C, UP + RIGHT, buff=0.06),
                       label("G", 0.3, GLOW).next_to(G, DOWN, buff=0.1))
        p_title = label("Phillips, 1860", 0.28, WARM, bold=True).move_to(lc + UP * (RHO0 + 0.45))
        perp = ftext("OG  ⊥  OC", 0.5, GLOW)
        dist = ftext("OG  =  ρ₀² / ℓ", 0.5, GLOW)
        conds = VGroup(perp, dist).arrange(RIGHT, buff=0.7).move_to([LEFT_C[0], -2.2, 0])
        key = label("ℓ: length of the end curve,  ρ₀: coil radius", 0.2).next_to(conds, DOWN, buff=0.12)
        check = label(f"this curve:  ℓ = {F.PH_L:.3f} ρ₀,   OG = {F.PH_OG:.4f} ρ₀ = ρ₀²/ℓ,   ∠GOC = {F.PH_ANGLE:.1f}°",
                      0.22, GLOW).next_to(key, DOWN, buff=0.14)
        phillips = VGroup(coils, p_term, oc, og, square, dots, names, p_title)

        silicon = VGroup(label("silicon springs:", 0.28, COOL, bold=True),
                         label("the same cancellation, from coils etched unevenly", 0.28, COOL)).arrange(RIGHT, buff=0.2)
        silicon.to_edge(DOWN, buff=0.35)

        head = heading("THE OVERCOIL", "breathing concentrically").to_corner(UL, buff=0.5)
        cur = curtain()
        self.add(clk, vflat, vover, cg_vis, load_vis, flat, body, load, f_cg, cur)

        # ---------------------------------------------------------- timeline
        self.play(cur.animate.set_fill(opacity=0), run_time=FADE_IN, rate_func=smooth)
        self.remove(cur)
        wait_until(HEAD_AT)                                 # the flat spiral breathes
        self.play(FadeIn(head), vflat.animate.set_value(1.0), FadeIn(f_static[:3]), run_time=0.9)
        wait_until(CG_AT)                                   # its center of gravity wanders
        self.add(trail)
        self.play(cg_vis.animate.set_value(1.0), FadeIn(cg_tag), run_time=0.8)
        wait_until(PUSH_AT)                                 # and pushes on the pivots
        self.play(load_vis.animate.set_value(1.0), FadeIn(load_lbl), run_time=0.8)
        wait_until(RATE_AT)
        self.play(FadeIn(effects[0], shift=UP * 0.1), run_time=0.7)
        wait_until(POS_AT)
        self.play(FadeIn(effects[1], shift=UP * 0.1), run_time=0.7)
        wait_until(BREGUET_AT)                              # the overcoil
        self.play(vover.animate.set_value(1.0), Create(term), FadeIn(o_stud), FadeIn(o_title), run_time=1.4)
        wait_until(SIDE_AT)
        self.play(FadeIn(side), FadeIn(side_lbl), run_time=0.9)
        wait_until(PHILLIPS_AT)                             # Phillips: the flat spiral gives way to the conditions
        self.play(vflat.animate.set_value(0.0), cg_vis.animate.set_value(0.0), load_vis.animate.set_value(0.0),
                  FadeOut(f_static), FadeOut(effects), FadeOut(side), FadeOut(side_lbl), run_time=0.8)
        self.remove(trail)
        self.play(FadeIn(coils), FadeIn(p_title), Create(p_term), run_time=1.2)
        self.play(FadeIn(dots[:2]), FadeIn(names[:2]), Create(oc), run_time=0.8)
        wait_until(PERP_AT)                                 # G on the perpendicular radius
        self.play(FadeIn(dots[2]), FadeIn(names[2]), Create(og), Create(square), Write(perp), run_time=1.2)
        wait_until(DIST_AT)                                 # at rho0^2 / l
        self.play(Write(dist), FadeIn(key), run_time=1.1)
        wait_until(CHECK_AT)
        self.play(FadeIn(check, shift=UP * 0.1), run_time=0.8)
        wait_until(CONC_AT)                                 # concentric breathing
        self.play(FadeIn(o_g), FadeIn(o_g_lbl), FadeIn(sch), run_time=0.8)
        self.play(Indicate(o_g, color=GLOW, scale_factor=1.6), run_time=1.0)
        wait_until(SILICON_AT)
        self.play(FadeIn(silicon, shift=UP * 0.1), run_time=0.9)

        wait_until(FINAL_HOLD_UNTIL)
        cur.set_fill(opacity=0)
        self.add(cur)
        self.play(cur.animate.set_fill(opacity=1), run_time=FADE_OUT)
