"""Film 3, scene 10 - "Better fractions": the continued fraction of the
lunation, 29.530589 = [29; 1, 1, 7, 1, 2, ...], computed step by step; its
convergents with how long each keeps a moon display within a day; the
Stern-Brocot tree's mediant steps descending on the same fractions; and a
nearby fraction that factors into small stages, 945/32 = (90/16) x (42/8).

Build (render + voice + mux):   python build.py 3/scene10_fractions
Render only (quick preview):    PYTHONPATH=.:films/film03_gear_train manim -ql films/film03_gear_train/scene10_fractions.py Scene10
Narration lines and their start times live in scene10_fractions.voice.txt.

Every number on screen is computed here from LUNATION. In the tree, a node's
height is its step down the tree and its x is its log distance from the
target (left: too small, right: too big), so the path closes in on the center line.
"""
from fractions import Fraction
from manim import *
from movement import vignette, BG, GLOW, FONT_SANS, FONT_SERIF

# =====================================================================
# SETTINGS - safe to edit. Times are in seconds.
# Keep the timeline roughly in step with scene10_fractions.voice.txt.
# =====================================================================

# --- timeline --------------------------------------------------------
FADE_IN = 1.0
TARGET_AT = 1.4                         # 29.530589
ROWS_AT = (5.6, 7.6, 9.4, 10.1, 10.8, 11.5)   # each step of the continued fraction
CF_AT = 12.0                            # [29; 1, 1, 7, 1, 2, ...]
CONV_AT = {"59/2": 15.0, "443/15": 17.0, "1447/49": 19.6}
OTHERS_AT = 22.0                        # "and so on": the rest of the list
BEST_AT = 24.4                          # "the best fraction with a denominator that small"
TREE_AT = 29.2                          # the Stern-Brocot tree
NODES_FROM, NODES_TO = 31.6, 39.6       # the mediant steps
CONV_GLOW_AT = 40.0                     # the convergents among them
YEARS_AT = {"443/15": 41.6, "1447/49": 46.4}
PRIME_AT = 52.6                         # "those numerators are prime"
NEARBY_AT = 57.4                        # 945/32 = (90/16) x (42/8)
FINAL_HOLD_UNTIL = 66.8                 # the last line ends about 65.4 s
FADE_OUT = 1.5

# --- numbers -----------------------------------------------------------
LUNATION = 29.530589
CF_STEPS = 6
CONVERGENTS = ("29/1", "30/1", "59/2", "443/15", "502/17", "1447/49")
NEARBY = ("945/32", "90/16", "42/8")

# --- layout -------------------------------------------------------------
CASCADE_AT = (-6.7, 1.95)               # left end of the first cascade row
ROW_GAP = 0.52
TABLE_AT = (1.0, 1.0)                  # left end of the convergents table's first row
TREE_ROW0, TREE_DY = 2.45, 0.43
TREE_K = 1.12                           # x = sign * (log10(distance) + 5) * TREE_K
TREE_STEPS = 11

# --- text and colors -------------------------------------------------------
LOW, HIGH = "#6fb3ff", "#ff9a5c"        # below and above the target
TABLE_HEAD = ("fraction", "value", "a day off after")
BEST = "each is the best fraction with a denominator that small"
TREE_TITLE = "STERN–BROCOT:  the mediant of a/b and c/d is (a + c)/(b + d)"
TARGET_LAB = "29.530589"
PRIME = "prime"
NEARBY_TEXT = "945/32  =  (90/16) × (42/8)  =  29.53125:   a day off after about 120 years"
# =====================================================================


def label(s, scale=0.28, color=GREY_B, bold=False):
    return Text(s, font=FONT_SANS, weight=BOLD if bold else NORMAL, color=color).scale(scale)


def ftext(s, scale=0.5, color=WHITE):
    return Text(s, font=FONT_SERIF, slant=ITALIC, color=color).scale(scale)


def years_off(fr):
    """Years until a display geared to fr drifts a full day from the moon."""
    e = abs(fr.numerator / fr.denominator - LUNATION)
    return LUNATION / e / 365.25


def nice_years(y):
    if y < 1:
        return f"{y * 12:.0f} months"
    if y < 10:
        return f"{y:.1f} years"
    return f"{y:,.0f} years" if y < 1000 else f"{round(y, -2):,.0f} years"


