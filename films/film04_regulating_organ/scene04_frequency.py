"""Film 4, scene 04 - "The natural frequency": the swing's rate written three
ways, omega0 = sqrt(kappa / I), T0 = 2 pi sqrt(I / kappa), f0 = (1 / 2 pi) sqrt(kappa / I):
one timebase, set by I and kappa alone. This balance runs at 2.5 Hz: 5 beats a
second, 18,000 an hour. That is Film 3's B: n = B / (120 Z) turns the 15-tooth
escape wheel 10 times a minute (shown stepping, in time with the balance).

Build (render + voice + mux):   python build.py 4/scene04_frequency
Render only (quick preview):    PYTHONPATH=.:films/film04_regulating_organ manim -ql films/film04_regulating_organ/scene04_frequency.py Scene04
Narration lines and their start times live in scene04_frequency.voice.txt.
The balance runs in real time (2.5 Hz). The scene writes scene04_frequency.ticks.txt on every render.
"""
from manim import *
import figures as F
from movement import vignette, BG, GLOW, STEEL, STEEL_HI, vm
from balance import BalanceModel, BeatLog, escape_wheel_g
from ui import ftext, label, heading, curtain, clock, WARM

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds.
# Keep the timeline roughly in step with scene04_frequency.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 1.0
HEAD_AT = 1.6                         # "one natural rate"
FORM_AT = {"omega": 7.4, "T": 12.8, "f": 14.7}   # angular frequency, period, frequency
SAME_AT = 19.4                        # "All three say the same thing"
ONLY_AT = 22.6                        # "only I and kappa appear"
NOT_AT = 24.4                         # "not the mainspring, and not the gears"
CHAIN_AT = (28.0, 30.4, 31.8)         # 2.5 Hz, five beats a second, eighteen thousand an hour
FILM3_AT = 35.2                       # "That's the B in film three's formula"
ESCAPE_AT = 38.4                      # "the fifteen-tooth escape wheel turns ten times a minute"
FINAL_HOLD_UNTIL = 43.6               # the last line ends about 41.9 s
FADE_OUT = 1.5

# --- pictures ----------------------------------------------------------
BAL_AT, BAL_R, AMP = (-4.6, 1.0), 1.55, 1.2
ESC_AT, ESC_R = (-4.6, -2.1), 0.9
FORM_X, FORM_Y = 1.6, (2.4, 1.35, 0.3)
# =====================================================================


