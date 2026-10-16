"""Film 6, scene 02 - "Lock, unlock, impulse": the Swiss lever in close-up, running
in slow motion, each part named as the narration first mentions it (escape wheel,
pallet fork, pallet stones, fork, roller jewel, banking pins), then the
escapement's three jobs.

Build (render + voice + mux):   python build.py 6/scene02_three_jobs
Render only (quick preview):    PYTHONPATH=.:films/film06_escapement manim -ql films/film06_escapement/scene02_three_jobs.py Scene02
Narration lines and their start times live in scene02_three_jobs.voice.txt.
The close-up is lever.py's schematic Swiss lever (the chapter's figure geometry).
The scene writes scene02_three_jobs.ticks.txt on every render (one tick per drop).
"""
from manim import *
import prev  # noqa: F401  (first: Film 4 and 5 helpers on the path)
from lever import LeverEscapement
from movement import vignette, BG, GLOW
from ui import label, heading, tag, curtain, clock, WARM, COOL
from ui6 import callout, callouts, write_ticks

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds.
# Keep the timeline roughly in step with scene02_three_jobs.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 1.0
SHOW_AT = 1.2                         # "The escapement is the link between the gear train and the balance."
PARTS_AT = 6.2                        # "In a Swiss lever watch, it has three parts: ..."
WHEEL_AT = 14.1                       # "The escape wheel is the last wheel of the train, with fifteen teeth."
FORK_AT = 19.5                        # "Beside it pivots the pallet fork."
STONES_AT = 22.0                      # "...carry red jewels, the pallet stones..."
FORKEND_AT = 25.4                     # "...and its far end is a fork."
JEWEL_AT = 28.6                       # "...the roller jewel, also called the impulse pin..."
PINS_AT = 37.3                        # "Two banking pins..."
OSC_AT = 41.9                         # "The balance and hairspring are not part of the escapement ..."
JOBS_AT = (51.0, 52.8, 55.0)          # "locks the train", "unlocks it once per beat", "a push, called the impulse"
FINAL_HOLD_UNTIL = 59.4               # the last line ends about 57.4 s
FADE_OUT = 1.5

# --- the close-up ----------------------------------------------------
CENTER, SCALE = (0.3, -0.8), 1.9      # escape-wheel center on screen, and geometry units -> screen units
RIM_R = 0.75                          # the faint balance rim, geometry units
# label positions (screen coordinates); everything stays above the caption band (y > -2.7)
AT = dict(wheel=(-3.9, -1.4), lever=(-3.4, 1.0), stones=(3.6, 0.3), fork=(-2.9, 2.15), jewel=(-2.3, 3.05),
          pins=(3.4, 1.85), osc=(4.3, 2.45))
RATE, LIFT_RATE = 1 / 25, 1 / 8       # slow motion: 25x, and 8x slower again near the center
TEXT = dict(train="from the gear train", balance="to the balance", wheel="escape wheel (15 teeth)",
            lever="pallet fork", stones="pallet stones", fork="fork", jewel="roller jewel\n(impulse pin)",
            pins="banking pins", slow="slow motion: about 25 to 200 times",
            jobs_title="The escapement's three jobs",
            jobs=("1   lock the train", "2   unlock it, once per beat", "3   impulse the balance"),
            schematic="schematic Swiss lever",
            parts="the escapement = escape wheel + pallet fork + roller jewel",
            osc="balance + hairspring:\nthe oscillator, not part\nof the escapement")
# =====================================================================


