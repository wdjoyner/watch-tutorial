"""Film 5, scene 07 - "Beat error": a slowed balance with its roller jewel and
the line of centers. The balance comes to rest; the collet turns on the staff,
and at rest the jewel now sits off the line. Swinging again, it crosses the
line at alternately long and short intervals, 1/(2f) + eps and 1/(2f) - eps
(exaggerated, and tagged so), and the tick track limps. Beside it a
timing-machine-style trace: tick and tock fall on two flat rows, apart by the
beat error, which the film reports as 2 eps = |dt1 - dt2| (the chapter's
timegrapher convention). Each pair still sums to 1/f = 0.4 s: the rows stay
flat, the rate is untouched.

Build (render + voice + mux):   python build.py 5/scene07_beat_error
Render only (quick preview):    PYTHONPATH=.:films/film05_isochronism manim -ql films/film05_isochronism/scene07_beat_error.py Scene07
Narration lines and their start times live in scene07_beat_error.voice.txt. Numbers from figures.py.
The scene writes scene07_beat_error.ticks.txt on every render (one tick per crossing of the line of centers).
"""
from manim import *
import os
import iso  # noqa: F401  (first: puts Film 4's helpers on the path)
import figures as F
from iso import IsoBalance, CrossLog
from movement import vignette, BG, GLOW, RUBY, STEEL, STEEL_HI
from ui import ftext, label, heading, tag, curtain, clock, WARM, COOL

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds.
# Keep the timeline roughly in step with scene07_beat_error.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 1.0
HEAD_AT = 1.2                         # "Last, beat error"
STOP_AT = 3.4                         # the balance comes to rest
TURN_AT = 6.0                         # "If the collet is turned on the staff relative to the stud"
OFF_AT = 9.0                          # "the roller jewel sits off the line of centers when the balance is at rest"
GO_AT = 12.2                          # swinging again
DT_AT = (13.6, 16.8)                  # "one interval is a fifth of a second plus epsilon", "the next a fifth minus"
LISTEN_AT = 21.0                      # "Listen to the difference. First, a watch in beat."
DEMO_A_AT = 25.3                      # in-beat ticks (wood block), no narration
OUT_AT = 29.6                         # "Now one out of beat, exaggerated so you can hear it."
DEMO_B_AT = 33.8                      # out-of-beat ticks (bell), no narration
DEMO_END = 38.0                       # the balance's own tick track is muted from LISTEN_AT + 3 to here
BE_AT = 38.4                          # "A timing machine reports the difference, two epsilon, in milliseconds"
SUM_AT = 44.2                         # "each pair still adds up to two fifths of a second"
UNTOUCHED_AT = 47.1                   # "so the rate is untouched"
BUT_AT = 53.1                         # "though it starts less reliably, and suffers more from escapement error"
FINAL_HOLD_UNTIL = 60.8               # the last line ends about 59.2 s
FADE_OUT = 1.5

# --- the balance ---------------------------------------------------------
BAL_AT, BAL_R, AMP = (-4.5, 1.0), 1.5, 1.2
RATE = 0.25                           # slow motion
OFFSET = AMP * np.sin(np.pi * F.BEAT_ERR_SHOWN / 2)   # EXAGGERATED: each interval 1/(2f) (1 +/- BEAT_ERR_SHOWN)
LEVER_AT = (-4.5, -1.75)              # pallet-lever pivot, on the line of centers

# --- the listening demo: two short runs of louder ticks, each its own sound (build.py SOUNDS)
DEMO_HALF = 0.5                       # seconds between ticks in beat (slowed: a real 6497 ticks every 0.2 s)
DEMO_N = 8                            # ticks in each run
DEMO_LEVEL = 3.0                      # sfx level multiplier (build.py --sfx-level scales it)
DEMO_Y, DEMO_X0, DEMO_DX = (-1.95, -2.75), 1.9, 0.62   # rows' y, first dot's x, x per second

# --- the trace ---------------------------------------------------------------
TRACE_X0, TRACE_Y, TRACE_W = 0.4, 1.05, 5.6
DX = 0.095                            # horizontal step per beat
K = 3.2                               # vertical units per second of video-time deviation
# =====================================================================


