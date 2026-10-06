# Pandas Analyst Path

**One Colab notebook that takes you from the first `df.head()` to answering real business questions** with pandas,
matplotlib and seaborn, built on Google's public e‑commerce dataset (`bigquery-public-data.thelook_ecommerce`).

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/StanislavSidorovich/pandas-analyst-path/blob/main/Pandas_Analyst_Path.ipynb)

You play a junior analyst at **TheLook**, an online fashion store. Every part is a day in your first weeks: your manager
asks a question, you learn the technique, see a worked example, then solve tasks yourself. The tasks are auto-checked,
and the checker explains *why* an answer is wrong.

| Part | Topic |
|---|---|
| 0 | How the notebook works · the data · SQL → pandas |
| 1 | First look: `head` `info` `describe`, selecting, `value_counts`, sorting |
| 2 | Filtering: boolean masks, `isin`, `between`, `loc` / `iloc` |
| 3 | New columns: `np.where`, `np.select`, `map`, `cut` / `qcut`, `.str` |
| 4 | Dates: `to_datetime`, `.dt`, durations, date ranges |
| 5 | Cleaning a messy CSV: missing values, duplicates, types, outliers (IQR) |
| 6 | Joining: `merge`, anti-join, row explosion, `concat` |
| 7 | `groupby`, named aggregation, `transform`, `pivot_table`, `crosstab` → category scorecard |
| 8 | Charts: matplotlib anatomy, seaborn hist / box / bar / scatter / heatmap / line |
| 9 | KPIs over time: MoM, YoY, rolling, YTD |
| 10 | Customer analytics: Pareto, cohorts & retention, RFM, churn, funnel |
| 11 | Final case: quarterly business review + findings memo |
| 12 | Bonus for Data Mining: correlation, one-hot, scaling, k-means segmentation |
| A | Exam drill, cheat sheet, error decoder, glossary EN→RU |

**137 auto-checked tasks.** When stuck: `hint("7.2")` → `compare("7.2")` → `solution("7.2")`.

## How to use it (laptop, tablet or phone)

1. Click **Open in Colab** above, then **File → Save a copy in Drive**.
2. From then on open *your copy* (Colab → Recent, or Google Drive) on any device. Your code and ✅ outputs are saved there.
3. Run the hidden **⚙️ Setup** cell, then the **▶ Part setup** cell of the part you're on.

No Google login is needed for the data: a frozen snapshot (~10 MB, `data/*.parquet`) downloads from this repo.
To use the live BigQuery data instead, set `DATA_SOURCE = "bigquery"` and your `PROJECT_ID` in the Setup cell
(the free BigQuery sandbox works).

## Repository layout

```
Pandas_Analyst_Path.ipynb   the notebook (generated, don't edit by hand)
data/                       snapshot of thelook_ecommerce (through 2026-09-30) + the messy CRM CSV for Part 5
tools/
  extract_snapshot.py       BigQuery → data/*.parquet (the same SQL the notebook uses in bigquery mode)
  make_crm.py               generates the deliberately messy CSV
  content_a/b/c.py          lesson content, tasks, hints, reference solutions
  engine.py                 the checker (inlined into the hidden Setup cell)
  book.py, build_notebook.py  build the notebook
  test_notebook.py          runs the solutions version (every check must pass) and the blank version
```

Rebuild after editing content: `python tools/build_notebook.py && python tools/test_notebook.py`

## Data

`bigquery-public-data.thelook_ecommerce` is a synthetic e-commerce dataset published by Google in the BigQuery public
datasets program. The snapshot keeps only non-personal columns (no names, emails or addresses).

---

### Кратко по-русски
Один ноутбук для Colab: от основ pandas до бизнес-задач аналитика (KPI, когорты, RFM, отток, воронка) и подготовки
к экзамену по Data Mining. Открыть по кнопке → «Сохранить копию на Диске» → дальше работать в своей копии, в том числе
с телефона или планшета. Данные грузятся без входа в Google. Для каждого задания есть проверка `check()`,
шпаргалка к заданию `cheat()` (и поиск: `cheat("merge")`; она же [отдельной страницей](https://stanislavsidorovich.github.io/pandas-analyst-path/cheatsheet.html)), подсказки `hint()`, сравнение `compare()` и решение `solution()`. Глоссарий EN→RU в конце ноутбука.
