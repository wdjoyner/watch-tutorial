"""Film 6's numbers, each computed here from its inputs, with its source.

Every number shown on screen or spoken in Film 6 should come from this module
(or be checked against it). Run `python figures.py` to print the table.

Sources
  [MAW] The Mathematics of the Automatic Mechanical Watch (AI and W. David Joyner,
        2026), section "The escapement: impulses, Airy's theorem, and the limit
        cycle": the hybrid equation, the kick energy, Airy's theorem (1826), the
        energy balance W_loss = 4 mu_Cou Theta + pi mu_vis omega0 Theta^2, the
        limit-cycle figure (scaled units, exaggerated friction), the lift-angle
        formula and its 4 Hz example.
  [GP]  G. Petrangeli, "Mathematics of a Watch Escapement" (29 May 2017): Swiss
        lever at T = 0.4 s (2.5 Hz), I = 2e-6 N mm s^2, K = 5.03e-4 N mm/rad,
        amplitude 270 deg; Airy estimate (eq. 5); energy audit and one-step
        correction (sec. 7.8); phase timings (sec. 5). As corrected in [MAW]:
        unlocking loss 0.27 % (not 2.7 %), corrected speed 75.71 rad/s.
  [ETA] ETA technical communication CT 6497-1 (version 13, 15.04.2025):
        2.5 Hz (18,000 A/h), typical lift angle of the balance 44 deg. The same
        44 deg is in CT 6497-1 ESI 452207 version 02 (23.05.07) and CT 6497-1
        FDE 482160 version 10 (08.02.2016). None of these gives barrel torque.
  [WOS] WOSTEP, The Theory of Horology, ch. 6: normal lift angles 38-55 deg.
  [SKO] Seiko Epson, US Patent 6,431,746 B1 (2002), "Mechanical timepiece with
        timed annular balance rotating angle control mechanism", FIG. 8: measured
        mainspring torque about 27 g cm at full wind, 23 at 20 h, 18 at 40 h. A
        Seiko wristwatch, not the 6497: label it so.
  [F4], [F5] Films 4 and 5's figures.py (2.5 Hz, Q 300, 270 / 220 deg).

ETA does not publish the 6497's amplitude, losses, impulse energy or Q.
Values marked REPRESENTATIVE are illustrative and must be labeled that way on
screen. Values marked EXAGGERATED are for the picture or the sound only.
Petrangeli's balance is a model Swiss lever at the 6497's frequency, not the
6497 itself; say so when quoting him.
"""
import numpy as np

TAU = 2 * np.pi
DAY = 86_400.0
DEG = np.pi / 180

# --------------------------------------------------------------- the 6497 [ETA] [F4]
F_6497 = 2.5                                     # Hz
OMEGA0 = TAU * F_6497                            # 15.708 rad/s
BEATS_PER_S = 2 * F_6497
HALF_PERIOD = 1 / BEATS_PER_S                    # 0.2 s
AMP = 270 * DEG                                  # REPRESENTATIVE [F4]
AMP_LOW = 220 * DEG                              # REPRESENTATIVE [F5]
Q = 300.0                                        # REPRESENTATIVE [F4]
LIFT_6497 = 44 * DEG                             # [ETA] typical lift angle
LIFT_RANGE = (38, 55)                            # deg [WOS]

# --------------------------------------------------------------- kicks [MAW]
def kick_energy(J, phidot, I):
    """Delta E = J phidot- + J^2 / (2 I)  (exact for an instantaneous kick)."""
    return J * phidot + J ** 2 / (2 * I)


def speed_frac(phi_star, amp):
    """Speed at angle phi* as a fraction of the peak speed, for a free swing."""
    return np.sqrt(max(0.0, 1 - (phi_star / amp) ** 2))


KICK_AT_HALF = speed_frac(0.5 * AMP, AMP)        # a kick at half the amplitude transfers 87 %


# --------------------------------------------------------------- Airy [MAW] [GP]
def airy_shift(J_over_I, phi_star, amp, omega0):
    """Delta T = (J/I) phi* / (A^2 omega0^2), first order in J; > 0 means later."""
    return J_over_I * phi_star / (amp ** 2 * omega0 ** 2)


