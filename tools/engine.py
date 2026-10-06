# ---------------------------------------------------------------------------
# Checker engine. Inlined into the notebook's hidden Setup cell by build_notebook.py.
# Expects these globals to exist before it runs: _PAYLOAD (base64 zlib JSON), _BASE (dict of
# pristine DataFrames), TODAY, CRM_PATH, pd, np, plt, sns.
# Public helpers: check(id), hint(id), solution(id), compare(id), show_me(id), cheat(), progress()
# ---------------------------------------------------------------------------
import io as _io
from contextlib import redirect_stdout as _redirect
import base64 as _b64, json as _json, zlib as _zlib, math as _math, copy as _copy, traceback as _tb
from IPython.display import display as _display, Markdown as _Markdown

_P = _json.loads(_zlib.decompress(_b64.b64decode(_PAYLOAD)).decode("utf-8"))
_TASKS, _PARTS, _SECTIONS = _P["tasks"], _P["parts"], _P["sections"]
_PASSED, _HINT_LEVEL, _REF_VALUES, _NS_CACHE = set(), {}, {}, {}
_LAST = {"id": None, "via": None}   # task of the last run task cell or check(): hint()/compare()/solution() default to it


def _track_task_cell(result):
    """After every cell: if it was a '# Task X.Y' cell, remember that task (check() records its own)."""
    import re
    src = getattr(getattr(result, "info", None), "raw_cell", "") or ""
    m = re.match(r"\s*#\s*Task\s+([A-Za-z0-9.]+)", src)
    if m and m.group(1) in _TASKS:
        _LAST["id"], _LAST["via"] = m.group(1), "cell"


try:
    _ev = get_ipython().events
    for _cb in list(_ev.callbacks.get("post_run_cell", [])):   # Setup may be re-run: keep one hook
        if getattr(_cb, "__name__", "") == "_track_task_cell":
            _ev.unregister("post_run_cell", _cb)
    _ev.register("post_run_cell", _track_task_cell)
except Exception:
    pass


def fresh_data():
    """Return untouched copies of the five tables: users, products, orders, order_items, sessions."""
    return tuple(_BASE[t].copy() for t in ("users", "products", "orders", "order_items", "sessions"))


# ----------------------------------------------------------------- reference values
def _new_ns():
    return {"pd": pd, "np": np, "plt": plt, "sns": sns, "TODAY": TODAY, "CRM_PATH": CRM_PATH,
            "fresh_data": fresh_data, "__builtins__": __builtins__}


def _run_part_until(part, stop_id, run_plot=False):
    """Execute the part's canonical blocks (setup, examples, solutions) up to and including stop_id."""
    blocks = _PARTS[part]
    st = _NS_CACHE.get(part)
    stop_pos = next(i for i, b in enumerate(blocks) if b.get("id") == stop_id)
    if st is None or st["pos"] > stop_pos:
        st = {"ns": _new_ns(), "pos": 0}
        _NS_CACHE[part] = st
        if len(_NS_CACHE) > 3:                      # keep memory small in Colab
            _NS_CACHE.pop(next(k for k in _NS_CACHE if k != part))
    ns = st["ns"]
    figs_before = set(plt.get_fignums())
    while st["pos"] <= stop_pos:
        b = blocks[st["pos"]]
        is_target = b.get("id") == stop_id
        if b["kind"] == "task" and b.get("plot") and not (is_target and run_plot):
            st["pos"] += 1
            continue
        with warnings.catch_warnings(), _redirect(_io.StringIO()):
            warnings.simplefilter("ignore")
            exec(b["code"], ns)
        if b["kind"] == "task" and not b.get("plot"):
            t = _TASKS[b["id"]]
            try:
                _REF_VALUES[b["id"]] = _snapshot(eval(t["var"], ns))
            except Exception:
                pass
        st["pos"] += 1
    if not run_plot:                                    # never leave stray reference figures around
        for num in set(plt.get_fignums()) - figs_before:
            plt.close(num)
    return ns