class Scene02(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.add(vignette())
        wait_until = clock(self)

        esc = LeverEscapement(center=CENTER, scale=SCALE, rim_r=RIM_R)
        esc.rate.set_value(RATE)
        esc.lift_rate.set_value(LIFT_RATE)
        esc.vis.set_value(0.0)
        esc.attach(self)

        head = heading("THE ESCAPEMENT", "lock, unlock, impulse").to_corner(UL, buff=0.5)
        slow = tag(TEXT["slow"], GLOW, 0.2).to_corner(UR, buff=0.4)
        sch = tag(TEXT["schematic"], GREY_B, 0.18).next_to(slow, DOWN, buff=0.12, aligned_edge=RIGHT)

        wheel_c = esc.pt((0, 0))
        train = VGroup(Arrow(wheel_c + LEFT * 4.6 + UP * 0.2, wheel_c + LEFT * 1.95 + UP * 0.7, buff=0,
                             stroke_width=3, color=WARM, tip_length=0.18),
                       label(TEXT["train"], 0.24, WARM))
        train[1].next_to(train[0].get_start(), DOWN, buff=0.15)
        roller = esc.anchor("staff")
        to_bal = VGroup(Arrow(roller + RIGHT * 0.75, roller + RIGHT * 3.0, buff=0, stroke_width=3, color=COOL,
                              tip_length=0.18), label(TEXT["balance"], 0.24, COOL))
        to_bal[1].next_to(to_bal[0], UP, buff=0.1)

        c_wheel = callout(TEXT["wheel"], lambda: esc.anchor("escape_wheel"), AT["wheel"])
        c_lever = callout(TEXT["lever"], lambda: esc.anchor("pallet_fork"), AT["lever"])
        c_stones = callouts(TEXT["stones"], [lambda: esc.anchor("entry_stone"), lambda: esc.anchor("exit_stone")],
                            AT["stones"], color="#ff9aa0")
        c_fork = callout(TEXT["fork"], lambda: esc.anchor("fork"), AT["fork"])
        c_jewel = callout(TEXT["jewel"], lambda: esc.anchor("roller_jewel"), AT["jewel"],
                          color="#ff9aa0")
        c_pins = callouts(TEXT["pins"], [lambda: esc.anchor("banking_left"), lambda: esc.anchor("banking_right")],
                          AT["pins"])

        parts = tag(TEXT["parts"], GLOW, 0.22).move_to([0.3, 3.55, 0])
        rim_pt = lambda: esc.anchor("staff") + RIM_R * SCALE * np.array([np.cos(-0.3), np.sin(-0.3), 0])
        c_osc = callout(TEXT["osc"], rim_pt, AT["osc"], color=COOL)

        jobs = VGroup(label(TEXT["jobs_title"], 0.27, GLOW, bold=True),
                      *[label(j, 0.27, WHITE) for j in TEXT["jobs"]]).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        box = SurroundingRectangle(jobs, buff=0.25, corner_radius=0.1).set_stroke(GLOW, 1.2, 0.8).set_fill(BG, 0.9)
        panel = VGroup(box, jobs).move_to([4.6, -1.55, 0])

        cur = curtain()
        self.add(cur)

        # ---------------------------------------------------------- timeline
        self.play(cur.animate.set_fill(opacity=0), run_time=FADE_IN, rate_func=smooth)
        self.remove(cur)
        wait_until(SHOW_AT)
        self.play(FadeIn(head), esc.vis.animate.set_value(1.0), FadeIn(slow), FadeIn(sch), run_time=1.0)
        self.play(GrowArrow(train[0]), FadeIn(train[1]), GrowArrow(to_bal[0]), FadeIn(to_bal[1]), run_time=1.0)
        wait_until(PARTS_AT)
        self.play(FadeIn(parts, shift=DOWN * 0.1), run_time=0.8)
        wait_until(WHEEL_AT)
        self.play(FadeOut(train), FadeOut(to_bal), FadeIn(c_wheel), run_time=0.8)
        wait_until(FORK_AT)
        self.play(FadeIn(c_lever), run_time=0.7)
        wait_until(STONES_AT)
        self.play(FadeIn(c_stones), run_time=0.7)
        wait_until(FORKEND_AT)
        self.play(FadeIn(c_fork), run_time=0.7)
        wait_until(JEWEL_AT)
        self.play(FadeIn(c_jewel), run_time=0.7)
        wait_until(PINS_AT)
        self.play(FadeIn(c_pins), run_time=0.7)
        wait_until(OSC_AT)
        self.play(FadeIn(c_osc), run_time=0.7)
        wait_until(JOBS_AT[0] - 2.4)
        self.play(FadeOut(c_stones), FadeIn(box), FadeIn(jobs[0]), run_time=0.8)
        for k, t in enumerate(JOBS_AT):
            wait_until(t)
            self.play(FadeIn(jobs[k + 1], shift=RIGHT * 0.1), run_time=0.5)

        wait_until(FINAL_HOLD_UNTIL)
        cur.set_fill(opacity=0)
        self.add(cur)
        self.play(cur.animate.set_fill(opacity=1), run_time=FADE_OUT)
        write_ticks(__file__, [t for t, k in esc.events if k == "drop"])
