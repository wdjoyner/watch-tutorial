"""Film 3, scene 09 - "The moon problem": a lunation is 29.53059 days, not a
whole number or a simple fraction. The classic moon disk has 59 teeth and two
moons and steps one tooth a day, so each moon takes 59/2 = 29.5 days, about
44 minutes short each month. A number line shows the gap; a drift bar shows the
painted moon a full day ahead of the real one after about 2.6 years.

Build (render + voice + mux):   python build.py 3/scene09_moon
Render only (quick preview):    PYTHONPATH=.:films/film03_gear_train manim -ql films/film03_gear_train/scene09_moon.py Scene09
Narration lines and their start times live in scene09_moon.voice.txt.

Mean synodic month: 29.530589 days. 59/2 is short by 0.030589 days (44.0 minutes)
per lunation; a full day accumulates in 32.7 lunations, 965 days, 2.64 years.
"""
from manim import *
from shapely.geometry import box as sbox
from movement import vignette, teeth_g, disk_g, vm, BG, GLOW, FONT_SANS, FONT_SERIF, BRASS, BRASS_HI, STEEL, STEEL_HI

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds.
# Keep the timeline roughly in step with scene09_moon.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 1.0
LUNATION_AT = 6.0                      # "twenty-nine point five three days"
NOT_WHOLE_AT = 10.2                    # "not a whole number, and not a simple fraction"
DISK_LABELS_AT = 14.6                  # 59 teeth, two moons
STEPS_AT, STEPS = 17.2, 6              # one tooth a day (shown step by step)
STEP_TIME = 0.5
HALVES_AT = 20.6                       # 59 / 2 = 29.5
WINDOW_AT = 22.6                       # the dial's moon window
SHORT_AT, MINUTES_AT = 25.3, 26.6      # the number line; "forty-four minutes"
DRIFT_AT, DRIFT_DURATION = 29.6, 4.4   # 2.6 years: a full day ahead
FINAL_HOLD_UNTIL = 36.6                # the last line ends about 35.1 s
FADE_OUT = 1.5

# --- the moon disk -----------------------------------------------------------
DISK_AT = (-3.3, -0.55)
DISK_R = 1.75
MOON_R, MOON_D = 0.5, 1.05             # painted moons: radius, distance from the center
SKY = "#1b2d5a"
DIAL = "#23262d"
WINDOW_R = 1.62                        # the dial window (upper half) and its two humps
HUMP_R = 0.52
DIAL_R = 2.25                          # a round piece of dial around the window
SPIN_FAST = 0.9                        # radians per second during the drift

# --- number line -------------------------------------------------------------
NL_RANGE = (29.46, 29.56)
NL_X = (0.9, 6.5)
NL_Y = -1.35
LUNATION = 29.530589

# --- text --------------------------------------------------------------
TITLE = "THE MOON PROBLEM"
LUNATION_TEXT = "new moon to new moon:  29.53059 days"
NOT_WHOLE = "not a whole number,  not a simple fraction"
DISK_TEXT = ("59 teeth", "2 moons", "1 tooth a day")
HALVES = "59 / 2  =  29.5 days"
SHORT = "29.5  is short by  0.0306 day  ≈  44 minutes"
LABELS_NL = ("moon disk", "the sky")
DRIFT_TEXT = ("years", "painted moon ahead by")
# =====================================================================


def label(s, scale=0.28, color=GREY_B, bold=False):
    return Text(s, font=FONT_SANS, weight=BOLD if bold else NORMAL, color=color).scale(scale)


def ftext(s, scale=0.5, color=WHITE):
    return Text(s, font=FONT_SERIF, slant=ITALIC, color=color).scale(scale)