def _clone_ns(ns):
    return {k: (v.copy() if isinstance(v, (pd.DataFrame, pd.Series)) else v) for k, v in ns.items()}


def _snapshot(v):
    if isinstance(v, (pd.DataFrame, pd.Series, pd.Index)):
        return v.copy()
    try:
        return _copy.deepcopy(v)
    except Exception:
        return v


def _ref(tid):
    if tid not in _REF_VALUES:
        _run_part_until(_TASKS[tid]["part"], tid)
    return _REF_VALUES[tid]


# ----------------------------------------------------------------- comparison helpers
def _is_num(x):
    return isinstance(x, (int, float, np.integer, np.floating)) and not isinstance(x, (bool, np.bool_))


def _kind(x):
    if isinstance(x, pd.DataFrame):
        return f"a DataFrame with {x.shape[0]:,} rows × {x.shape[1]} columns"
    if isinstance(x, pd.Series):
        return f"a Series with {len(x):,} values"
    if isinstance(x, (pd.Index, np.ndarray, list, tuple, set)):
        return f"a {type(x).__name__} with {len(x)} items"
    return f"a {type(x).__name__} ({x!r})" if not hasattr(x, "shape") else type(x).__name__


def _fmt(v):
    if _is_num(v):
        return f"{v:,.4f}".rstrip("0").rstrip(".") if isinstance(v, (float, np.floating)) else f"{v:,}"
    return repr(v)


def _vals_equal(u, r, rtol, atol):
    """Element-wise equality of two 1-D sequences. Returns (ok, first_bad_position, note)."""
    u = pd.Series(list(u) if not isinstance(u, pd.Series) else u.to_numpy(), dtype=object)
    r = pd.Series(list(r) if not isinstance(r, pd.Series) else r.to_numpy(), dtype=object)
    un, rn = u.isna().to_numpy(), r.isna().to_numpy()
    r_numeric = all(_is_num(x) or isinstance(x, (bool, np.bool_)) for x in r[~rn]) and not all(
        isinstance(x, (bool, np.bool_)) for x in r[~rn]) or (
        all(isinstance(x, (bool, np.bool_)) for x in r[~rn]) and any(_is_num(x) for x in u[~un]))
    if r_numeric and (~rn).any():
        uu = pd.to_numeric(u, errors="coerce")
        if (uu.isna().to_numpy() & ~un).any():
            return False, int(np.argmax(uu.isna().to_numpy() & ~un)), "text where numbers were expected"
        a, b = uu.to_numpy(float), pd.to_numeric(r).to_numpy(float)
        ok = np.isclose(a, b, rtol=rtol, atol=atol, equal_nan=True)
    else:
        ok = np.array([(nu and nr) or (not nu and not nr and str(x) == str(y))
                       for x, y, nu, nr in zip(u.to_numpy(), r.to_numpy(), un, rn)])
    if ok.all():
        return True, None, ""
    return False, int(np.argmax(~ok)), ""


def _cmp_number(u, r, o):
    if isinstance(u, (pd.Series, pd.DataFrame)):
        if u.size == 1:
            return False, ("You have a single value *inside* a " + type(u).__name__ +
                           ". Pull the number out, e.g. with `.iloc[0]` or `.item()`.")
        return False, f"Expected a single number, but you have {_kind(u)}."
    if isinstance(u, (bool, np.bool_)) or not _is_num(u):
        try:
            u = float(u)
        except Exception:
            return False, f"Expected a number, but you have {_kind(u)}."
    rtol, atol = o.get("rtol", 1e-4), o.get("atol", 1e-6)
    if _math.isclose(float(u), float(r), rel_tol=rtol, abs_tol=atol):
        return True, ""
    if 0 < abs(r) <= 1 and _math.isclose(float(u), float(r) * 100, rel_tol=1e-3):
        return False, "Looks like a percentage. This task wants a fraction between 0 and 1 (no ×100)."
    if r != 0:
        diff = (float(u) - float(r)) / abs(float(r))
        return False, f"Your value {_fmt(u)} is {'higher' if diff > 0 else 'lower'} than expected by {abs(diff):.1%}."
    return False, f"Your value {_fmt(u)} is not the expected one."