class Scene07(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.add(vignette())
        wait_until = clock(self)

        bal = IsoBalance(center=BAL_AT, radius=BAL_R, amp=AMP, amp_full=AMP)
        c = bal.c
        jewel = Dot(c + DOWN * BAL_R * 0.34, radius=0.075, color=RUBY)
        roller = Circle(radius=BAL_R * 0.38).move_to(c).set_stroke(STEEL_HI, 1.4)
        bal.rotor.add(roller, jewel)                        # turns with the staff
        bal.rate.set_value(RATE)
        bal.attach(self)
        muted = lambda: LISTEN_AT + 3.0 < self.renderer.time < DEMO_END
        log = CrossLog(self, bal, active=lambda: bal.drive.get_value() > 0.5 and not muted())
        slow = tag("slowed 4×").next_to(bal, UP, buff=0.25)

        lever = np.array([*LEVER_AT, 0.0])
        loc = DashedLine(c + UP * (BAL_R + 0.2), lever, dash_length=0.08).set_stroke(GREY_B, 1.6)
        pivot = Dot(lever, radius=0.09, color=STEEL)
        fork = VGroup(Line(lever, lever + UP * 0.75), Line(lever + UP * 0.75 + LEFT * 0.12, lever + UP * 0.95 + LEFT * 0.12),
                      Line(lever + UP * 0.75 + RIGHT * 0.12, lever + UP * 0.95 + RIGHT * 0.12),
                      Line(lever + UP * 0.75 + LEFT * 0.12, lever + UP * 0.75 + RIGHT * 0.12)).set_stroke(STEEL_HI, 2.5)
        loc_lbl = label("line of centers", 0.22).next_to(lever, RIGHT, buff=0.25).shift(UP * 0.35)
        lever_lbl = label("pallet lever", 0.22).next_to(pivot, DOWN, buff=0.12)
        turned = label("collet turned\non the staff", 0.24, WARM).move_to(c + RIGHT * 2.45 + UP * 0.55)
        offl = label("at rest: the jewel\nsits off the line", 0.24, WARM).move_to(c + RIGHT * 2.3 + DOWN * 1.15)
        arrow_off = Arrow(offl.get_left() + LEFT * 0.05, c + DOWN * BAL_R * 0.34 + RIGHT * 0.2, buff=0.1,
                          stroke_width=2.5, tip_length=0.14, color=WARM)

        # timing-machine trace: each beat a dot, its time's deviation from a steady grid
        tr_frame = Rectangle(width=TRACE_W + 0.3, height=2.5).move_to([TRACE_X0 + TRACE_W / 2, TRACE_Y, 0])
        tr_frame.set_stroke(GREY_C, 1.2).set_fill("#0d1016", 1)
        tr_title = label("timing machine (schematic)", 0.22).next_to(tr_frame, UP, buff=0.08).align_to(tr_frame, LEFT)
        tr_time = label("beats →", 0.2).next_to(tr_frame, DOWN, buff=0.08).align_to(tr_frame, RIGHT)
        dots = VGroup()
        state = {"n": 0, "ref": None}
        half = 1 / (2 * bal.hz * RATE)                      # nominal half-period in video seconds

        def grow(m):
            while state["n"] < len(log.times):
                t = log.times[state["n"]]
                if state["ref"] is None:
                    state["ref"] = (t, state["n"])
                t0, n0 = state["ref"]
                k = int(round((t - t0) / half))
                dev = t - (t0 + k * half)
                x = TRACE_X0 + 0.15 + (k * DX) % TRACE_W
                col = WARM if k % 2 == 0 else COOL
                m.add(Dot([x, TRACE_Y - K * dev, 0], radius=0.045, color=col))
                state["n"] += 1
        dots.add_updater(grow)
        tick_key = VGroup(label("tick", 0.2, WARM), label("tock", 0.2, COOL)).arrange(RIGHT, buff=0.25)
        tick_key.next_to(tr_frame, DOWN, buff=0.08).align_to(tr_frame, LEFT)

        gap = K * F.BEAT_ERR_SHOWN * half                   # tick and tock rows are 2 eps apart in time
        rows_gap = DoubleArrow([TRACE_X0 + TRACE_W + 0.35, TRACE_Y + gap / 2, 0],
                               [TRACE_X0 + TRACE_W + 0.35, TRACE_Y - gap / 2, 0],
                               buff=0, stroke_width=2.5, tip_length=0.1, color=GLOW)

        dts = VGroup(ftext("Δt₁  =  1/(2f)  +  ε", 0.5), ftext("Δt₂  =  1/(2f)  −  ε", 0.5))
        dts.arrange(DOWN, buff=0.16, aligned_edge=LEFT).move_to([0.5, -1.15, 0], aligned_edge=LEFT)
        fifth = label(f"1/(2f)  =  {F.HALF_PERIOD:g} s", 0.24).next_to(dts, RIGHT, buff=0.4)
        exag = tag("beat error exaggerated, in picture and sound").move_to([BAL_AT[0], -3.15, 0])
        be = VGroup(ftext("beat error  =  Δt₁ − Δt₂  =  2ε", 0.46, GLOW),
                    label(f"reported in ms,  e.g. {F.BEAT_ERR_REPR * 1e3:.1f} ms", 0.24, GLOW)).arrange(DOWN, buff=0.17, aligned_edge=LEFT)
        be.next_to(dts, DOWN, buff=0.25).align_to(dts, LEFT)
        rep = tag("representative").next_to(be[1], RIGHT, buff=0.2)
        total = ftext(f"Δt₁  +  Δt₂  =  1/f  =  {F.FULL_PERIOD:g} s", 0.46, COOL).next_to(be, DOWN, buff=0.22).align_to(be, LEFT)
        flat = label("flat rows: the rate is untouched", 0.24, COOL).next_to(tr_frame, DOWN, buff=0.08).align_to(tr_frame, RIGHT)
        but = label("but:  less reliable self-starting,  more escapement error at low amplitude", 0.26, WARM)
        but.to_edge(DOWN, buff=0.3).align_to(dts, LEFT)

        # listening demo: each row's dots light as its ticks sound; the intervals are printed between them
        s_err = F.BEAT_ERR_SHOWN
        times_a = [DEMO_A_AT + k * DEMO_HALF for k in range(DEMO_N)]
        gaps_b = [DEMO_HALF * (1 + s_err if k % 2 == 0 else 1 - s_err) for k in range(DEMO_N - 1)]
        times_b = [DEMO_B_AT + sum(gaps_b[:k]) for k in range(DEMO_N)]

        def demo_row(times, y, color, name, start):
            dots = VGroup(*[Dot([DEMO_X0 + (t - start) * DEMO_DX * 2, y, 0], radius=0.09, color=color) for t in times])
            gaps = VGroup(*[label(f"{b - a:.2f}", 0.2, color).move_to((dots[i].get_center() + dots[i + 1].get_center()) / 2 + UP * 0.25)
                            for i, (a, b) in enumerate(zip(times, times[1:]))])
            name_l = label(name, 0.24, color, bold=True).next_to(dots[0], LEFT, buff=0.3)

            def flash(m):
                now = self.renderer.time
                for d, t in zip(m, times):
                    lit = 0 <= now - t < 0.18
                    d.set_opacity(1.0 if lit else (0.45 if now >= t else 0.12)).scale_to_fit_width(0.3 if lit else 0.18)
            dots.add_updater(flash)
            return VGroup(name_l, dots, gaps)
        row_a = demo_row(times_a, DEMO_Y[0], COOL, "in beat", DEMO_A_AT)
        row_b = demo_row(times_b, DEMO_Y[1], WARM, "out of beat", DEMO_B_AT)
        note_a = label(f"every interval {DEMO_HALF:.2f} s", 0.22, COOL).next_to(row_a[1], DOWN, buff=0.12).align_to(row_a[1], LEFT)
        note_b = label(f"long, short:  off by ±{s_err * DEMO_HALF:.2f} s,  2ε = {2 * s_err * DEMO_HALF:.2f} s  (exaggerated)",
                       0.22, WARM).next_to(row_b[1], DOWN, buff=0.12).align_to(row_b[1], LEFT)
        real = label(f"a real 6497 (representative):  {F.TICK_A:.4f} s,  {F.TICK_B:.4f} s,  2ε = {F.BEAT_ERR_REPR * 1e3:.1f} ms",
                     0.22, GREY_B).next_to(note_b, DOWN, buff=0.14).align_to(note_b, LEFT)
        demo = VGroup(row_a, row_b, note_a, note_b, real)
        demo_head = label("listen  (slowed)", 0.24, GLOW, bold=True).next_to(row_a, UP, buff=0.35).align_to(row_a, LEFT)
        demo.add(demo_head)

        sfx = os.path.splitext(__file__)[0] + ".sfx.txt"
        with open(sfx, "w") as f:
            f.write("# Written by the scene on every render: the listening demo's ticks.\n")
            for t in times_a:
                f.write(f"{t:.3f} | wood | {DEMO_LEVEL}\n")
            for t in times_b:
                f.write(f"{t:.3f} | bell | {DEMO_LEVEL}\n")

        head = heading("BEAT ERROR", "a lopsided tick").to_corner(UL, buff=0.5)
        cur = curtain()
        self.add(dots, cur)

        # ---------------------------------------------------------- timeline
        self.play(cur.animate.set_fill(opacity=0), run_time=FADE_IN, rate_func=smooth)
        self.remove(cur)
        wait_until(HEAD_AT)
        self.play(FadeIn(head), FadeIn(slow), FadeIn(loc), FadeIn(pivot), FadeIn(fork), FadeIn(loc_lbl), FadeIn(lever_lbl),
                  FadeIn(tr_frame), FadeIn(tr_title), FadeIn(tr_time), FadeIn(tick_key), run_time=0.9)
        self.add(dots)                                      # in front of the trace's panel
        wait_until(STOP_AT)                                 # the balance comes to rest, in beat
        bal.manual.set_value(0.0)
        self.play(bal.drive.animate.set_value(0.0), run_time=1.6)
        wait_until(TURN_AT)                                 # the collet turns on the staff
        self.play(FadeIn(turned), run_time=0.6)
        self.play(bal.offset.animate.set_value(OFFSET), run_time=1.6)
        wait_until(OFF_AT)                                  # at rest, off the line
        self.play(FadeIn(offl), GrowArrow(arrow_off), run_time=0.8)
        wait_until(GO_AT)                                   # swinging again: out of beat
        self.play(bal.drive.animate.set_value(1.0), FadeOut(arrow_off), FadeOut(offl), run_time=1.2)
        wait_until(DT_AT[0])
        self.play(FadeIn(dts[0], shift=RIGHT * 0.1), FadeIn(fifth), run_time=0.8)
        wait_until(DT_AT[1])
        self.play(FadeIn(dts[1], shift=RIGHT * 0.1), run_time=0.8)
        wait_until(LISTEN_AT)                               # the listening demo
        self.play(FadeOut(dts), FadeOut(fifth), FadeIn(exag), run_time=0.6)
        self.play(FadeIn(demo_head), FadeIn(row_a), FadeIn(note_a), run_time=0.7)
        wait_until(OUT_AT)
        self.play(FadeIn(row_b), run_time=0.7)
        wait_until(DEMO_B_AT + 4.2)
        self.play(FadeIn(note_b), FadeIn(real), run_time=0.8)
        wait_until(BE_AT - 0.7)
        self.play(FadeOut(demo), FadeIn(dts), FadeIn(fifth), run_time=0.6)
        wait_until(BE_AT)                                   # beat error = 2 eps
        self.play(FadeIn(be, shift=UP * 0.1), FadeIn(rep), GrowFromCenter(rows_gap), run_time=0.9)
        wait_until(SUM_AT)                                  # each pair: 1/f
        self.play(FadeIn(total, shift=UP * 0.1), run_time=0.8)
        wait_until(UNTOUCHED_AT)
        self.play(FadeOut(tr_time), FadeIn(flat), run_time=0.7)
        wait_until(BUT_AT)
        self.play(FadeIn(but, shift=UP * 0.1), run_time=0.8)

        wait_until(FINAL_HOLD_UNTIL)
        cur.set_fill(opacity=0)
        self.add(cur)
        self.play(cur.animate.set_fill(opacity=1), run_time=FADE_OUT)
        log.write(__file__)
