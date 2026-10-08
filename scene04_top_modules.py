"""Scene 04 - "The Top Modules": hovering over the bridges as the automatic
rotor swings in and drives the reversing wheels; a chronograph module waits,
ghosted, in the background and engages when the narration names it.

Build (render + voice + mux):   python build.py scene04_top_modules
Render only (quick preview):    manim -ql scene04_top_modules.py Scene04

Scene-local additions (movement.py is unchanged):
  * the rotor follows rotor_angle(t) below instead of the default sway;
  * two reversing wheels under the rotor, meshed with the rotor pinion;
  * the ratchet and crown wheel turn one way only, whichever way the rotor
    swings, which is what the reversing wheels are for;
  * a ghosted chronograph module (column wheel, operating and coupling levers)
    floating above the movement as the alternative top module.
"""
from manim import *
from movement import (Movement, attach_driver, vignette, camera_move, cue, slab, lift, at, wheel_g, pinion_g, teeth_g,
                      rounded, jewel, disk_g, polar, vm, P, MOD, BG, GLOW, FONT_SANS, GILT, BRASS_DK, BRASS_HI,
                      STEEL, STEEL_DK, STEEL_HI)

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds, angles in degrees.
# Keep the timeline roughly in step with scene04_top_modules.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 1.6
SWING_START, SWING_END = 4.0, 9.5    # the rotor swings over the bridges
ROTOR_SWING = 175                    # degrees of the swing
ROTOR_SWAY = 30                      # gentle sway afterwards (degrees, peak)
PAN_START, PAN_END = 12.4, 15.0      # camera moves to the chronograph module
GHOST_UP = 12.8                      # chronograph module brightens
ENGAGE_AT = 15.6                     # column wheel indexes, coupling lever drops in
END_HOLD = 3.6
FADE_OUT = 1.5
LABEL_TIMES = {"title": 1.6, "rotor": 9.0, "wheels": 11.0, "chrono": 13.2}
LABEL_FADE = 0.5
LABEL_BACKING = 0.72

# --- camera (hovering slightly above the top bridges) ------------------
CAM_START = dict(phi=44, theta=-80, zoom=1.55, center=(0.7, -0.2, 0.9))
CAM_CHRONO = dict(phi=50, theta=-98, zoom=2.3, target=(-1.25, 0.9, 1.92))   # centered on the chronograph module

# --- reversing wheels --------------------------------------------------
PINION_TEETH, REV_TEETH = 10, 26
REV_A_ANGLE, REV_B_ANGLE = -20, -70   # layout angles: A around the rotor pinion, B around A
RATCHET_GAIN = 0.15                   # ratchet turn per unit of rotor travel

# --- chronograph module (ghosted) --------------------------------------
CHRONO_AT = (-1.35, 0.95)             # center of the module, plate coordinates
CHRONO_HEIGHT = 1.30                  # floating height above the top tier
CHRONO_COLOR = "#9cc2ff"
GHOST_OPACITY = (0.30, 0.95)          # waiting, engaged
PANEL_GLASS = 0.82                    # darkness of the module panel when engaged

# --- on-screen text --------------------------------------------------
TITLE = ("TIER 3  ·  TOP MODULES", "on top of the primary bridges")
ITEMS = {
    "rotor": "automatic rotor  ·  winds the mainspring",
    "wheels": "reversing and reduction wheels",
    "chrono": "or a chronograph  ·  levers and column wheel",
}
Z_ASSEMBLED = {"dial": 0.00, "engine": 0.30, "top": 0.62}
# =====================================================================


def rotor_angle(t):
    """Rotor angle (radians) at time t: parked, a smooth swing in, then a sway."""
    if t <= SWING_START:
        return 0.0
    sw = ROTOR_SWING * DEGREES
    if t <= SWING_END:
        return sw * smooth((t - SWING_START) / (SWING_END - SWING_START))
    u = t - SWING_END
    return sw + ROTOR_SWAY * DEGREES * np.sin(0.8 * u) * min(1.0, u / 1.5)