def _cmp_list(u, r, o):
    if isinstance(u, pd.Series) and not isinstance(r, pd.Series):
        u = u.index if o.get("list_from_index") else u.tolist()
    if not isinstance(u, (list, tuple, set, pd.Index, np.ndarray)):
        return False, f"Expected a list of values, but you have {_kind(u)}."
    ul, rl = list(u), list(r)
    if len(ul) != len(rl):
        return False, f"Your list has {len(ul)} items, expected {len(rl)}."
    if o.get("ordered", True) and not isinstance(r, set):
        ok, pos, _ = _vals_equal(ul, rl, 1e-4, 1e-6)
        if ok:
            return True, ""
        if sorted(map(str, ul)) == sorted(map(str, rl)):
            return False, "Right items, wrong order. Check the sorting direction."
        return False, f"Item #{pos + 1} is {ul[pos]!r} — not what was expected."
    if set(map(str, ul)) == set(map(str, rl)):
        return True, ""
    return False, f"Unexpected items: {sorted(set(map(str, ul)) - set(map(str, rl)))[:5]}"


def _align(u, r, o, what="rows"):
    """Return (u_aligned, note) with u's rows in r's order, or (None, message) on failure."""
    ui, ri = [str(x) for x in u.index], [str(x) for x in r.index]
    if o.get("ignore_index"):
        return u, ""
    if ui == ri:
        return u, ""
    if sorted(ui) == sorted(ri):
        if o.get("ordered"):
            return "ORDER", ""
        pos = {k: i for i, k in enumerate(ui)}
        return u.iloc[[pos[k] for k in ri]], ""
    if isinstance(u.index, pd.RangeIndex) and len(u) == len(r):
        return u, "(compared row by row: your index was reset, which is fine)"
    missing = [k for k in ri if k not in set(ui)][:4]
    extra = [k for k in ui if k not in set(ri)][:4]
    msg = "The index labels differ from the expected ones."
    if missing:
        msg += f" Expected but missing: {missing}."
    if extra:
        msg += f" Unexpected: {extra}."
    return None, msg


def _cmp_series(u, r, o):
    if isinstance(u, pd.DataFrame):
        if u.shape[1] == 1:
            return False, ("You have a one-column DataFrame, but a Series is expected. "
                           "Use single brackets `df['col']` (double brackets `df[['col']]` give a DataFrame).")
        return False, f"Expected a Series (one column), but you have {_kind(u)}."
    if not isinstance(u, pd.Series):
        return False, f"Expected a pandas Series, but you have {_kind(u)}."
    if len(u) != len(r):
        return False, f"Your Series has {len(u):,} values, expected {len(r):,}."
    ua, note = _align(u, r, o)
    if isinstance(ua, str):                                     # same labels, other order
        ok, _, _ = _vals_equal(u, r, o.get("rtol", 1e-4), o.get("atol", 1e-6))
        if ok:                                                  # ties: same value sequence
            return True, ""
        pos_ = {k: i for i, k in enumerate(str(x) for x in u.index)}
        by_label = u.iloc[[pos_[str(k)] for k in r.index]]
        ok, pos, why = _vals_equal(by_label, r, o.get("rtol", 1e-4), o.get("atol", 1e-6))
        if not ok:
            return False, (f"Value at {r.index[pos]!r}: yours {_fmt(by_label.iloc[pos])}, expected "
                           f"{_fmt(r.iloc[pos])}. {why}").strip()
        return False, "Right values, wrong order. Did you sort as asked (e.g. `ascending=False`)?"
    if ua is None:
        return False, note
    ok, pos, why = _vals_equal(ua, r, o.get("rtol", 1e-4), o.get("atol", 1e-6))
    if ok:
        return True, note
    lab = r.index[pos]
    return False, (f"First difference at index {lab!r}: yours {_fmt(ua.iloc[pos])}, expected "
                   f"{_fmt(r.iloc[pos])}. {why}").strip()


