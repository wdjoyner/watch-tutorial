"""Film 7, scene 04 - "Winding": the crown pushed in.

Left: the keyless close-up (keyless.py), pushed in. Right: the bridge side,
flat: the crown wheel meshing the ratchet wheel on the barrel arbor, the click,
and the barrel drum under them driving the center pinion. An amber path runs
crown -> sliding pinion -> winding pinion -> (through the plate) -> crown wheel
-> ratchet -> arbor, with Film 2's clicks, one per ratchet tooth. An inset shows
the spring winding (Film 2's packed-coil model, at the 6497's real numbers).
Turned backward, the Breguet teeth ride over and the click holds the ratchet.
One slow crown turn with a counter: 16 clicks (in this model). Then the count
to a full wind, about 8 barrel turns x 60/16 = 30 crown turns (figures.py). Last
the running path: the drum turns and drives the train; the arbor stays still.

Build (render + voice + mux):   python build.py 7/scene04_winding
Render only (quick preview):    PYTHONPATH=.:films/film07_keyless_works manim -ql films/film07_keyless_works/scene04_winding.py Scene04
Narration lines and their start times live in scene04_winding.voice.txt.
The scene writes scene04_winding.sfx.txt (one click per ratchet tooth) on every render.
"""
from manim import *
from shapely import affinity
import prev  # noqa: F401  (first: earlier films' helpers on the path)
import figures as F
from movement import (vignette, vm, teeth_g, pinion_g, ratchet_teeth_g, disk_g, polar, BG, GLOW, STEEL, STEEL_DK,
                      STEEL_HI, BRASS, BRASS_DK, BRASS_HI)
from shapely.geometry import LineString
from shapely.ops import unary_union
from ui import label, ftext, heading, tag, curtain, clock
from ui6 import callout, write_sfx
from keyless import KeylessWorks, Spinner
from barrel import pack_state_g, arbor_core_g, drum_floor_g, drum_wall_g, development, R_ROOT

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds.
# Keep the timeline roughly in step with scene04_winding.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 1.0
HEAD_AT = 1.0                  # "Pushed in, turning the crown winds the mainspring."
WIND = (2.4, 22.4)             # the crown turns forward
WIND_TURNS = 7.0               # crown turns during WIND
LABEL_AT = dict(sliding=5.4, winding=7.0, crown_wheel=9.0, ratchet=10.9, arbor=12.4)
INSET_AT = 14.0                # "The arbor reels in the spring, as we saw in Film 2."
CLICK_AT = 18.9                # "The click lets the ratchet turn one way only."
BACK_AT = 23.1                 # "Turn the crown backward, and the Breguet teeth ride over each other ..."
BACK = (23.6, 28.8)
BACK_TURNS = 1.25
COUNT_AT = 29.8                # "In this model, each turn of the crown moves the ratchet sixteen teeth ..."
COUNT = (30.4, 35.6)           # one slow crown turn, counted
FULL_AT = 36.6                 # "The barrel has about eight turns to give ... about thirty turns of the crown."
RUN_AT = 43.9                  # "Then the running path takes over ..."
RUN = (44.6, 55.0)
RUN_DRUM_TURNS = 0.12          # drum turns during RUN (sped up, tagged)
PATHS_AT = 51.6                # "Winding turns the arbor, and running turns the drum."
FINAL_HOLD_UNTIL = 56.2        # the last line ends about 55.3 s
FADE_OUT = 1.5

# --- layout ----------------------------------------------------------
KW_ORIGIN, KW_SCALE = (-5.25, 1.85), 1.0
BR_C = np.array([3.55, 0.55])  # barrel / ratchet center (bridge side)
R_DRUM, Z_DRUM = 1.85, 85
R_RATCHET, Z_RATCHET = 1.12, F.Z_RATCHET
Z_CW = F.Z_CROWN_WHEEL
CW_ANGLE = 152                 # crown wheel direction from the barrel center (degrees)
CENTER_ANGLE = -28             # center pinion direction from the barrel center
INSET_C, INSET_R = np.array([-4.95, -1.55]), 0.95
WIND_COLOR, RUN_COLOR = "#ffb54a", GLOW
SFX_LEVEL = 1.0

