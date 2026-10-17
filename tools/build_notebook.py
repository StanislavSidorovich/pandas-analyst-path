"""Build Pandas_Analyst_Path.ipynb (student version) and build/..._SOLUTIONS.ipynb (for testing).

    python tools/build_notebook.py
"""
import inspect
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import extract_snapshot                                   # noqa: E402
from book import Book, _src                              # noqa: E402
import content_a, content_b, content_c                   # noqa: E402

REPO = "StanislavSidorovich/pandas-analyst-path"
NB_NAME = "Pandas_Analyst_Path.ipynb"
COLAB_URL = f"https://colab.research.google.com/github/{REPO}/blob/main/{NB_NAME}"
# Git tag the Setup cell loads tools/engine.py and data/tasks.payload from. A saved copy of the
# notebook keeps working after later changes because it always fetches the files of its own tag.
# After changing content or the engine: bump this, rebuild, commit, then `git tag <ASSET_REF>` and push the tag.
ASSET_REF = "nb-v1"
PAYLOAD_PATH = "data/tasks.payload"

SETUP_HEAD = '''# @title ⚙️ Setup: run this cell first (≈15 s). The code is hidden; double-click here to see it.
DATA_SOURCE = "github"  # @param ["github", "bigquery"]
PROJECT_ID = "my-project-2026-484105"  # @param {{type:"string"}}
# github   = frozen snapshot, no login, the same numbers every time (recommended)
# bigquery = live public data via your Google Cloud project, Colab asks you to sign in

import os, warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)
pd.set_option("display.max_columns", 30)
pd.set_option("display.width", 160)
sns.set_theme(style="whitegrid")

_REPO_RAW = "https://raw.githubusercontent.com/{repo}/main/data/"
_TABLES = ["users", "products", "orders", "order_items", "sessions"]
D = "bigquery-public-data.thelook_ecommerce"

{queries_src}

{normalize_src}

def _load():
    if all(os.path.exists(f"data/{{t}}.parquet") for t in _TABLES):
        return "local data/ folder", {{t: pd.read_parquet(f"data/{{t}}.parquet") for t in _TABLES}}
    if DATA_SOURCE == "bigquery":
        from google.colab import auth
        auth.authenticate_user()
        from google.cloud import bigquery
        client = bigquery.Client(project=PROJECT_ID)
        cutoff = pd.Timestamp.today().to_period("M").start_time.strftime("%Y-%m-%d")
        data = {{t: normalize(client.query(q).to_dataframe()) for t, q in queries(cutoff).items()}}
        return f"BigQuery live data (before {{cutoff}})", data
    return "GitHub snapshot", {{t: pd.read_parquet(_REPO_RAW + f"{{t}}.parquet") for t in _TABLES}}

_source, _BASE = _load()
TODAY = (_BASE["orders"]["created_at"].max().to_period("M") + 1).to_timestamp()   # first day after the data
CRM_PATH = "crm_signups_export.csv"

# Tasks and the checker live in the repo, pinned to this notebook's version (tag {ref}).
_ASSETS = "https://raw.githubusercontent.com/{repo}/{ref}/"
def _asset(path):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return f.read()
    import urllib.request
    with urllib.request.urlopen(_ASSETS + path) as r:
        return r.read().decode("utf-8")
_PAYLOAD = _asset("{payload_path}")
exec(compile(_asset("tools/engine.py"), "engine.py", "exec"))
'''

SETUP_TAIL = '''
with open(CRM_PATH, "w", encoding="utf-8") as _f:
    _f.write(_P["crm"])
users, products, orders, order_items, sessions = fresh_data()
print(f"✅ Setup done · data: {_source} · TODAY = {TODAY.date()} · pandas {pd.__version__}")
for _t in _TABLES:
    print(f"   {_t:12s} {len(_BASE[_t]):>9,} rows")
print("Helpers: check('1.3') · then, for the task you ran or checked last: cheat() · hint() · compare() · solution() · show_me() · data() = map of the tables · progress() · reset_data()")
'''


