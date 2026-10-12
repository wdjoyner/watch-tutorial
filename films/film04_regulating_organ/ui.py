"""Film 4 helpers shared by the scenes: text styles, tags and a timeline clock.

Formulas are set with Text (serif italic), never LaTeX; that rules out Integer,
DecimalNumber and Brace too, which go through LaTeX.
"""
from manim import *
from movement import BG, GLOW, FONT_SANS, FONT_SERIF

FORMULA_COLOR = WHITE
NOTE = GREY_B
WARM, COOL = "#ff9a6a", "#8fc3ff"          # hot / cold, spring energy / rim energy


# Unicode sub/superscripts -> plain characters set with Pango <sub>/<sup>. Georgia and
# Helvetica Neue (the macOS fonts) lack most of these glyphs (subscript 0 and s,
# superscript minus and 4-9), so they came out as look-alikes or empty boxes.
# Latin-1's own superscripts 1, 2, 3 exist in every font and stay as they are,
# unless they share a run with characters that need markup.
_SUB = dict(zip("₀₁₂₃₄₅₆₇₈₉ₛᵣₐₑₒₓ", "0123456789sraeox"))
_SUP = dict(zip("⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺", "0123456789−+"))
_LATIN1 = set("¹²³")


def _markup(s):
    """None if *s* needs no markup, else Pango markup with <sub>/<sup> runs."""
    if not any(c in _SUB or (c in _SUP and c not in _LATIN1) for c in s):
        return None
    out, i = [], 0
    esc = lambda c: {"&": "&amp;", "<": "&lt;", ">": "&gt;"}.get(c, c)
    while i < len(s):
        for table, tagname in ((_SUB, "sub"), (_SUP, "sup")):
            j = i
            while j < len(s) and s[j] in table:
                j += 1
            run = s[i:j]
            if run and not (tagname == "sup" and set(run) <= _LATIN1):
                out.append(f"<{tagname}>" + "".join(esc(table[c]) for c in run) + f"</{tagname}>")
                i = j
                break
        else:
            out.append(esc(s[i]))
            i += 1
    return "".join(out)


def text(s, **kw):
    """Text, or MarkupText when *s* has sub/superscripts that need markup."""
    mk = _markup(s)
    return Text(s, **kw) if mk is None else MarkupText(mk, **kw)


def ftext(s, scale=0.5, color=FORMULA_COLOR):
    """A formula: serif italic."""
    return text(s, font=FONT_SERIF, slant=ITALIC, color=color).scale(scale)


def label(s, scale=0.28, color=NOTE, bold=False):
    return text(s, font=FONT_SANS, weight=BOLD if bold else NORMAL, color=color).scale(scale)


def heading(title, sub=None):
    """Chapter heading for a corner: bold glow title, grey subtitle."""
    rows = [Text(title, font=FONT_SANS, weight=BOLD, color=GLOW).scale(0.40)]
    if sub:
        rows.append(Text(sub, font=FONT_SANS, color=GREY_B).scale(0.26))
    return VGroup(*rows).arrange(DOWN, aligned_edge=LEFT, buff=0.1)


def tag(s, color=GLOW, scale=0.24):
    """A small boxed note, e.g. 'slowed 10x' or 'representative values'."""
    t = text(s, font=FONT_SANS, color=color).scale(scale)
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
