"""Film 3, scene 04 - "Why teeth must match": the module m = D / z, a gear's
pitch diameter shared out among its teeth. Two gears with different modules
jam within a tooth or two (the jam angle is found from the actual tooth
outlines); two with the same module mesh, at a center distance fixed by
a = m (z1 + z2) / 2. Last, the movement's own train: each mesh has its own
module, set so the pitch circles touch exactly at the drilled pivots.

Build (render + voice + mux):   python build.py 3/scene04_module
Render only (quick preview):    PYTHONPATH=.:films/film03_gear_train manim -ql films/film03_gear_train/scene04_module.py Scene04
Narration lines and their start times live in scene04_module.voice.txt.

The movement's modules (in mm) come from movement.MESH with the documented
6497 tooth counts; they are about 0.20, 0.14, 0.14 and 0.11 mm.
"""
from manim import *
from shapely import affinity
import movement
movement.use_train(movement.TEETH_6497)
from movement import vignette, teeth_g, P, R, MESH, BG, GLOW, FONT_SANS, FONT_SERIF, BRASS, STEEL_HI
from train import GearSet, Gear, TOOTH_MID, GAP_MID

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds.
# Keep the timeline roughly in step with scene04_module.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 1.0
PITCH_AT, DIAMETER_AT, TEETH_AT, FORMULA_AT = 2.0, 3.4, 5.4, 6.4
SHARE_AT, ONE_TOOTH_AT = 8.3, 10.0     # D shared out among the teeth; one share is m
MISMATCH_AT = 12.8                     # two gears, different modules
ROLL_AT, JAM_AT = 15.0, 18.3           # they turn ... and jam
MATCH_AT = 21.2                        # equal modules: they mesh
DISTANCE_AT, CENTER_FORMULA_AT = 23.6, 25.6
MOVEMENT_AT = 30.8                     # the movement's own meshes
CIRCLES_AT, TABLE_AT = 32.2, 33.6
FINAL_HOLD_UNTIL = 39.5                # the last line ends about 38.0 s
FADE_OUT = 1.5

# --- part 1: one gear ---------------------------------------------------
ONE = dict(z=24, m=0.15, at=(-3.3, 0.3))
SPEED = -0.12                          # radians per second
BAR_Y = -1.7                           # the shared-out diameter, drawn as a bar

# --- part 2: different modules ---------------------------------------------
COARSE = dict(z=16, m=0.15, at=(-1.4, 0.1))
FINE = dict(z=24, m=0.10)              # same pitch radius (1.2) as COARSE, finer teeth
JAM_AREA = 0.006                       # tooth overlap (scene units squared) that counts as jammed

# --- part 3: equal modules ------------------------------------------------
PAIR = dict(z1=16, z2=24, m=0.15, at=(-2.9, -0.35))

# --- part 4: the movement ---------------------------------------------------
MV_SCALE, MV_AT = 1.6, (-1.5, -0.85)   # the pivots, scaled and placed
MESHES = (("barrel", "center", "barrel", "center_p"), ("center", "third", "center", "third_p"),
          ("third", "fourth", "third", "fourth_p"), ("fourth", "escape", "fourth", "escape_p"))
MM_PER_UNIT = 6.1

# --- text --------------------------------------------------------------
FORMULA = "m  =  D / z"
LEGEND = "m  module        D  pitch diameter        z  number of teeth"
SHARE = "m"
MISMATCH = "m₁  ≠  m₂"
MISMATCH_LABELS = ("16 coarse teeth", "24 fine teeth")
CENTER_FORMULA = "a  =  m (z₁ + z₂) / 2"
CENTER_INSTANCE = "0.15 × (16 + 24) / 2  =  3.0"
TABLE_HEAD = "module of each mesh"
TABLE = (("barrel → center", "barrel"), ("center → third", "center"), ("third → fourth", "third"),
         ("fourth → escape", "fourth"))
JAM = "#ff5a4a"
# =====================================================================


def ftext(s, scale=0.5, color=WHITE):
    return Text(s, font=FONT_SERIF, slant=ITALIC, color=color).scale(scale)