GP_I = 2e-6 * 1e-3                               # N mm s^2 -> kg m^2 (2e-9)
GP_K = 5.03e-4 * 1e-3                            # N mm/rad -> N m/rad
GP_OMEGA0 = np.sqrt(GP_K / GP_I)                 # 15.86 rad/s (his T = 0.4 s rounds this)
GP_DV = 0.01                                     # rad/s, his largest kick per fork shock
GP_PHI = 24 * DEG
GP_DT = (GP_I / GP_K) * GP_PHI * GP_DV / AMP ** 2          # his eq. (5): 7.5e-7 s
GP_DT_CHECK = airy_shift(GP_DV, GP_PHI, AMP, GP_OMEGA0)    # same thing, MAW's form

# escapement error scales like 1 / A^2 for a fixed unlocking impulse [MAW]
ESC_ERR_RATIO = (AMP / AMP_LOW) ** 2             # 1.51: half as large again at 220 as at 270 deg

# ROUGH ESTIMATE, shown in a box crediting [GP] as its basis (scene 06): size of the
# unlocking error if the unlocking resistance is Petrangeli's friction loss,
# J = Delta E / phidot, applied at the middle of his 12 deg unlocking, which
# starts about 23 deg before center (his 12 + 24 + 10 deg span, centered).
GP_UNLOCK_E = 7.3e-6 * 1e-3                      # J per unlocking [GP eq. 16]
GP_PEAK = GP_OMEGA0 * AMP                        # ~74 rad/s
UNLOCK_J = GP_UNLOCK_E / GP_PEAK                 # angular impulse, N m s
UNLOCK_PHI = -(46 / 2 - 6) * DEG                 # -17 deg: before center
UNLOCK_DT = airy_shift(-UNLOCK_J / GP_I, UNLOCK_PHI, AMP, GP_OMEGA0)   # > 0: later, loses
UNLOCK_S_DAY = UNLOCK_DT * BEATS_PER_S * DAY                           # ~1 s/day lost
UNLOCK_S_DAY_LOW = UNLOCK_S_DAY * ESC_ERR_RATIO                        # at 220 deg
UNLOCK_BOX = ("Rough estimate, built on Petrangeli's Swiss-lever model (2017):",
              f"unlocking friction {GP_UNLOCK_E * 1e9:.1f} nJ per beat, taken as a backward kick",
              f"about {-UNLOCK_PHI / DEG:.0f}\u00b0 before center",
              f"loses about {UNLOCK_S_DAY:.1f} s/day at 270\u00b0, {UNLOCK_S_DAY_LOW:.1f} s/day at 220\u00b0")

# --------------------------------------------------------------- energy balance [MAW]
def w_loss(theta, mu_cou, mu_vis, omega0):
    return 4 * mu_cou * theta + np.pi * mu_vis * omega0 * theta ** 2


def theta_star(e_in, mu_cou, mu_vis, omega0):
    """Positive root of E_in = 4 mu_Cou Theta + pi mu_vis omega0 Theta^2."""
    a, b = np.pi * mu_vis * omega0, 4 * mu_cou
    return (-b + np.sqrt(b * b + 4 * a * e_in)) / (2 * a)


# --- the chapter's phase-portrait run: scaled units I = omega0 = 1, EXAGGERATED friction
LC_Q, LC_MU_COU, LC_E_IN = 12.0, 0.1, 6.40
LC_MU_VIS = 1 / LC_Q                             # c = I omega0 / Q
LC_THETA = theta_star(LC_E_IN, LC_MU_COU, LC_MU_VIS, 1.0)    # ~4.24
LC_STARTS = (1.20, 6.80)                         # small and large starting amplitudes [MAW fig.]


def limit_cycle_run(theta0, cycles=6, n=400, e_in=LC_E_IN, mu_cou=LC_MU_COU, mu_vis=LC_MU_VIS):
    """Integrate phi'' + c phi' + phi = -mu_Cou sgn(phi') with a fixed energy packet
    E_in/2 added at each crossing of phi = 0 (constant energy). Returns (phi, v) points
    and the amplitude at each turning point. Units: I = omega0 = 1."""
    phi, v, dt, path, peaks = theta0, 0.0, 2 * np.pi / n, [], [theta0]
    for _ in range(cycles * n):
        a = -phi - mu_vis * v - mu_cou * np.sign(v)
        v_new, phi_new = v + a * dt, phi + (v + a * dt) * dt
        if phi * phi_new < 0:                    # crossed center: add E_in/2
            e = 0.5 * v_new ** 2 + e_in / 2
            v_new = np.sign(v_new) * np.sqrt(2 * e)
        if v * v_new < 0:
            peaks.append(abs(phi_new))
        phi, v = phi_new, v_new
        path.append((phi, v))
    return np.array(path), np.array(peaks)


