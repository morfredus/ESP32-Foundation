#!/usr/bin/env python3
"""
minify_web.py — Minifie les sources web de web_src/ (.html, .css, .js) et
écrit le résultat dans data/, avant chaque compilation. data/ est l'image
servie depuis LittleFS : c'est un dossier généré, jamais édité à la main.
Contrairement à Gateway Lab/MeteoHub, ESP32-Foundation sert ces fichiers
directement depuis LittleFS (pas de génération de headers PROGMEM) : ce
script ne fait que réduire leur taille pour économiser de l'espace flash,
sans changer leur contenu fonctionnel.

Idempotent : peut être exécuté plusieurs fois sans dégrader le résultat
(à partir des fichiers déjà minifiés, il n'y a simplement plus rien à gagner).

Requirements (optionnels — fallback regex intégré) :
    pip install rcssmin rjsmin
"""

import re
import subprocess
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

SRC_DIR = PROJECT_ROOT / "web_src"
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
    if not SRC_DIR.exists():
        print("[minify_web] web_src/ absent — rien à faire")
        return True

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    total_before = total_after = 0
    for src_path in sorted(SRC_DIR.glob("*")):
        if not src_path.is_file():
            continue
        raw = src_path.read_text(encoding="utf-8", errors="ignore")
        if src_path.suffix == ".css":
            minified = minify_css(raw)
        elif src_path.suffix == ".js":
            minified = minify_js(raw)
        elif src_path.suffix == ".html":
            minified = minify_html(raw)
        else:
            continue

        total_before += len(raw)
        total_after += len(minified)
        (DATA_DIR / src_path.name).write_text(minified, encoding="utf-8")

    if total_before:
        ratio = 100 * (1 - total_after / total_before)
        print(f"[minify_web] web_src/ -> data/ : {total_before:,} -> {total_after:,} octets (gain {ratio:.1f}%)")
    return True


def prompt_uploadfs() -> None:
    # Uniquement en lancement manuel (python tools/minify_web.py) : en
    # extra_scripts, pio run est déjà en cours d'exécution et appeler
    # uploadfs ici serait à la fois récursif et non interactif (CI).
    reply = input("Téléverser data/ vers LittleFS maintenant (pio run --target uploadfs) ? [o/N] ").strip().lower()
    if reply in ("o", "oui", "y", "yes"):
        subprocess.run(["pio", "run", "--target", "uploadfs"])


if __name__ == "__main__":
    ok = run()
    if ok:
        prompt_uploadfs()
    sys.exit(0 if ok else 1)
else:
    # Appelé via extra_scripts (pre:tools/minify_web.py) par PlatformIO
    run()