def chrono_module():
    """Column wheel, operating lever, coupling lever with its wheel, chronograph wheel."""
    cx, cy = CHRONO_AT
    col = lambda m, op=0.18: m.set_fill(CHRONO_COLOR, op).set_stroke(CHRONO_COLOR, 1.8, 1)
    plate = col(vm(rounded([(cx - 1.25, cy - 0.85), (cx + 1.35, cy - 0.95), (cx + 1.45, cy + 0.75),
                            (cx - 1.1, cy + 0.9)], 0.2), STEEL)).set_fill(BG, PANEL_GLASS)
    cw_c = (cx - 0.55, cy + 0.05)
    column_wheel = VGroup(col(vm(teeth_g(0.34, 18, 0.05, 0.05).difference(disk_g(0.05)), STEEL)),
                          *[col(vm(disk_g(0.06, (0.2 * np.cos(a), 0.2 * np.sin(a)), 16), STEEL), 0.5)
                            for a in np.linspace(0, TAU, 6, endpoint=False)])
    column_wheel[1:].shift(OUT * 0.03)
    at(column_wheel, cw_c)
    chrono_c = (cx + 0.75, cy - 0.15)
    chrono_wheel = at(col(vm(wheel_g(0.5, 60, spokes=4), STEEL)), chrono_c)
    op_lever = col(vm(rounded([(cx - 1.05, cy - 0.6), (cx - 0.85, cy - 0.7), (cx - 0.45, cy - 0.25),
                               (cx - 0.6, cy - 0.15)], 0.04), STEEL), 0.3)
    coup_pivot = (cx - 0.2, cy + 0.6)
    coupling = VGroup(col(vm(rounded([(coup_pivot[0] - 0.08, coup_pivot[1] + 0.05), (coup_pivot[0] + 0.1, coup_pivot[1]),
                                       (cx + 0.15, cy - 0.15), (cx - 0.05, cy - 0.2)], 0.04), STEEL), 0.3),
                      at(col(vm(teeth_g(0.17, 24, 0.035, 0.035), STEEL), 0.35), (cx + 0.1, cy - 0.12)))
    return VGroup(plate, chrono_wheel, op_lever, coupling, column_wheel), column_wheel, cw_c, coupling, coup_pivot


