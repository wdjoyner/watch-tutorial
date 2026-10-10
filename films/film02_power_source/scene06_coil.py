"""Film 2, scene 06 - "Advanced: the geometry of the coil": a coiled ribbon is an
Archimedean spiral (each turn adds one thickness h to the radius); unrolled,
it is a long thin rectangle L x h whose area is the ring the coil fills, so
L h = pi (r2^2 - r1^2); applied to the 6497's wound spring, that gives a
little under half a meter.

Build (render + voice + mux):   python build.py scene06_coil
Render only (quick preview):    PYTHONPATH=.:films/film02_power_source manim -ql films/film02_power_source/scene06_coil.py Scene06
Narration lines and their start times live in scene06_coil.voice.txt.

The demonstration coil is schematic (6.5 turns, thick ribbon). It is drawn
with a hairline gap between turns so the turns read; the area argument
uses the pitch h. The coil unrolls like a carpet: it rolls along a floor and
lays the ribbon down behind it. The 6497 numbers come from barrel.py.
"""
from manim import *
from shapely.geometry import LineString
from shapely import affinity
from movement import vignette, BG, GLOW, FONT_SANS, FONT_SERIF, BRASS, BRASS_DK, BRASS_HI, STEEL, STEEL_HI
from barrel import arbor_core_g, drum_floor_g, drum_wall_g, pack_turns, vm, R_ROOT, CORE_R, REAL_H, REAL_L

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds.
# Keep the timeline roughly in step with scene06_coil.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 0.8
GROW_AT, GROW_DURATION = 1.0, 3.8        # the spiral draws itself from the arbor out
RULER_AT, PITCH_AT = 5.0, 6.2            # ruler across the turns; "+h each turn"
RADII_AT = 10.0                          # r1 and r2
UNROLL_AT = 14.0                         # camera pulls back, coil moves to the floor
UNROLL_MOVE, UNROLL_DURATION = 1.4, 3.0
STRIP_LABELS_AT = 18.0                   # L and h on the strip
ROLLUP_AT, ROLLUP_DURATION = 18.9, 1.8   # "Coiled, the same area fills a ring"
RING_AT = 20.6
EQ_AT, SOLVE_AT = 22.6, 24.8
REAL_AT = 27.4                           # the 6497
REAL_TIMES = {"r1": 28.4, "r2": 29.6, "h": 31.0, "L": 33.0, "catalog": 34.4}
FINAL_HOLD = 1.6
FADE_OUT = 1.5

# --- the demonstration coil (scene units, before scaling) -----------------
R_IN = 0.55                              # arbor radius
H = 0.17                                 # ribbon thickness = pitch of the spiral
TURNS = 6.5
GAP = 0.18                               # drawn gap between turns, as a fraction of h
COIL_C = np.array([-3.3, 0.15, 0])       # where the coil sits in the opening shot
COIL_SCALE = 1.42
FLOOR_Y = -3.0                           # the floor the coil rolls along (unrolled view)

# --- colors and text ---------------------------------------------------
RIBBON = STEEL_HI
AREA = "#ffb54a"
EQ_X = 0.2                               # left edge of the equations
TEXT = {"pitch": "each turn adds one thickness", "long": "a long thin rectangle",
        "same": "the same area", "real": "ETA 6497, fully wound", "arbor": "arbor",
        "catalog": "catalog value: 450 mm", "half": "a little under half a meter"}
# =====================================================================


def ftext(s, scale=0.5, color=WHITE):
    return Text(s, font=FONT_SERIF, slant=ITALIC, color=color).scale(scale)


def label(s, scale=0.28, color=GREY_B, bold=False):
    return Text(s, font=FONT_SANS, weight=BOLD if bold else NORMAL, color=color).scale(scale)


# centerline of the coil, by arclength from the inner end; it winds clockwise
# going outward, so at the bottom of the coil the outer part heads left
_phi = np.linspace(0, TURNS * TAU, 4000)
_r = R_IN + H / 2 + H * _phi / TAU
_xy = np.column_stack([_r * np.cos(-_phi), _r * np.sin(-_phi)])
_s = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(_xy, axis=0), axis=1))])
S_TOTAL = _s[-1]
R_OUT = R_IN + H * TURNS + H              # outside face of the coil (approximately)


def ribbon_g(pts):
    if len(pts) < 2:
        return None
    # simplify first: a near-zero last segment makes the flat end cap spike far off
    return LineString(pts).simplify(1e-4).buffer(H * (1 - GAP) / 2, cap_style=2, join_style=2)


