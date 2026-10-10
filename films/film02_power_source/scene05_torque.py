"""Film 2, scene 05 - "Torque falls as it unwinds": the spring unwinds on the
left while a torque-versus-turns plot on the right follows it: first the
ideal straight line M = kappa theta with the stored energy shaded under it,
then a real spring's curve (steep at full wind, a plateau, a sag at the end);
the S-shaped free form that flattens the middle; and the firm stop at full
wind of a hand-wound barrel.

Build (render + voice + mux):   python build.py scene05_torque
Render only (quick preview):    PYTHONPATH=.:films/film02_power_source manim -ql films/film02_power_source/scene05_torque.py Scene05
Narration lines and their start times live in scene05_torque.voice.txt.

The x-axis is turns wound from let down, 0 to the 6497's development of
about 8 turns (barrel.development()). The torque axis carries no numbers:
the real curve is schematic (its shape, not its values, is the point).
"""
from manim import *
from shapely import affinity
from movement import vignette, BG, GLOW, FONT_SANS, FONT_SERIF, BRASS, BRASS_DK, BRASS_HI, STEEL, STEEL_HI, RUBY_HI
from barrel import pack_state_g, arbor_core_g, drum_floor_g, drum_wall_g, development, vm, R_ROOT, HOOK_IN_DEG

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds.
# Keep the timeline roughly in step with scene05_torque.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 1.0
FULL_AT = 1.4                         # the dot at full wind
UNWIND1 = (4.2, 7.8, 4.0)             # (start, end, turns wound at the end): "the push weakens"
LINE_AT, AREA_AT = 9.6, 12.4          # the whole line; the shaded energy
REAL_AT, REAL_DURATION = 15.8, 2.2    # the real curve
STEEP_AT, SAG_AT = 18.4, 21.7         # "coils press together", "sagging near the end"
UNWIND2 = (19.4, 21.6, 0.9)
FREEFORM_AT = 25.4                    # the free forms, ordinary and S-curve
USEFUL_AT = 28.4                      # "flatten the useful middle"
STEADY_AT = 31.4                      # "a steadier push"
FREEFORM_OUT = 33.8
REWIND = (36.0, 39.8)                 # wound back up to full
STOP_AT = 39.9                        # "a firm stop"
FINAL_HOLD = 3.9                      # the last line ends about 44 s; the fade starts after it
FADE_OUT = 1.5

# --- layout -------------------------------------------------------------
SPRING_C = np.array([-4.1, -0.3, 0])  # the barrel, seen from above
SPRING_R = 2.2                        # drawn radius of the drum's outside
AX_ORIGIN = np.array([0.6, -2.4, 0])
AX_W, AX_H = 5.9, 4.3

# --- the curves (torque relative to the straight line's value at full wind) ---
def real_torque(a, n):
    """A schematic real torque curve: a sag near let down, a long plateau, and a
    steep rise in the last fraction of a turn where the coils press together."""
    return (0.25 + 0.33 * (1 - np.exp(-a / 0.8)) + 0.04 * a / n + 0.33 * np.exp((a - n) / 0.35))


USEFUL = (2.0, 7.0)                   # the flat useful middle, in turns wound

# --- colors and text ---------------------------------------------------
LINE_COLOR = GREY_A
REAL_COLOR = GLOW
ENERGY = "#ffb54a"
TEXT = {"x": "turns wound", "y": "torque", "line": "M = κ θ", "energy": "stored energy",
        "steep": "coils press together", "sag": "sag near the end", "useful": "useful range",
        "steady": "flatter: a steadier push", "ordinary": "ordinary spring", "scurve": "S-curve spring",
        "free": "free form, out of the barrel", "stop": "hooked to the drum: a firm stop",
        "full": "full wind", "down": "let down"}
# =====================================================================


def label(s, scale=0.28, color=GREY_B, bold=False):
    return Text(s, font=FONT_SANS, weight=BOLD if bold else NORMAL, color=color).scale(scale)


