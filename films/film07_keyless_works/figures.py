"""Film 7's numbers, each computed here from its inputs, with its source.

Every number shown on screen or spoken in Film 7 should come from this module
(or be checked against it). Run `python figures.py` to print the table.

Sources
  [MAW] The Mathematics of the Automatic Mechanical Watch (AI and W. David Joyner,
        2026), section "Keyless works of a mechanical watch: winding, time
        setting, and date setting": the parts, the crown positions 0 / 1 / 2,
        the winding and setting paths, the cannon pinion's friction fit, the
        motion work's 12 : 1 (36/12 x 40/10).
  [ETA] ETA technical communication CT 6497-1: hand-wound, no date; the stem
        has two positions (pushed in: winding; pulled out: hand setting).
        TO CHECK against the CT the user will attach (stem numbering, and
        whether the 6497-1 stops the balance when the stem is pulled).
  [F2]  Film 2: about 8 barrel turns of development for the 6497's spring.
  [F3]  Film 3: motion work 36/12 x 40/10 = 12.
  [MOD] movement.py WIND_TEETH: winding pinion 16, crown wheel 36, ratchet 60.
        These are the MODEL's counts (ETA does not publish them in the CT):
        label results that depend on them "about" / "in this model".

Values marked MODEL depend on tooth counts ETA does not publish.
"""
from fractions import Fraction

# --------------------------------------------------------------- winding [MOD] [F2]
Z_WIND_PINION = 16
Z_CROWN_WHEEL = 36
Z_RATCHET = 60
DEV_TURNS = 8.0                                   # barrel turns, let down to fully wound [F2]

# The crown wheel is an idler between the winding pinion and the ratchet,
# so it cancels: ratchet (arbor) turns per crown turn = 16/60.
ARBOR_PER_CROWN = Fraction(Z_WIND_PINION, Z_CROWN_WHEEL) * Fraction(Z_CROWN_WHEEL, Z_RATCHET)   # 4/15
CROWN_PER_ARBOR = 1 / ARBOR_PER_CROWN             # 15/4 = 3.75   MODEL
CROWN_TURNS_FULL = DEV_TURNS * float(CROWN_PER_ARBOR)   # about 30   MODEL
CLICKS_PER_CROWN_TURN = float(ARBOR_PER_CROWN) * Z_RATCHET   # 16: one ratchet tooth per click   MODEL
CLICKS_FULL = DEV_TURNS * Z_RATCHET               # about 480   MODEL

# --------------------------------------------------------------- motion work [MAW] [F3]
MW = (Fraction(36, 12), Fraction(40, 10))
MW_RATIO = MW[0] * MW[1]                          # 12

# --------------------------------------------------------------- setting train [MAW] [MOD]
# Sliding pinion -> setting wheel -> intermediate setting wheel -> minute wheel -> cannon pinion.
# Both setting wheels are idlers, so minute-hand turns per crown turn = z_slide / z_cannon,
# whatever their tooth counts. ETA does not publish z_slide: keep this symbolic on screen.
Z_CANNON = 12


def minute_turns_per_crown_turn(z_slide):
    return Fraction(z_slide, Z_CANNON)


# --------------------------------------------------------------- crown positions [MAW] [ETA]
POSITIONS_MAW = {0: "winding", 1: "date setting", 2: "time setting"}
POSITIONS_6497 = {"pushed in": "winding (MAW position 0)", "pulled out": "time setting (MAW position 2)"}


if __name__ == "__main__":
    rows = [
        ("arbor turns per crown turn (MODEL)", f"{ARBOR_PER_CROWN} = {float(ARBOR_PER_CROWN):.4f}"),
        ("crown turns per barrel turn (MODEL)", f"{CROWN_PER_ARBOR} = {float(CROWN_PER_ARBOR):.2f}"),
        ("crown turns to wind fully (MODEL, ~8 barrel turns)", f"{CROWN_TURNS_FULL:.0f}"),
        ("clicks per crown turn (MODEL)", f"{CLICKS_PER_CROWN_TURN:.0f}"),
        ("clicks for a full wind (MODEL)", f"{CLICKS_FULL:.0f}"),
        ("motion work 36/12 x 40/10", f"{MW_RATIO}"),
        ("minute-hand turns per crown turn, 12-tooth sliding pinion (example)",
         f"{minute_turns_per_crown_turn(12)}"),
    ]
    w = max(len(k) for k, _ in rows)
    for k, v in rows:
        print(f"{k:<{w}}  {v}")