def _cmp_frame(u, r, o):
    if isinstance(u, pd.Series):
        return False, ("Expected a table (DataFrame), but you have a Series. "
                       "Double brackets `df[['a','b']]`, `.reset_index()` or `.to_frame()` give a DataFrame.")
    if not isinstance(u, pd.DataFrame):
        return False, f"Expected a DataFrame, but you have {_kind(u)}."
    names = [n for n in r.index.names if n is not None]
    if names and all(n in u.columns for n in names) and not all(n in u.index.names for n in names):
        u = u.set_index(names)
    if (isinstance(r.index, pd.RangeIndex) and not isinstance(u.index, pd.RangeIndex)
            and any(n in r.columns for n in u.index.names if n)):
        u = u.reset_index()
    cols = o.get("cols") or list(r.columns)
    ucols = [str(c) for c in u.columns]
    missing = [c for c in cols if str(c) not in ucols]
    if missing:
        return False, f"Missing column(s): {missing}. Your columns: {ucols[:12]}"
    extra = [c for c in ucols if c not in [str(x) for x in r.columns]]
    if extra and not o.get("allow_extra") and not o.get("cols"):
        return False, f"Unexpected extra column(s): {extra}. Keep only the columns the task asks for."
    if len(u) != len(r):
        return False, f"Your table has {len(u):,} rows, expected {len(r):,}."
    u = u.rename(columns=str)
    rr = r.rename(columns=str)
    ua, note = _align(u, rr, o)
    if isinstance(ua, str):                                  # same row labels, different order
        pos_ = {k: i for i, k in enumerate(str(x) for x in u.index)}
        by_label = u.iloc[[pos_[str(k)] for k in rr.index]]
        for c in cols:
            ok, pos, why = _vals_equal(by_label[str(c)], rr[str(c)], o.get("rtol", 1e-4), o.get("atol", 1e-6))
            if not ok:
                return False, (f"Column '{c}' differs. First difference in row {rr.index[pos]!r}: yours "
                               f"{_fmt(by_label[str(c)].iloc[pos])}, expected {_fmt(rr[str(c)].iloc[pos])}. {why}").strip()
        for c in cols:                                       # values right; is the order acceptable (ties)?
            ok, _, _ = _vals_equal(u[str(c)], rr[str(c)], o.get("rtol", 1e-4), o.get("atol", 1e-6))
            if not ok:
                return False, "Right rows, wrong order. Check your sort (column and direction)."
        return True, ""
    if ua is None:
        return False, note
    for c in cols:
        ok, pos, why = _vals_equal(ua[str(c)], rr[str(c)], o.get("rtol", 1e-4), o.get("atol", 1e-6))
        if not ok:
            return False, (f"Column '{c}' differs. First difference in row {rr.index[pos]!r}: "
                           f"yours {_fmt(ua[str(c)].iloc[pos])}, expected {_fmt(rr[str(c)].iloc[pos])}. {why}").strip()
    return True, note


def _compare(u, r, o):
    try:
        if isinstance(r, pd.DataFrame):
            return _cmp_frame(u, r, o)
        if isinstance(r, pd.Series):
            return _cmp_series(u, r, o)
        if isinstance(r, (list, tuple, set, pd.Index, np.ndarray)):
            return _cmp_list(u, r, o)
        if isinstance(r, (bool, np.bool_)):
            return (bool(u) == bool(r) and isinstance(u, (bool, np.bool_))), "Expected True or False."
        if _is_num(r):
            return _cmp_number(u, r, o)
        if isinstance(r, str):
            if not isinstance(u, str):
                return False, f"Expected text (a string), but you have {_kind(u)}."
            return (u.strip().lower() == r.strip().lower()), f"Your answer {u!r} is not the expected one."
        return (str(u) == str(r)), f"Your answer {u!r} is not the expected one."
    except Exception as e:                                              # never crash the learner's cell
        return False, f"Could not compare ({type(e).__name__}: {e})."


