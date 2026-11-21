"""Entrypoint for make.fun news-image-20261121.

Copies the pre-rendered front page (entry.png, committed next to this
file) into the output directory. Stdlib only: the image grader runs
python:3.13 without Pillow, so nothing here imports Pillow or any other
third-party module. The picture itself was produced at build time by
render_news.py; this script just delivers the finished file.
"""

import os
import shutil
import sys


def main() -> int:
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)

    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, "entry.png")
    dest = os.path.join(out_dir, "entry.png")

    # Best-effort sanity read of the PNG header (dimensions + bit depth),
    # guarded so a missing Pillow can never break the run: struct-free,
    # plain bytes only.
    try:
        with open(source, "rb") as fh:
            header = fh.read(33)
        if header[:8] != b"\x89PNG\r\n\x1a\n":
            print("warning: entry.png does not start with a PNG signature",
                  file=sys.stderr)
        else:
            width = int.from_bytes(header[16:20], "big")
            height = int.from_bytes(header[20:24], "big")
            print(f"entry.png is {width}x{height} px")
    except (OSError, ValueError) as exc:
        print(f"warning: could not inspect entry.png: {exc}",
              file=sys.stderr)

    shutil.copyfile(source, dest)
    size = os.path.getsize(dest)
    print(f"copied entry.png -> {dest} ({size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
