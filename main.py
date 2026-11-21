"""Entrypoint for make.fun news-image-20261121.

Renders the front page for Saturday 21 November 2026 and copies it to
the output directory as entry.png. Pure Pillow, no network, deterministic.
"""

import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import render_news


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    # Render to a temp name first so a failed render never leaves a stale
    # entry.png behind; the move is atomic on the same filesystem.
    tmp = os.path.join(out_dir, ".entry-tmp.png")
    render_news.render(tmp)
    dest = os.path.join(out_dir, "entry.png")
    shutil.move(tmp, dest)
    print("wrote", dest, os.path.getsize(dest), "bytes")


if __name__ == "__main__":
    main()
