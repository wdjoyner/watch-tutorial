"""Film 2, scene 04 - "A bent beam": a short piece of the mainspring is taken
out of the coil, straightened and bent; the strain through its thickness
(stretched outside, compressed inside, a neutral axis between) and its b x h
cross-section; torque grows with curvature; adding the bending up along the
length gives the fundamental stiffness formula of horology, kappa = E b h^3 / 12 L.

Build (render + voice + mux):   python build.py scene04_beam
Render only (quick preview):    PYTHONPATH=.:films/film02_power_source manim -ql films/film02_power_source/scene04_beam.py Scene04
Narration lines and their start times live in scene04_beam.voice.txt.

A flat (2D) scene. Formulas are set with Text, not LaTeX, so no TeX install
is needed. The band's thickness is magnified; the strain colors are schematic.
"""
from manim import *
from movement import vignette, BG, GLOW, FONT_SANS, FONT_SERIF, STEEL_HI, STEEL

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds.
# Keep the timeline roughly in step with scene04_beam.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 1.0
PICK_AT = 1.0                  # a piece of the coil lights up
LIFT_AT, LIFT_DURATION = 1.8, 1.3      # it comes out of the coil and straightens
BEND_AT, BEND_DURATION = 3.4, 1.2      # "It bends it."
STRETCH_AT, COMPRESS_AT, AXIS_AT = 7.2, 8.9, 13.6   # face labels, then the neutral axis
SECTION_AT = 10.6              # the b x h cross-section
TORQUE_AT = 16.0               # "proportional to how much it is bent"
SUM_AT, SUM_DURATION = 21.0, 3.0       # the ribbon lengthens into a long arc
EQ_TIMES = (16.6, 22.2, 24.6)  # the three lines of the derivation
BOX_AT = 27.4                  # "the fundamental stiffness formula of horology"
LEGEND_AT = 29.6
CUBE_AT, ONE_PCT_AT, THREE_PCT_AT = 32.0, 34.6, 36.8
HAIRSPRING_AT = 39.6
FINAL_HOLD = 1.6
FADE_OUT = 1.5

# --- the band (its thickness is magnified) -----------------------------
HOME = np.array([-3.4, -0.9, 0])        # midpoint of the band, once out of the coil
BAND_L, BAND_H = 5.6, 0.62              # length and drawn thickness
LONG_L = 8.6                            # length when "added up along the whole length"
BEND_C = 0.17                           # curvature of the first bend (1 / scene units)
TORQUE_C = 0.29                         # curvature at the peak of the torque demo
ARC_C = 0.55                            # curvature of the long arc (total turn about 270 degrees)
FIBERS = 11                             # strips through the thickness
TICKS = 15                              # cross marks along the length

# --- the coil at the start ---------------------------------------------
COIL_C = np.array([-3.4, 1.15, 0])
COIL_R0, COIL_R1, COIL_TURNS = 0.35, 2.05, 6

# --- colors -------------------------------------------------------------
TENSION = "#ff8a5c"                     # stretched
COMPRESSION = "#6fb3ff"                 # compressed
PICK = "#ffb54a"                        # the piece taken out of the coil
AXIS_COLOR = "#1b2230"                  # the neutral axis: dark, over the pale unstrained middle

# --- text --------------------------------------------------------------
FACE_TEXT = {"stretch": "stretched", "compress": "compressed", "axis": "neutral axis"}
SECTION_TEXT = "cross-section"
EQ_LINES = (("M", "=", "E J  /  ρ", "torque grows with the bending"),
            ("θ", "=", "L  /  ρ", "the bending adds up along the length"),
            ("M", "=", "(E J / L) θ", "with  J = b h³ / 12"))
BOX_CAPTION = "the fundamental stiffness formula of horology"
LEGEND = "κ  stiffness (torque per radian)    E  elasticity of the steel    b  height    h  thickness    L  length"
ONE_PCT = "h × 1.01   ⟹   h³ × 1.0303"
THREE_PCT = "one percent thicker, three percent stiffer"
SPRINGS = ("mainspring", "hairspring")
# =====================================================================


def ftext(s, scale=0.5, color=WHITE):
    """Formula text: serif italic."""
    return Text(s, font=FONT_SERIF, slant=ITALIC, color=color).scale(scale)


def label(s, scale=0.3, color=GREY_B, bold=False):
    return Text(s, font=FONT_SANS, weight=BOLD if bold else NORMAL, color=color).scale(scale)


