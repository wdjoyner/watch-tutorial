"""Film 2, scene 07 - "Advanced: how many turns?": two 6497 barrels side by side,
fully wound (the spring packed around the arbor) and let down (packed against
the wall). The barrel delivers the difference in turns between the two packs,
the development N(L). A slider changes the spring length L; both packs resize
while the curve N(L) traces out. The peak is at half fill, where the two packs
meet at the same radius; the 6497's 450 mm spring sits just beside it. Last,
the longer spring that stores the most energy.

Build (render + voice + mux):   python build.py scene07_turns
Render only (quick preview):    PYTHONPATH=.:films/film02_power_source manim -ql films/film02_power_source/scene07_turns.py Scene07
Narration lines and their start times live in scene07_turns.voice.txt.

Barrels and packs are drawn to scale (true 6497 radii and spring thickness,
one faint line per turn). Area conservation (barrel.pack_turns):
  wound:    pi (R1^2 - r^2) = L h,   N_wound = (R1 - r) / h
  let down: pi (R^2 - R2^2) = L h,   N_down  = (R - R2) / h
  N(L) = N_wound - N_down, largest at L_opt = pi (R^2 - r^2) / 2h, where R1 = R2.
"""
from manim import *
from shapely import affinity
from movement import vignette, BG, GLOW, FONT_SANS, FONT_SERIF, BRASS, BRASS_DK, BRASS_HI, STEEL, STEEL_HI
from barrel import arbor_core_g, drum_floor_g, drum_wall_g, pack_turns, vm, R_ROOT, R_IN, CORE_R, REAL_H, REAL_L

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds.
# Keep the timeline roughly in step with scene07_turns.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 0.8
BARRELS_AT = 1.0                         # "How many turns can a barrel give?"
WOUND_AT, DOWN_AT = 4.0, 6.7             # the two packs
COUNTS_AT, DIFF_AT = 10.0, 12.0          # turns in each pack; their difference
PLOT_AT = 13.4                           # axes, and the first point at 450 mm
SHORT = (15.0, 17.2, 40.0)               # (start, end, L in mm): "too short"
LONG = (17.6, 20.2, 880.0)               # "too long"
BEST = (21.0, 23.0)                      # back to the peak
HALF_AT = 23.4                           # "fills exactly half the free space"; R1 = R2
LOPT_AT = 27.0                           # "about 454 mm"
ETA_AT = 31.2                            # "ETA's spring is 450"
TURNS_AT, CROWN_AT = 35.5, 38.8          # "eight turns of the barrel", "thirty turns of the crown"
ENERGY_AT, ENERGY_MOVE = 43.4, 2.0       # "a somewhat longer spring stores a little more"
FINAL_HOLD_UNTIL = 50.4                  # the last line ends about 49.2 s
FADE_OUT = 1.5

# --- layout -------------------------------------------------------------
S_MM = 0.17                              # scene units per mm for the barrels
WOUND_C = np.array([-5.05, 1.35, 0])
DOWN_C = np.array([-1.75, 1.35, 0])
SLIDER_Y, SLIDER_X = -2.75, (-6.1, -0.7)
AX_ORIGIN = np.array([0.95, -2.55, 0])
AX_W, AX_H = 5.6, 3.9
L_MAX = np.pi * (R_IN ** 2 - CORE_R ** 2) / REAL_H     # the spring that fills the barrel, about 908 mm
L_OPT = L_MAX / 2                                       # about 454 mm
L_ENERGY = 1.2 * L_OPT                                  # Theory of Horology: about 20% longer for most energy
CROWN_PER_BARREL = 60 / 16                              # crown turns per barrel turn (ratchet / winding train)

# --- colors and text ---------------------------------------------------
PACK = STEEL_HI
AREA = "#ffb54a"
CURVE = GLOW
TEXT = {"wound": "fully wound", "down": "let down", "wraps": "wraps the arbor", "wall": "against the wall",
        "x": "spring length L (mm)", "y": "barrel turns N", "half": "half full", "full": "full",
        "same": "same radius", "eta": "ETA 6497: 450 mm", "energy": ("most energy:", "about 20% longer"),
        "flat": "the flat top costs few turns"}
# =====================================================================


def label(s, scale=0.28, color=GREY_B, bold=False):
    return Text(s, font=FONT_SANS, weight=BOLD if bold else NORMAL, color=color).scale(scale)


def ftext(s, scale=0.5, color=WHITE):
    return Text(s, font=FONT_SERIF, slant=ITALIC, color=color).scale(scale)


def packs(L):
    """(N_wound, N_down, R1, R2, N) for a spring of length L mm in the 6497 barrel."""
    n_w, _, R1, _ = pack_turns(1.0, L=L)
    _, n_d, _, R2 = pack_turns(0.0, L=L)
    return n_w, n_d, R1, R2, n_w - n_d


