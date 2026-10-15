"""Reuse Film 4's and Film 5's helpers without moving or changing them.

Import this first in a Film 6 scene:  import prev  (then: from balance import ...,
from ui import ..., from iso import ...). It appends Film 5's folder and then
Film 4's folder to sys.path, after Film 6's own folder, so Film 6's figures.py
still wins over theirs. (Film 5's iso.py does `import f4`, which it finds in
Film 5's folder.) Their numbers, when needed, are prev.figures4 and prev.figures5.
No shared file is touched, so Films 1-5 build exactly as before.
"""
import os, sys, importlib.util

FILMS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F5_DIR = os.path.join(FILMS, "film05_isochronism")
F4_DIR = os.path.join(FILMS, "film04_regulating_organ")
for d in (F5_DIR, F4_DIR):
    if d not in sys.path:
        sys.path.append(d)


def _load(name, folder):
    spec = importlib.util.spec_from_file_location(name, os.path.join(folder, "figures.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


figures4 = _load("figures4", F4_DIR)
figures5 = _load("figures5", F5_DIR)
