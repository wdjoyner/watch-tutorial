"""Film 4's numbers, each computed here from its inputs, with its source.

Every number shown on screen or spoken in Film 4 should come from this module
(or be checked against it). Run `python figures.py` to print the table.

Sources
  [MAW] The Mathematics of the Automatic Mechanical Watch (AI and W. David Joyner,
        2026), section "The regulating organ". Example ex:balance (4 Hz wristwatch
        balance), Example ex:balance6497 (2.5 Hz, 6497-sized balance, values
        representative), Example ex:rimguldin (Glucydur rim), the Elinvar and
        damping subsections.
  [ETA] ETA technical communication for the 6497-1: 18,000 vph, 46 h power reserve.
  [F2]  Film 2: the 6497 mainspring, 1.50 x 0.18 x 450 mm, about 8 turns of development.
  [F3]  Film 3: n = B / (120 Z), 15-tooth escape wheel.

ETA does not publish the 6497's balance inertia, hairspring dimensions,
amplitude or Q. Values marked REPRESENTATIVE are the chapter's illustrative ones
and must be labeled that way on screen.
"""
import numpy as np

TAU = 2 * np.pi
DAY = 86_400.0                                   # seconds


# --------------------------------------------------------------- frequency
F_6497 = 2.5                                     # Hz [ETA]: 18,000 vph
BPH_6497 = 7200 * F_6497                         # beats per hour, B = 2 f (3600)
BEATS_PER_S = 2 * F_6497
T0_6497 = 1 / F_6497                             # s
OMEGA0_6497 = TAU * F_6497                       # rad/s (5 pi)
Z_ESCAPE = 15                                    # [F3]
ESCAPE_RPM = BPH_6497 / (120 * Z_ESCAPE)         # [F3] n = B / (120 Z) -> 10 rpm


def stiffness(I, f):
    """kappa = I omega0^2."""
    return I * (TAU * f) ** 2


def energy(kappa, amp_rad):
    """E = (1/2) kappa A^2."""
    return 0.5 * kappa * amp_rad ** 2


def ribbon_length(E, b, h, kappa):
    """L = E b h^3 / (12 kappa), the beam formula solved for length."""
    return E * b * h ** 3 / (12 * kappa)


AMP = np.radians(270.0)                          # REPRESENTATIVE healthy amplitude [MAW]
E_HS = 190e9                                     # Pa, temperature-compensating alloy [MAW]

# --- the worked example at 2.5 Hz (6497-sized balance) [MAW ex:balance6497], REPRESENTATIVE
I_6497 = 4.0e-9                                  # kg m^2 (40 mg cm^2)
K_6497 = stiffness(I_6497, F_6497)               # ~9.9e-7 N m/rad
E_6497 = energy(K_6497, AMP)                     # ~11.0 uJ
B_HS_6497, H_HS_6497 = 0.20e-3, 0.040e-3         # m
L_HS_6497 = ribbon_length(E_HS, B_HS_6497, H_HS_6497, K_6497)   # ~0.21 m
OMEGA_MAX_6497 = OMEGA0_6497 * AMP               # peak angular speed at the center, rad/s

# --- the chapter's 4 Hz wristwatch balance [MAW ex:balance], for comparison
I_4HZ = 1.2e-9                                   # kg m^2 (12 mg cm^2)
K_4HZ = stiffness(I_4HZ, 4.0)                    # ~7.6e-7
E_4HZ = energy(K_4HZ, AMP)                       # ~8.4 uJ
L_HS_4HZ = ribbon_length(E_HS, 0.15e-3, 0.035e-3, K_4HZ)        # ~0.13 m

# --- mainspring vs hairspring [F2]: same formula, different ribbon
MS_B, MS_H, MS_L = 1.50e-3, 0.18e-3, 0.450       # m [F2]
E_MS = 200e9                                     # Pa, the chapter's barrel example [MAW]
K_MS = E_MS * MS_B * MS_H ** 3 / (12 * MS_L)     # N m/rad
STIFFNESS_RATIO = K_MS / K_6497                  # how many times stiffer the mainspring is
THICKNESS_CUBED_RATIO = (MS_H / H_HS_6497) ** 3