def free_form(k_fn, total=14.0, n=900):
    """A curve from its curvature along the length: the shape a spring takes out of its barrel."""
    s = np.linspace(0, total, n)
    th = np.concatenate([[0], np.cumsum(k_fn(s[:-1]) * np.diff(s))])
    x = np.concatenate([[0], np.cumsum(np.cos(th[:-1]) * np.diff(s))])
    y = np.concatenate([[0], np.cumsum(np.sin(th[:-1]) * np.diff(s))])
    pts = np.column_stack([x, y, 0 * x])
    return VMobject().set_points_smoothly(pts[::3])


class Scene05(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.add(vignette())
        N = development()                                 # about 8 turns

        def wait_until(when):
            d = when - self.renderer.time
            if d > 1e-3:
                self.wait(d)

        turns = ValueTracker(N - 0.02)                    # turns wound
        mix = ValueTracker(0.0)                           # 0: the dot follows the line; 1: the real curve

        # ------------------------------------------------------------ the spring, from above
        s_mm = SPRING_R / (R_ROOT + 0.2)

        def sc(g):
            return affinity.scale(g, s_mm, s_mm, origin=(0, 0))

        base = VGroup(vm(sc(drum_floor_g()), BRASS_DK, stroke=BRASS_DK, sw=0),
                      vm(sc(drum_wall_g()), BRASS, stroke=BRASS_HI, sw=0.8)).shift(SPRING_C)

        def torque_now():
            a = turns.get_value()
            m = mix.get_value()
            return (1 - m) * a / N + m * real_torque(a, N)

        def spring():
            inner, outer, free, arbor_deg, w = pack_state_g(max(0.0, turns.get_value()), outer_deg=200.0)
            core = affinity.rotate(arbor_core_g(), arbor_deg - HOOK_IN_DEG, origin=(0, 0))
            g = VGroup(vm(sc(outer), STEEL_HI, stroke=WHITE, sw=0.4), vm(sc(inner), STEEL_HI, stroke=WHITE, sw=0.4),
                       vm(sc(free), STEEL_HI, stroke=WHITE, sw=0.4), vm(sc(core), STEEL, stroke=STEEL_HI, sw=0.6))
            g.shift(SPRING_C)
            # the torque on the arbor: a curved arrow whose sweep and weight follow the torque
            t = max(0.05, torque_now())
            arc = Arc(radius=SPRING_R + 0.28, start_angle=PI / 2 + 0.2, angle=-(0.35 + 1.25 * t) * PI / 2 * 1.4,
                      arc_center=SPRING_C, stroke_width=2 + 6 * t, color=ENERGY)
            g.add(arc.add_tip(tip_length=0.14 + 0.12 * t, tip_width=0.14 + 0.12 * t))
            return g

        spring_mob = always_redraw(spring)

        # ------------------------------------------------------------ the plot
        ax = Axes(x_range=[0, 8.6, 1], y_range=[0, 1.12, 0.25], x_length=AX_W, y_length=AX_H,
                  tips=True, axis_config={"color": GREY_B, "stroke_width": 2, "include_ticks": False},
                  x_axis_config={"include_ticks": True, "tick_size": 0.05})
        ax.move_to(AX_ORIGIN, aligned_edge=DL)
        x_lbl = label(TEXT["x"], 0.28).next_to(ax.x_axis, DOWN, buff=0.38).align_to(ax.x_axis, RIGHT)
        y_lbl = label(TEXT["y"], 0.28).next_to(ax.y_axis, UP, buff=0.12).align_to(ax.y_axis, LEFT)
        nums = VGroup(*[label(str(k), 0.24).next_to(ax.c2p(k, 0), DOWN, buff=0.12) for k in (0, 2, 4, 6, 8)])
        ends = VGroup(label(TEXT["down"], 0.22).next_to(nums[0], DOWN, buff=0.08),
                      label(TEXT["full"], 0.22).next_to(nums[-1], DOWN, buff=0.08))
        line = ax.plot(lambda a: a / N, x_range=[0, N], color=LINE_COLOR, stroke_width=3)
        line_lbl = Text(TEXT["line"], font=FONT_SERIF, slant=ITALIC, color=LINE_COLOR).scale(0.4)
        line_lbl.next_to(ax.c2p(N * 0.8, 0.8), UL, buff=0.08)
        area = ax.get_area(line, x_range=[0, N], color=ENERGY, opacity=0.28)
        area_lbl = label(TEXT["energy"], 0.28, ENERGY, True).move_to(ax.c2p(N * 0.7, 0.22))
        real = ax.plot(lambda a: real_torque(a, N), x_range=[0, N], color=REAL_COLOR, stroke_width=4)

        def dot():
            a = turns.get_value()
            p = ax.c2p(a, torque_now())
            return VGroup(DashedLine(ax.c2p(a, 0), p, dash_length=0.06).set_stroke(GREY_B, 1.5),
                          Dot(p, radius=0.08, color=ENERGY))

        dot_mob = always_redraw(dot)
        trace = TracedPath(lambda: ax.c2p(turns.get_value(), turns.get_value() / N), stroke_color=ENERGY,
                           stroke_width=4)

        curtain = FullScreenRectangle().set_fill(BG, 1).set_stroke(width=0)
        self.add(base, spring_mob, ax, x_lbl, y_lbl, nums, ends, curtain)
        self.play(curtain.animate.set_fill(opacity=0), run_time=FADE_IN)
        self.remove(curtain)

        # full wind: the hardest push
        wait_until(FULL_AT)
        self.play(FadeIn(dot_mob), run_time=0.6)
        self.add(trace)

        # unwinding: the push weakens, along the straight line
        wait_until(UNWIND1[0])
        self.play(turns.animate.set_value(UNWIND1[2]), run_time=UNWIND1[1] - UNWIND1[0], rate_func=smooth)
        wait_until(LINE_AT)
        self.play(Create(line), FadeIn(line_lbl), FadeOut(trace), run_time=1.2)
        wait_until(AREA_AT)
        self.play(FadeIn(area), FadeIn(area_lbl), run_time=1.0)

        # the real curve; the dot moves over to it
        wait_until(REAL_AT)
        self.play(Create(real), mix.animate.set_value(1.0), area.animate.set_fill(opacity=0.12),
                  area_lbl.animate.set_opacity(0.5), run_time=REAL_DURATION)
        steep_pt = ax.c2p(N - 0.12, real_torque(N - 0.12, N))
        steep_lbl = label(TEXT["steep"], 0.26, REAL_COLOR, True).next_to(steep_pt, LEFT, buff=0.35).shift(UP * 0.35)
        steep_lead = Line(steep_lbl.get_right() + RIGHT * 0.06, steep_pt).set_stroke(REAL_COLOR, 1.4, 0.8)
        sag_pt = ax.c2p(0.25, real_torque(0.25, N))
        sag_lbl = label(TEXT["sag"], 0.26, REAL_COLOR, True).next_to(sag_pt, UP, buff=1.25).shift(RIGHT * 0.5)
        sag_lead = Line(sag_lbl.get_bottom() + DOWN * 0.06, sag_pt).set_stroke(REAL_COLOR, 1.4, 0.8)
        wait_until(STEEP_AT)
        self.play(Create(steep_lead), FadeIn(steep_lbl), run_time=0.7)
        wait_until(UNWIND2[0])
        self.play(turns.animate.set_value(UNWIND2[2]), run_time=UNWIND2[1] - UNWIND2[0], rate_func=smooth)
        wait_until(SAG_AT)
        self.play(Create(sag_lead), FadeIn(sag_lbl), run_time=0.7)

        # the free form: an ordinary spring and an S-curve spring, out of the barrel
        wait_until(FREEFORM_AT)
        ordinary = free_form(lambda s: 4.0 / (s + 0.6) + 0.1, total=16)
        scurve = free_form(lambda s: 4.0 / (s + 0.6) - 0.55, total=16)
        for m, c in ((ordinary, np.array([-5.2, 0.4, 0])), (scurve, np.array([-2.7, 0.4, 0]))):
            m.set_stroke(STEEL_HI, 3).scale_to_fit_height(2.6).move_to(c)
        scurve.set_stroke(ENERGY, 3.5)
        f_lbls = VGroup(label(TEXT["ordinary"], 0.26, GREY_B, True).next_to(ordinary, DOWN, buff=0.3),
                        label(TEXT["scurve"], 0.26, ENERGY, True).next_to(scurve, DOWN, buff=0.3))
        f_lbls[1].align_to(f_lbls[0], DOWN)
        f_title = label(TEXT["free"], 0.28).move_to(np.array([-3.95, 2.7, 0]))
        self.play(FadeOut(VGroup(spring_mob, base)), run_time=0.6)
        self.play(Create(ordinary), Create(scurve), FadeIn(f_lbls), FadeIn(f_title), run_time=1.6)

        # the useful middle, and why flatter is better
        wait_until(USEFUL_AT)
        band = Polygon(ax.c2p(USEFUL[0], 0), ax.c2p(USEFUL[1], 0), ax.c2p(USEFUL[1], 1.05), ax.c2p(USEFUL[0], 1.05))
        band.set_fill(GLOW, 0.08).set_stroke(GLOW, 1, 0.4)
        useful_lbl = label(TEXT["useful"], 0.26, GLOW, True).next_to(ax.c2p(sum(USEFUL) / 2, 1.05), DOWN, buff=0.12)
        self.play(FadeIn(band), FadeIn(useful_lbl), FadeOut(VGroup(steep_lbl, steep_lead, sag_lbl, sag_lead)),
                  real.animate.set_stroke(width=5), run_time=0.9)
        wait_until(STEADY_AT)
        y0 = real_torque(USEFUL[0], N)
        y1 = real_torque(USEFUL[1], N)
        flat = DoubleArrow(ax.c2p(USEFUL[0], (y0 + y1) / 2 + 0.16), ax.c2p(USEFUL[1], (y0 + y1) / 2 + 0.16),
                           buff=0, stroke_width=3, color=GLOW, tip_length=0.15)
        steady = label(TEXT["steady"], 0.26, GLOW).next_to(flat, UP, buff=0.1)
        self.play(GrowFromCenter(flat), FadeIn(steady), run_time=0.8)

        # back to the barrel; wind up to the firm stop
        wait_until(FREEFORM_OUT)
        self.play(FadeOut(VGroup(ordinary, scurve, f_lbls, f_title)), FadeIn(VGroup(base, spring_mob)),
                  FadeOut(VGroup(flat, steady)), run_time=0.8)
        wait_until(REWIND[0])
        self.play(turns.animate.set_value(N), run_time=REWIND[1] - REWIND[0], rate_func=rate_functions.ease_in_quad)
        wall = Line(ax.c2p(N + 0.03, 0), ax.c2p(N + 0.03, 1.08)).set_stroke(RUBY_HI, 5)
        stop_lbl = label(TEXT["stop"], 0.26, RUBY_HI, True).next_to(wall, UP, buff=0.12).shift(LEFT * 1.4)
        wait_until(STOP_AT)
        self.play(Create(wall), FadeIn(stop_lbl), turns.animate(rate_func=there_and_back).set_value(N - 0.08),
                  run_time=0.6)

        self.wait(FINAL_HOLD)
        curtain.set_fill(opacity=0)
        self.add(curtain)
        self.play(curtain.animate.set_fill(opacity=1), run_time=FADE_OUT)
