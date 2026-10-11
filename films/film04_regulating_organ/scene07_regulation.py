"""Film 4, scene 07 - "Regulation": the running movement, close on the balance
cock, while the regulator's index swings; beside it a flat close-up of the
hairspring shows what the index does: two curb pins slide along the outer coil
and change its active length (lit). kappa goes as 1 / l, so df/f = -(1/2) dl/l:
shorter runs fast, longer runs slow; 10 s/day is a shift of about 0.05 mm on a
21 cm spring. Then a free-sprung balance: no index; masselottes on the rim turn
in or out to change I.

Build (render + voice + mux):   python build.py 4/scene07_regulation
Render only (quick preview):    PYTHONPATH=.:films/film04_regulating_organ manim -ql films/film04_regulating_organ/scene07_regulation.py Scene07

The scene starts with frame_center at the origin (no fixed-layer offset; see
CLAUDE.md) and moves the camera while the curtain is still down. The inset lives
in the screen-fixed layer, so it updates persistent mobjects (no always_redraw).
One tracker, `index`, drives both the 3D regulator (mv.regulate) and the inset's pins.
"""
from manim import *
import figures as F
from movement import Movement, attach_driver, camera_move, vignette, P, R, BG, GLOW, STEEL, STEEL_HI
from balance import BalanceModel
from ui import ftext, label, heading, tag, curtain, clock, WARM, COOL

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds, angles in degrees.
# Keep the timeline roughly in step with scene07_regulation.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 1.2
HEAD_AT = 2.0                         # "every watch is adjusted"
INDEX_AT = 11.4                       # "the regulator's index"
INSET_AT = 13.8                       # "moves two small pins along the hairspring's outer coil"
ACTIVE_AT = 17.0                      # "changing its active length"
LAW_AT = 20.4                         # "Stiffness goes as one over length"
SHORT_AT, LONG_AT = 22.8, 25.4        # "Shorten ... runs fast", "Lengthen ... runs slow"
SHIFT_AT = 29.2                       # "Ten seconds a day takes a shift of about..."
FREE_AT = 36.6                        # "Free-sprung balances have no index"
MASS_AT = 40.6                        # "small weights on the rim, masselottes, turn in or out"
FINAL_HOLD_UNTIL = 46.6               # the last line ends about 44.9 s
FADE_OUT = 1.5

# --- the index ---------------------------------------------------------
INDEX_DEG = 9.0                       # index swing in the 3D model, each way
PINS_MID, PINS_RANGE = 0.86, 0.06     # inset pin position (fraction of spring length) and its swing

# --- tier heights, camera ------------------------------------------------
Z = {"dial": 0.00, "engine": 0.30, "top": 0.62}
CAM = dict(phi=22, theta=-90, zoom=2.2)
TARGET_OFFSET = (1.75, 0.35)          # puts the balance on the left of the screen

# --- inset (screen-fixed, right half) ----------------------------------
INSET_C, INSET_R = (3.9, 0.55), 1.75
PANEL = (0.75, -3.65, 7.0, 3.1)       # x0, y0, x1, y1 of the inset's backing panel
# =====================================================================


