"""Film 6, scene 03 - "One beat in slow motion": the Swiss lever close-up, driven
by hand through one vibration so that each event lands on its line of narration:
lock, unlock, impulse, drop, lock again on the exit stone. The current phase is
named at the top as it happens (lever.py's phase(), from the contact kinematics).
Then Petrangeli's timings: the active part of a beat is about 14 ms of 200, so
the train stands still about 93 % of the time.

Build (render + voice + mux):   python build.py 6/scene03_one_beat
Render only (quick preview):    PYTHONPATH=.:films/film06_escapement manim -ql films/film06_escapement/scene03_one_beat.py Scene03
Narration lines and their start times live in scene03_one_beat.voice.txt. Numbers from figures.py.
The close-up is lever.py's schematic Swiss lever; the beat is slowed over a thousand times.
The scene writes scene03_one_beat.ticks.txt on every render (one tick, at the drop).
"""
from manim import *
import prev  # noqa: F401  (first: Film 4 and 5 helpers on the path)
import figures as F
import lever as LV
from lever import LeverEscapement
from movement import vignette, BG, GLOW
from ui import label, heading, tag, curtain, clock, WARM, COOL
from ui6 import write_ticks

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds.
# Keep the timeline roughly in step with scene03_one_beat.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 1.0
SHOW_AT = 1.0                         # "Here is one beat in slow motion."
# the balance swing psi (degrees from the dead point), as keyframes (time, psi); events follow from the contacts:
# unlock at psi ~ -19.5, impulse ~ -11.2, drop ~ +15.7, banking ~ +19.6 (lever.events())
PSI_KEYS = [(0.0, -200.0), (2.0, -200.0), (14.2, -40.0), (16.0, -25.0), (22.6, -11.5),   # lock, then unlock
            (23.0, -11.5), (31.0, 15.0),                                                  # impulse
            (32.3, 15.0), (35.5, 21.0), (41.5, 150.0)]                                    # drop, lock, free swing
TIMING_AT = 42.7                      # "In Petrangeli's worked model ... about fourteen milliseconds"
LOCKED_AT = 49.0                      # "For ninety-three percent of each beat, the train stands still."
FINAL_HOLD_UNTIL = 56.0               # the last line ends about 54.1 s
FADE_OUT = 1.5

# --- the close-up ----------------------------------------------------
CENTER, SCALE, RIM_R = (0.0, -4.35), 3.4, 0.6
CAP_RATE = 1 / 200                    # model clock for the drop's speed cap (the drop takes a moment to see)
PHASE_COLOR = dict(lock=GREY_A, unlock=COOL, impulse=WARM, drop=GLOW)
TEXT = dict(slow="slowed down over a thousand times", schematic="schematic Swiss lever",
            phase=dict(lock="LOCK", unlock="UNLOCK", impulse="IMPULSE", drop="DROP"),
            beat="one beat:  0.2 s", active="active:  {:.1f} ms", locked="locked {:.0f} % of the time",
            phases=("unlock", "impulse I", "impulse II", "drop"),
            source="Petrangeli (2017): a model Swiss lever at 2.5 Hz")
# =====================================================================


def psi_at(t):
    ts, ps = zip(*PSI_KEYS)
    return float(np.interp(t, ts, ps))


