"""Reuse Film 4's helpers (balance.py, ui.py) without moving or changing them.

Import this first in a Film 5 scene:  import f4  (then: from balance import ...,
from ui import ...). It appends Film 4's folder to sys.path, after Film 5's own
folder, so Film 5's figures.py still wins over Film 4's. Film 4's numbers, when
needed, come from f4.figures4.
"""
import os, sys, importlib.util

F4_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "film04_regulating_organ")
if F4_DIR not in sys.path:
    sys.path.append(F4_DIR)

_spec = importlib.util.spec_from_file_location("figures4", os.path.join(F4_DIR, "figures.py"))
figures4 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(figures4)