def label(s, scale=0.28, color=GREY_B, bold=False):
    return Text(s, font=FONT_SANS, weight=BOLD if bold else NORMAL, color=color).scale(scale)


def jam_angle(c1, c2, z1, m1, z2, m2, a1_0, a2_0, step=-0.004, limit=-1.5):
    """Turn gear 1 (clockwise) from a1_0, rolling gear 2 on equal pitch circles,
    until their teeth overlap by JAM_AREA. Returns (turn of gear 1, overlap shape)."""
    r1, r2 = m1 * z1 / 2, m2 * z2 / 2
    g1, g2 = teeth_g(r1, z1, m=m1), teeth_g(r2, z2, m=m2)
    a = 0.0
    while a > limit:
        s1 = affinity.translate(affinity.rotate(g1, a1_0 + a, origin=(0, 0), use_radians=True), *c1)
        s2 = affinity.translate(affinity.rotate(g2, a2_0 - a * r1 / r2, origin=(0, 0), use_radians=True), *c2)
        hit = s1.intersection(s2)
        if hit.area > JAM_AREA:
            return a, hit
        a += step
    return limit, None


class Scene04(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.add(vignette())

        def wait_until(when):
            d = when - self.renderer.time
            if d > 1e-3:
                self.wait(d)

        # ------------------------------------------------------------ 1: one gear
        gs1 = GearSet()
        one = gs1.gear("one", ONE["z"], ONE["m"], center=ONE["at"], kind="plain")
        gs1.attach(self)
        c1 = one.pivot
        pitch = DashedVMobject(Circle(radius=one.r, num_components=120).move_to(c1), num_dashes=60)
        pitch.set_stroke(GLOW, 2.5)
        diam = DoubleArrow(c1 + LEFT * one.r, c1 + RIGHT * one.r, buff=0, stroke_width=3, tip_length=0.18,
                           color=GLOW)
        d_lab = ftext("D", 0.45, GLOW).next_to(diam, UP, buff=0.1).shift(RIGHT * 0.6)
        z_lab = label(f"z = {ONE['z']} teeth", 0.3, WHITE).next_to(one, DOWN, buff=0.3)
        formula = ftext(FORMULA, 0.75).move_to([2.6, 1.7, 0])
        legend = label(LEGEND, 0.24).next_to(formula, DOWN, buff=0.25)
        D = one.r * 2
        bar_l = np.array([2.6 - D / 2, BAR_Y, 0])
        bar = Line(bar_l, bar_l + RIGHT * D).set_stroke(GLOW, 5)
        ticks = VGroup(*[Line(bar_l + RIGHT * D * k / ONE["z"] + UP * 0.12, bar_l + RIGHT * D * k / ONE["z"] + DOWN * 0.12)
                         .set_stroke(WHITE, 1.5) for k in range(ONE["z"] + 1)])
        bar_lab = ftext("D", 0.4, GLOW).next_to(bar, LEFT, buff=0.2)
        piece = Line(bar_l + RIGHT * D * 11 / ONE["z"], bar_l + RIGHT * D * 12 / ONE["z"]).set_stroke(WHITE, 12)
        piece_lab = ftext(SHARE, 0.45, WHITE).next_to(piece, DOWN, buff=0.18)
        part1 = VGroup(pitch, diam, d_lab, z_lab, formula, legend, bar, ticks, bar_lab, piece, piece_lab)

        # ------------------------------------------------------------ 2: different modules
        cA = np.array([*COARSE["at"], 0.0])
        rA, rB = COARSE["m"] * COARSE["z"] / 2, FINE["m"] * FINE["z"] / 2
        cB = cA + RIGHT * (rA + rB)
        gA = Gear(COARSE["z"], COARSE["m"], kind="plain").place(cA)
        gB = Gear(FINE["z"], FINE["m"], kind="plain", color="#b08a3a").place(cB)
        a0 = -TOOTH_MID * TAU / COARSE["z"]                    # a tooth of A facing B
        b0 = PI - GAP_MID * TAU / FINE["z"]                    # a gap of B facing A
        gA.set_angle(a0); gB.set_angle(b0)
        jam, hit = jam_angle(cA[:2], cB[:2], COARSE["z"], COARSE["m"], FINE["z"], FINE["m"], a0, b0)
        roll = ValueTracker(0.0)
        roller = Mobject().add_updater(lambda _: (gA.set_angle(a0 + roll.get_value()),
                                                  gB.set_angle(b0 - roll.get_value() * rA / rB)))
        hit_m = movement.vm(hit, JAM, 1.0, JAM, 1.5) if hit is not None else VGroup()
        jam_ring = Circle(radius=0.45).move_to(cA + RIGHT * rA).set_stroke(JAM, 4)
        mis = ftext(MISMATCH, 0.7).move_to([0, 2.8, 0])
        mis_labels = VGroup(label(MISMATCH_LABELS[0], 0.28, WHITE).next_to(gA, DOWN, buff=0.35),
                            label(MISMATCH_LABELS[1], 0.28, WHITE).next_to(gB, DOWN, buff=0.35))
        part2 = VGroup(gA, gB, mis, mis_labels)

        # ------------------------------------------------------------ 3: equal modules
        gs3 = GearSet()
        p1 = gs3.gear("p1", PAIR["z1"], PAIR["m"], center=PAIR["at"], kind="plain")
        p2 = gs3.gear("p2", PAIR["z2"], PAIR["m"], driven_by="p1", angle=0, kind="plain")
        y_dim = PAIR["at"][1] - p2.r - 0.55
        dim = DoubleArrow([p1.pivot[0], y_dim, 0], [p2.pivot[0], y_dim, 0], buff=0, stroke_width=3,
                          tip_length=0.18, color=GLOW)
        dim_ticks = VGroup(*[DashedLine(g.pivot, [g.pivot[0], y_dim - 0.1, 0], dash_length=0.08)
                             .set_stroke(GREY_B, 1.5) for g in (p1, p2)])
        dim_lab = ftext("a", 0.45, GLOW).next_to(dim, DOWN, buff=0.12)
        pitch3 = VGroup(*[DashedVMobject(Circle(radius=g.r, num_components=100).move_to(g.pivot), num_dashes=50)
                          .set_stroke(GLOW, 2, 0.8) for g in (p1, p2)])
        cformula = ftext(CENTER_FORMULA, 0.65).move_to([3.1, 2.85, 0])
        cinstance = ftext(CENTER_INSTANCE, 0.45, GLOW).next_to(cformula, DOWN, buff=0.25)

        # ------------------------------------------------------------ 4: the movement
        def mvp(k):
            return np.array(MV_AT + (0,)) + MV_SCALE * P[k]
        pivots = VGroup(*[Dot(mvp(k), radius=0.06, color=STEEL_HI) for k in ("barrel", "center", "third", "fourth", "escape")])
        names = VGroup(*[label(k, 0.27).next_to(mvp(k), d, buff=0.15) for k, d in
                         (("barrel", UR), ("center", DR), ("third", UL), ("fourth", LEFT), ("escape", DL))])
        circles = VGroup()
        for a, b, rw, rp in MESHES:
            circles.add(Circle(radius=MV_SCALE * R[rw], num_components=100).move_to(mvp(a)).set_stroke(BRASS, 2, 0.9),
                        Circle(radius=MV_SCALE * R[rp], num_components=40).move_to(mvp(b)).set_stroke(STEEL_HI, 2, 0.9))
        rows = [label(TABLE_HEAD, 0.28, GLOW, True)]
        for text, mesh in TABLE:
            rows.append(VGroup(label(text, 0.28, WHITE),
                               label(f"{MESH[mesh] * MM_PER_UNIT:.2f} mm", 0.28, GLOW)).arrange(RIGHT, buff=0.5))
        for r in rows[1:]:
            r[1].align_to(rows[1][1], LEFT)
        table = VGroup(*rows).arrange(DOWN, aligned_edge=LEFT, buff=0.22).move_to([3.9, 0.0, 0])
        for r in rows[1:]:
            r[1].move_to([table.get_right()[0] - r[1].width / 2, r[1].get_center()[1], 0])

        curtain = FullScreenRectangle().set_fill(BG, 1).set_stroke(width=0)
        self.add(curtain)

        # ---------------------------------------------------------- timeline
        self.play(curtain.animate.set_fill(opacity=0), gs1.speed.animate.set_value(SPEED),
                  run_time=FADE_IN, rate_func=smooth)
        self.remove(curtain)
        wait_until(PITCH_AT)                               # the pitch circle and its diameter
        self.play(Create(pitch), run_time=1.0)
        wait_until(DIAMETER_AT)
        self.play(GrowFromCenter(diam), FadeIn(d_lab), run_time=0.8)
        wait_until(TEETH_AT)
        self.play(FadeIn(z_lab, shift=UP * 0.1), run_time=0.6)
        wait_until(FORMULA_AT)
        self.play(Write(formula), FadeIn(legend), run_time=1.2)
        wait_until(SHARE_AT)                               # D shared out among the teeth
        self.play(Create(bar), FadeIn(bar_lab), run_time=0.8)
        self.play(LaggedStart(*[Create(t) for t in ticks], lag_ratio=0.08, run_time=1.2))
        wait_until(ONE_TOOTH_AT)
        self.play(Create(piece), FadeIn(piece_lab, shift=DOWN * 0.1), run_time=0.8)

        wait_until(MISMATCH_AT - 0.6)                      # different modules
        self.play(FadeOut(part1), gs1.speed.animate.set_value(0), run_time=0.6)
        self.play(FadeOut(gs1.group), run_time=0.4)
        self.play(FadeIn(gA), FadeIn(gB), FadeIn(mis, shift=DOWN * 0.1), FadeIn(mis_labels), run_time=1.0)
        self.add(roller)
        wait_until(ROLL_AT)                                # turn ... and jam
        self.play(roll.animate.set_value(jam), run_time=JAM_AT - ROLL_AT, rate_func=rate_functions.ease_in_sine)
        self.add(hit_m)
        self.play(Create(jam_ring), FadeIn(hit_m),
                  roll.animate(rate_func=lambda t: 0.5 * np.sin(6 * PI * t) * (1 - t)).set_value(jam + 0.02),
                  run_time=0.8)

        wait_until(MATCH_AT - 0.6)                         # equal modules
        self.play(FadeOut(part2), FadeOut(jam_ring), FadeOut(hit_m), run_time=0.6)
        self.remove(roller)
        gs3.attach(self, add=False)
        self.play(FadeIn(gs3.group), run_time=0.8)
        self.play(gs3.speed.animate.set_value(SPEED * 1.6), run_time=0.8)
        wait_until(DISTANCE_AT)                            # the distance between the centers
        self.play(Create(pitch3), Create(dim_ticks), GrowFromCenter(dim), FadeIn(dim_lab), run_time=1.0)
        wait_until(CENTER_FORMULA_AT)
        self.play(Write(cformula), run_time=1.2)
        self.play(FadeIn(cinstance, shift=UP * 0.1), run_time=0.8)

        wait_until(MOVEMENT_AT - 0.8)                      # the movement's meshes
        self.play(gs3.speed.animate.set_value(0), FadeOut(VGroup(pitch3, dim, dim_ticks, dim_lab, cformula, cinstance)),
                  run_time=0.6)
        self.play(FadeOut(gs3.group), run_time=0.4)
        self.play(FadeIn(pivots), FadeIn(names), run_time=0.8)
        wait_until(CIRCLES_AT)                             # pitch circles touch at the pivots' spacing
        self.play(LaggedStart(*[Create(c) for c in circles], lag_ratio=0.25, run_time=2.0))
        wait_until(TABLE_AT)
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.15) for r in rows], lag_ratio=0.3, run_time=2.0))

        wait_until(FINAL_HOLD_UNTIL)
        curtain.set_fill(opacity=0)
        self.add(curtain)
        self.play(curtain.animate.set_fill(opacity=1), run_time=FADE_OUT)