# --------------------------------------------------------------- Pappus-Guldin [MAW ex:rimguldin]
RHO_GLUCYDUR = 8300.0                            # kg/m^3
RIM_W, RIM_H, RIM_R = 0.80e-3, 0.32e-3, 4.5e-3   # m: radial width, axial height, mean radius
RIM_A0 = RIM_W * RIM_H                           # 0.256 mm^2
RIM_V = TAU * RIM_R * RIM_A0                     # V = 2 pi rbar A0
RIM_M = RHO_GLUCYDUR * RIM_V                     # ~60 mg
RIM_I_THIN = RIM_M * RIM_R ** 2                  # ~1.2e-9
RIM_CORR = RIM_W ** 2 / (4 * RIM_R ** 2)         # ~0.8 %
RIM_I = RIM_I_THIN * (1 + RIM_CORR)
# exact check: I = 2 pi rho h * integral r^3 dr over the rectangle
_r1, _r2 = RIM_R - RIM_W / 2, RIM_R + RIM_W / 2
RIM_I_EXACT = TAU * RHO_GLUCYDUR * RIM_H * (_r2 ** 4 - _r1 ** 4) / 4

# --------------------------------------------------------------- rate sensitivity
PPM_PER_S_DAY = 1e6 / DAY                        # 1 s/day = 11.57 ppm
COSC = (-4.0, +6.0)                              # s/day, mean daily rate [MAW]
COSC_FRAC = max(abs(c) for c in COSC) / DAY      # ~6.9e-5 in frequency
COSC_KAPPA_OVER_I = 2 * COSC_FRAC                # ~1.4e-4 in kappa / I ("about 1e-4")
EX_KAPPA_UP = 2e-4                               # [MAW remark] kappa up 0.02 % ...
EX_RATE = 0.5 * EX_KAPPA_UP                      # ... frequency up 0.01 %
EX_S_DAY = EX_RATE * DAY                         # = 8.64 s/day

# --------------------------------------------------------------- regulation
REG_S_DAY = 10.0                                 # an example correction, s/day
REG_DL = 2 * (REG_S_DAY / DAY) * L_HS_6497       # dl = 2 (df/f) l  (taking the whole spring as active)

# --------------------------------------------------------------- temperature [MAW]
BETA_E_STEEL = -2.4e-4                           # per deg C, carbon steel
ALPHA_ORDER = 1e-5                               # per deg C, typical expansion coefficients
STEEL_FRAC_PER_C = BETA_E_STEEL / 2              # the modulus term alone
STEEL_S_DAY_PER_C = STEEL_FRAC_PER_C * DAY       # ~ -10.4 s/day per deg C
EXPANSION_SHIFT = 1.5 * ALPHA_ORDER * DAY        # each expansion term is worth ~1 s/day per deg C
STEEL_10C_S_DAY = 10 * STEEL_S_DAY_PER_C         # a 10 deg C change: ~ -104 s/day
GUILLAUME_NOBEL = 1920

# --------------------------------------------------------------- damping [MAW]
Q = 300.0                                        # REPRESENTATIVE: "a few hundred" for a cased balance
LOSS_FRAC = TAU / Q                              # ~2.1 % of the energy per cycle
LOSS_6497 = LOSS_FRAC * E_6497                   # ~0.23 uJ per cycle
POWER_6497 = LOSS_6497 * F_6497                  # ~0.57 uW
HALF_AMP_TIME = 2 * Q * np.log(2) / OMEGA0_6497  # free swing halves in ~26 s
LOSS_4HZ, POWER_4HZ = LOSS_FRAC * E_4HZ, LOSS_FRAC * E_4HZ * 4.0   # chapter's 0.18 uJ, 0.7 uW

# --- the honest audit, 6497 [F2] [ETA] [MAW]: rough supply vs demand
RESERVE_S = 46 * 3600.0                          # [ETA]
DEV_TURNS = 8.0                                  # [F2]
U_LINEAR = 0.5 * K_MS * (TAU * DEV_TURNS) ** 2   # linear model, let down to fully wound
SIGMA_MAX, E_DESIGN = 3000e6, 2.25e11            # Pa, design-practice values [MAW, WOSTEP]
U_DESIGN = MS_B * MS_H * MS_L / 6 * SIGMA_MAX ** 2 / E_DESIGN
P_BARREL = (U_LINEAR / RESERVE_S, U_DESIGN / RESERVE_S)        # W, mean power from the barrel
ESC_EFF = (0.30, 0.40)                           # lever escapement efficiency [MAW]
P_AT_BALANCE = (P_BARREL[0] * ESC_EFF[0], P_BARREL[1] * ESC_EFF[1])