def strain_color(eps):
    """eps in [-1, 1]: negative = compression (cool), positive = tension (warm)."""
    if eps >= 0:
        return interpolate_color(ManimColor(STEEL_HI), ManimColor(TENSION), min(1, eps))
    return interpolate_color(ManimColor(STEEL_HI), ManimColor(COMPRESSION), min(1, -eps))


class Scene04(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.add(vignette())

        def wait_until(when):
            d = when - self.renderer.time
            if d > 1e-3:
                self.wait(d)

        # ------------------------------------------------------------ the band
        curv, length = ValueTracker(0.0), ValueTracker(BAND_L)
        thick, show_c = ValueTracker(BAND_H), ValueTracker(0.0)      # show_c: strength of the strain colors
        mid = Dot(HOME, radius=0).set_opacity(0)                       # midpoint position (animatable)
        ticks_on = ValueTracker(1.0)

        def frame(s, y, c):
            """Point at arclength s along the centerline, offset y toward the center of curvature."""
            if abs(c) < 1e-6:
                return np.array([s, y, 0.0])
            ph = s * c
            return np.array([np.sin(ph) / c - y * np.sin(ph), (1 - np.cos(ph)) / c + y * np.cos(ph), 0.0])

        def band():
            c, L, H = curv.get_value(), length.get_value(), thick.get_value()
            p0 = mid.get_center()
            s = np.linspace(-L / 2, L / 2, 90)
            g = VGroup()
            ys = np.linspace(-H / 2, H / 2, FIBERS + 1)
            cmax = max(BEND_C, abs(c))
            for y0, y1 in zip(ys[:-1], ys[1:]):
                ym = (y0 + y1) / 2
                lower = [frame(si, y0, c) for si in s]
                upper = [frame(si, y1, c) for si in s[::-1]]
                strip = Polygon(*lower, *upper).shift(p0)
                eps = -ym / (H / 2) * show_c.get_value() * min(1.0, abs(c) / cmax if cmax else 0)
                strip.set_fill(strain_color(eps), 1).set_stroke(width=0)
                g.add(strip)
            edge_lo = VMobject().set_points_smoothly([frame(si, -H / 2, c) for si in s]).shift(p0)
            edge_hi = VMobject().set_points_smoothly([frame(si, H / 2, c) for si in s]).shift(p0)
            g.add(edge_lo.set_stroke(WHITE, 1.5), edge_hi.set_stroke(WHITE, 1.5))
            if ticks_on.get_value() > 0.01:
                for sk in np.linspace(-L / 2 * 0.92, L / 2 * 0.92, TICKS):
                    g.add(Line(frame(sk, -H / 2, c), frame(sk, H / 2, c)).shift(p0)
                          .set_stroke(BG, 1.6, 0.7 * ticks_on.get_value()))
            return g

        def axis_line():
            c, L = curv.get_value(), length.get_value()
            s = np.linspace(-L / 2, L / 2, 60)
            m = DashedVMobject(VMobject().set_points_smoothly([frame(si, 0, c) for si in s]), num_dashes=28)
            return m.shift(mid.get_center()).set_stroke(AXIS_COLOR, 3.5)

        def moment_arrows():
            """Curved arrows at the ends of the band: the bending moment, sized by the curvature."""
            c, L = curv.get_value(), length.get_value()
            k = min(1.0, c / TORQUE_C)
            g = VGroup()
            for sgn in (-1, 1):
                end = frame(sgn * L / 2, 0, c) + mid.get_center()
                tang = normalize(frame(sgn * L / 2 + 1e-3, 0, c) - frame(sgn * L / 2 - 1e-3, 0, c))
                ang = np.arctan2(tang[1], tang[0])
                arc = Arc(radius=0.42 + 0.25 * k, start_angle=ang + (PI / 2 if sgn > 0 else -PI / 2) - sgn * 0.9,
                          angle=sgn * 1.8, arc_center=end, stroke_width=3 + 4 * k, color=GLOW)
                g.add(arc.add_tip(tip_length=0.16 + 0.08 * k, tip_width=0.16 + 0.08 * k))
            return g

        band_mob = always_redraw(band)
        axis_mob = always_redraw(axis_line)
        moments = always_redraw(moment_arrows)

        # ------------------------------------------------------------ the coil, and the piece taken from it
        u = np.linspace(0, COIL_TURNS * TAU, 900)
        r = COIL_R0 + (COIL_R1 - COIL_R0) * u / u[-1]
        coil_pts = np.column_stack([r * np.cos(u), r * np.sin(u), 0 * u]) + COIL_C
        coil = VMobject().set_points_smoothly(coil_pts).set_stroke(STEEL_HI, 4)
        a_mid = (COIL_TURNS - 1) * TAU + 1.5 * PI          # bottom of the outer turn: center of curvature above
        sel = (u > a_mid - 0.55) & (u < a_mid + 0.55)
        piece = VMobject().set_points_smoothly(coil_pts[sel]).set_stroke(PICK, 7)
        r_piece = COIL_R0 + (COIL_R1 - COIL_R0) * a_mid / u[-1]
        piece_mid = COIL_C + np.array([0, -r_piece, 0])

        curtain = FullScreenRectangle().set_fill(BG, 1).set_stroke(width=0)
        self.add(coil, curtain)
        self.play(curtain.animate.set_fill(opacity=0), run_time=FADE_IN)
        self.remove(curtain)
        wait_until(PICK_AT)
        self.play(Create(piece), run_time=0.7)

        # the piece comes out: it becomes the band, at the coil's curvature and thin, then straightens and thickens
        wait_until(LIFT_AT)
        curv.set_value(1 / r_piece)
        length.set_value(1.1 * r_piece)
        thick.set_value(0.08)
        mid.move_to(piece_mid)
        ticks_on.set_value(0.0)
        self.add(band_mob)
        self.remove(piece)
        self.play(curv.animate.set_value(0.0), length.animate.set_value(BAND_L), thick.animate.set_value(BAND_H),
                  mid.animate.move_to(HOME), ticks_on.animate.set_value(1.0), coil.animate.set_stroke(opacity=0.0),
                  run_time=LIFT_DURATION, rate_func=smooth)
        self.remove(coil)

        # it bends: the moment arrows appear and the strain colors come up
        wait_until(BEND_AT)
        self.add(moments)
        self.play(curv.animate.set_value(BEND_C), show_c.animate.set_value(1.0), run_time=BEND_DURATION)

        # the faces and the neutral axis
        c = BEND_C
        lo = frame(0, -BAND_H / 2, c) + HOME
        hi = frame(0, BAND_H / 2, c) + HOME
        stretch = label(FACE_TEXT["stretch"], 0.32, TENSION, True).next_to(lo, DOWN, buff=0.25)
        compress = label(FACE_TEXT["compress"], 0.32, COMPRESSION, True).next_to(hi, UP, buff=0.25)
        ax_end = frame(BAND_L / 2, 0, c) + HOME
        axis_lbl = label(FACE_TEXT["axis"], 0.3, GLOW, True).next_to(ax_end, RIGHT, buff=0.6).shift(UP * 0.55)
        axis_lead = Line(ax_end + RIGHT * 0.08, axis_lbl.get_left() + LEFT * 0.08).set_stroke(GLOW, 1.4, 0.8)
        axis_lbl = VGroup(axis_lead, axis_lbl)
        wait_until(STRETCH_AT)
        self.play(FadeIn(stretch, shift=UP * 0.1), run_time=0.6)
        wait_until(COMPRESS_AT)
        self.play(FadeIn(compress, shift=DOWN * 0.1), run_time=0.6)

        # the cross-section: b wide, h thick, strain varying linearly through h
        wait_until(SECTION_AT)
        sx = np.array([3.6, -0.6, 0])
        bw, hh = 2.4, BAND_H * 1.6
        rows = 16
        section = VGroup()
        for k in range(rows):
            y0 = -hh / 2 + hh * k / rows
            yc = y0 + hh / (2 * rows)
            section.add(Rectangle(width=bw, height=hh / rows).move_to(sx + UP * yc)
                        .set_fill(strain_color(-yc / (hh / 2)), 1).set_stroke(width=0))
        section.add(Rectangle(width=bw, height=hh).move_to(sx).set_stroke(WHITE, 1.5))
        sec_axis = DashedLine(sx + LEFT * bw / 2, sx + RIGHT * bw / 2, dash_length=0.08).set_stroke(AXIS_COLOR, 3.5)
        b_brace = BraceBetweenPoints(sx + LEFT * bw / 2 + DOWN * hh / 2, sx + RIGHT * bw / 2 + DOWN * hh / 2, DOWN)
        b_lbl = ftext("b", 0.5).next_to(b_brace, DOWN, buff=0.08)
        h_brace = BraceBetweenPoints(sx + LEFT * bw / 2 + UP * hh / 2, sx + LEFT * bw / 2 + DOWN * hh / 2, LEFT)
        h_lbl = ftext("h", 0.5).next_to(h_brace, LEFT, buff=0.08)
        # strain profile: a straight line through zero at the neutral axis
        px = sx + RIGHT * (bw / 2 + 0.9)
        prof_axis = Line(px + DOWN * hh * 0.7, px + UP * hh * 0.7).set_stroke(GREY_B, 1.5)
        prof = Line(px + DOWN * hh / 2 + RIGHT * 0.55, px + UP * hh / 2 + LEFT * 0.55).set_stroke(WHITE, 2.5)
        tri = VGroup(Polygon(px, px + DOWN * hh / 2, px + DOWN * hh / 2 + RIGHT * 0.55).set_fill(TENSION, 0.5),
                     Polygon(px, px + UP * hh / 2, px + UP * hh / 2 + LEFT * 0.55).set_fill(COMPRESSION, 0.5))
        tri.set_stroke(width=0)
        sec_title = label(SECTION_TEXT, 0.3).next_to(section, UP, buff=0.3)
        sec_group = VGroup(section, b_brace, b_lbl, h_brace, h_lbl, tri, prof_axis, prof, sec_title)
        self.play(FadeIn(VGroup(section, sec_title)), GrowFromCenter(b_brace), FadeIn(b_lbl),
                  GrowFromCenter(h_brace), FadeIn(h_lbl), run_time=0.9)
        self.play(Create(prof_axis), FadeIn(tri), Create(prof), run_time=0.8)

        wait_until(AXIS_AT)
        self.add(axis_mob)
        self.play(FadeIn(axis_lbl), Create(sec_axis), run_time=0.7)
        self.remove(axis_mob)
        self.add(axis_mob)

        # ------------------------------------------------------------ torque grows with curvature
        wait_until(TORQUE_AT)
        eq_x = 0.7
        eqs = []
        for k, (lhs, eq, rhs, note) in enumerate(EQ_LINES):
            row = VGroup(ftext(lhs, 0.62), ftext(eq, 0.62, GREY_B), ftext(rhs, 0.62)).arrange(RIGHT, buff=0.22)
            row.move_to(np.array([eq_x, 2.75 - 0.95 * k, 0]), aligned_edge=LEFT)
            eqs.append(VGroup(row, label(note, 0.24).next_to(row, DOWN, aligned_edge=LEFT, buff=0.1)))
        self.play(FadeOut(VGroup(sec_group, sec_axis, stretch, compress, axis_lbl)), run_time=0.5)
        wait_until(EQ_TIMES[0])
        self.play(FadeIn(eqs[0], shift=RIGHT * 0.15), run_time=0.7)
        self.play(curv.animate.set_value(TORQUE_C), run_time=1.3, rate_func=smooth)
        self.play(curv.animate.set_value(BEND_C), run_time=1.1, rate_func=smooth)

        # ------------------------------------------------------------ adding it up along the length
        wait_until(SUM_AT)
        self.remove(axis_mob)
        self.play(length.animate.set_value(LONG_L), curv.animate.set_value(ARC_C), thick.animate.set_value(0.32),
                  ticks_on.animate.set_value(0.0), mid.animate.move_to(HOME + DOWN * 0.9),
                  run_time=SUM_DURATION, rate_func=smooth)
        self.remove(moments)
        # tangent arrows at the two ends, and the total turn between them
        c, L = ARC_C, LONG_L
        p_mid = mid.get_center()
        ends = []
        for sgn in (-1, 1):
            e = frame(sgn * L / 2, 0, c) + p_mid
            t = normalize(frame(sgn * L / 2 + 1e-3, 0, c) - frame(sgn * L / 2 - 1e-3, 0, c))
            ends.append((e, t))
        tangents = VGroup(*[Arrow(e, e + t * 0.9, buff=0, stroke_width=4, color=GLOW,
                                  max_tip_length_to_length_ratio=0.25) for e, t in ends])
        center_c = p_mid + UP / c
        theta_arc = Arc(radius=0.55, start_angle=-PI / 2 - L * c / 2, angle=L * c, arc_center=center_c,
                        stroke_width=3, color=GLOW)
        theta_lbl = ftext("θ", 0.55, GLOW).move_to(center_c + DOWN * 0.95)
        L_lbl = ftext("L", 0.55).next_to(frame(0, -0.16, c) + p_mid, DOWN, buff=0.15)
        wait_until(EQ_TIMES[1])
        self.play(GrowArrow(tangents[0]), GrowArrow(tangents[1]), Create(theta_arc), FadeIn(theta_lbl),
                  FadeIn(L_lbl), FadeIn(eqs[1], shift=RIGHT * 0.15), run_time=0.9)
        wait_until(EQ_TIMES[2])
        self.play(FadeIn(eqs[2], shift=RIGHT * 0.15), run_time=0.8)

        # the boxed formula
        frac = VGroup(ftext("E b h³", 0.8), Line(LEFT * 0.9, RIGHT * 0.9).set_stroke(WHITE, 2),
                      ftext("12 L", 0.8)).arrange(DOWN, buff=0.12)
        formula = VGroup(ftext("κ", 0.85, GLOW), ftext("=", 0.8, GREY_B), frac).arrange(RIGHT, buff=0.25)
        formula.move_to(np.array([eq_x + 2.3, -1.35, 0]))
        box = SurroundingRectangle(formula, color=GLOW, buff=0.25, corner_radius=0.08, stroke_width=2.5)
        box_cap = label(BOX_CAPTION, 0.27, GLOW).next_to(box, DOWN, buff=0.18)
        m_kt = ftext("M = κ θ", 0.5, GREY_B).next_to(box, UP, buff=0.2)
        legend = label(LEGEND, 0.24).to_edge(DOWN, buff=0.6)
        wait_until(BOX_AT)
        self.play(Write(formula), Create(box), FadeIn(m_kt), run_time=1.4)
        self.play(FadeIn(box_cap), run_time=0.6)
        wait_until(LEGEND_AT)
        self.play(FadeIn(legend), run_time=0.6)

        # thickness cubed
        wait_until(CUBE_AT)
        h3 = frac[0]
        self.play(FadeOut(VGroup(*eqs)), h3.animate.set_color(PICK), run_time=0.6)
        self.play(Indicate(h3, color=PICK, scale_factor=1.15), run_time=0.9)
        one = ftext(ONE_PCT, 0.5).move_to(np.array([eq_x + 2.3, 2.3, 0]))
        three = label(THREE_PCT, 0.3, PICK, True).next_to(one, DOWN, buff=0.3)
        wait_until(ONE_PCT_AT)
        self.play(FadeIn(one, shift=DOWN * 0.1), run_time=0.7)
        wait_until(THREE_PCT_AT)
        self.play(FadeIn(three, shift=DOWN * 0.1), run_time=0.7)

        # the same formula sets the hairspring
        wait_until(HAIRSPRING_AT)
        old = VGroup(band_mob, tangents, theta_arc, theta_lbl, L_lbl, one, three)
        self.remove(band_mob)
        self.add(band_mob)

        def spiral(c0, r0, r1, turns, width, color=STEEL_HI):
            uu = np.linspace(0, turns * TAU, 1200)
            rr = r0 + (r1 - r0) * uu / uu[-1]
            pts = np.column_stack([rr * np.cos(uu), rr * np.sin(uu), 0 * uu]) + c0
            return VMobject().set_points_smoothly(pts).set_stroke(color, width)

        main = spiral(np.array([-4.6, 0.5, 0]), 0.3, 1.55, 6, 5.5)
        hair = spiral(np.array([-1.5, 0.5, 0]), 0.12, 1.2, 13, 1.1)
        names = VGroup(label(SPRINGS[0], 0.3, GLOW, True).next_to(main, DOWN, buff=0.3),
                       label(SPRINGS[1], 0.3, GLOW, True).next_to(hair, DOWN, buff=0.3))
        names[1].align_to(names[0], DOWN)
        self.play(FadeOut(old), h3.animate.set_color(WHITE), run_time=0.7)
        self.play(Create(main), Create(hair), FadeIn(names), run_time=1.6)

        self.wait(FINAL_HOLD)
        curtain.set_fill(opacity=0)
        self.add(curtain)
        self.play(curtain.animate.set_fill(opacity=1), run_time=FADE_OUT)