class Scene03(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.add(vignette())
        wait_until = clock(self)

        esc = LeverEscapement(center=CENTER, scale=SCALE, rim_r=RIM_R)
        esc.drive.set_value(0.0)
        esc.rate.set_value(CAP_RATE)
        esc.manual.set_value(psi_at(0))
        esc.vis.set_value(0.0)
        esc.attach(self)
        driver = Mobject().add_updater(lambda m: esc.manual.set_value(psi_at(self.renderer.time)))
        self.add(driver)

        head = heading("ONE BEAT", "in slow motion").to_corner(UL, buff=0.5)
        slow = tag(TEXT["slow"], GLOW, 0.2).to_corner(UR, buff=0.4)
        sch = tag(TEXT["schematic"], GREY_B, 0.18).next_to(slow, DOWN, buff=0.12, aligned_edge=RIGHT)

        # the phase, named as it happens
        def phase_word():
            p = esc.phase()
            return label(TEXT["phase"][p], 0.62, PHASE_COLOR[p], bold=True).move_to([0, 3.35, 0])
        word = phase_word()
        word.add_updater(lambda m: m.become(phase_word()))

        # Petrangeli's timings
        W = 10.0
        x0 = -W / 2
        y_top, y_mag = -0.9, -2.5
        beat = Rectangle(width=W, height=0.32).set_stroke(GREY_B, 1.2).set_fill(GREY_D, 0.6).move_to([0, y_top, 0])
        act_w = W * F.GP_ACTIVE / F.HALF_PERIOD
        act = Rectangle(width=act_w, height=0.32).set_stroke(width=0).set_fill(GLOW, 0.9)
        act.move_to([x0 + act_w / 2, y_top, 0])
        beat_lbl = label(TEXT["beat"], 0.26).next_to(beat, UP, buff=0.12).align_to(beat, RIGHT)
        act_lbl = label(TEXT["active"].format(F.GP_ACTIVE * 1e3), 0.26, GLOW).next_to(act, UP, buff=0.12).align_to(act, LEFT)
        segs, x, cols = VGroup(), x0, (COOL, WARM, WARM, GLOW)
        for (name, dt), c, nm in zip(F.GP_PHASES.items(), cols, TEXT["phases"]):
            w = W * dt / F.GP_ACTIVE
            r = Rectangle(width=w, height=0.42).set_stroke(BG, 2).set_fill(c, 0.85 if "II" not in nm else 0.6)
            r.move_to([x + w / 2, y_mag, 0])
            t = VGroup(label(nm, 0.22, WHITE), label(f"{dt * 1e3:.1f} ms", 0.2, GREY_B)).arrange(DOWN, buff=0.06)
            t.next_to(r, DOWN, buff=0.12)
            segs.add(VGroup(r, t))
            x += w
        fan = VGroup(DashedLine(act.get_corner(DL), [x0, y_mag + 0.21, 0], stroke_width=1.2, color=GREY_B),
                     DashedLine(act.get_corner(DR), [x0 + W, y_mag + 0.21, 0], stroke_width=1.2, color=GREY_B))
        locked = label(TEXT["locked"].format(F.GP_LOCKED_FRAC * 100), 0.34, WHITE, bold=True)
        locked.next_to(beat, UP, buff=0.55).shift(RIGHT * 1.5)
        src = tag(TEXT["source"], GREY_B, 0.18).to_edge(DOWN, buff=0.35)
        timing = VGroup(beat, act, beat_lbl, act_lbl, fan, segs)
        shade = Rectangle(width=W + 1.4, height=3.6).set_stroke(width=0).set_fill(BG, 0.85).move_to([0, -1.9, 0])

        cur = curtain()
        self.add(cur)

        # ---------------------------------------------------------- timeline
        self.play(cur.animate.set_fill(opacity=0), run_time=FADE_IN, rate_func=smooth)
        self.remove(cur)
        wait_until(SHOW_AT)
        self.play(FadeIn(head), esc.vis.animate.set_value(1.0), FadeIn(slow), FadeIn(sch), run_time=1.0)
        self.add(word)

        wait_until(TIMING_AT)
        self.play(esc.vis.animate.set_value(0.35), FadeIn(shade), FadeOut(word), run_time=0.8)
        self.play(FadeIn(beat), FadeIn(beat_lbl), run_time=0.6)
        self.play(FadeIn(act), FadeIn(act_lbl), run_time=0.6)
        self.play(Create(fan), LaggedStart(*[FadeIn(s) for s in segs], lag_ratio=0.3), FadeIn(src), run_time=1.6)
        wait_until(LOCKED_AT)
        self.play(FadeIn(locked, shift=UP * 0.1), Indicate(beat, color=GREY_A, scale_factor=1.03), run_time=1.0)

        wait_until(FINAL_HOLD_UNTIL)
        cur.set_fill(opacity=0)
        self.add(cur)
        self.play(cur.animate.set_fill(opacity=1), run_time=FADE_OUT)
        write_ticks(__file__, [t for t, k in esc.events if k == "drop"])
