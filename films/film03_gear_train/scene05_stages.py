"""Film 3, scene 05 - "Stages multiply": a bicycle in a high gear (slow pedals,
fast wheel, a harder push), then the same trade along the going train. A chart
on a log scale shows each arbor's speed rising and its torque falling by the
stage ratios: 85/12, 80/10, 60/8, 70/7, which multiply to 4250. Speed times
torque is power, so on a log scale the two bars mirror each other and power
is a flat line; friction steps it down a little at each mesh.

Build (render + voice + mux):   python build.py 3/scene05_stages
Render only (quick preview):    PYTHONPATH=.:films/film03_gear_train manim -ql films/film03_gear_train/scene05_stages.py Scene05
Narration lines and their start times live in scene05_stages.voice.txt.

The friction steps are schematic (no efficiency values are claimed).
"""
from manim import *
from movement import vignette, teeth_g, vm, BG, GLOW, FONT_SANS, FONT_SERIF, BRASS, BRASS_HI, STEEL, STEEL_HI

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds.
# Keep the timeline roughly in step with scene05_stages.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 1.0
SLOW_AT, FAST_AT, PUSH_AT = 3.6, 5.0, 6.6        # "pedals turn slowly", "wheel turns fast", "push harder"
BIKE_OUT = 9.0
FIRST_STAGE_AT = 12.0                  # "speed goes up by the ratio", one stage
TORQUE1_AT = 15.4                      # "torque comes down by the same ratio"
CHIP_AT = (23.4, 25.0, 26.3, 28.0)     # "just over seven", "times eight", "times seven and a half", "times ten"
PRODUCT_AT = 29.4                      # "about forty-two hundred fifty"
FAST_ESC_AT, WEAK_ESC_AT = 33.4, 36.4  # escape wheel: x 4250 speed, / 4250 torque
POWER_AT = 41.6                        # torque times speed is power: a flat line
FRICTION_AT = 48.0                     # friction steps it down at each mesh
FINAL_HOLD_UNTIL = 55.0                # the last line ends about 53.6 s
FADE_OUT = 1.5

# --- the bicycle ------------------------------------------------------------
RING = dict(z=48, r=0.95, at=(-2.6, -0.9))     # chainring
COG = dict(z=12, r=0.26, at=(1.7, -0.9))       # rear cog (on the wheel's hub)
WHEEL_R = 2.0
CRANK_L = 1.15
CRANK_SPEED = 0.55                     # radians per second (the wheel turns 4x as fast)
CHAIN_DOTS = 26

# --- the chart (log scale) ------------------------------------------------------
ARBORS = ("barrel", "center", "third", "fourth", "escape")
STAGES = ((85, 12), (80, 10), (60, 8), (70, 7))
X0, DX = -4.6, 2.15                    # x of the first arbor, spacing
BASE_Y = -0.2                         # the "same as the barrel" line
DECADE = 0.75                          # height of one factor of ten
BAR_W = 0.36
SPEED_C, TORQUE_C, POWER_C = GLOW, "#6fb3ff", "#ffffff"
LABEL_SPOT = (-5.3, 1.45, 0)           # left end of the power and friction captions
FRICTION_STEP = 0.10                   # schematic drop of the power line at each mesh

# --- text --------------------------------------------------------------
BIKE_TEXT = {"title": "a high gear:  48 teeth  →  12", "slow": "pedals: slow", "fast": "wheel: fast",
             "push": "push harder"}
LEGEND = ("speed", "torque")
CHIPS = ("85/12 ≈ 7.08", "×  80/10 = 8", "×  60/8 = 7.5", "×  70/7 = 10", "=  4250")
POWER_TEXT = "power  =  torque × speed:  unchanged"
FRICTION_TEXT = "minus friction at each mesh:  η₁ η₂ η₃ η₄"
# =====================================================================


def label(s, scale=0.28, color=GREY_B, bold=False):
    return Text(s, font=FONT_SANS, weight=BOLD if bold else NORMAL, color=color).scale(scale)


