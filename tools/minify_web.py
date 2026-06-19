#!/usr/bin/env python3
"""
minify_web.py — Minifie les assets statiques de data/ (.html, .css, .js)
en place, avant chaque compilation. Contrairement à Gateway Lab/MeteoHub,
ESP32-Foundation sert ces fichiers directement depuis LittleFS (pas de
génération de headers PROGMEM) : ce script ne fait que réduire leur taille
pour économiser de l'espace flash, sans changer leur contenu fonctionnel.

Idempotent : peut être exécuté plusieurs fois sans dégrader le résultat
(à partir des fichiers déjà minifiés, il n'y a simplement plus rien à gagner).

Requirements (optionnels — fallback regex intégré) :
    pip install rcssmin rjsmin
"""

import re
import sys
from pathlib import Path

env = None
if "Import" in globals():
    # "Import" est injecté par PlatformIO/SCons dans le contexte exec() ;
    # absent en exécution standalone (python tools/minify_web.py).
    globals()["Import"]("env")

# Exécuté par PlatformIO via exec() dans SConscript : __file__ n'existe pas.
# env["PROJECT_DIR"] est alors la seule source fiable du chemin du projet.
if env is not None:
    PROJECT_ROOT = Path(env.get("PROJECT_DIR"))
else:
    PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"

try:
    import rcssmin
except ImportError:
    rcssmin = None

try:
    import rjsmin
except ImportError:
    rjsmin = None


def minify_css(css: str) -> str:
    if rcssmin is not None:
        return str(rcssmin.cssmin(css))
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)
    css = re.sub(r"\s*([{}:;,>~+])\s*", r"\1", css)
    return re.sub(r"\s+", " ", css).strip()


def minify_js(js: str) -> str:
    if rjsmin is not None:
        return str(rjsmin.jsmin(js))
    js = re.sub(r"//[^\n]*", "", js)
    return re.sub(r"\s+", " ", js).strip()


def minify_html(html: str) -> str:
    html = re.sub(r"<!--(?!\[if).*?-->", "", html, flags=re.DOTALL)
    html = re.sub(r">\s+<", "><", html)
    return html.strip()


def run() -> bool:
    if not DATA_DIR.exists():
        print("[minify_web] data/ absent — rien à faire")
        return True

    total_before = total_after = 0
    for path in sorted(DATA_DIR.glob("*")):
        if not path.is_file():
            continue
        raw = path.read_text(encoding="utf-8", errors="ignore")
        if path.suffix == ".css":
            minified = minify_css(raw)
        elif path.suffix == ".js":
            minified = minify_js(raw)
        elif path.suffix == ".html":
            minified = minify_html(raw)
        else:
            continue

        total_before += len(raw)
        total_after += len(minified)
        if minified != raw:
            path.write_text(minified, encoding="utf-8")

    if total_before:
        ratio = 100 * (1 - total_after / total_before)
        print(f"[minify_web] data/ : {total_before:,} -> {total_after:,} octets (gain {ratio:.1f}%)")
    return True


if __name__ == "__main__":
    sys.exit(0 if run() else 1)
else:
    # Appelé via extra_scripts (pre:tools/minify_web.py) par PlatformIO
    run()
