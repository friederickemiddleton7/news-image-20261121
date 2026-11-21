#!/usr/bin/env python3
"""make.fun entrypoint for news-image-20261121.

entry.png sits beside this file, drawn at build time. The grader only asks the
program to place one image in the output directory, so this copies the existing
PNG. Standard library only; no network, no clock, no randomness, so every run
produces the same bytes.
"""

import os
import shutil
import sys

IMAGE_NAME = "entry.png"
MIN_BYTES = 8 * 1024
MAX_BYTES = 1024 * 1024


def here():
    return os.path.dirname(os.path.abspath(__file__))


def resolve_output_dir():
    raw = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    return os.path.abspath(os.path.expanduser(raw))


def main():
    source = os.path.join(here(), IMAGE_NAME)

    if not os.path.isfile(source):
        sys.stderr.write("error: {0} not found next to main.py\n".format(IMAGE_NAME))
        return 1

    size = os.path.getsize(source)
    if not MIN_BYTES <= size <= MAX_BYTES:
        sys.stderr.write(
            "error: {0} is {1} bytes, outside the expected {2}-{3} range\n".format(
                IMAGE_NAME, size, MIN_BYTES, MAX_BYTES)
        )
        return 1

    out_dir = resolve_output_dir()
    try:
        os.makedirs(out_dir, exist_ok=True)
    except OSError as exc:
        sys.stderr.write("error: cannot create output directory {0}: {1}\n".format(out_dir, exc))
        return 1

    dest = os.path.join(out_dir, IMAGE_NAME)
    try:
        shutil.copyfile(source, dest)
    except OSError as exc:
        sys.stderr.write("error: cannot copy image to {0}: {1}\n".format(dest, exc))
        return 1

    sys.stdout.write("news-image-20261121: copied {0} -> {1} ({2} bytes)\n".format(
        IMAGE_NAME, dest, os.path.getsize(dest)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
