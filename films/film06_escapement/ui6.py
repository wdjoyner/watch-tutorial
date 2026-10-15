"""Film 6 helpers on top of Film 4's ui.py (reached through prev.py).

callout(text, anchor, at)    a label at `at` with a thin leader line whose far end
                             follows anchor() every frame (anchor: a function
                             returning a point, e.g. lambda: esc.anchor("fork")).
                             Fade it in with FadeIn: only the leader has an updater.
callouts(text, anchors, at)  one label, several leader lines.
write_ticks(scene_file, times)  <scene>.ticks.txt from a list of video times.
write_sfx(scene_file, rows)     <scene>.sfx.txt from (time, sound, level) rows.
"""
import os
import prev  # noqa: F401  (Film 4 and 5 helpers on the path)
import numpy as np
from manim import *
import ui
from ui import label

# Film 6 uses a few more subscripts (J sub k, t sub k, phi-dot minus); Film 4's table is
# extended here, at import, so Films 4 and 5 render exactly as before.
ui._SUB.update({"ₖ": "k", "₋": "−", "ₗ": "l", "ᵢ": "i", "ₙ": "n", "ₘ": "m"})

LEADER = GREY_B


def _p3(at):
    a = np.array(at, dtype=float)
    return np.append(a, 0.0) if a.shape == (2,) else a


def _leader(lbl, anchor, color):
    ln = Line(ORIGIN, RIGHT, stroke_width=1.6, color=color)
    dot = Dot(radius=0.035, color=color)

    def upd(m):
        p = np.array(anchor(), dtype=float)
        box = lbl.get_center()
        # start at the label's edge nearest the anchor
        d = p - box
        hw, hh = lbl.width / 2 + 0.08, lbl.height / 2 + 0.06
        s = min(hw / max(abs(d[0]), 1e-6), hh / max(abs(d[1]), 1e-6), 1.0)
        start = box + d * s
        m.put_start_and_end_on(start, p if np.linalg.norm(p - start) > 1e-3 else start + RIGHT * 1e-3)
        dot.move_to(p)
    ln.add_updater(upd)
    upd(ln)
    return VGroup(ln, dot)


def callout(text, anchor, at, color=WHITE, scale=0.26, line_color=LEADER):
    lbl = label(text, scale, color).move_to(_p3(at))
    return VGroup(lbl, _leader(lbl, anchor, line_color))


def callouts(text, anchors, at, color=WHITE, scale=0.26, line_color=LEADER):
    lbl = label(text, scale, color).move_to(_p3(at))
    return VGroup(lbl, *[_leader(lbl, a, line_color) for a in anchors])


def write_ticks(scene_file, times):
    path = os.path.splitext(scene_file)[0] + ".ticks.txt"
    with open(path, "w") as f:
        f.write("# Written by the scene on every render: video time of each beat, for build.py's tick track.\n")
        for t in times:
            f.write(f"{t:.3f}\n")


def write_sfx(scene_file, rows):
    path = os.path.splitext(scene_file)[0] + ".sfx.txt"
    with open(path, "w") as f:
        f.write("# Written by the scene on every render: time | sound | level.\n")
        for t, snd, lvl in rows:
            f.write(f"{t:.3f} | {snd} | {lvl}\n")
