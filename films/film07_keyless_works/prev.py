"""Reuse earlier films' helpers without moving or changing them.

Import this first in a Film 7 scene:  import prev  (then: from ui import ...,
from ui6 import ..., from train import ..., from barrel import ...). It appends Film 6's, Film 4's and
Film 3's and Film 2's folders to sys.path, after Film 7's own folder, so Film 7's figures.py
still wins over Film 6's. (Film 6's ui6.py does `import prev`, which finds this
file first; that is fine, since this one puts Film 4's folder on the path too.)
Film 6's numbers, when needed, are prev.figures6. No shared file is touched,
so Films 1-6 build exactly as before.
"""
import os, sys, importlib.util

FILMS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F6_DIR = os.path.join(FILMS, "film06_escapement")
F4_DIR = os.path.join(FILMS, "film04_regulating_organ")
F3_DIR = os.path.join(FILMS, "film03_gear_train")
F2_DIR = os.path.join(FILMS, "film02_power_source")
for d in (F6_DIR, F4_DIR, F3_DIR, F2_DIR):
    if d not in sys.path:
        sys.path.append(d)


def _load(name, folder):
    spec = importlib.util.spec_from_file_location(name, os.path.join(folder, "figures.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


figures6 = _load("figures6", F6_DIR)