class Scene07(ThreeDScene):
    def construct(self):
        self.camera.background_color = BG
        self.set_camera_orientation(phi=CAM["phi"] * DEGREES, theta=-90 * DEGREES, zoom=1.0, frame_center=ORIGIN)
        self.add_fixed_in_frame_mobjects(vignette())
        wait_until = clock(self)

        mv = Movement()
        mv.tiers["dial"].remove(mv.parts["dial_works"])
        mv.rot = [r for r in mv.rot if r[2] != "dial"]
        attach_driver(self, mv, Z, Z)
        index = ValueTracker(0.0)                          # -1 .. 1, drives the regulator and the inset's pins

        # ---- inset: the hairspring close-up, regulated by curb pins
        panel = RoundedRectangle(width=PANEL[2] - PANEL[0], height=PANEL[3] - PANEL[1], corner_radius=0.15)
        panel.move_to([(PANEL[0] + PANEL[2]) / 2, (PANEL[1] + PANEL[3]) / 2, 0]).set_fill(BG, 0).set_stroke(GREY_D, 1, 0)   # faded in later, in place (under the inset)
        bal = BalanceModel(center=INSET_C, radius=INSET_R, amp=0.9, pins=PINS_MID)
        bal.vis.set_value(0.0)
        bal._apply_vis()
        active = VMobject().set_stroke(GLOW, 4.5, 0).set_fill(opacity=0)
        show_active = ValueTracker(0.0)

        def follow(_):
            mv.regulate.set_value(INDEX_DEG * index.get_value())
            bal.pins.set_value(PINS_MID + PINS_RANGE * index.get_value())
            active.set_points_smoothly(bal.active_points())
            active.set_stroke(opacity=show_active.get_value())
        sync = Mobject()
        sync.add_updater(follow)

        # ---- the free-sprung balance with masselottes
        free = BalanceModel(center=INSET_C, radius=INSET_R, amp=0.9, pins=1.0)
        free.vis.set_value(0.0)
        free._apply_vis()
        mass_in = ValueTracker(0.0)                         # 0 = out, 1 = turned in
        masses = VGroup(*[Rectangle(width=0.16, height=0.26).set_fill(STEEL_HI, 1).set_stroke(WHITE, 0.8) for _ in range(4)])

        def place_masses(m):
            v = free.vis.get_value()
            for k, sq in enumerate(m):
                a = free._ang + PI / 4 + k * PI / 2
                r = INSET_R * (0.76 - 0.07 * mass_in.get_value())
                sq.become(Rectangle(width=0.16, height=0.26).set_fill(STEEL_HI, v).set_stroke(WHITE, 0.8, v)
                          .rotate(a).move_to([INSET_C[0] + r * np.cos(a), INSET_C[1] + r * np.sin(a), 0]))
        masses.add_updater(place_masses)

        inset_head = label("what the index does", 0.27, GLOW).move_to([(PANEL[0] + PANEL[2]) / 2, PANEL[3] - 0.3, 0])
        pin_lab = label("curb pins", 0.26, WHITE)
        active_lab = label("active length  ℓ", 0.26, GLOW)
        law = VGroup(ftext("κ  ∝  1 / ℓ", 0.5), ftext("Δf / f  ≈  −½ Δℓ / ℓ", 0.5)).arrange(RIGHT, buff=0.6)
        law.move_to([(PANEL[0] + PANEL[2]) / 2, PANEL[1] + 0.85, 0])
        fast = label("shorter: runs fast", 0.27, WARM)
        slow = label("longer: runs slow", 0.27, COOL)
        for t in (fast, slow):
            t.move_to([(PANEL[0] + PANEL[2]) / 2, PANEL[1] + 0.35, 0])
        shift = VGroup(ftext(f"{F.REG_S_DAY:.0f} s/day:   Δℓ  ≈  2 × {F.REG_S_DAY / F.DAY * 1e6:.0f} ppm × {F.L_HS_6497 * 100:.0f} cm", 0.36),
                       ftext(f"≈  {F.REG_DL * 1e3:.2f} mm", 0.44, GLOW),
                       label(f"taking the whole {F.L_HS_6497 * 100:.0f} cm (representative) as active", 0.22)).arrange(DOWN, buff=0.1)
        shift.move_to([(PANEL[0] + PANEL[2]) / 2, PANEL[1] + 0.62, 0])
        free_head = label("free-sprung: no index", 0.27, GLOW).move_to(inset_head)
        mass_lab = label("masselottes", 0.26, WHITE)
        mass_law = label("turn them in: I falls, the watch runs faster", 0.27, WARM).move_to(law)

        head = heading("REGULATION", "adjusting after assembly").to_corner(UL, buff=0.5)
        head = VGroup(SurroundingRectangle(head, buff=0.15, corner_radius=0.08).set_fill(BG, 0.85).set_stroke(width=0), head)
        index_lab = label("regulator index", 0.3, WHITE)

        cur = curtain()
        fixed = [panel, bal, active, free, masses, inset_head, pin_lab, active_lab, law, fast, slow, shift,
                 free_head, mass_lab, mass_law, head, index_lab]
        self.add_fixed_in_frame_mobjects(*fixed, cur)
        bal.attach(self, add=False)
        free.attach(self, add=False)
        self.add(index, show_active, mass_in, sync)
        self.remove(inset_head, pin_lab, active_lab, law, fast, slow, shift, free_head, mass_lab,
                    mass_law, head, index_lab)

        # ---------------------------------------------------------- timeline
        bc = P["balance"]
        target = bc + np.array([TARGET_OFFSET[0], TARGET_OFFSET[1], Z["engine"] + 0.3])
        self.play(*camera_move(self, 0.1, target=target, frame_origin=ORIGIN, **CAM))   # behind the curtain
        self.remove(self.camera._frame_center)
        self.play(cur.animate.set_fill(opacity=0), run_time=FADE_IN, rate_func=smooth)
        wait_until(HEAD_AT)
        self.play(FadeIn(head, shift=RIGHT * 0.2), run_time=0.8)

        wait_until(INDEX_AT)                                # the regulator's index (pinned with the camera's projection)
        tip = self.camera.project_point(bc + np.array([1.24 * np.cos(np.radians(-11.7)), 1.24 * np.sin(np.radians(-11.7)),
                                                       Z["top"] + 0.2]))
        index_lab.move_to(tip + np.array([-0.2, -1.1, 0]))
        lead = Line(index_lab.get_top() + UP * 0.05, tip).set_stroke(GREY_A, 2, 0.9)
        self.add_fixed_in_frame_mobjects(lead)
        self.remove(lead)
        self.play(FadeIn(index_lab), Create(lead), run_time=0.8)
        self.play(index.animate.set_value(1.0), run_time=1.2, rate_func=smooth)

        wait_until(INSET_AT)                                # the inset: pins on the outer coil
        self.play(panel.animate.set_fill(opacity=0.92).set_stroke(opacity=1), FadeIn(inset_head),
                  bal.vis.animate.set_value(1.0), run_time=1.0)
        pin_lab.next_to(bal.curb, DOWN, buff=0.25)
        self.play(FadeIn(pin_lab), index.animate.set_value(-1.0), run_time=1.8, rate_func=smooth)
        wait_until(ACTIVE_AT)                               # the active length
        active_lab.move_to([INSET_C[0] - INSET_R - 0.05, INSET_C[1] + INSET_R * 0.85, 0], aligned_edge=LEFT)
        self.play(show_active.animate.set_value(1.0), FadeOut(pin_lab), FadeIn(active_lab), run_time=1.0)
        self.play(index.animate.set_value(0.0), run_time=1.2, rate_func=smooth)

        wait_until(LAW_AT)                                  # kappa ~ 1/l
        self.play(FadeIn(law, shift=UP * 0.1), run_time=1.0)
        wait_until(SHORT_AT)                                # shorter: fast
        self.play(index.animate.set_value(-1.0), FadeIn(fast), run_time=1.4, rate_func=smooth)
        wait_until(LONG_AT)                                 # longer: slow
        self.play(index.animate.set_value(1.0), FadeOut(fast), FadeIn(slow), run_time=2.0, rate_func=smooth)
        wait_until(SHIFT_AT)                                # 10 s/day = about 0.05 mm
        self.play(index.animate.set_value(0.0), FadeOut(slow), FadeOut(law), FadeIn(shift, shift=UP * 0.1),
                  run_time=1.2)

        wait_until(FREE_AT)                                 # free-sprung: no index
        self.play(bal.vis.animate.set_value(0.0), show_active.animate.set_value(0.0), FadeOut(active_lab),
                  FadeOut(shift), FadeOut(inset_head), FadeIn(free_head), free.vis.animate.set_value(1.0),
                  FadeOut(index_lab), FadeOut(lead), run_time=1.2)
        wait_until(MASS_AT)                                 # masselottes turn in
        mass_lab.move_to([INSET_C[0] + INSET_R + 0.3, INSET_C[1] + INSET_R + 0.12, 0], aligned_edge=RIGHT)
        self.play(FadeIn(mass_lab), FadeIn(mass_law, shift=UP * 0.1), run_time=0.8)
        self.play(mass_in.animate.set_value(1.0), run_time=1.6, rate_func=smooth)

        wait_until(FINAL_HOLD_UNTIL)
        self.remove(cur)
        self.add_fixed_in_frame_mobjects(cur)
        self.play(cur.animate.set_fill(opacity=1), run_time=FADE_OUT)
