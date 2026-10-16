"""Report every visible piece of a Film 7 scene that dips into the caption band.

    python films/film07_keyless_works/check_captions.py scene03_two_positions Scene03

Runs the scene without writing video (dry run) and, after each animation,
lists text and shapes whose bottom is below SAFE_Y (default -2.7; set the
SAFE_Y environment variable to change it), with the times they are on screen.
Silence means the band is clear. In scene 03 the zoom on the clutch runs the lower parts
into the band behind a mask, so those reports (about 13.3 to 21 s) are expected."""
import sys, importlib, os
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path[:0] = [ROOT, HERE]
os.chdir(ROOT)
from manim import *
SAFE_Y = float(os.environ.get("SAFE_Y", -2.7))
mod_name, cls_name = sys.argv[1], sys.argv[2]
config.quality = "low_quality"; config.dry_run = True; config.disable_caching = True
mod = importlib.import_module(mod_name)
Cls = getattr(mod, cls_name)
hits = {}

def describe(m):
    for a in [m] + list(m.get_family()):
        if hasattr(a, "text") and isinstance(getattr(a, "text"), str) and a.text.strip():
            return "T:" + a.text.strip().replace("\n", " ")[:50]
        if hasattr(a, "original_text"):
            return "T:" + str(a.original_text)[:50]
    return type(m).__name__ + f" w={m.width:.1f} h={m.height:.1f}"

def visible(m):
    fam = [x for x in m.get_family() if x.has_points()]
    return any((x.get_stroke_opacity() > 0.05 and x.get_stroke_width() > 0) or x.get_fill_opacity() > 0.05 for x in fam)

def check(scene):
    t = scene.renderer.time
    for top in scene.mobjects:
        stack = [top]
        while stack:
            m = stack.pop()
            if m.width >= config.frame_width * 0.95:      # vignette, curtain, full-width groups: look inside
                stack.extend(m.submobjects); continue
            if not m.has_points() and not m.submobjects:
                continue
            if m.get_bottom()[1] < SAFE_Y and visible(m):
                if len(m.submobjects) > 1 and not hasattr(m, "text") and m.height > 0.8:
                    stack.extend(m.submobjects); continue
                k = describe(m)
                lo, t0, t1 = hits.get(k, (9, t, t))
                hits[k] = (min(lo, m.get_bottom()[1]), min(t0, t), max(t1, t))

orig_play, orig_wait = Scene.play, Scene.wait
def play(self, *a, **k):
    r = orig_play(self, *a, **k); check(self); return r
def wait(self, *a, **k):
    r = orig_wait(self, *a, **k); check(self); return r
Scene.play, Scene.wait = play, wait
Cls().render()
for k, (lo, t0, t1) in sorted(hits.items(), key=lambda kv: kv[1][1]):
    print(f"  {t0:5.1f}-{t1:5.1f}s  bottom {lo:5.2f}  {k}")