def ftext(s, scale=0.5, color=WHITE):
    return Text(s, font=FONT_SERIF, slant=ITALIC, color=color).scale(scale)


def spin(mob, center, angle_fn):
    """Updater: keep mob turned to angle_fn() about center."""
    mob._ang = 0.0

    def up(m):
        a = angle_fn()
        if a != m._ang:
            m.rotate(a - m._ang, about_point=center)
            m._ang = a
    mob.add_updater(up)
    return mob


class Scene05(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.add(vignette())

        def wait_until(when):
            d = when - self.renderer.time
            if d > 1e-3:
                self.wait(d)

        # ------------------------------------------------------------ the bicycle
        crank = ValueTracker(0.0)                       # chainring angle (negative = clockwise)
        speed = ValueTracker(0.0)
        clock = Mobject().add_updater(lambda _, dt: crank.increment_value(-speed.get_value() * dt))
        c1, c2 = np.array([*RING["at"], 0.0]), np.array([*COG["at"], 0.0])
        ratio = RING["z"] / COG["z"]
        m1 = 2 * RING["r"] / RING["z"]
        ring = vm(teeth_g(RING["r"], RING["z"], m=m1).difference(teeth_g(RING["r"] * 0.55, 5, m=0.1)),
                  BRASS, 1, BRASS_HI, 0.8).shift(c1)
        cog = vm(teeth_g(COG["r"], COG["z"], m=m1), STEEL_HI, 1, WHITE, 0.8).shift(c2)
        tire = Circle(radius=WHEEL_R, num_components=120).move_to(c2).set_stroke(STEEL, 9)
        rim = Circle(radius=WHEEL_R - 0.12, num_components=120).move_to(c2).set_stroke(STEEL_HI, 2)
        spokes = VGroup(*[Line(c2, c2 + (WHEEL_R - 0.12) * np.array([np.cos(a), np.sin(a), 0])).set_stroke(GREY_B, 1.2)
                          for a in np.linspace(0, TAU, 18, endpoint=False)])
        wheel = VGroup(spokes, rim)
        pedal_end = c1 + CRANK_L * RIGHT
        crank_arm = VGroup(Line(c1, pedal_end).set_stroke(STEEL_HI, 7),
                           Rectangle(width=0.5, height=0.14).move_to(pedal_end).set_fill(STEEL, 1).set_stroke(WHITE, 1))
        # the chain: around the ring's left side, across the top, around the cog's right side, back underneath
        d = c2[0] - c1[0]
        r1, r2 = RING["r"] + 0.03, COG["r"] + 0.03
        nx = (r1 - r2) / d
        ny = np.sqrt(1 - nx ** 2)
        a_up, a_dn = np.arctan2(ny, nx), np.arctan2(-ny, nx)
        pts = [c1 + r1 * np.array([np.cos(a), np.sin(a), 0]) for a in np.linspace(a_up, a_dn + TAU, 60)]
        pts += [c2 + r2 * np.array([np.cos(a), np.sin(a), 0]) for a in np.linspace(a_dn, a_up, 20)]
        pts.append(pts[0])
        chain_path = VMobject().set_points_as_corners(pts).set_stroke(GREY_C, 2.5)
        chain_len = sum(np.linalg.norm(np.array(b) - np.array(a)) for a, b in zip(pts[:-1], pts[1:]))
        dots = VGroup(*[Dot(radius=0.045, color=WHITE) for _ in range(CHAIN_DOTS)])

        def move_dots(g):
            # the chain moves at the ring's pitch speed; it runs over the top toward the cog
            s = (-crank.get_value() * r1 / chain_len) % 1.0
            for k, dot in enumerate(g):
                dot.move_to(chain_path.point_from_proportion((1 - (k / CHAIN_DOTS + s)) % 1.0))
        dots.add_updater(move_dots)
        spin(ring, c1, lambda: crank.get_value())
        spin(crank_arm, c1, lambda: crank.get_value())
        spin(cog, c2, lambda: crank.get_value() * ratio)
        spin(wheel, c2, lambda: crank.get_value() * ratio)
        bike = VGroup(tire, wheel, chain_path, ring, cog, dots, crank_arm)

        b_title = label(BIKE_TEXT["title"], 0.32, WHITE).move_to([0, 2.95, 0])
        slow = label(BIKE_TEXT["slow"], 0.3, WHITE).next_to(c1 + DOWN * 1.35, DOWN, buff=0.1)
        fast = label(BIKE_TEXT["fast"], 0.3, GLOW).next_to(c2 + DOWN * WHEEL_R, DOWN, buff=0.2)
        push = VGroup(Arrow(UP * 1.1, ORIGIN, buff=0, stroke_width=8, max_tip_length_to_length_ratio=0.35,
                            color="#ff8a5c"), label(BIKE_TEXT["push"], 0.3, "#ff8a5c"))
        push[1].next_to(push[0], UP, buff=0.1)
        push.add_updater(lambda m: m.next_to(crank_arm[1], UP, buff=0.05))

        # ------------------------------------------------------------ the chart
        speeds = [1.0]
        for a, b in STAGES:
            speeds.append(speeds[-1] * a / b)
        xs = [X0 + DX * i for i in range(len(ARBORS))]
        baseline = DashedLine([X0 - 0.9, BASE_Y, 0], [xs[-1] + 0.9, BASE_Y, 0], dash_length=0.1).set_stroke(GREY_B, 1.5)
        names = VGroup(*[label(n, 0.27, WHITE).move_to([x, -3.75, 0]) for n, x in zip(ARBORS, xs)])
        sbars, tbars, slabs, tlabs = VGroup(), VGroup(), VGroup(), VGroup()
        for i, (x, v) in enumerate(zip(xs, speeds)):
            h = max(0.04, np.log10(v) * DECADE)
            sb = Rectangle(width=BAR_W, height=h).move_to([x - BAR_W * 0.55, BASE_Y + h / 2, 0])
            tb = Rectangle(width=BAR_W, height=h).move_to([x + BAR_W * 0.55, BASE_Y - h / 2, 0])
            sbars.add(sb.set_fill(SPEED_C, 0.9).set_stroke(width=0))
            tbars.add(tb.set_fill(TORQUE_C, 0.9).set_stroke(width=0))
            sl = "1" if i == 0 else f"× {v:,.0f}" if v > 20 else f"× {v:.3g}"
            tl = "1" if i == 0 else f"÷ {v:,.0f}" if v > 20 else f"÷ {v:.3g}"
            slabs.add(label(sl, 0.26, SPEED_C).next_to(sb, UP, buff=0.1))
            tlabs.add(label(tl, 0.26, TORQUE_C).next_to(tb, DOWN, buff=0.1))
        legend = VGroup(*[VGroup(Square(0.18).set_fill(c, 0.9).set_stroke(width=0), label(t, 0.27, c)).arrange(RIGHT, buff=0.12)
                          for t, c in zip(LEGEND, (SPEED_C, TORQUE_C))]).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        legend.move_to([X0 + 0.2, 2.3, 0])
        chips = VGroup(*[ftext(c, 0.42, WHITE if i < 4 else GLOW) for i, c in enumerate(CHIPS)])
        chips.arrange(RIGHT, buff=0.32).move_to([0.6, 3.55, 0])
        stage_marks = VGroup(*[Arrow([xs[i] + 0.55, -3.75, 0], [xs[i + 1] - 0.55, -3.75, 0], buff=0, stroke_width=2.5,
                                     tip_length=0.14, color=GREY_B) for i in range(4)])
        power = Line([xs[0] - 0.6, BASE_Y, 0], [xs[-1] + 0.6, BASE_Y, 0]).set_stroke(POWER_C, 5)
        power_lab = label(POWER_TEXT, 0.3, POWER_C).move_to(LABEL_SPOT, aligned_edge=LEFT)
        steps = [[xs[0] - 0.6, BASE_Y, 0]]
        for i in range(1, len(xs)):
            xm = (xs[i - 1] + xs[i]) / 2
            y_prev, y_new = BASE_Y - (i - 1) * FRICTION_STEP, BASE_Y - i * FRICTION_STEP
            steps += [[xm, y_prev, 0], [xm, y_new, 0]]
        steps.append([xs[-1] + 0.6, BASE_Y - 4 * FRICTION_STEP, 0])
        lossy = VMobject().set_points_as_corners(steps).set_stroke(POWER_C, 5)
        friction_lab = ftext(FRICTION_TEXT, 0.4, POWER_C).move_to(LABEL_SPOT, aligned_edge=LEFT)

        curtain = FullScreenRectangle().set_fill(BG, 1).set_stroke(width=0)
        self.add(bike, clock, crank, speed, curtain)

        # ---------------------------------------------------------- timeline
        self.play(curtain.animate.set_fill(opacity=0), speed.animate.set_value(CRANK_SPEED),
                  FadeIn(b_title), run_time=FADE_IN, rate_func=smooth)
        self.remove(curtain)
        wait_until(SLOW_AT)
        self.play(FadeIn(slow, shift=UP * 0.1), run_time=0.6)
        wait_until(FAST_AT)
        self.play(FadeIn(fast, shift=UP * 0.1), run_time=0.6)
        wait_until(PUSH_AT)
        self.play(FadeIn(push), run_time=0.6)

        wait_until(BIKE_OUT)                               # the same trade in the train
        self.play(FadeOut(VGroup(bike, b_title, slow, fast, push)), run_time=1.0)
        self.remove(clock)
        self.play(Create(baseline), FadeIn(names), FadeIn(legend), run_time=1.2)
        self.play(GrowFromEdge(sbars[0], DOWN), GrowFromEdge(tbars[0], UP), FadeIn(slabs[0]), run_time=0.6)
        wait_until(FIRST_STAGE_AT)                         # one stage: speed up by the ratio ...
        self.play(Create(stage_marks[0]), GrowFromEdge(sbars[1], DOWN), FadeIn(slabs[1]), run_time=1.0)
        wait_until(TORQUE1_AT)                             # ... and torque down by the same ratio
        self.play(GrowFromEdge(tbars[1], UP), FadeIn(tlabs[1]), run_time=1.0)

        for i, t in enumerate(CHIP_AT):                    # the stages multiply
            wait_until(t)
            anims = [FadeIn(chips[i], shift=DOWN * 0.1)]
            if i == 0:
                anims.append(Indicate(stage_marks[0], color=GLOW))
            else:
                anims += [Create(stage_marks[i]), GrowFromEdge(sbars[i + 1], DOWN), GrowFromEdge(tbars[i + 1], UP),
                          FadeIn(slabs[i + 1]), FadeIn(tlabs[i + 1])]
            self.play(*anims, run_time=0.8)
        wait_until(PRODUCT_AT)
        self.play(FadeIn(chips[4], shift=DOWN * 0.1), run_time=0.8)

        wait_until(FAST_ESC_AT)                            # the escape wheel: fast ...
        self.play(Indicate(slabs[4], scale_factor=1.5), Indicate(sbars[4], color=WHITE, scale_factor=1.05),
                  run_time=1.2)
        wait_until(WEAK_ESC_AT)                            # ... and weak
        self.play(Indicate(tlabs[4], scale_factor=1.5, color=WHITE), Indicate(tbars[4], color=WHITE, scale_factor=1.05),
                  run_time=1.2)

        wait_until(POWER_AT)                               # power: torque x speed, a flat line
        self.play(Create(power), FadeIn(power_lab, shift=UP * 0.1), run_time=1.4)
        wait_until(FRICTION_AT)                            # friction steps it down at each mesh
        self.play(Transform(power, lossy), FadeOut(power_lab), FadeIn(friction_lab, shift=UP * 0.1), run_time=1.6)

        wait_until(FINAL_HOLD_UNTIL)
        curtain.set_fill(opacity=0)
        self.add(curtain)
        self.play(curtain.animate.set_fill(opacity=1), run_time=FADE_OUT)