def table():
    rows = [
        ("6497 frequency / beats per hour", f"{F_6497} Hz / {BPH_6497:,.0f}"),
        ("T0, omega0 (6497)", f"{T0_6497} s, {OMEGA0_6497:.2f} rad/s"),
        ("escape wheel speed n = B/(120 Z)", f"{ESCAPE_RPM:g} rpm"),
        ("6497-sized balance I (REPR.)", f"{I_6497:.1e} kg m^2 = {I_6497 * 1e10:.0f} mg cm^2"),
        ("  kappa = I omega0^2", f"{K_6497:.2e} N m/rad"),
        ("  E at 270 deg", f"{E_6497 * 1e6:.2f} uJ"),
        ("  hairspring length (0.20 x 0.040 mm, 190 GPa)", f"{L_HS_6497 * 100:.1f} cm"),
        ("  peak speed omega0 A", f"{OMEGA_MAX_6497:.1f} rad/s = {OMEGA_MAX_6497 / TAU:.1f} rev/s"),
        ("4 Hz balance kappa / E / L", f"{K_4HZ:.2e} / {E_4HZ * 1e6:.2f} uJ / {L_HS_4HZ * 100:.1f} cm"),
        ("mainspring kappa (200 GPa)", f"{K_MS:.2e} N m/rad"),
        ("  mainspring / hairspring stiffness", f"{STIFFNESS_RATIO:.0f} x (thickness^3 alone: {THICKNESS_CUBED_RATIO:.0f} x)"),
        ("rim area / mass", f"{RIM_A0 * 1e6:.3f} mm^2 / {RIM_M * 1e6:.1f} mg"),
        ("rim I thin / corrected / exact", f"{RIM_I_THIN:.3e} / {RIM_I:.3e} / {RIM_I_EXACT:.3e}"),
        ("  correction w^2/(4 r^2)", f"{RIM_CORR * 100:.2f} %"),
        ("1 s/day", f"{PPM_PER_S_DAY:.2f} ppm"),
        ("COSC +6 s/day as a fraction (f; kappa/I)", f"{COSC_FRAC:.1e}; {COSC_KAPPA_OVER_I:.1e}"),
        ("kappa +0.02 % -> rate", f"+{EX_RATE * 100:.2f} % = {EX_S_DAY:.2f} s/day"),
        ("index move for 10 s/day (l = 21 cm)", f"{REG_DL * 1e6:.0f} um"),
        ("steel: beta_E/2, s/day per deg C", f"{STEEL_FRAC_PER_C:.1e}, {STEEL_S_DAY_PER_C:.1f}"),
        ("  each expansion term ~", f"{EXPANSION_SHIFT:.1f} s/day per deg C"),
        ("  10 deg C change", f"{STEEL_10C_S_DAY:.0f} s/day"),
        ("loss per cycle at Q 300", f"{LOSS_FRAC * 100:.2f} %"),
        ("6497 loss / power", f"{LOSS_6497 * 1e6:.3f} uJ / {POWER_6497 * 1e6:.2f} uW"),
        ("4 Hz loss / power (chapter)", f"{LOSS_4HZ * 1e6:.3f} uJ / {POWER_4HZ * 1e6:.2f} uW"),
        ("free swing halves in", f"{HALF_AMP_TIME:.1f} s"),
        ("barrel energy linear / design", f"{U_LINEAR:.2f} J / {U_DESIGN:.2f} J"),
        ("barrel mean power over 46 h", f"{P_BARREL[0] * 1e6:.1f} - {P_BARREL[1] * 1e6:.1f} uW"),
        ("after the escapement (30-40 %)", f"{P_AT_BALANCE[0] * 1e6:.2f} - {P_AT_BALANCE[1] * 1e6:.2f} uW"),
    ]
    w = max(len(a) for a, _ in rows)
    return "\n".join(f"{a:<{w}}  {b}" for a, b in rows)


if __name__ == "__main__":
    print(table())
