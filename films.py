"""Locate films and scenes under films/. Shared by build.py and film.py.

A film is a folder films/filmNN_<name>/ holding its scene files, their
.voice.txt narration, and running_order.py (TITLE, OUT_NAME, SCENES).
A film can be named by its number ("1", "01"), its prefix ("film01"),
or its full folder name. A scene can be named as "<film>/<scene>", or by
the bare scene name when only one film has a scene of that name.
"""
import glob, os, re, runpy, sys

HERE = os.path.dirname(os.path.abspath(__file__))
FILMS = os.path.join(HERE, "films")


def all_films():
    return sorted(d for d in os.listdir(FILMS) if re.match(r"film\d+_", d) and os.path.isdir(os.path.join(FILMS, d)))


def film_dir(name):
    """Resolve a film name to its folder name."""
    name = name.strip("/").split("/")[-1]
    for d in all_films():
        num = re.match(r"film(\d+)_", d).group(1)
        if name in (d, f"film{num}") or (name.isdigit() and int(name) == int(num)):
            return d
    sys.exit(f"no film '{name}'; films are: " + ", ".join(all_films()))


def find_scene(arg):
    """Resolve a scene argument to (film_folder, scene_name)."""
    arg = os.path.splitext(arg.rstrip("/"))[0]
    if os.sep in arg or "/" in arg:
        film, scene = arg.replace(os.sep, "/").rsplit("/", 1)
        return film_dir(film), scene
    hits = [os.path.basename(os.path.dirname(p)) for p in glob.glob(os.path.join(FILMS, "*", arg + ".py"))]
    if len(hits) == 1:
        return hits[0], arg
    if not hits:
        sys.exit(f"no scene '{arg}' in any film")
    sys.exit(f"'{arg}' exists in several films ({', '.join(sorted(hits))}); name it as <film>/{arg}, e.g. 2/{arg}")


def running_order(film):
    return runpy.run_path(os.path.join(FILMS, film, "running_order.py"))