# ----------------------------------------------------------------- plot checks
def _check_plot(t, u):
    spec = t["plot"]
    if hasattr(u, "ax") and not hasattr(u, "get_title"):                # seaborn FacetGrid
        u = u.ax
    axs = list(np.ravel(u)) if isinstance(u, (np.ndarray, list, tuple)) else [u]
    if not axs or not all(hasattr(a, "get_title") for a in axs):
        return False, ("`{}` should be a matplotlib Axes. Create it with `fig, ax = plt.subplots()` and draw "
                       "with `ax=ax` (or `ax = sns.histplot(...)`).").format(t["var"])
    probs = []
    if "n_axes" in spec and len(axs) != spec["n_axes"]:
        probs.append(f"expected {spec['n_axes']} charts, found {len(axs)}")
    for k, ax in enumerate(axs):
        tag = f"chart {k + 1}: " if len(axs) > 1 else ""
        n_p = len([p for p in ax.patches if not hasattr(p, "get_height") or p.get_height() != 0 or p.get_width() != 0])
        if "patches" in spec and n_p != spec["patches"]:
            probs.append(f"{tag}expected {spec['patches']} bars, found {n_p}")
        if "min_patches" in spec and n_p < spec["min_patches"]:
            probs.append(f"{tag}expected at least {spec['min_patches']} bars, found {n_p}")
        if spec.get("lines") and len(ax.lines) < 1:
            probs.append(f"{tag}no line found — use a line chart")
        if spec.get("points"):
            n_pts = sum(len(c.get_offsets()) for c in ax.collections if hasattr(c, "get_offsets"))
            if n_pts < spec["points"]:
                probs.append(f"{tag}expected a scatter with ≥{spec['points']:,} points, found {n_pts:,}")
        if spec.get("heatmap") and not any(type(c).__name__ == "QuadMesh" for c in ax.collections):
            probs.append(f"{tag}no heatmap found — use sns.heatmap(...)")
        if spec.get("annot") and len(ax.texts) == 0:
            probs.append(f"{tag}numbers are not written in the cells — add annot=True")
        if spec.get("legend") and ax.get_legend() is None:
            probs.append(f"{tag}no legend — add hue=... (seaborn) or ax.legend()")
        if spec.get("any_content") and not (ax.patches or ax.lines or ax.collections):
            probs.append(f"{tag}the chart is empty")
        if spec.get("title", True) and not ax.get_title():
            probs.append(f"{tag}add a title: ax.set_title('...')")
        if spec.get("xlabel") and not ax.get_xlabel():
            probs.append(f"{tag}label the x axis: ax.set_xlabel('...')")
        if spec.get("ylabel") and not ax.get_ylabel():
            probs.append(f"{tag}label the y axis: ax.set_ylabel('...')")
        if "xticks" in spec:
            labs = {tl.get_text() for tl in ax.get_xticklabels()}
            if not set(spec["xticks"]) <= labs:
                probs.append(f"{tag}x axis should show {spec['xticks']}, found {sorted(labs)[:6]}")
        if spec.get("biggest_on_top"):
            bars = [p for p in ax.patches if hasattr(p, "get_width") and p.get_width() > 0]
            if bars:
                key = (lambda p: p.get_y()) if ax.yaxis_inverted() else (lambda p: -p.get_y())
                top = sorted(bars, key=key)[0]
                if top.get_width() < max(p.get_width() for p in bars) - 1e-9:
                    probs.append(f"{tag}the longest bar should be at the TOP (sort ascending before .barh, "
                                 "or use seaborn with the order you want)")
    if probs:
        return False, "; ".join(probs) + "."
    return True, ""


