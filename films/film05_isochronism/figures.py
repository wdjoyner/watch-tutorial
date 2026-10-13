"""Film 5's numbers, each computed here from its inputs, with its source.

Every number shown on screen or spoken in Film 5 should come from this module
(or be checked against it). Run `python figures.py` to print the table and
the Phillips-curve check.

Sources
  [MAW] The Mathematics of the Automatic Mechanical Watch (AI and W. David Joyner,
        2026), section "Isochronism: anharmonicity, the Duffing correction, and
        the overcoil": the Poincare-Lindstedt formula, Example "How small must
        beta be?", the Phillips conditions, the beat-error intervals. The
        timegrapher appendix defines beat error as |T_tick - T_tock| (= 2 eps).
  [ETA] ETA technical communication for the 6497-1: 18,000 vph, 46 h power reserve.
  [F4]  Film 4's figures.py: 2.5 Hz, the representative 270 deg amplitude, 1 s/day = 11.57 ppm.

ETA does not publish the 6497's beta, amplitude curve or beat error. Values
marked REPRESENTATIVE are the chapter's illustrative ones (or chosen here to
show an effect) and must be labeled that way on screen. Values marked
EXAGGERATED are for the picture or the sound only and must be tagged so.
"""
import numpy as np

TAU = 2 * np.pi
DAY = 86_400.0

# --------------------------------------------------------------- the 6497 [ETA] [F4]
F_6497 = 2.5                                     # Hz, 18,000 vph
HALF_PERIOD = 1 / (2 * F_6497)                   # 0.2 s between ticks
RESERVE_H = 46                                   # h
PPM_PER_S_DAY = 1e6 / DAY                        # 1 s/day = 11.57 ppm


def rate_shift(beta_over_kappa, amp_rad):
    """Delta f / f = 3 beta Theta^2 / (8 kappa)  (Poincare-Lindstedt) [MAW]."""
    return 3 * beta_over_kappa * amp_rad ** 2 / 8


def s_per_day(frac):
    return frac * DAY


# --------------------------------------------------------------- how small must beta be? [MAW]
AMP_FULL = np.radians(270.0)                     # REPRESENTATIVE amplitude at full wind
AMP_LOW = np.radians(220.0)                      # REPRESENTATIVE amplitude late in the reserve
BUDGET = 1.0 / DAY                               # 1 s/day as a fraction (11.6 ppm)
BETA_MAX = BUDGET * 8 / (3 * (AMP_FULL ** 2 - AMP_LOW ** 2))   # |beta|/kappa bound, ~4.1e-6 rad^-2
BETA_ROUND = 4e-6                                # the chapter's "about 4 x 10^-6"
CUBIC_OVER_LINEAR = BETA_ROUND * AMP_FULL ** 2   # beta Theta^2 / kappa at the turning point, ~1e-4
# at the bound, the two ends of the drift (relative to a perfectly linear spring)
SHIFT_FULL = rate_shift(BETA_ROUND, AMP_FULL)    # ~33 ppm
SHIFT_LOW = rate_shift(BETA_ROUND, AMP_LOW)      # ~22 ppm
DRIFT_S_DAY = s_per_day(SHIFT_FULL - SHIFT_LOW)  # ~0.97 s/day

# --------------------------------------------------------------- for the parabola picture
BETA_SHOWN = 2e-3                                # EXAGGERATED beta/kappa, so the curve bends visibly
AMP_AXIS = np.radians(np.array([0.0, 330.0]))    # plotted amplitude range

# --------------------------------------------------------------- beat error [MAW]
BEAT_ERR_REPR = 0.6e-3                           # s, REPRESENTATIVE |T_tick - T_tock| (= 2 eps)
EPS_REPR = BEAT_ERR_REPR / 2
TICK_A = HALF_PERIOD + EPS_REPR                  # 0.2003 s
TICK_B = HALF_PERIOD - EPS_REPR                  # 0.1997 s
FULL_PERIOD = TICK_A + TICK_B                    # 0.4 s exactly: the rate is untouched
BEAT_ERR_SHOWN = 0.16                            # EXAGGERATED, as a fraction of the half-period, for the ear


