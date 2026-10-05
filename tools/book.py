"""Tiny framework that turns lesson content into a Colab notebook + hidden checker payload."""
import base64
import json
import textwrap
import zlib

LEVEL = {1: "🟢 warm-up", 2: "🟡 core", 3: "🔴 stretch"}


def _src(text):
    text = textwrap.dedent(text).strip("\n")
    lines = text.split("\n")
    return [l + "\n" for l in lines[:-1]] + [lines[-1]]


class Book:
    def __init__(self):
        self.cells = []
        self.tasks = {}
        self.parts = {}
        self.cur = None

    # ---------------------------------------------------------------- cells
    def md(self, text):
        self.cells.append({"cell_type": "markdown", "metadata": {}, "source": _src(text)})

    def code(self, src, ctx=False, hidden=False, solution_only=False):
        """ctx=True: the code also runs inside the checker (it creates state later tasks rely on)."""
        meta = {"cellView": "form"} if hidden else {}
        cell = {"cell_type": "code", "metadata": meta, "execution_count": None,
                "outputs": [], "source": _src(src)}
        if solution_only:
            cell["_solution_only"] = True
        self.cells.append(cell)
        if ctx:
            self.parts[self.cur].append({"kind": "ex", "code": textwrap.dedent(src).strip()})

    # ---------------------------------------------------------------- structure
    def part(self, key, title, setup):
        self.cur = key
        self.parts[key] = []
        self.md(f"# {key}. {title}")
        setup = textwrap.dedent(setup).strip()
        header = (f"# ▶ {key} setup: run this first whenever you start or come back to this part.\n"
                  f"# It rebuilds everything this part needs, so you can start here in a fresh session.\n")
        self.cells.append({"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
                           "source": _src(header + setup + f'\nprint("✅ {key} ready")')})
        self.parts[key].append({"kind": "setup", "id": f"{key}/setup", "code": setup})

    def task(self, tid, title, prompt, var, solution, hints, level=2, traps=(), cmp=None,
             custom=None, plot=None, takeaway=None, why=None, needs=None, starter=""):
        assert tid not in self.tasks, tid
        solution = textwrap.dedent(solution).strip()
        self.tasks[tid] = {
            "id": tid, "part": self.cur, "title": title, "var": var, "solution": solution,
            "hints": list(hints), "traps": [[textwrap.dedent(c).strip(), m] for c, m in traps], "cmp": cmp or {},
            "custom": textwrap.dedent(custom).strip() if custom else None, "plot": plot,
            "takeaway": takeaway, "why": why, "needs": needs,
        }
        self.parts[self.cur].append({"kind": "task", "id": tid, "code": solution, "plot": bool(plot)})
        self.md(f"#### ✍️ Task {tid} · {LEVEL[level]} · {title}\n\n" + textwrap.dedent(prompt).strip()
                + f"\n\n*Result goes into:* `{var}`")
        starter = textwrap.dedent(starter).strip()
        learner = f"# Task {tid}: your code here\n" + (starter + "\n" if starter else "")
        self.cells.append({"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
                           "source": _src(learner), "_solution": f"# Task {tid}\n" + solution})
        self.cells.append({"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
                           "source": _src(f'check("{tid}")   # stuck? hint("{tid}") · compare("{tid}") · solution("{tid}")')})

    # ---------------------------------------------------------------- output
    def payload(self):
        raw = json.dumps({"tasks": self.tasks, "parts": self.parts}, ensure_ascii=False).encode("utf-8")
        return base64.b64encode(zlib.compress(raw, 9)).decode("ascii")

    def notebook(self, with_solutions=False):
        cells = []
        for c in self.cells:
            c = dict(c)
            if c.pop("_solution_only", False) and not with_solutions:
                continue
            sol = c.pop("_solution", None)
            if with_solutions and sol:
                c["source"] = _src(sol)
            cells.append(c)
        return {
            "nbformat": 4, "nbformat_minor": 0,
            "metadata": {
                "colab": {"provenance": [], "toc_visible": True},
                "kernelspec": {"name": "python3", "display_name": "Python 3"},
                "language_info": {"name": "python"},
            },
            "cells": cells,
        }