# --- on-screen text --------------------------------------------------
TEXT = dict(
    head=("WINDING", "crown pushed in"),
    dial_side="dial side", bridge_side="bridge side",
    sliding="sliding pinion", winding="winding pinion", crown_wheel="crown wheel", ratchet="ratchet wheel",
    arbor="barrel arbor", click="click: one way only", plate="through the plate",
    inset="mainspring (Film 2)",
    crown="crown", stem="stem", back="turned backward", ride="Breguet teeth\nride over",
    held="held by the click", count="clicks", model="in this model",
    one_turn="1 crown turn  =  {} clicks", full="{:.0f} barrel turns  ×  {} / {}  ≈  {:.0f} crown turns",
    full_note="about 8 turns from let down to fully wound (Film 2)",
    drum="barrel drum", center="center pinion: on to the gear train", sped="sped up",
    paths=("winding  ·  turns the arbor", "running  ·  turns the drum"),
)
# =====================================================================


def _scale(g, s):
    return affinity.scale(g, s, s, origin=(0, 0))


class Scene04(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.add(vignette())
        wait_until = clock(self)
        sfx = []

        # ---------------------------------------------------------- the dial side: keyless works
        kw = KeylessWorks(origin=KW_ORIGIN, scale=KW_SCALE)
        kw.vis.set_value(0.0)
        self.add(kw, *kw.trackers())

        # the winding train turns from the winding pinion's angle (only driven forward)
        def ratchet_angle():
            return kw._wp_ang * F.Z_WIND_PINION / Z_RATCHET

        def cw_angle():
            return -kw._wp_ang * F.Z_WIND_PINION / Z_CW

        drum_turn = ValueTracker(0.0)
        m_r = 2 * R_RATCHET / Z_RATCHET
        r_cw = m_r * Z_CW / 2
        cw_c = BR_C + polar(R_RATCHET + r_cw, CW_ANGLE)[:2]
        m_d = 2 * R_DRUM / Z_DRUM
        r_cp = m_d * 12 / 2
        cp_c = BR_C + polar(R_DRUM + r_cp, CENTER_ANGLE)[:2]

        drum = Spinner(vm(affinity.translate(teeth_g(R_DRUM, Z_DRUM).difference(disk_g(R_RATCHET + 0.05)), *BR_C),
                          BRASS, 1.0, BRASS_HI, 0.8), BR_C, lambda: drum_turn.get_value() * TAU)
        center = Spinner(vm(affinity.translate(pinion_g(12, m_d).difference(disk_g(0.04)), *cp_c), STEEL_HI, 1.0,
                            WHITE, 0.8), cp_c, lambda: -drum_turn.get_value() * TAU * Z_DRUM / 12)
        ratchet = Spinner(vm(affinity.translate(ratchet_teeth_g(R_RATCHET, Z_RATCHET, 0.06)
                                                .difference(disk_g(0.12)), *BR_C), STEEL, 1.0, STEEL_HI, 0.8),
                          BR_C, ratchet_angle)
        arbor = vm(disk_g(0.13, BR_C), STEEL_DK, 1.0, STEEL_HI, 0.8)
        crown_wheel = Spinner(vm(affinity.translate(teeth_g(r_cw, Z_CW).difference(disk_g(0.05)), *cw_c), STEEL, 1.0,
                                 STEEL_HI, 0.8), cw_c, cw_angle)
        # the click: rides up each tooth's slope and drops off its face (as in Film 2)
        tooth = TAU / Z_RATCHET
        cl_p = BR_C + polar(R_RATCHET + 0.32, 163)[:2]
        cl_t = BR_C + polar(R_RATCHET - 0.03, 147)[:2]
        click_g = unary_union([disk_g(0.11, cl_p), LineString([tuple(cl_p), tuple(cl_t)]).buffer(0.06)])
        click = Spinner(vm(click_g, STEEL_HI, 1.0, WHITE, 0.6), cl_p,
                        lambda: 0.12 * ((ratchet_angle() % tooth) / tooth))
        bridge = VGroup(drum, center, ratchet, arbor, crown_wheel, click)
        bridge_vis = ValueTracker(0.0)
        base_op = [(m, m.get_fill_opacity(), m.get_stroke_opacity()) for m in bridge.family_members_with_points()]

        def fade_bridge(m):
            v = bridge_vis.get_value()
            for mm, fo, so in base_op:
                mm.set_fill(opacity=fo * v, family=False).set_stroke(opacity=so * v, family=False)
        bridge.add_updater(fade_bridge)
        self.add(bridge, bridge_vis, drum_turn)

        # clicks: one each time the ratchet passes a tooth
        last_tooth = {"k": 0}

        def listen(m, dt):
            k = int(np.floor(ratchet_angle() / tooth + 1e-6))
            if k > last_tooth["k"]:
                sfx.extend((self.renderer.time, "click", SFX_LEVEL) for _ in range(min(1, k - last_tooth["k"])))
            last_tooth["k"] = k
        ear = Mobject().add_updater(listen)
        self.add(ear)

        # ---------------------------------------------------------- the spring inset (Film 2's model)
        s_in = INSET_R / (R_ROOT + 0.4)
        dev = development()
        a0_turns = 1.5                              # arbor turns already wound at the start (illustrative)
        inset_vis = ValueTracker(0.0)

        def inset():
            a_turns = min(dev, a0_turns + ratchet_angle() / TAU)
            inner, outer, free, arbor_deg, w = pack_state_g(a_turns, outer_deg=200.0)
            core = affinity.rotate(arbor_core_g(), arbor_deg - 55.0, origin=(0, 0))
            g = VGroup(Circle(radius=INSET_R).set_fill(BG, 1).set_stroke(width=0),
                       vm(_scale(drum_floor_g(), s_in), BRASS_DK, stroke=BRASS_DK, sw=0),
                       vm(_scale(drum_wall_g(), s_in), BRASS, stroke=BRASS_HI, sw=0.8),
                       *[vm(_scale(p, s_in), STEEL_HI, stroke=WHITE, sw=0.4) for p in (outer, inner, free)],
                       vm(_scale(core, s_in), STEEL, stroke=STEEL_HI, sw=0.6),
                       Circle(radius=INSET_R).set_stroke(WIND_COLOR, 2))
            g.move_to([*INSET_C, 0])
            v = inset_vis.get_value()
            for m in g.family_members_with_points():
                m.set_fill(opacity=m.get_fill_opacity() * v, family=False)
                m.set_stroke(opacity=m.get_stroke_opacity() * v, family=False)
            return g
        inset_mob = always_redraw(inset)
        self.add(inset_mob, inset_vis)
        inset_cap = label(TEXT["inset"], 0.22, GREY_B).next_to([*INSET_C, 0], RIGHT, buff=INSET_R + 0.15)

        # ---------------------------------------------------------- text
        head = heading(*TEXT["head"]).to_corner(UL, buff=0.45)
        side_l = label(TEXT["dial_side"], 0.22, GREY_B).move_to([-2.3, -0.75, 0])
        side_r = label(TEXT["bridge_side"], 0.22, GREY_B).move_to([BR_C[0], -1.55, 0])

        def P(xy):
            return np.array([xy[0], xy[1], 0.0])
        c_slide = callout(TEXT["sliding"], lambda: kw.anchor("sliding_pinion"), (-3.6, 2.6), color=WIND_COLOR)
        c_wind = callout(TEXT["winding"], lambda: kw.anchor("winding_pinion"), (-1.2, 2.6), color=WIND_COLOR)
        c_cw = callout(TEXT["crown_wheel"], lambda: P(cw_c + np.array([-0.2, 0.5])), (1.2, 2.4), color=WIND_COLOR)
        c_rat = callout(TEXT["ratchet"], lambda: P(BR_C + np.array([0.5, 0.75])), (5.9, 2.5), color=WIND_COLOR)
        c_arb = callout(TEXT["arbor"], lambda: P(BR_C), (6.2, 1.2), color=WIND_COLOR)
        c_click = callout(TEXT["click"], lambda: P(cl_p), (1.0, -0.6), color=WHITE)
        c_crown = callout(TEXT["crown"], lambda: kw.anchor("crown"), (-0.85, 1.3), color=WIND_COLOR)
        c_stem = callout(TEXT["stem"], lambda: kw.anchor("stem"), (-3.45, 1.15), color=WIND_COLOR)
        plate = DashedVMobject(ArcBetweenPoints(kw.anchor("winding_pinion") + UP * 0.25, P(cw_c) + LEFT * 0.4,
                                                angle=-0.9), num_dashes=22).set_stroke(WIND_COLOR, 2.5)
        plate_lbl = label(TEXT["plate"], 0.2, WIND_COLOR).move_to([0.35, 2.05, 0])
        pushed = tag("pushed in: winding", WIND_COLOR, 0.24).next_to(head, DOWN, buff=0.15, aligned_edge=LEFT)

        cur = curtain()
        self.add(cur)
        self.play(cur.animate.set_fill(opacity=0), kw.vis.animate.set_value(1.0), bridge_vis.animate.set_value(1.0),
                  run_time=FADE_IN)
        self.remove(cur)
        wait_until(HEAD_AT)
        self.play(FadeIn(head), FadeIn(pushed), FadeIn(side_l), FadeIn(side_r), run_time=0.8)

        # ---------------------------------------------------------- winding forward, with the labels
        wait_until(WIND[0])
        turns = WIND_TURNS * TAU

        def at(t, *anims, run_time=0.7):
            return Succession(Wait(max(0.0, t - WIND[0])), AnimationGroup(*anims, run_time=run_time))
        self.play(kw.spin.animate(run_time=WIND[1] - WIND[0], rate_func=rate_functions.ease_in_out_sine)
                  .increment_value(turns),
                  at(WIND[0] + 0.2, FadeIn(c_crown), FadeIn(c_stem)),
                  at(LABEL_AT["sliding"], FadeIn(c_slide), kw.glow["sliding_pinion"].animate.set_value(1.0)),
                  at(LABEL_AT["winding"], FadeIn(c_wind), kw.glow["winding_pinion"].animate.set_value(1.0)),
                  at(LABEL_AT["crown_wheel"], Create(plate), FadeIn(plate_lbl), FadeIn(c_cw), run_time=1.0),
                  at(LABEL_AT["ratchet"], FadeIn(c_rat)),
                  at(LABEL_AT["arbor"], FadeIn(c_arb)),
                  at(INSET_AT, inset_vis.animate.set_value(1.0), FadeIn(inset_cap), run_time=0.9),
                  at(CLICK_AT, FadeIn(c_click)))

        # ---------------------------------------------------------- backward: ride over, held by the click
        wait_until(BACK_AT)
        back = tag(TEXT["back"], WHITE, 0.22).move_to([-1.6, -1.3, 0])
        c_ride = callout(TEXT["ride"], lambda: kw.anchor("breguet"), (-0.2, 0.85), color=WHITE)
        held = label(TEXT["held"], 0.22, WHITE).next_to(c_click[0], DOWN, buff=0.12)
        self.play(FadeOut(c_slide), FadeOut(c_wind), FadeOut(c_cw), FadeOut(c_rat), FadeOut(c_arb), FadeOut(plate_lbl),
                  FadeIn(back), FadeIn(c_ride), FadeIn(held), *[kw.glow[p].animate.set_value(0.0)
                                                                for p in ("sliding_pinion", "winding_pinion")],
                  run_time=0.5)
        wait_until(BACK[0])
        self.play(kw.spin.animate.increment_value(-BACK_TURNS * TAU), run_time=BACK[1] - BACK[0], rate_func=linear)
        self.play(FadeOut(back), FadeOut(c_ride), FadeOut(held), FadeOut(c_click), FadeOut(plate), run_time=0.5)

        # ---------------------------------------------------------- one turn, counted
        wait_until(COUNT_AT)
        count = {"n": 0, "k0": None}
        count_lbl = label(TEXT["count"], 0.3, WHITE).move_to([-2.35, -1.3, 0])
        num = label("0", 0.6, WIND_COLOR, bold=True).next_to(count_lbl, RIGHT, buff=0.25)
        model = tag(TEXT["model"], GREY_B, 0.2).next_to(count_lbl, RIGHT, buff=1.0)

        def recount(m):
            k = int(np.floor(ratchet_angle() / tooth + 1e-6))
            if count["k0"] is None:
                return
            n = max(0, k - count["k0"])
            if n != count["n"]:
                count["n"] = n
                m.become(label(str(n), 0.6, WIND_COLOR, bold=True).next_to(count_lbl, RIGHT, buff=0.25))
        num.add_updater(recount)
        self.play(FadeIn(count_lbl), FadeIn(num), FadeIn(model), run_time=0.5)
        wait_until(COUNT[0])
        count["k0"] = int(np.floor(ratchet_angle() / tooth + 1e-6))
        self.play(kw.spin.animate.increment_value(TAU), run_time=COUNT[1] - COUNT[0], rate_func=linear)
        self.wait(0.15)
        num.clear_updaters()
        one = label(TEXT["one_turn"].format(int(F.CLICKS_PER_CROWN_TURN)), 0.3, WIND_COLOR, bold=True)
        one.next_to(count_lbl, DOWN, buff=0.3, aligned_edge=LEFT)
        self.play(FadeIn(one, shift=UP * 0.1), run_time=0.6)

        # ---------------------------------------------------------- to a full wind
        wait_until(FULL_AT)
        full = ftext(TEXT["full"].format(F.DEV_TURNS, Z_RATCHET, F.Z_WIND_PINION, F.CROWN_TURNS_FULL), 0.42,
                     WIND_COLOR).move_to([2.85, -2.0, 0])
        note = label(TEXT["full_note"], 0.2, GREY_B).next_to(full, DOWN, buff=0.15)
        self.play(FadeIn(full, shift=UP * 0.1), FadeIn(note), run_time=0.9)

        # ---------------------------------------------------------- running: the drum turns
        wait_until(RUN_AT)
        sped = tag(TEXT["sped"], GLOW, 0.2).move_to([BR_C[0] + 1.6, 2.5, 0])
        c_drum = callout(TEXT["drum"], lambda: P(BR_C + polar(R_DRUM, 225)[:2]), (1.4, -0.75), color=RUN_COLOR)
        c_cent = callout(TEXT["center"], lambda: P(cp_c), (4.9, -2.3), color=RUN_COLOR)
        self.play(FadeOut(count_lbl), FadeOut(num), FadeOut(model), FadeOut(one), FadeOut(full), FadeOut(note),
                  FadeOut(pushed), inset_vis.animate.set_value(0.0), FadeOut(inset_cap), run_time=0.6)
        self.play(FadeIn(c_drum), FadeIn(c_cent), FadeIn(sped), run_time=0.7)
        paths = VGroup(label(TEXT["paths"][0], 0.3, WIND_COLOR, bold=True),
                       label(TEXT["paths"][1], 0.3, RUN_COLOR, bold=True)).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        paths.move_to([-2.4, -1.5, 0])
        t0 = RUN[0] + 1.3
        wait_until(t0)
        self.play(drum_turn.animate(run_time=RUN[1] - t0, rate_func=linear).set_value(RUN_DRUM_TURNS),
                  Succession(Wait(PATHS_AT - t0), FadeIn(paths, shift=UP * 0.1, run_time=0.9)))

        wait_until(FINAL_HOLD_UNTIL)
        cur.set_fill(opacity=0)
        self.add(cur)
        self.play(cur.animate.set_fill(opacity=1), run_time=FADE_OUT)
        write_sfx(__file__, sfx)