class Scene10(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.add(vignette())

        def wait_until(when):
            d = when - self.renderer.time
            if d > 1e-3:
                self.wait(d)

        # ------------------------------------------------------------ the continued fraction
        target = ftext(f"{LUNATION:.6f}  days", 0.55, WHITE).move_to([CASCADE_AT[0], CASCADE_AT[1] + 0.8, 0], aligned_edge=LEFT)
        rows, x, wholes = [], LUNATION, []
        for i in range(CF_STEPS):
            w, f = int(x), x - int(x)
            left = f"{LUNATION:.6f}" if i == 0 else f"1 / {prev:.6f}  =  {x:.6f}"
            row = VGroup(ftext(left + "  =", 0.36), ftext(str(w), 0.42, GLOW), ftext(f"+  {f:.6f}", 0.36))
            row.arrange(RIGHT, buff=0.18).move_to([CASCADE_AT[0], CASCADE_AT[1] - i * ROW_GAP, 0], aligned_edge=LEFT)
            rows.append(row)
            wholes.append(w)
            prev, x = f, 1 / f
        cf = ftext("[ " + str(wholes[0]) + ";  " + ",  ".join(map(str, wholes[1:])) + ",  … ]", 0.6, GLOW)
        cf.move_to([CASCADE_AT[0], CASCADE_AT[1] - CF_STEPS * ROW_GAP - 0.2, 0], aligned_edge=LEFT)

        # convergents table
        head = VGroup(*[label(h, 0.26) for h in TABLE_HEAD])
        table_rows = {}
        for i, c in enumerate(CONVERGENTS):
            fr = Fraction(c)
            v = fr.numerator / fr.denominator
            table_rows[c] = VGroup(ftext(c, 0.46, WHITE), label(f"{v:.6f}", 0.28, GREY_A),
                                   label(nice_years(years_off(fr)), 0.28, GLOW))
        cols = (TABLE_AT[0], TABLE_AT[0] + 2.0, TABLE_AT[0] + 4.0)
        for k, h in enumerate(head):
            h.move_to([cols[k], TABLE_AT[1] + 0.55, 0], aligned_edge=LEFT)
        for i, c in enumerate(CONVERGENTS):
            for k, cell in enumerate(table_rows[c]):
                cell.move_to([cols[k], TABLE_AT[1] - i * 0.48, 0], aligned_edge=LEFT)
        best = label(BEST, 0.28, GLOW).move_to([TABLE_AT[0] + 2.6, TABLE_AT[1] - 6 * 0.48 - 0.2, 0])
        part1 = VGroup(target, *rows, cf, head, *table_rows.values(), best)

        # ------------------------------------------------------------ the Stern-Brocot path
        def tx(fr):
            d = fr.numerator / fr.denominator - LUNATION
            return np.sign(d) * (np.log10(abs(d)) + 5) * TREE_K

        lo, hi = Fraction(29, 1), Fraction(30, 1)
        nodes, edges, order = {}, VGroup(), []

        def node(fr, row):
            v = fr.numerator / fr.denominator
            col = LOW if v < LUNATION else HIGH
            t = ftext(f"{fr.numerator}/{fr.denominator}", 0.36, col)
            return t.move_to([tx(fr), TREE_ROW0 - row * TREE_DY, 0])
        nodes["29/1"], nodes["30/1"] = node(lo, 0), node(hi, 0)
        for step in range(1, TREE_STEPS + 1):
            m = Fraction(lo.numerator + hi.numerator, lo.denominator + hi.denominator)
            key = f"{m.numerator}/{m.denominator}"
            nodes[key] = node(m, step)
            for parent in (lo, hi):
                p = nodes[f"{parent.numerator}/{parent.denominator}"]
                edges.add(Line(p.get_bottom() + DOWN * 0.03, nodes[key].get_top() + UP * 0.03).set_stroke(GREY_C, 1.2, 0.6))
            order.append((key, edges[-2:]))
            if m.numerator / m.denominator < LUNATION:
                lo = m
            else:
                hi = m
        center = DashedLine([0, TREE_ROW0 + 0.4, 0], [0, TREE_ROW0 - TREE_STEPS * TREE_DY - 0.3, 0], dash_length=0.1)
        center.set_stroke(WHITE, 1.5, 0.7)
        center_lab = label(TARGET_LAB, 0.26, WHITE).next_to(center, UP, buff=0.08)
        tree_title = label(TREE_TITLE, 0.3, GLOW, True).to_corner(UL, buff=0.45)
        sides = VGroup(label("too small", 0.26, LOW).move_to([-4.6, TREE_ROW0 + 0.45, 0]),
                       label("too big", 0.26, HIGH).move_to([4.6, TREE_ROW0 + 0.45, 0]))
        conv_rings = VGroup(*[SurroundingRectangle(nodes[c], buff=0.07, corner_radius=0.06).set_stroke(GLOW, 2.5)
                              for c in CONVERGENTS if c in nodes])
        year_tags = {c: label(nice_years(years_off(Fraction(c))), 0.28, GLOW) for c in YEARS_AT}
        for c, t in year_tags.items():
            n = nodes[c]
            t.next_to(n, RIGHT if tx(Fraction(c)) > 0 else LEFT, buff=0.25)
        primes = {c: label(PRIME, 0.24, WHITE).next_to(year_tags[c], RIGHT if tx(Fraction(c)) > 0 else LEFT, buff=0.2)
                  for c in YEARS_AT}
        primes["1447/49"].next_to(year_tags["1447/49"], DOWN, buff=0.08, aligned_edge=LEFT)
        nearby = ftext(NEARBY_TEXT, 0.4, WHITE).move_to([0, -3.45, 0])
        nearby_box = SurroundingRectangle(nearby, buff=0.16, corner_radius=0.08).set_stroke(GLOW, 2)

        curtain = FullScreenRectangle().set_fill(BG, 1).set_stroke(width=0)
        self.add(curtain)

        # ---------------------------------------------------------- timeline
        self.play(curtain.animate.set_fill(opacity=0), run_time=FADE_IN, rate_func=smooth)
        self.remove(curtain)
        wait_until(TARGET_AT)
        self.play(FadeIn(target, shift=DOWN * 0.1), run_time=0.8)
        for row, t in zip(rows, ROWS_AT):                  # whole part off, flip the rest, repeat
            wait_until(t)
            self.play(FadeIn(row, shift=DOWN * 0.1), run_time=0.5)
        wait_until(CF_AT)
        self.play(Write(cf), run_time=1.0)

        wait_until(CONV_AT["59/2"] - 0.8)                  # the convergents
        self.play(FadeIn(head), run_time=0.6)
        for c, t in CONV_AT.items():
            wait_until(t)
            self.play(FadeIn(table_rows[c], shift=LEFT * 0.1), run_time=0.7)
        wait_until(OTHERS_AT)
        self.play(*[FadeIn(table_rows[c], shift=LEFT * 0.1) for c in CONVERGENTS if c not in CONV_AT], run_time=0.8)
        wait_until(BEST_AT)
        self.play(FadeIn(best, shift=UP * 0.1), run_time=0.8)

        wait_until(TREE_AT - 0.8)                          # the Stern-Brocot tree
        self.play(FadeOut(part1), run_time=0.8)
        self.play(FadeIn(tree_title), Create(center), FadeIn(center_lab), FadeIn(sides),
                  FadeIn(nodes["29/1"]), FadeIn(nodes["30/1"]), run_time=1.2)
        step_t = (NODES_TO - NODES_FROM) / len(order)
        for i, (key, es) in enumerate(order):
            wait_until(NODES_FROM + i * step_t)
            self.play(Create(es), FadeIn(nodes[key], scale=1.3), run_time=min(0.6, step_t * 0.9))
        wait_until(CONV_GLOW_AT)
        self.play(LaggedStart(*[Create(r) for r in conv_rings], lag_ratio=0.2), run_time=1.2)

        for c, t in YEARS_AT.items():                      # how long each keeps the moon
            wait_until(t)
            self.play(FadeIn(year_tags[c], shift=UP * 0.1), Indicate(nodes[c], color=WHITE), run_time=0.8)

        wait_until(PRIME_AT)                               # prime numerators
        self.play(*[FadeIn(p, shift=UP * 0.1) for p in primes.values()], run_time=0.8)
        wait_until(NEARBY_AT)                              # a nearby fraction with small factors
        self.play(FadeIn(nearby, shift=UP * 0.1), Create(nearby_box), run_time=1.2)

        wait_until(FINAL_HOLD_UNTIL)
        curtain.set_fill(opacity=0)
        self.add(curtain)
        self.play(curtain.animate.set_fill(opacity=1), run_time=FADE_OUT)