# ----------------------------------------------------------------- public helpers
def check(task_id):
    """Check your answer for a task, e.g. check('3.2')."""
    t = _get(task_id)
    if t is None:
        return
    _LAST["id"], _LAST["via"] = t["id"], "check"
    g = globals()
    try:
        u = eval(t["var"], g)
    except NameError as e:
        missing = getattr(e, "name", None) or str(e)
        if missing and missing != t["var"] and not t["var"].startswith(missing + "("):
            print(f"❌ `{missing}` doesn't exist in this session. Run the ▶ {t['part']} setup cell "
                  f"(and the tasks before this one), then your solution, then check again.")
        else:
            print(f"❌ I can't find `{t['var']}` yet.\n   1) Did you RUN your solution cell (▶ or Shift+Enter)?  "
                  f"2) Is it named exactly `{t['var']}`?")
        return
    except KeyError as e:
        print(f"❌ `{t['var']}` → column {e} not found. Did you create that column?")
        return
    except Exception as e:
        print(f"❌ Evaluating `{t['var']}` raised {type(e).__name__}: {e}")
        return
    if t.get("plot"):
        ok, msg = _check_plot(t, u)
    else:
        try:
            r = _ref(t["id"])
        except Exception as e:
            print(f"⚠️ The checker itself failed ({type(e).__name__}: {e}). Re-run the Setup cell and the "
                  f"Part setup cell. If it persists, it's a bug in the notebook, not in your code.")
            return
        if t.get("custom"):
            ns = {"u": u, "r": r, "pd": pd, "np": np, "g": g}
            try:
                exec(t["custom"], ns)
                ok, msg = ns["ok"], ns.get("msg", "")
            except Exception as e:
                ok, msg = False, f"Could not check ({type(e).__name__}: {e})."
        else:
            ok, msg = _compare(u, r, t.get("cmp", {}))
    if ok:
        _PASSED.add(t["id"])
        tail = f"  {msg}" if msg else ""
        print(f"✅ Task {t['id']} passed!{tail}")
        if t.get("takeaway"):
            print(f"   💡 {t['takeaway']}")
        return
    print(f"❌ Task {t['id']}: not yet. {msg}")
    for code, tip in t.get("traps", []):                                 # recognise typical mistakes
        try:
            ns = _clone_ns(_run_part_until(t["part"], _prev_block(t["id"])))
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                exec(code, ns)
            trap_val = eval(t["var"], ns)
            if _compare(u, trap_val, t.get("cmp", {}))[0]:
                print(f"   🔎 Typical mistake: {tip}")
                break
        except Exception:
            pass
    if t.get("needs"):
        print(f"   ↪ This task builds on {', '.join(t['needs'])}. Make sure those pass first.")
    print(f"   Stuck? In a new cell (+ Code) run  cheat()  ·  hint()  ·  then compare()  ·  then solution()   (they refer to task {t['id']})")


def _prev_block(tid):
    blocks = _PARTS[_TASKS[tid]["part"]]
    i = next(k for k, b in enumerate(blocks) if b.get("id") == tid)
    return blocks[i - 1]["id"]


def _get(task_id):
    if task_id is None:
        task_id = _LAST["id"]
        if task_id is None:
            print("⚠️ Run your task cell (or its check) first, then hint() knows which task you mean. "
                  "Or name it: hint('1.3').")
            return None
        if _LAST["via"] == "check" and task_id in _PASSED:   # last checked task is done → the learner is stuck on the next one
            ids = list(_TASKS)
            i = ids.index(task_id)
            if i + 1 < len(ids):
                task_id = ids[i + 1]
                print(f"(Task {_LAST['id']} is done, so this is for the next one, {task_id}. "
                      f"Another task? Name it: hint('X.Y').)")
    if not isinstance(task_id, str):
        print(f"⚠️ Put the task id in quotes: check('{task_id}'). Without quotes 3.10 and 3.1 look the same.")
    t = _TASKS.get(str(task_id))
    if t is None:
        print(f"⚠️ Unknown task id {task_id!r}. Task ids look like '3.2' (in quotes).")
    return t