def build():
    b = Book()
    content_a.intro(b, COLAB_URL)
    content_a.setup_placeholder(b)
    b.part("Part 0", "Start here: your first check", """
        users, products, orders, order_items, sessions = fresh_data()
    """)
    content_a.meet_data(b)
    b.md("""
    ### Try the checker once (this is how every task works)
    1. Run the `check("0.1")` cell below **before** writing anything. You'll see ❌. That's expected: `n_users` doesn't exist yet.
    2. Run the ready-made `hint()` cell under it. Run it **again** for a stronger hint.
       `cheat()`, `hint()`, `compare()` and `solution()` refer to **the task you ran or checked last**, so you never type task numbers.
       Later tasks have no ready-made hint cell: add one with **+ Code** (see *Colab basics*) and type `hint()`.
    3. Write your code in the `# Task 0.1` cell, **run it** (Shift+Enter), then run `check("0.1")` again → ✅.

    ### If something looks wrong
    | What you see | Usually means | Fix |
    |---|---|---|
    | ❌ "not yet", but the code looks right | `check` was run **before** the solution cell (compare the `[N]` numbers: the larger one ran later) | run the solution cell, then `check` again |
    | `hint()` talks about another task | you are looking at an **old output** (Colab keeps it), or the cell's first line is not `# Task X.Y` | re-run `hint()` in a new cell, or name the task: `hint("2.11")` |
    | `NameError` (e.g. `products` not defined) | the Colab runtime was reset | re-run ⚙️ Setup, then the "▶ Part N setup" cell |
    | table looks changed after experiments | you modified it in place | re-run the "▶ Part N setup" cell or `reset_data()` |

    Rules: keep the `# Task X.Y` first line · order is solution → `check` → `hint()` · run top to bottom.
    """)
    b.task("0.1", "How many customers?", """
        Store the number of rows of `users` in a variable called `n_users`.
        """, "n_users", "n_users = len(users)",
        ["`len(df)` gives the number of rows.", "`n_users = len(users)`"], level=1,
        takeaway="That's the whole loop: write → run → check → (hint) → fix. Now go to Part 1.")
    b.code('hint()   # ← run me after the ❌ above. Run me again for a stronger hint.')
    for part in (content_a.part1, content_a.part2, content_a.part3, content_a.part4,
                 content_b.part5, content_b.part6, content_b.part7, content_b.part8,
                 content_c.part9, content_c.part10, content_c.part11, content_c.part12, content_c.appendix):
        part(b)

    with open(os.path.join(ROOT, "data", "crm_signups_export.csv"), encoding="utf-8") as f:
        crm = f.read().replace("\r\n", "\n")
    b.crm = crm
    payload_raw = {"tasks": b.tasks, "parts": b.parts, "sections": b.sections, "data_md": b.data_md, "crm": crm}
    import base64, zlib
    payload = base64.b64encode(zlib.compress(json.dumps(payload_raw, ensure_ascii=False).encode(), 9)).decode()

    with open(os.path.join(ROOT, PAYLOAD_PATH), "w", encoding="utf-8", newline="\n") as f:
        f.write(payload)
    setup = (SETUP_HEAD.format(repo=REPO, ref=ASSET_REF, payload_path=PAYLOAD_PATH,
                               queries_src=inspect.getsource(extract_snapshot.queries).strip(),
                               normalize_src=inspect.getsource(extract_snapshot.normalize).strip())
             + SETUP_TAIL)
    for c in b.cells:
        if c["cell_type"] == "code" and c["source"] and c["source"][0].startswith("# SETUP_PLACEHOLDER"):
            c["source"] = _src(setup)
            c["metadata"] = {"cellView": "form", "id": "setup"}
    return b


if __name__ == "__main__":
    b = build()
    import build_cheatsheet
    os.makedirs(os.path.join(ROOT, "docs"), exist_ok=True)
    with open(os.path.join(ROOT, "docs", "cheatsheet.html"), "w", encoding="utf-8", newline="\n") as f:
        f.write(build_cheatsheet.build_page(b.sections, b.part_titles))
    os.makedirs(os.path.join(ROOT, "build"), exist_ok=True)
    for path, sol in ((os.path.join(ROOT, NB_NAME), False),
                      (os.path.join(ROOT, "build", NB_NAME.replace(".ipynb", "_SOLUTIONS.ipynb")), True)):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(b.notebook(with_solutions=sol), f, ensure_ascii=False, indent=1)
    n_code = sum(c["cell_type"] == "code" for c in b.cells)
    print(f"{len(b.tasks)} tasks · {len(b.cells)} cells ({n_code} code) · parts: {list(b.parts)}")