class Scene04(ThreeDScene):
    def construct(self):
        self.camera.background_color = BG
        self.set_camera_orientation(phi=CAM_START["phi"] * DEGREES, theta=CAM_START["theta"] * DEGREES,
                                    zoom=CAM_START["zoom"], frame_center=np.array(CAM_START["center"]))
        self.add_fixed_in_frame_mobjects(vignette())

        # one clock for the rotor and everything it drives (added before the driver)
        clock = {"t": 0.0, "rotor": 0.0, "travel": 0.0}

        def tick(_, dt):
            clock["t"] += dt
            a = rotor_angle(clock["t"])
            clock["travel"] += abs(a - clock["rotor"])
            clock["rotor"] = a
        ticker = Mobject().add_updater(tick)
        self.add(ticker)

        mv = Movement()
        top = mv.tiers["top"]
        rotor, ratchet, crown_wheel = mv.parts["rotor"], mv.parts["ratchet_wheel"], mv.parts["crown_wheel"]

        # reversing wheels under the rotor, meshed with the rotor pinion (all on the shared module)
        r_p, r_w = MOD * PINION_TEETH / 2, MOD * REV_TEETH / 2
        pa = polar(r_p + r_w, REV_A_ANGLE)
        pb = pa + polar(2 * r_w, REV_B_ANGLE)

        def rev_wheel(p):
            w = VGroup(slab(wheel_g(r_w, REV_TEETH, spokes=5, curved=True).difference(disk_g(0.04)),
                            GILT, BRASS_DK, 0.03, BRASS_HI, 0.6),
                       lift(slab(pinion_g(8).difference(disk_g(0.02)), STEEL_HI, STEEL_DK, 0.03, WHITE, 0.4), 0.03),
                       lift(jewel((0, 0), 0.045), 0.035))
            return at(lift(w, 0.17), p)

        rev_a, rev_b = rev_wheel(pa), rev_wheel(pb)
        rotor_pinion = lift(slab(pinion_g(PINION_TEETH).difference(disk_g(0.03)), STEEL_HI, STEEL_DK, 0.04), 0.2)
        top.submobjects.insert(top.submobjects.index(rotor), VGroup(rotor_pinion, rev_a, rev_b))

        # drive the rotor from rotor_angle(); the ratchet and crown wheel only ever wind one way
        mine = (rotor, ratchet, crown_wheel)
        mv.rot = [r for r in mv.rot if not any(r[0] is m for m in mine)]
        g = REV_TEETH / PINION_TEETH
        mv.rot += [(rotor, np.zeros(3), "top", lambda s: clock["rotor"]),
                   (rotor_pinion, np.zeros(3), "top", lambda s: clock["rotor"]),
                   (rev_a, pa, "top", lambda s: -clock["rotor"] / g),
                   (rev_b, pb, "top", lambda s: clock["rotor"] / g),
                   (ratchet, P["barrel"], "top", lambda s: -RATCHET_GAIN * clock["travel"]),
                   (crown_wheel, P["barrel"] + polar(0.62 + 0.26, 15), "top",
                    lambda s: RATCHET_GAIN * clock["travel"] * 0.62 / 0.26)]
        attach_driver(self, mv, Z_ASSEMBLED, Z_ASSEMBLED)

        # chronograph module, ghosted, floating above the movement
        ghost, column_wheel, cw_c, coupling, coup_pivot = chrono_module()
        ghost.shift(OUT * (Z_ASSEMBLED["top"] + CHRONO_HEIGHT))
        base = [(m, m.get_fill_opacity(), m.get_stroke_opacity()) for m in ghost.family_members_with_points()]
        glow = ValueTracker(GHOST_OPACITY[0])
        index = ValueTracker(0.0)       # column wheel steps (one column = TAU/12, a tooth pair)
        drop = ValueTracker(0.0)        # coupling lever swing, 0..1
        z_g = Z_ASSEMBLED["top"] + CHRONO_HEIGHT

        def ghost_update(m):
            v = glow.get_value()
            for mob, fo, so in base:
                mob.set_fill(opacity=fo * v / GHOST_OPACITY[1], family=False)
                mob.set_stroke(opacity=so * v / GHOST_OPACITY[1], family=False)
            a = index.get_value() * TAU / 12
            column_wheel.rotate(a - getattr(column_wheel, "_a", 0.0), axis=OUT,
                                about_point=np.array([cw_c[0], cw_c[1], z_g]))
            column_wheel._a = a
            d = -9 * DEGREES * drop.get_value()
            coupling.rotate(d - getattr(coupling, "_a", 0.0), axis=OUT,
                            about_point=np.array([coup_pivot[0], coup_pivot[1], z_g]))
            coupling._a = d
        ghost.add_updater(ghost_update)
        self.add(ghost, glow, index, drop)

        # screen-fixed text
        head = Text(TITLE[0], font=FONT_SANS, weight=BOLD, color=GLOW).scale(0.40)
        sub = Text(TITLE[1], font=FONT_SANS, color=GREY_B).scale(0.26)
        items = {k: Text(t, font=FONT_SANS, color=GREY_B).scale(0.26) for k, t in ITEMS.items()}
        block = VGroup(head, sub, *items.values()).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        VGroup(*items.values()).shift(DOWN * 0.12)
        bar = Line(ORIGIN, RIGHT * 0.45).set_stroke(GLOW, 2)
        panel = VGroup(bar, block).arrange(RIGHT, buff=0.15, aligned_edge=UP).to_corner(DL, buff=0.5)
        backing = RoundedRectangle(corner_radius=0.12, width=panel.width + 0.5, height=panel.height + 0.4)
        backing.move_to(panel).set_fill(BG, LABEL_BACKING).set_stroke(width=0)
        panel = VGroup(backing, panel)
        curtain = FullScreenRectangle().set_fill(BG, 1).set_stroke(width=0)
        self.add_fixed_in_frame_mobjects(panel, curtain)
        self.remove(panel)

        def fade(*mobs):
            return [FadeIn(m, shift=RIGHT * 0.2) for m in mobs]

        # ---------------------------------------------------------- timeline
        self.play(curtain.animate.set_fill(opacity=0), run_time=FADE_IN, rate_func=smooth)
        t = FADE_IN
        # hover over the bridges while the rotor swings in (driven by the clock)
        seg = dict(start=t, end=PAN_START)
        self.play(cue(LABEL_TIMES["title"], *fade(backing, bar, head, sub), **seg),
                  cue(LABEL_TIMES["rotor"], *fade(items["rotor"]), **seg),
                  cue(LABEL_TIMES["wheels"], *fade(items["wheels"]), **seg))
        t = PAN_START
        # move to the chronograph module, which brightens and then engages
        seg = dict(start=t, end=PAN_END)
        self.play(*camera_move(self, PAN_END - t, phi=CAM_CHRONO["phi"], theta=CAM_CHRONO["theta"],
                               zoom=CAM_CHRONO["zoom"], target=CAM_CHRONO["target"],
                               frame_origin=CAM_START["center"]),
                  cue(GHOST_UP, glow.animate.set_value(GHOST_OPACITY[1]), run_time=1.6, **seg),
                  cue(LABEL_TIMES["chrono"], *fade(items["chrono"]), **seg))
        self.remove(self.camera._frame_center)
        t = PAN_END
        self.wait(ENGAGE_AT - t)
        self.play(index.animate.set_value(1.0), run_time=0.18, rate_func=rate_functions.ease_in_quad)
        self.play(drop.animate.set_value(1.0), run_time=0.25, rate_func=rate_functions.ease_out_back)
        self.wait(END_HOLD)
        self.remove(curtain)
        self.add_fixed_in_frame_mobjects(curtain)        # re-add so it sits above the text
        self.play(FadeOut(panel), curtain.animate.set_fill(opacity=1), run_time=FADE_OUT)