def hint(task_id=None):
    """Show the next hint for a task. Call again for a stronger hint."""
    t = _get(task_id)
    if t is None:
        return
    hints = t.get("hints", [])
    k = _HINT_LEVEL.get(t["id"], 0)
    if k < len(hints):
        print(f"💡 Hint {k + 1}/{len(hints)} for task {t['id']}:\n   {hints[k]}")
        _HINT_LEVEL[t["id"]] = k + 1
        if k + 1 < len(hints):
            print("   (run hint() again for a stronger hint)")
    else:
        print("No more hints. Look at the solution: solution() — then close it and retype it yourself.")


def solution(task_id=None):
    """Print the reference solution. Read it, close it, then retype it from memory."""
    t = _get(task_id)
    if t is None:
        return
    print(f"🔑 One possible solution for task {t['id']} (other correct ways exist):\n")
    print(t["solution"].strip())
    if t.get("why"):
        print(f"\n📖 Why: {t['why']}")
    print("\n✍️  Now retype it yourself in your cell (don't copy-paste) and run check() again.")


def compare(task_id=None, n=5):
    """Show the start of YOUR result next to the EXPECTED one."""
    t = _get(task_id)
    if t is None:
        return
    if t.get("plot"):
        print(f"For charts use show_me('{t['id']}') to see a reference chart.")
        return
    r = _ref(t["id"])
    try:
        u = eval(t["var"], globals())
    except Exception as e:
        u = f"<not available: {type(e).__name__}: {e}>"
    for title, v in (("YOURS", u), ("EXPECTED", r)):
        print(f"── {title}: {_kind(v)}")
        if isinstance(v, (pd.DataFrame, pd.Series)):
            _display(v.head(n))
        else:
            print("  ", v if not isinstance(v, (list, np.ndarray, pd.Index)) else list(v)[:n * 2])


def show_me(task_id=None):
    """Draw the reference chart for a plotting task."""
    t = _get(task_id)
    if t is None:
        return
    _run_part_until(t["part"], t["id"], run_plot=True)
    plt.show()


_CHEAT_URL = "https://stanislavsidorovich.github.io/pandas-analyst-path/cheatsheet.html"


def _cheat_show(sids, note=""):
    md = [note] if note else []
    for sid in sids:
        sec = _SECTIONS[sid]
        md.append(f"#### 📋 {sid} {sec['title']}\n\n{sec['md']}")
    md.append(f"🌐 [The whole cheat sheet as a page]({_CHEAT_URL}) (with search): keep it open on a second screen or phone.")
    _display(_Markdown("\n\n---\n\n".join(md)))


def _cheat_for_task(t):
    sid = t.get("section")
    if sid and _SECTIONS[sid]["md"] and not sid.startswith("A."):
        return [sid], f"*Cheat sheet for task {t['id']}* (section {sid} of the lesson)"
    part = [k for k, v in _SECTIONS.items() if v["part"] == t["part"] and v["md"] and not k.startswith("A.")]
    if part and not sid:                     # a checkpoint mixes the whole part
        return part, f"*Cheat sheet for task {t['id']}*: a checkpoint, so everything from {t['part']}"
    return ["A.2"], f"*Cheat sheet for task {t['id']}*: it mixes several parts, so here is the full cheat sheet"


def _cheat_items(md):
    """Split a cheat block into (table header or None, item): one table row, one bullet or one paragraph each."""
    lines, items, header, buf = md.split("\n"), [], None, []

    def flush():
        if buf:
            items.append((None, " ".join(x.strip() for x in buf)))
            buf.clear()
    for i, line in enumerate(lines):
        s = line.strip().lstrip("- ").strip() if line.strip().startswith("- |") else line.strip()
        if s.startswith("|"):
            flush()
            if i + 1 < len(lines) and lines[i + 1].strip().lstrip("- ").startswith("|--"):
                header = s + "\n" + lines[i + 1].strip().lstrip("- ")
            elif not s.startswith("|--"):
                items.append((header, s))
        elif not s:
            flush()
        elif s.startswith("- ") or s[:2] in ("💡", "⚠️", "📘", "🧩"):
            flush()
            buf.append(s)
        else:
            buf.append(s)
    flush()
    return items