class Scene06(MovingCameraScene):
    def construct(self):
        self.camera.background_color = BG
        cam = self.camera.frame
        home_w = cam.width
        vig = vignette()
        # keep the vignette fixed to the frame while the camera zooms
        vig.add_updater(lambda m: m.stretch_to_fit_width(cam.width).stretch_to_fit_height(cam.height).move_to(cam.get_center()))
        self.add(vig)

        def wait_until(when):
            d = when - self.renderer.time
            if d > 0.07:
                self.wait(d)

        grow = ValueTracker(0.0)          # fraction of the ribbon drawn, from the inner end
        laid = ValueTracker(0.0)          # length unrolled from the outer end
        place = ValueTracker(0.0)         # 0: big, in the opening position; 1: on the floor
        x_start = -S_TOTAL / 2 - 1.0      # where the outer end touches the floor

        def coil():
            ell = laid.get_value()
            keep = _s <= min(grow.get_value() * S_TOTAL, S_TOTAL - ell) + 1e-9
            pts = _xy[keep]
            g = VGroup()
            if ell > 0.02:   # a near-zero-width rectangle makes Cairo draw a stray line
                strip = Rectangle(width=ell, height=H * (1 - GAP)).set_fill(RIBBON, 1).set_stroke(WHITE, 0.5)
                strip.move_to(np.array([x_start + ell / 2, FLOOR_Y + H / 2, 0]))
                g.add(strip)
            if len(pts) < 2:
                return g
            # roll: turn the coil so the peel point (end of what is left) is at the bottom
            pe = pts[-1]
            alpha = -PI / 2 - np.arctan2(pe[1], pe[0]) if ell > 0 or place.get_value() > 0 else 0.0
            rot = np.array([[np.cos(alpha), -np.sin(alpha)], [np.sin(alpha), np.cos(alpha)]])
            pts_r = pts @ rot.T
            u = place.get_value()
            sc = COIL_SCALE + (1 - COIL_SCALE) * u
            r_peel = np.linalg.norm(pe)
            floor_c = np.array([x_start + ell, FLOOR_Y + H / 2 + r_peel, 0])
            c = COIL_C * (1 - u) + floor_c * u
            rib = ribbon_g(pts_r)
            g.add(vm(affinity.scale(rib, sc, sc, origin=(0, 0)), RIBBON, stroke=WHITE, sw=0.5).shift(c))
            return g

        arbor = Circle(radius=R_IN * 0.92 * COIL_SCALE).set_fill(STEEL, 1).set_stroke(STEEL_HI, 1).move_to(COIL_C)
        coil_mob = always_redraw(coil)

        curtain = FullScreenRectangle().set_fill(BG, 1).set_stroke(width=0)
        self.add(arbor, coil_mob, curtain)
        self.play(curtain.animate.set_fill(opacity=0), run_time=FADE_IN)
        self.remove(curtain)

        # ------------------------------------------------------------ the spiral draws itself
        wait_until(GROW_AT)
        self.play(grow.animate.set_value(1.0), run_time=GROW_DURATION, rate_func=rate_functions.ease_in_out_sine)

        # a ruler across the turns: each crossing is one thickness further out
        wait_until(RULER_AT)
        ang = 0.0
        crossings = [R_IN + H / 2 + H * k for k in range(int(TURNS) + 1)]
        ruler = Line(COIL_C, COIL_C + RIGHT * (R_OUT + 0.5) * COIL_SCALE).set_stroke(GLOW, 2)
        ticks = VGroup(*[Line(UP * 0.12, DOWN * 0.12).move_to(COIL_C + RIGHT * rc * COIL_SCALE).set_stroke(GLOW, 2.5)
                         for rc in crossings])
        self.play(Create(ruler), LaggedStart(*[Create(t) for t in ticks], lag_ratio=0.15), run_time=1.0)
        wait_until(PITCH_AT)
        a = COIL_C + RIGHT * crossings[-2] * COIL_SCALE
        b = COIL_C + RIGHT * crossings[-1] * COIL_SCALE
        brace = BraceBetweenPoints(a, b, UP, buff=0.18).set_color(GLOW)
        h_lbl = ftext("h", 0.5, GLOW).next_to(brace, UP, buff=0.06)
        pitch_note = label(TEXT["pitch"], 0.28, GLOW).next_to(COIL_C + RIGHT * (R_OUT + 0.6) * COIL_SCALE, RIGHT, buff=0.2)
        spiral_eq = ftext("r = r₁ + h · (turns)", 0.5).next_to(pitch_note, DOWN, aligned_edge=LEFT, buff=0.25)
        self.play(GrowFromCenter(brace), FadeIn(h_lbl), FadeIn(pitch_note), run_time=0.8)
        self.play(FadeIn(spiral_eq, shift=RIGHT * 0.1), run_time=0.7)

        # the inner and outer radii
        wait_until(RADII_AT)
        r1_end = COIL_C + np.array([np.cos(2.4), np.sin(2.4), 0]) * R_IN * COIL_SCALE
        r2_end = COIL_C + np.array([np.cos(3.75), np.sin(3.75), 0]) * R_OUT * COIL_SCALE
        r1 = VGroup(Arrow(COIL_C, r1_end, buff=0, stroke_width=3, color=AREA, max_tip_length_to_length_ratio=0.3),
                    ftext("r₁", 0.45, AREA).next_to(r1_end, UL, buff=0.05))
        r2 = VGroup(Arrow(COIL_C, r2_end, buff=0, stroke_width=3, color=AREA, max_tip_length_to_length_ratio=0.1),
                    ftext("r₂", 0.45, AREA).next_to(r2_end, DL, buff=0.05))
        self.play(FadeOut(VGroup(ruler, ticks, brace, h_lbl, spiral_eq, pitch_note)), GrowArrow(r1[0]),
                  FadeIn(r1[1]), GrowArrow(r2[0]), FadeIn(r2[1]), run_time=0.9)

        # ------------------------------------------------------------ unroll it into a long thin rectangle
        wait_until(UNROLL_AT)
        z = (S_TOTAL + 7.0) / home_w
        view_c = np.array([0.0, FLOOR_Y + 0.25 * home_w * z * 9 / 16 * 0.6, 0])
        self.play(cam.animate.scale(z).move_to(view_c), place.animate.set_value(1.0),
                  FadeOut(VGroup(r1, r2, arbor)), run_time=UNROLL_MOVE, rate_func=smooth)
        self.play(laid.animate.set_value(S_TOTAL), run_time=UNROLL_DURATION, rate_func=rate_functions.ease_in_out_sine)
        wait_until(STRIP_LABELS_AT)
        y_top = FLOOR_Y + H
        L_brace = BraceBetweenPoints(np.array([x_start, y_top, 0]), np.array([x_start + S_TOTAL, y_top, 0]), UP,
                                     buff=0.3 * z).stretch(z, 1)
        L_lbl = ftext("L", 0.5 * z).next_to(L_brace, UP, buff=0.1 * z)
        long_lbl = label(TEXT["long"], 0.28 * z, GLOW).next_to(L_lbl, UP, buff=0.15 * z)
        h_end = ftext("h", 0.5 * z, GLOW).next_to(np.array([x_start + S_TOTAL, FLOOR_Y + H / 2, 0]), RIGHT, buff=0.25 * z)
        self.play(FadeIn(L_brace), FadeIn(L_lbl), FadeIn(long_lbl), FadeIn(h_end), run_time=0.7)

        # rolled back up, the same area fills a ring
        wait_until(ROLLUP_AT)
        self.play(FadeOut(VGroup(L_brace, L_lbl, long_lbl, h_end)), laid.animate.set_value(0.0),
                  run_time=ROLLUP_DURATION * 0.55, rate_func=rate_functions.ease_in_quad)
        self.play(cam.animate.scale(1 / z).move_to(ORIGIN), place.animate.set_value(0.0), FadeIn(arbor),
                  run_time=ROLLUP_DURATION * 0.45, rate_func=smooth)
        wait_until(RING_AT)
        ring = Annulus(inner_radius=R_IN * COIL_SCALE, outer_radius=R_OUT * COIL_SCALE).move_to(COIL_C)
        ring.set_fill(AREA, 0.42).set_stroke(AREA, 2)
        same = label(TEXT["same"], 0.3, AREA, True).next_to(ring, DOWN, buff=0.3)
        self.play(FadeIn(ring), FadeIn(same), FadeIn(r1), FadeIn(r2), run_time=0.9)

        # ------------------------------------------------------------ length times thickness = area of the ring
        wait_until(EQ_AT)
        eq1 = ftext("L · h  =  π (r₂² − r₁²)", 0.62).move_to(np.array([EQ_X, 1.3, 0]), aligned_edge=LEFT)
        rect_icon = Rectangle(width=1.6, height=0.12).set_fill(RIBBON, 1).set_stroke(width=0)
        rect_icon.next_to(eq1, UP, buff=0.35).align_to(eq1, LEFT)
        ring_icon = Annulus(inner_radius=0.12, outer_radius=0.3).set_fill(AREA, 0.6).set_stroke(width=0)
        ring_icon.next_to(rect_icon, RIGHT, buff=1.5)
        self.play(FadeIn(eq1, shift=RIGHT * 0.1), FadeIn(rect_icon), FadeIn(ring_icon), run_time=0.8)
        wait_until(SOLVE_AT)
        frac = VGroup(ftext("π (r₂² − r₁²)", 0.62), Line(LEFT * 1.25, RIGHT * 1.25).set_stroke(WHITE, 2),
                      ftext("h", 0.62)).arrange(DOWN, buff=0.12)
        eq2 = VGroup(ftext("L  =", 0.62), frac).arrange(RIGHT, buff=0.25)
        eq2.next_to(eq1, DOWN, buff=0.55).align_to(eq1, LEFT)
        box = SurroundingRectangle(eq2, color=GLOW, buff=0.2, corner_radius=0.08, stroke_width=2.5)
        self.play(FadeIn(eq2, shift=DOWN * 0.1), Create(box), run_time=0.9)

        # ------------------------------------------------------------ the 6497
        wait_until(REAL_AT)
        _, _, R1, _ = pack_turns(1.0)          # outer radius of the fully wound pack, mm
        s_mm = R_OUT * COIL_SCALE / (R_ROOT + 0.1)

        def sc(g):
            return affinity.scale(g, s_mm, s_mm, origin=(0, 0))

        pack = Annulus(inner_radius=CORE_R * s_mm, outer_radius=R1 * s_mm).set_fill(STEEL_HI, 1).set_stroke(WHITE, 0.6)
        lines = VGroup(*[Circle(radius=(CORE_R + k * (R1 - CORE_R) / 9) * s_mm).set_stroke(STEEL, 0.6, 0.7)
                         for k in range(1, 9)])
        real = VGroup(vm(sc(drum_floor_g()), BRASS_DK, stroke=BRASS_DK, sw=0),
                      vm(sc(drum_wall_g()), BRASS, stroke=BRASS_HI, sw=0.8),
                      pack, lines, vm(sc(arbor_core_g()), STEEL, stroke=STEEL_HI, sw=0.6)).move_to(COIL_C)
        real[0].move_to(COIL_C)
        real_title = label(TEXT["real"], 0.3, GLOW, True).next_to(real, UP, buff=0.3)
        self.play(FadeOut(VGroup(coil_mob, arbor, ring, same, r1, r2, rect_icon, ring_icon)), FadeIn(real),
                  FadeIn(real_title), eq1.animate.set_opacity(0.45), run_time=1.0)
        self.remove(coil_mob)

        def radius_arrow(r_mm, deg, name, val, col):
            end = COIL_C + np.array([np.cos(np.radians(deg)), np.sin(np.radians(deg)), 0]) * r_mm * s_mm
            arr = Arrow(COIL_C, end, buff=0, stroke_width=3, color=col, max_tip_length_to_length_ratio=0.15)
            return arr, ftext(f"{name} = {val}", 0.42, col)

        a1, t1 = radius_arrow(CORE_R, 205, "r₁", "2.05 mm", AREA)
        a2, t2 = radius_arrow(R1, 320, "r₂", "5.5 mm", AREA)
        vals = VGroup(t1, t2, ftext("h  =  0.18 mm", 0.42, GLOW)).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        vals.next_to(box, DOWN, buff=0.45).align_to(eq1, LEFT)
        wait_until(REAL_TIMES["r1"])
        self.play(GrowArrow(a1), FadeIn(t1), run_time=0.7)
        wait_until(REAL_TIMES["r2"])
        self.play(GrowArrow(a2), FadeIn(t2), run_time=0.7)
        wait_until(REAL_TIMES["h"])
        self.play(FadeIn(vals[2]), run_time=0.6)
        L_mm = np.pi * (5.5 ** 2 - CORE_R ** 2) / REAL_H
        result = ftext(f"L  ≈  {L_mm:.0f} mm", 0.62, AREA)
        half = label(TEXT["half"], 0.28, AREA, True)
        res = VGroup(result, half).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        res.next_to(vals, RIGHT, buff=0.6).align_to(vals, UP)
        wait_until(REAL_TIMES["L"])
        self.play(FadeIn(res, shift=RIGHT * 0.1), run_time=0.8)
        wait_until(REAL_TIMES["catalog"])
        cat = label(TEXT["catalog"], 0.26).next_to(res, DOWN, aligned_edge=LEFT, buff=0.18)
        self.play(FadeIn(cat), run_time=0.6)

        self.wait(FINAL_HOLD)
        curtain.set_fill(opacity=0)
        self.add(curtain)
        self.play(curtain.animate.set_fill(opacity=1), run_time=FADE_OUT)