# --- the 6497, REPRESENTATIVE: losses at 270 deg match Q 300, split half dry, half viscous
K_6497 = 4.0e-9 * OMEGA0 ** 2                    # N m/rad, [F4] I = 4e-9 kg m^2 (REPRESENTATIVE)
E_BAL = 0.5 * K_6497 * AMP ** 2                  # J, ~11 uJ, as in Film 4
LOSS = TAU / Q * E_BAL                           # per cycle, ~0.23 uJ
MU_COU = (LOSS / 2) / (4 * AMP)                  # N m
MU_VIS = (LOSS / 2) / (np.pi * OMEGA0 * AMP ** 2)
E_IN = LOSS                                      # steady at 270 deg by construction
assert abs(theta_star(E_IN, MU_COU, MU_VIS, OMEGA0) - AMP) < 1e-9

# constant energy vs constant impulse: the same 270 deg operating point
J_CONST = E_IN / (2 * OMEGA0 * AMP)              # E_in = 2 J omega0 Theta when J is fixed

# running down: the escapement delivers a fixed energy per beat set by the train's
# torque [MAW, constant energy], so E_in follows the mainspring torque. The torque
# curve is the measured one in [SKO] FIG. 8 (a Seiko wristwatch, not the 6497),
# applied to our REPRESENTATIVE 6497 balance, with E_in = loss at 270 deg at full wind.
SKO_HOURS = (0, 20, 40)
SKO_TORQUE = (27.0, 23.0, 18.0)                  # g cm [SKO]
SKO_FRAC = tuple(t / SKO_TORQUE[0] for t in SKO_TORQUE)                 # 1, 0.85, 0.67
SKO_DROP_PCT = (1 - SKO_FRAC[-1]) * 100                                 # 33 % over 40 h
SKO_THETA = tuple(theta_star(f * E_IN, MU_COU, MU_VIS, OMEGA0) / DEG for f in SKO_FRAC)  # 270, ~242, ~205 deg
E_IN_LOW_FRAC = SKO_FRAC[-1]
THETA_LOW = SKO_THETA[-1] * DEG

# --- Petrangeli's one correction step [GP sec. 7.8], as corrected in [MAW]
GP_LOSS = 2.176e-4                               # N mm per period
GP_GAIN = 4.71e-4                                # N mm per period
GP_DE = GP_GAIN - GP_LOSS                        # 2.534e-4 N mm
GP_E_BAL = 5.48e-3                               # N mm
GP_WMAX = 74.0224                                # rad/s at 270 deg
GP_WMAX_NEW = np.sqrt(GP_WMAX ** 2 + 2 * GP_DE / 2e-6)       # N mm and N mm s^2: units cancel
GP_OMEGA0_MAW = 15.708                           # rad/s, 2 pi / 0.4 s
GP_DTHETA = (GP_WMAX_NEW - GP_WMAX) / GP_OMEGA0_MAW          # ~0.107 rad ~ 6.2 deg
GP_LOSS_PCT = GP_LOSS / GP_E_BAL * 100           # ~4 % of the balance's energy per period
GP_GAIN_PCT = GP_GAIN / GP_E_BAL * 100           # ~8.6 %

# --------------------------------------------------------------- lift angle [MAW] [ETA]
def lift_time(lift, amp, f):
    """Delta t = (2 / omega) arcsin(lift / 2 Theta), omega = 2 pi f."""
    return 2 / (TAU * f) * np.arcsin(lift / (2 * amp))


def amp_from_lift(lift, dt, f):
    """Theta = lift / (2 sin(pi f Delta t))."""
    return lift / (2 * np.sin(np.pi * f * dt))


DT_4HZ = lift_time(52 * DEG, AMP, 4.0)           # chapter's example: ~7.7 ms
DT_6497 = lift_time(LIFT_6497, AMP, F_6497)      # ~10.4 ms
DT_6497_LOW = lift_time(LIFT_6497, AMP_LOW, F_6497)
ROUND_TRIP = amp_from_lift(LIFT_6497, DT_6497, F_6497) / DEG          # 270 deg
WRONG_LIFT = 52 * DEG                            # a common default setting
WRONG_AMP = amp_from_lift(WRONG_LIFT, DT_6497, F_6497) / DEG          # ~319 deg
GP_LIFT = 2 * AMP * np.sin(np.pi * F_6497 * 0.01133) / DEG            # [MAW] Petrangeli check, ~48 deg

