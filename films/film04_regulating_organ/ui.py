"""Film 4 helpers shared by the scenes: text styles, tags and a timeline clock.

Formulas are set with Text (serif italic), never LaTeX; that rules out Integer,
DecimalNumber and Brace too, which go through LaTeX.
"""
from manim import *
from movement import BG, GLOW, FONT_SANS, FONT_SERIF

FORMULA_COLOR = WHITE
NOTE = GREY_B
WARM, COOL = "#ff9a6a", "#8fc3ff"          # hot / cold, spring energy / rim energy


def ftext(s, scale=0.5, color=FORMULA_COLOR):
    """A formula: serif italic."""
    return Text(s, font=FONT_SERIF, slant=ITALIC, color=color).scale(scale)


def label(s, scale=0.28, color=NOTE, bold=False):
    return Text(s, font=FONT_SANS, weight=BOLD if bold else NORMAL, color=color).scale(scale)


def heading(title, sub=None):
    """Chapter heading for a corner: bold glow title, grey subtitle."""
    rows = [Text(title, font=FONT_SANS, weight=BOLD, color=GLOW).scale(0.40)]
    if sub:
        rows.append(Text(sub, font=FONT_SANS, color=GREY_B).scale(0.26))
    return VGroup(*rows).arrange(DOWN, aligned_edge=LEFT, buff=0.1)


def tag(s, color=GLOW, scale=0.24):
    """A small boxed note, e.g. 'slowed 10x' or 'representative values'."""
    t = Text(s, font=FONT_SANS, color=color).scale(scale)
    box = SurroundingRectangle(t, buff=0.09, corner_radius=0.06).set_stroke(color, 1.2, 0.8).set_fill(BG, 0.85)
    return VGroup(box, t)


def curtain():
    return FullScreenRectangle().set_fill(BG, 1).set_stroke(width=0)


def clock(scene):
    """wait_until(t): wait until absolute scene time t (no-op if already past)."""
    def wait_until(when):
        d = when - scene.renderer.time
        if d > 1e-3:
            scene.wait(d)
    return wait_until


def faded(g, v):
    """Scale each part's own fill and stroke opacity by v (set_opacity would fill lines and frames)."""
    for m in g.family_members_with_points():
        m.set_fill(opacity=m.get_fill_opacity() * v, family=False)
        m.set_stroke(opacity=m.get_stroke_opacity() * v, family=False)
    return g


SUP = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")


def sci(x, digits=1):
    """4.0e-09 -> '4.0 × 10⁻⁹' (Text-friendly scientific notation)."""
    m, e = f"{x:.{digits}e}".split("e")
    return f"{m} × 10{str(int(e)).translate(SUP)}"


def m(s):
    """Typographic minus signs in a number string: '-10.4' -> '−10.4'."""
    return s.replace("-", "−")
