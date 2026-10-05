"""Execute the SOLUTIONS notebook (every check must print ✅) and the STUDENT notebook (must run without errors).

    python tools/test_notebook.py [solutions|student|both]
"""
import json
import os
import sys
import time

import nbformat
from nbclient import NotebookClient

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def run(path, extra_cells=()):
    nb = nbformat.read(path, as_version=4)
    for src in extra_cells:
        nb.cells.append(nbformat.v4.new_code_cell(src))
    t = time.time()
    client = NotebookClient(nb, timeout=900, kernel_name="python3", allow_errors=True,
                            resources={"metadata": {"path": ROOT}})
    client.execute()
    print(f"executed {os.path.basename(path)} in {time.time() - t:.0f}s")
    return nb


def text_of(cell):
    out = []
    for o in cell.get("outputs", []):
        if o.get("output_type") == "stream":
            out.append(o.get("text", ""))
        elif o.get("output_type") == "error":
            out.append(f"ERROR {o.get('ename')}: {o.get('evalue')}")
        elif "data" in o and "text/plain" in o["data"]:
            out.append(o["data"]["text/plain"])
    return "".join(out)


def check_solutions():
    nb = run(os.path.join(ROOT, "build", "Pandas_Analyst_Path_SOLUTIONS.ipynb"),
             extra_cells=["print('SELFTEST', _selftest())"])
    problems = 0
    for i, c in enumerate(nb.cells):
        if c.cell_type != "code":
            continue
        txt = text_of(c)
        src = c.source.strip()
        if "ERROR" in txt or (src.startswith("check(") and "✅" not in txt) or "Traceback" in txt:
            problems += 1
            print(f"--- cell {i}: {src[:90]!r}\n{txt[:900]}")
        if src.startswith("print('SELFTEST'"):
            print(txt)
        if "Setup done" in txt:
            print(txt)
    print("PROBLEMS:", problems)


def check_student():
    nb = run(os.path.join(ROOT, "Pandas_Analyst_Path.ipynb"))
    problems = 0
    for i, c in enumerate(nb.cells):
        if c.cell_type != "code":
            continue
        txt = text_of(c)
        if "ERROR" in txt and "Task" not in c.source[:20]:
            problems += 1
            print(f"--- cell {i}: {c.source[:90]!r}\n{txt[:600]}")
    print("STUDENT PROBLEMS:", problems)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "both"
    if mode in ("solutions", "both"):
        check_solutions()
    if mode in ("student", "both"):
        check_student()