# --------------------------------------------------------------- event timeline [GP] [MAW]
GP_PHASES = {"unlock": 2.774e-3, "impulse I": 5.770e-3, "impulse II": 4.4e-3, "drop": 0.958e-3}  # s
GP_ACTIVE = sum(GP_PHASES.values())              # ~13.9 ms
GP_LOCKED_FRAC = 1 - GP_ACTIVE / HALF_PERIOD     # ~0.93
GP_WHEEL_FAST = 12 / (GP_ACTIVE - GP_PHASES["unlock"])     # ~1080 deg/s while moving
GP_WHEEL_AVG = 24 / (2 * HALF_PERIOD)                      # 60 deg/s on average
SLOWMO_EVENTS = 20.0                             # slow-motion factor to show the 13.9 ms (EXAGGERATED timing)


def table():
    rows = [
        ("6497: f, omega0, half-period", f"{F_6497} Hz, {OMEGA0:.3f} rad/s, {HALF_PERIOD} s"),
        ("kick at half amplitude transfers", f"{KICK_AT_HALF * 100:.0f} % of a kick at center"),
        ("Petrangeli omega0 from I, K", f"{GP_OMEGA0:.3f} rad/s"),
        ("Petrangeli Airy shift (eq. 5)", f"{GP_DT:.2e} s (MAW form: {GP_DT_CHECK:.2e} s)"),
        ("escapement error 220 vs 270 deg", f"x {ESC_ERR_RATIO:.2f}"),
        ("ROUGH unlocking error 270 / 220 deg", f"{UNLOCK_S_DAY:.2f} / {UNLOCK_S_DAY_LOW:.2f} s/day lost"),
        ("  box", " | ".join(UNLOCK_BOX)),
        ("limit cycle (scaled) Theta*", f"{LC_THETA:.3f}  (chapter: 4.24)"),
        ("6497 REPR.: E_bal, loss/cycle", f"{E_BAL * 1e6:.2f} uJ, {LOSS * 1e6:.3f} uJ"),
        ("  mu_Cou, mu_vis", f"{MU_COU:.2e} N m, {MU_VIS:.2e} N m s"),
        ("  constant-impulse J", f"{J_CONST:.2e} N m s"),
        ("Seiko torque 0/20/40 h (g cm)", f"{SKO_TORQUE}  -> E_in x {tuple(round(f, 3) for f in SKO_FRAC)}"),
        ("  -> Theta* at 0/20/40 h", f"{tuple(round(t) for t in SKO_THETA)} deg  ({SKO_DROP_PCT:.0f} % less torque)"),
        ("Petrangeli loss / gain per period", f"{GP_LOSS_PCT:.1f} % / {GP_GAIN_PCT:.1f} % of E_bal"),
        ("  corrected peak speed", f"{GP_WMAX_NEW:.2f} rad/s"),
        ("  amplitude step", f"{GP_DTHETA:.3f} rad = {GP_DTHETA / DEG:.2f} deg"),
        ("lift time, 4 Hz, 52 deg, 270 deg", f"{DT_4HZ * 1e3:.2f} ms  (chapter: 7.7)"),
        ("lift time, 6497, 44 deg, 270 / 220 deg", f"{DT_6497 * 1e3:.2f} / {DT_6497_LOW * 1e3:.2f} ms"),
        ("  round trip", f"{ROUND_TRIP:.2f} deg"),
        ("  read with 52 deg entered", f"{WRONG_AMP:.0f} deg (rate unchanged)"),
        ("Petrangeli effective lift angle", f"{GP_LIFT:.1f} deg  (chapter: 48.0)"),
        ("event timeline: active / locked", f"{GP_ACTIVE * 1e3:.1f} ms / {GP_LOCKED_FRAC * 100:.0f} %"),
        ("  wheel speed moving / average", f"{GP_WHEEL_FAST:.0f} / {GP_WHEEL_AVG:.0f} deg/s"),
    ]
    w = max(len(a) for a, _ in rows)
    return "\n".join(f"{a:<{w}}  {b}" for a, b in rows)


if __name__ == "__main__":
    print(table())
    for t0 in LC_STARTS:
        _, pk = limit_cycle_run(t0)
        print(f"limit-cycle run from {t0}: turning points {np.round(pk[:9], 2)}")
