"""Check docs/family against its MANIFEST.json (the Quaera family kit copied from quaera/family/).

Run from the repository root:  python scripts/check_family.py
Exit code 0: every file matches the manifest and there are no extra files. 1: otherwise.

The hash rule is the one family-sync uses: text files (.css .js .json .svg .txt .html .ts)
are hashed with CRLF turned into LF, so a Windows checkout with autocrlf still matches.
"""
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAMILY = os.path.join(ROOT, "docs", "family")
TEXT = {".css", ".js", ".json", ".svg", ".txt", ".html", ".ts"}


def file_hash(path):
    with open(path, "rb") as f:
        data = f.read()
    if os.path.splitext(path)[1] in TEXT:
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def main():
    with open(os.path.join(FAMILY, "MANIFEST.json"), encoding="utf-8") as f:
        expected = json.load(f)["files"]

    problems = []
    for rel, digest in sorted(expected.items()):
        path = os.path.join(FAMILY, *rel.split("/"))
        if not os.path.isfile(path):
            problems.append(f"missing  {rel}")
        elif file_hash(path) != digest:
            problems.append(f"changed  {rel}")

    actual = set()
    for dirpath, _, files in os.walk(FAMILY):
        for name in files:
            rel = os.path.relpath(os.path.join(dirpath, name), FAMILY).replace(os.sep, "/")
            if rel != "MANIFEST.json":
                actual.add(rel)
    for rel in sorted(actual - set(expected)):
        problems.append(f"extra    {rel}")

    if problems:
        print("docs/family does not match MANIFEST.json:")
        print("\n".join("  " + p for p in problems))
        print("Fix: node quaera/scripts/family-sync.mjs --only pandas (run from the 22. Quaera folder)")
        return 1
    print(f"docs/family matches MANIFEST.json ({len(expected)} files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