class Scene04(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.add(vignette())
        wait_until = clock(self)

        bal = BalanceModel(center=BAL_AT, radius=BAL_R, amp=AMP)
        bal.attach(self)
        log = BeatLog(self, lambda: bal.model_t, 2 * bal.hz)

        # escape wheel: one half-tooth per beat, a quick snap at the start of each beat (as in movement.state)
        esc = vm(escape_wheel_g(ESC_R, F.Z_ESCAPE), STEEL, 1.0, STEEL_HI, 0.8).move_to([*ESC_AT, 0])
        esc_pivot = np.array([*ESC_AT, 0.0])
        esc_vis = ValueTracker(0.0)
        esc._ang = 0.0

        def step_escape(m):
            b = bal.model_t * 2 * bal.hz
            k = np.floor(b)
            a = -(k + min(1.0, (b - k) / 0.18)) * TAU / (2 * F.Z_ESCAPE)
            m.rotate(a - m._ang, about_point=esc_pivot)
            m._ang = a
            m.set_fill(opacity=esc_vis.get_value()).set_stroke(opacity=0.8 * esc_vis.get_value())
        esc.add_updater(step_escape)
        esc_name = label(f"escape wheel, {F.Z_ESCAPE} teeth", 0.26, WHITE).next_to(esc, DOWN, buff=0.18)
        esc_rate = label(f"{F.ESCAPE_RPM:g} turns a minute", 0.26, GLOW).next_to(esc_name, DOWN, buff=0.08)

        head = heading("THE NATURAL FREQUENCY", "set by I and κ alone").to_corner(UL, buff=0.5).shift(RIGHT * 5.4)
        forms = {
            "omega": VGroup(ftext("ω₀  =  √(κ / I)", 0.62), label("angular frequency, radians per second", 0.24)),
            "T": VGroup(ftext("T₀  =  2π √(I / κ)", 0.62), label("period, seconds", 0.24)),
            "f": VGroup(ftext("f₀  =  (1 / 2π) √(κ / I)", 0.62), label("frequency, cycles per second", 0.24)),
        }
        for (k, g), y in zip(forms.items(), FORM_Y):
            g.arrange(RIGHT, buff=0.5, aligned_edge=DOWN).move_to([FORM_X, y, 0], aligned_edge=LEFT)
            g.shift(LEFT * 2.0)
        block = VGroup(*forms.values())
        # a hand-drawn bracket (Brace goes through LaTeX)
        x = block.get_left()[0] - 0.25
        bracket = VMobject().set_points_as_corners([[x + 0.15, FORM_Y[0] + 0.3, 0], [x, FORM_Y[0] + 0.3, 0],
                                                    [x, FORM_Y[2] - 0.3, 0], [x + 0.15, FORM_Y[2] - 0.3, 0]])
        bracket.set_stroke(GLOW, 2.5)
        same = label("one timebase", 0.28, GLOW).rotate(PI / 2).next_to(bracket, LEFT, buff=0.12)
        notes = label("no mainspring, no gears", 0.28, WARM).next_to(block, DOWN, buff=0.35, aligned_edge=LEFT)

        chain = VGroup(ftext(f"f₀  =  {F.F_6497:g} Hz", 0.6, WHITE),
                       label(f"{F.BEATS_PER_S:g} beats a second", 0.3, WHITE),
                       label(f"{F.BPH_6497:,.0f} beats an hour", 0.3, GLOW))
        arrows = VGroup(*[ftext("→", 0.5, GREY_B) for _ in range(2)])
        row = VGroup(chain[0], arrows[0], chain[1], arrows[1], chain[2]).arrange(RIGHT, buff=0.3)
        row.move_to([1.6, -1.25, 0])
        film3 = VGroup(label("Film 3:", 0.28, GLOW),
                       ftext(f"n  =  B / (120 Z)  =  {F.BPH_6497:,.0f} / (120 × {F.Z_ESCAPE})  =  {F.ESCAPE_RPM:g}", 0.48))
        film3.arrange(RIGHT, buff=0.3).move_to([1.9, -2.45, 0])

        cur = curtain()
        self.add(esc, esc_vis, cur)

        # ---------------------------------------------------------- timeline
        self.play(cur.animate.set_fill(opacity=0), run_time=FADE_IN, rate_func=smooth)
        self.remove(cur)
        wait_until(HEAD_AT)
        self.play(FadeIn(head, shift=DOWN * 0.1), run_time=0.8)
        for k in ("omega", "T", "f"):
            wait_until(FORM_AT[k])
            self.play(FadeIn(forms[k], shift=RIGHT * 0.15), run_time=0.9)
        wait_until(SAME_AT)                                 # one timebase
        self.play(Create(bracket), FadeIn(same), run_time=1.0)
        wait_until(ONLY_AT)                                 # only I and kappa
        self.play(*[Indicate(f[0], color=GLOW, scale_factor=1.06) for f in forms.values()], run_time=1.4)
        wait_until(NOT_AT)
        self.play(FadeIn(notes, shift=UP * 0.1), run_time=0.8)

        for i, t in enumerate(CHAIN_AT):                    # 2.5 Hz -> 5 a second -> 18,000 an hour
            wait_until(t)
            parts = [chain[i]] + ([arrows[i - 1]] if i else [])
            self.play(*[FadeIn(p, shift=RIGHT * 0.1) for p in parts], run_time=0.7)

        wait_until(FILM3_AT)                                # Film 3's formula
        self.play(FadeIn(film3, shift=UP * 0.1), run_time=0.9)
        wait_until(ESCAPE_AT)                               # the escape wheel steps, 10 turns a minute
        self.play(esc_vis.animate.set_value(1.0), FadeIn(esc_name), FadeIn(esc_rate), run_time=0.9)

        wait_until(FINAL_HOLD_UNTIL)
        cur.set_fill(opacity=0)
        self.add(cur)
        self.play(cur.animate.set_fill(opacity=1), run_time=FADE_OUT)
        log.write(__file__)