class Scene07(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.add(vignette())

        def wait_until(when):
            d = when - self.renderer.time
            if d > 0.07:
                self.wait(d)

        Lt = ValueTracker(REAL_L)

        def sc(g):
            return affinity.scale(g, S_MM, S_MM, origin=(0, 0))

        def barrel_base(c):
            return VGroup(vm(sc(drum_floor_g()), BRASS_DK, stroke=BRASS_DK, sw=0),
                          vm(sc(drum_wall_g()), BRASS, stroke=BRASS_HI, sw=0.8)).shift(c)

        def arbor(c):
            return vm(sc(arbor_core_g()), STEEL, stroke=STEEL_HI, sw=0.6).shift(c)

        bases = VGroup(barrel_base(WOUND_C), barrel_base(DOWN_C))
        arbors = VGroup(arbor(WOUND_C), arbor(DOWN_C))

        def pack_mob(c, a, b, o):
            """A packed coil from radius a to b (mm) at c, with one faint line per turn, at opacity o.
            (Opacity is set per member: set_opacity on the group would fill the turn circles.)"""
            g = VGroup()
            if b - a < 1e-3 or o <= 0:
                return g
            g.add(Annulus(inner_radius=a * S_MM, outer_radius=b * S_MM).move_to(c)
                  .set_fill(PACK, o).set_stroke(WHITE, 0.6, o))
            k = int((b - a) / REAL_H)
            for i in range(1, k + 1):
                g.add(Circle(radius=(a + i * REAL_H) * S_MM).move_to(c).set_fill(opacity=0).set_stroke(STEEL, 0.5, 0.55 * o))
            return g

        show = {"wound": ValueTracker(0.0), "down": ValueTracker(0.0), "ghost": ValueTracker(0.0)}

        def wound_pack():
            _, _, R1, R2, _ = packs(Lt.get_value())
            return pack_mob(WOUND_C, CORE_R, R1, show["wound"].get_value())

        def down_pack():
            _, _, R1, R2, _ = packs(Lt.get_value())
            return pack_mob(DOWN_C, R2, R_IN, show["down"].get_value())

        def ghosts():
            # each barrel shows, dashed, where the other state's pack ends
            _, _, R1, R2, _ = packs(Lt.get_value())
            o = show["ghost"].get_value()
            near = abs(R1 - R2) < 0.06
            col = AREA if near else GREY_B
            g = VGroup(DashedVMobject(Circle(radius=R2 * S_MM), num_dashes=48).move_to(WOUND_C).set_stroke(col, 2, o),
                       DashedVMobject(Circle(radius=R1 * S_MM), num_dashes=48).move_to(DOWN_C).set_stroke(col, 2, o))
            return g

        wound_mob = always_redraw(wound_pack)
        down_mob = always_redraw(down_pack)
        ghost_mob = always_redraw(ghosts)

        names = VGroup(label(TEXT["wound"], 0.32, WHITE, True).next_to(WOUND_C + DOWN * R_ROOT * S_MM, DOWN, buff=0.22),
                       label(TEXT["down"], 0.32, WHITE, True).next_to(DOWN_C + DOWN * R_ROOT * S_MM, DOWN, buff=0.22))
        names[1].align_to(names[0], DOWN)
        notes = VGroup(label(TEXT["wraps"], 0.26).next_to(names[0], DOWN, buff=0.1),
                       label(TEXT["wall"], 0.26).next_to(names[1], DOWN, buff=0.1))

        # live turn counts under each barrel, and their difference
        def counts():
            n_w, n_d, _, _, n = packs(Lt.get_value())
            return VGroup(ftext(f"{n_w:.1f} turns", 0.42, PACK).next_to(notes[0], DOWN, buff=0.16),
                          ftext(f"{n_d:.1f} turns", 0.42, PACK).next_to(notes[1], DOWN, buff=0.16))

        def diff():
            n_w, n_d, _, _, n = packs(Lt.get_value())
            t = ftext(f"N  =  {n_w:.1f} − {n_d:.1f}  =  {n:.1f} turns", 0.46)
            return t.move_to(np.array([(WOUND_C[0] + DOWN_C[0]) / 2, -1.95, 0]))

        counts_mob = always_redraw(counts)
        diff_mob = always_redraw(diff)

        # ------------------------------------------------------------ the slider
        x0, x1 = SLIDER_X

        def sx(L):
            return x0 + (x1 - x0) * L / L_MAX

        track = Line(np.array([x0, SLIDER_Y, 0]), np.array([x1, SLIDER_Y, 0])).set_stroke(GREY_C, 3)
        s_ticks = VGroup(*[Line(UP * 0.09, DOWN * 0.09).move_to(np.array([sx(L), SLIDER_Y, 0])).set_stroke(GREY_C, 2)
                           for L in (0, L_OPT, L_MAX)])
        s_lbls = VGroup(label("0", 0.22).next_to(s_ticks[0], DOWN, buff=0.08),
                        label(TEXT["half"], 0.22).next_to(s_ticks[1], DOWN, buff=0.08),
                        label(TEXT["full"], 0.22).next_to(s_ticks[2], DOWN, buff=0.08))

        def knob():
            L = Lt.get_value()
            p = np.array([sx(L), SLIDER_Y, 0])
            return VGroup(Dot(p, radius=0.1, color=CURVE),
                          ftext(f"L = {L:.0f} mm", 0.4, CURVE).next_to(p, UP, buff=0.14))

        knob_mob = always_redraw(knob)
        slider = VGroup(track, s_ticks, s_lbls)

        # ------------------------------------------------------------ the plot of N(L)
        ax = Axes(x_range=[0, 960, 100], y_range=[0, 9.4, 2], x_length=AX_W, y_length=AX_H,
                  tips=True, axis_config={"color": GREY_B, "stroke_width": 2, "tick_size": 0.05})
        ax.move_to(AX_ORIGIN, aligned_edge=DL)
        x_nums = VGroup(*[label(str(k), 0.22).next_to(ax.c2p(k, 0), DOWN, buff=0.12) for k in (0, 200, 400, 600, 800)])
        y_nums = VGroup(*[label(str(k), 0.22).next_to(ax.c2p(0, k), LEFT, buff=0.12) for k in (2, 4, 6, 8)])
        x_lbl = label(TEXT["x"], 0.26).next_to(x_nums, DOWN, buff=0.14).align_to(ax.x_axis, RIGHT)
        y_lbl = label(TEXT["y"], 0.26).rotate(PI / 2).next_to(y_nums, LEFT, buff=0.14)
        plot = VGroup(ax, x_nums, y_nums, x_lbl, y_lbl)

        def N_of(L):
            return packs(L)[4]

        seen = {"lo": REAL_L, "hi": REAL_L, "on": False}

        def curve():
            L = Lt.get_value()
            if not seen["on"]:
                return VGroup()
            seen["lo"], seen["hi"] = min(seen["lo"], L), max(seen["hi"], L)
            xs = np.linspace(seen["lo"], seen["hi"], 160)
            c = VMobject().set_points_as_corners([ax.c2p(x, N_of(x)) for x in xs]).set_stroke(CURVE, 4)
            p = ax.c2p(L, N_of(L))
            return VGroup(c, DashedLine(ax.c2p(L, 0), p, dash_length=0.06).set_stroke(GREY_B, 1.5),
                          Dot(p, radius=0.08, color=CURVE))

        curve_mob = always_redraw(curve)

        curtain = FullScreenRectangle().set_fill(BG, 1).set_stroke(width=0)
        self.add(bases, wound_mob, down_mob, ghost_mob, arbors, curtain)
        self.play(curtain.animate.set_fill(opacity=0), run_time=FADE_IN)
        self.remove(curtain)

        # ------------------------------------------------------------ the two states
        wait_until(BARRELS_AT)
        self.play(FadeIn(names), FadeIn(plot), run_time=0.8)
        wait_until(WOUND_AT)
        self.play(show["wound"].animate.set_value(1.0), FadeIn(notes[0]), run_time=1.0)
        wait_until(DOWN_AT)
        self.play(show["down"].animate.set_value(1.0), FadeIn(notes[1]), run_time=1.0)

        # the turns it can deliver: the difference
        wait_until(COUNTS_AT)
        self.play(FadeIn(counts_mob), run_time=0.8)
        wait_until(DIFF_AT)
        self.play(FadeIn(diff_mob, shift=DOWN * 0.1), run_time=0.8)
        wait_until(PLOT_AT)
        seen["on"] = True
        curve_mob.update()
        self.play(FadeIn(slider), FadeIn(knob_mob), FadeIn(curve_mob), run_time=1.0)

        # too short, too long
        wait_until(SHORT[0])
        self.play(Lt.animate.set_value(SHORT[2]), run_time=SHORT[1] - SHORT[0], rate_func=smooth)
        wait_until(LONG[0])
        self.play(Lt.animate.set_value(LONG[2]), run_time=LONG[1] - LONG[0], rate_func=smooth)

        # the best: half the free space, where the two packs meet at the same radius
        wait_until(BEST[0])
        self.play(Lt.animate.set_value(L_OPT), show["ghost"].animate.set_value(1.0),
                  run_time=BEST[1] - BEST[0], rate_func=smooth)
        wait_until(HALF_AT)
        same = label(TEXT["same"], 0.26, AREA, True).move_to((WOUND_C + DOWN_C) / 2 + UP * (R_ROOT * S_MM + 0.3))
        r_eq = ftext("R₁ = R₂", 0.42, AREA).next_to(same, UP, buff=0.1)
        peak = ax.c2p(L_OPT, N_of(L_OPT))
        v_dash = DashedLine(ax.c2p(L_OPT, 0), peak, dash_length=0.06).set_stroke(AREA, 2)
        h_dash = DashedLine(ax.c2p(0, N_of(L_OPT)), peak, dash_length=0.06).set_stroke(AREA, 1.5)
        peak_dot = Dot(peak, radius=0.1, color=AREA)
        self.play(FadeIn(same), FadeIn(r_eq), Create(v_dash), Create(h_dash), FadeIn(peak_dot),
                  s_lbls[1].animate.set_color(AREA), run_time=0.9)

        # about 454 mm; ETA's 450, just beside it
        wait_until(LOPT_AT)
        lopt = VGroup(ftext("best L = π (R² − r²) / 2h", 0.31, AREA),
                      ftext(f"≈ {L_OPT:.0f} mm", 0.46, AREA)).arrange(DOWN, aligned_edge=RIGHT, buff=0.1)
        lopt.next_to(ax.c2p(L_OPT, 1.0), LEFT, buff=0.12).align_to(ax.c2p(0, 0.35), DOWN)
        self.play(FadeIn(lopt, shift=RIGHT * 0.1), run_time=0.8)
        wait_until(ETA_AT)
        eta_pt = ax.c2p(REAL_L, N_of(REAL_L))
        eta = VGroup(label(TEXT["eta"], 0.26, WHITE, True), label("within 1%", 0.24, GREY_B))
        eta.arrange(DOWN, aligned_edge=RIGHT, buff=0.08).next_to(eta_pt, UL, buff=0.1).shift(UP * 0.25 + LEFT * 0.45)
        eta_lead = Line(eta[0].get_right() + RIGHT * 0.08, eta_pt + UL * 0.05).set_stroke(WHITE, 1.4, 0.8)
        eta_dot = Dot(eta_pt, radius=0.06, color=WHITE)
        self.play(Lt.animate.set_value(REAL_L), FadeIn(eta[0]), Create(eta_lead), FadeIn(eta_dot),
                  FadeOut(VGroup(same, r_eq)), show["ghost"].animate.set_value(0.0), run_time=1.0)
        self.wait(0.6)
        self.play(FadeIn(eta[1]), run_time=0.5)

        # about 8 barrel turns, about 30 crown turns
        wait_until(TURNS_AT)
        N450 = N_of(REAL_L)
        t1 = ftext(f"≈ {N450:.0f} turns of the barrel", 0.48, CURVE)
        t2 = ftext(f"× 60/16  ≈  {N450 * CROWN_PER_BARREL:.0f} turns of the crown", 0.48, WHITE)
        tt = VGroup(t1, t2).arrange(DOWN, aligned_edge=LEFT, buff=0.18).move_to(np.array([3.6, 2.95, 0]))
        self.play(FadeIn(t1, shift=RIGHT * 0.1), run_time=0.8)
        wait_until(CROWN_AT)
        self.play(FadeIn(t2, shift=RIGHT * 0.1), run_time=0.8)

        # most turns isn't most energy: a somewhat longer spring
        wait_until(ENERGY_AT)
        e_pt = ax.c2p(L_ENERGY, N_of(L_ENERGY))
        e_lbl = VGroup(VGroup(*[label(t, 0.26, AREA, True) for t in TEXT["energy"]]).arrange(DOWN, aligned_edge=LEFT, buff=0.06),
                       label(TEXT["flat"], 0.24, GREY_B))
        e_lbl.arrange(DOWN, aligned_edge=LEFT, buff=0.1).next_to(e_pt, UR, buff=0.1).shift(RIGHT * 0.25 + UP * 0.2)
        e_lead = Line(e_lbl[0].get_left() + LEFT * 0.08, e_pt + RIGHT * 0.05).set_stroke(AREA, 1.4, 0.8)
        e_dot = Dot(e_pt, radius=0.08, color=AREA)
        self.play(lopt.animate.set_opacity(0.4), run_time=0.4)
        self.play(Lt.animate.set_value(L_ENERGY), run_time=ENERGY_MOVE, rate_func=smooth)
        self.play(FadeIn(e_dot), Create(e_lead), FadeIn(e_lbl[0]), run_time=0.7)
        self.play(FadeIn(e_lbl[1]), run_time=0.5)

        wait_until(FINAL_HOLD_UNTIL)
        curtain.set_fill(opacity=0)
        self.add(curtain)
        self.play(curtain.animate.set_fill(opacity=1), run_time=FADE_OUT)