# --------------------------------------------------------------- the Phillips curve
def terminal_curve(r1, a1, r2, a2, rho0=1.0, n=600):
    """Plan view of a two-arc terminal curve. It leaves the junction C = (0, rho0)
    tangent to the outer coil (heading -x, coils counterclockwise), turns inward
    along an arc of radius r1 through a1 radians, then along an arc of radius r2
    through a2 radians, to the stud. Returns an (N, 2) array of points."""
    pts, p, h = [], np.array([0.0, rho0]), np.pi
    for r, a in ((r1, a1), (r2, a2)):
        c = p + r * np.array([np.cos(h + np.pi / 2), np.sin(h + np.pi / 2)])
        t0 = np.arctan2(p[1] - c[1], p[0] - c[0])
        seg = c + r * np.c_[np.cos(t0 + np.linspace(0, a, n)), np.sin(t0 + np.linspace(0, a, n))]
        pts.append(seg)
        p, h = seg[-1], h + a
    return np.vstack(pts)


def length_and_cg(P):
    """Developed length and center of gravity of a polyline of uniform wire."""
    d = np.linalg.norm(np.diff(P, axis=0), axis=1)
    mid = (P[1:] + P[:-1]) / 2
    return d.sum(), (mid * d[:, None]).sum(0) / d.sum()


# Two of the four arc parameters are chosen; the other two are solved (scipy, in
# phillips_solve below) so that OG is perpendicular to OC and OG = rho0^2 / l.
PH_R2, PH_A2 = 0.65, np.radians(120.0)          # chosen: second arc, in units of rho0
PH_R1, PH_A1 = 0.846870, np.radians(161.2455)   # solved (see phillips_solve)


def phillips_solve():
    from scipy.optimize import fsolve

    def conditions(x):
        L, G = length_and_cg(terminal_curve(x[0], x[1], PH_R2, PH_A2))
        return [G[1], np.hypot(*G) - 1 / L]      # C is on the y-axis, so OG perpendicular to OC means G_y = 0
    return fsolve(conditions, [0.8, np.radians(150)])


PH_CURVE = terminal_curve(PH_R1, PH_A1, PH_R2, PH_A2)
PH_L, PH_G = length_and_cg(PH_CURVE)            # l ~ 3.74 rho0, G ~ (-0.267, 0)
PH_OG = float(np.hypot(*PH_G))
PH_TARGET = 1 / PH_L                             # rho0^2 / l with rho0 = 1
PH_ANGLE = 90.0 - np.degrees(np.arctan2(abs(PH_G[1]), abs(PH_G[0])))
PH_RMAX = float(np.hypot(*PH_CURVE.T).max())    # stays inside the outer coil


def table():
    rows = [
        ("6497: half-period, reserve", f"{HALF_PERIOD} s, {RESERVE_H} h"),
        ("1 s/day", f"{PPM_PER_S_DAY:.2f} ppm"),
        ("amplitudes (REPR.)", f"270 deg = {AMP_FULL:.2f} rad, 220 deg = {AMP_LOW:.2f} rad"),
        ("|beta|/kappa bound for 1 s/day", f"{BETA_MAX:.2e} rad^-2  (chapter: about 4e-6)"),
        ("cubic / linear torque at 270 deg", f"{CUBIC_OVER_LINEAR:.1e}"),
        ("at 4e-6: shift at 270 / 220 deg", f"{SHIFT_FULL * 1e6:.1f} / {SHIFT_LOW * 1e6:.1f} ppm"),
        ("  drift between them", f"{DRIFT_S_DAY:.2f} s/day"),
        ("beat error (REPR.) 2 eps", f"{BEAT_ERR_REPR * 1e3:.1f} ms: ticks {TICK_A:.4f} s / {TICK_B:.4f} s, sum {FULL_PERIOD:.4f} s"),
        ("Phillips curve: r1, a1 / r2, a2 (rho0 = 1)", f"{PH_R1:.4f}, {np.degrees(PH_A1):.2f} deg / {PH_R2}, {np.degrees(PH_A2):.0f} deg"),
        ("  developed length l", f"{PH_L:.4f} rho0"),
        ("  G", f"({PH_G[0]:+.5f}, {PH_G[1]:+.1e})"),
        ("  OG vs rho0^2 / l", f"{PH_OG:.5f} vs {PH_TARGET:.5f}"),
        ("  angle between OG and OC", f"{PH_ANGLE:.4f} deg"),
        ("  farthest point from O", f"{PH_RMAX:.4f} rho0 (inside the coil)"),
    ]
    w = max(len(a) for a, _ in rows)
    return "\n".join(f"{a:<{w}}  {b}" for a, b in rows)


if __name__ == "__main__":
    print(table())
    r1, a1 = phillips_solve()
    print(f"\nre-solved Phillips curve: r1 = {r1:.6f}, a1 = {np.degrees(a1):.4f} deg")