def _cheat_search(word):
    w, out = word.lower(), []
    for sid, sec in _SECTIONS.items():
        hits = [(h, it) for h, it in _cheat_items(sec["md"]) if w in it.lower()]
        if hits:
            block, last = [], object()
            for h, it in hits:
                if h != last:
                    block.append("\n" + h if h else "")
                    last = h
                block.append(it if it.startswith(("|", "- ")) else "- " + it)
            out.append(f"#### 📋 {sid} {sec['title']}\n" + "\n".join(block))
    return out


def cheat(what=None):
    """The 📘 cheat sheet right here: cheat() for the task you ran/checked last, cheat('merge') to search,
    cheat('3.2') for a section, cheat('Part 3') for a whole part, cheat('all') for the full table."""
    if what is None:
        t = _get(None)
        if t is None:
            return
        sids, note = _cheat_for_task(t)
        return _cheat_show(sids, note)
    key = str(what).strip()
    if key.lower() == "all":
        return _cheat_show(["A.2", "A.3"])
    if key in _SECTIONS:
        return _cheat_show([key])
    if key in _TASKS:
        return _cheat_show(*_cheat_for_task(_TASKS[key]))
    part = key if key.lower().startswith("part") else f"Part {key}"
    part = next((p for p in _PARTS if p.lower() == part.lower()), None)
    if part:
        return _cheat_show([k for k, v in _SECTIONS.items() if v["part"] == part and v["md"]])
    found = _cheat_search(key)
    if not found:
        print(f"Nothing about {key!r} in the cheat sheets. Try a shorter word ('merge', 'date', 'NaN'), "
              "or cheat('all') for the full table.")
        return
    _display(_Markdown(f"*Lines mentioning* `{key}`:\n\n" + "\n\n".join(found)))


def progress():
    """How many tasks you have passed in THIS session, per part."""
    rows = {}
    for tid, t in _TASKS.items():
        p = t["part"]
        rows.setdefault(p, [0, 0])
        rows[p][1] += 1
        rows[p][0] += tid in _PASSED
    lines = ["| Part | Passed | |", "|---|---|---|"]
    for p, (a, n) in rows.items():
        bar = "🟩" * a + "⬜" * (n - a)
        lines.append(f"| {p} | {a}/{n} | {bar} |")
    _display(_Markdown("\n".join(lines)))
    print("Progress counts this session only. Saved ✅ outputs in the notebook stay as your record.")


def reset_data():
    """Bring back untouched tables if you accidentally changed users/products/orders/...."""
    g = globals()
    g["users"], g["products"], g["orders"], g["order_items"], g["sessions"] = fresh_data()
    print("✅ users, products, orders, order_items, sessions restored.")


def _selftest():
    """Internal: verify every reference runs and every trap is really different from the answer."""
    bad = []
    for tid, t in _TASKS.items():
        try:
            if t.get("plot"):
                ns = _run_part_until(t["part"], tid, run_plot=True)
                ok, msg = _check_plot(t, eval(t["var"], ns))
                plt.close("all")
                if not ok:
                    bad.append((tid, "plot reference fails its own check: " + msg))
                continue
            r = _ref(tid)
            for code, tip in t.get("traps", []):
                ns = _clone_ns(_run_part_until(t["part"], _prev_block(tid)))
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    exec(code, ns)
                if _compare(eval(t["var"], ns), r, t.get("cmp", {}))[0]:
                    bad.append((tid, "trap equals the answer: " + code))
        except Exception as e:
            bad.append((tid, f"{type(e).__name__}: {e}"))
    return bad