class Scene09(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.add(vignette())

        def wait_until(when):
            d = when - self.renderer.time
            if d > 1e-3:
                self.wait(d)

        c = np.array([*DISK_AT, 0.0])
        m = 2 * DISK_R / 59
        sky = vm(teeth_g(DISK_R, 59, m=m), SKY, 1, "#5a74b8", 0.8)
        moons = VGroup(*[Circle(radius=MOON_R).move_to(s * RIGHT * MOON_D).set_fill(GLOW, 1).set_stroke(BRASS_HI, 1.5)
                         for s in (1, -1)])
        stars = VGroup(*[Dot(0.75 * DISK_R * np.array([np.cos(a), np.sin(a), 0]), radius=0.025, color=WHITE)
                         for a in np.linspace(0.6, TAU + 0.6, 14, endpoint=False) if abs(np.cos(a)) < 0.7])
        disk = VGroup(sky, stars, moons).move_to(c)
        disk.rotate(PI / 2, about_point=c)           # a moon starts out of sight, under the dial

        # the dial, with its two-humped window over the upper half of the disk
        win = disk_g(WINDOW_R).intersection(sbox(-3, 0, 3, 3))
        for s in (1, -1):
            win = win.difference(disk_g(HUMP_R, (s * MOON_D, 0)))
        plate = disk_g(DIAL_R, n=160).difference(win)
        dial = vm(plate, DIAL, 1.0, GREY_D, 1.2).shift(c)
        rim = Circle(radius=DIAL_R, num_components=120).move_to(c).set_stroke(GREY_C, 3)

        title = label(TITLE, 0.36, GLOW, True).to_corner(UL, buff=0.45)
        lun = ftext(LUNATION_TEXT, 0.44).move_to([3.5, 2.6, 0])
        not_whole = label(NOT_WHOLE, 0.28).next_to(lun, DOWN, buff=0.2)
        disk_text = VGroup(*[label(t, 0.3, WHITE) for t in DISK_TEXT]).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        disk_text.next_to(c + RIGHT * DISK_R, RIGHT, buff=0.4).shift(DOWN * 1.2)
        halves = ftext(HALVES, 0.55, GLOW).move_to([3.6, 1.15, 0])
        day = {"n": 0}
        day_text = always_redraw(lambda: label(f"day {day['n']}", 0.3, GLOW).next_to(disk, DOWN, buff=0.3))

        # number line
        def nx(v):
            return NL_X[0] + (v - NL_RANGE[0]) / (NL_RANGE[1] - NL_RANGE[0]) * (NL_X[1] - NL_X[0])
        axis = Line([NL_X[0] - 0.1, NL_Y, 0], [NL_X[1] + 0.1, NL_Y, 0]).set_stroke(GREY_B, 2)
        ticks = VGroup()
        for v in np.arange(NL_RANGE[0], NL_RANGE[1] + 1e-9, 0.02):
            ticks.add(Line([nx(v), NL_Y - 0.08, 0], [nx(v), NL_Y + 0.08, 0]).set_stroke(GREY_B, 1.5),
                      label(f"{v:.2f}", 0.22).move_to([nx(v), NL_Y - 0.32, 0]))
        mark_disk = VGroup(Triangle().scale(0.09).rotate(PI).move_to([nx(29.5), NL_Y + 0.2, 0]).set_fill(GLOW, 1).set_stroke(width=0),
                           label(LABELS_NL[0], 0.25, GLOW).move_to([nx(29.5) - 0.2, NL_Y + 0.5, 0]))
        mark_sky = VGroup(Triangle().scale(0.09).rotate(PI).move_to([nx(LUNATION), NL_Y + 0.2, 0]).set_fill(WHITE, 1).set_stroke(width=0),
                          label(LABELS_NL[1], 0.25, WHITE).move_to([nx(LUNATION) + 0.2, NL_Y + 0.5, 0]))
        ya, yb = NL_Y - 0.55, NL_Y - 0.68                  # a square bracket under the gap (Brace needs LaTeX)
        gap = VMobject().set_points_as_corners([[nx(29.5), ya, 0], [nx(29.5), yb, 0], [nx(LUNATION), yb, 0],
                                                [nx(LUNATION), ya, 0]]).set_stroke(GLOW, 3)
        short = label(SHORT, 0.28, WHITE).move_to([3.7, NL_Y - 1.35, 0])

        # drift: years and the painted moon's lead, in days
        years = ValueTracker(0.0)
        bar_x0, bar_w, bar_y = 1.2, 5.0, 0.15
        frame = Rectangle(width=bar_w, height=0.3).move_to([bar_x0 + bar_w / 2, bar_y, 0]).set_stroke(GREY_B, 1.5)
        fill = always_redraw(lambda: Rectangle(width=max(0.001, bar_w * years.get_value() / 2.64), height=0.3)
                             .move_to([bar_x0, bar_y, 0], aligned_edge=LEFT).set_fill(GLOW, 0.85).set_stroke(width=0))
        drift_lab = always_redraw(lambda: label(
            f"{years.get_value():.1f} {DRIFT_TEXT[0]}:  {DRIFT_TEXT[1]} {years.get_value() / 2.64:.2f} day", 0.28, WHITE)
            .next_to(frame, UP, buff=0.15))
        one_day = label("1 day", 0.26, GLOW).next_to(frame, RIGHT, buff=0.15)

        curtain = FullScreenRectangle().set_fill(BG, 1).set_stroke(width=0)
        self.add(disk, title, curtain)

        # ---------------------------------------------------------- timeline
        self.play(curtain.animate.set_fill(opacity=0), run_time=FADE_IN, rate_func=smooth)
        self.remove(curtain)
        wait_until(LUNATION_AT)                            # 29.53059 days
        self.play(Write(lun), run_time=1.4)
        wait_until(NOT_WHOLE_AT)
        self.play(FadeIn(not_whole, shift=UP * 0.1), run_time=0.8)

        wait_until(DISK_LABELS_AT)                         # 59 teeth, two moons, one tooth a day
        self.play(LaggedStart(*[FadeIn(t, shift=LEFT * 0.1) for t in disk_text], lag_ratio=0.5), run_time=1.6)
        wait_until(STEPS_AT)
        self.add(day_text)
        for _ in range(STEPS):
            day["n"] += 1
            self.play(Rotate(disk, -TAU / 59, about_point=c), run_time=0.14, rate_func=smooth)
            self.wait(STEP_TIME - 0.14)
        wait_until(HALVES_AT)                              # 59 / 2 = 29.5
        self.play(FadeIn(halves, shift=UP * 0.1), run_time=0.8)
        wait_until(WINDOW_AT)                              # behind the dial's window
        self.play(FadeOut(disk_text), FadeOut(day_text), FadeIn(dial), FadeIn(rim), run_time=1.0)

        wait_until(SHORT_AT)                               # short by 44 minutes
        self.play(Create(axis), FadeIn(ticks), FadeIn(mark_disk), FadeIn(mark_sky), run_time=1.0)
        wait_until(MINUTES_AT)
        self.play(GrowFromCenter(gap), FadeIn(short, shift=UP * 0.1), run_time=0.8)

        wait_until(DRIFT_AT)                               # a full day ahead in 2.6 years
        self.add(fill, drift_lab)
        self.play(FadeIn(frame), FadeIn(one_day), run_time=0.4)
        self.play(years.animate.set_value(2.64), Rotate(disk, -SPIN_FAST * DRIFT_DURATION, about_point=c),
                  run_time=DRIFT_DURATION, rate_func=linear)

        wait_until(FINAL_HOLD_UNTIL)
        curtain.set_fill(opacity=0)
        self.add(curtain)
        self.play(curtain.animate.set_fill(opacity=1), run_time=FADE_OUT)
