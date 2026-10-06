"""Intro + Parts 1-4."""


def intro(b, colab_url):
    b.md(f"""
    # 🧭 Pandas Analyst Path: from zero to business answers

    **One notebook, one company, one path.** You join **TheLook**, an online fashion store, as a junior data analyst.
    Each part is a day in your first weeks. Your manager **Ana (Head of E‑commerce)** asks questions, and you answer them with
    **pandas**, **matplotlib** and **seaborn** on real-sized data (≈100k customers, ≈175k sold items) from Google BigQuery.

    By the end you can:
    - explore, filter, clean and join tables without looking things up every minute;
    - build KPI tables with `groupby` / `pivot_table` and explain trends (MoM, YoY);
    - draw the right chart for the question;
    - run the classic customer analyses: **Pareto, cohorts/retention, RFM, churn, funnel**;
    - write a short findings memo, the part of the job that gets you hired;
    - (bonus) prepare data for **Data Mining** exams: correlation, encoding, scaling, k‑means.

    [Open in Colab]({colab_url})
    """)
    b.md("""
    ## How this notebook works (read once, 3 minutes)

    Every section has the same rhythm:

    | Block | What you do |
    |---|---|
    | 🎯 **Why** | the business reason. Analysts never compute things "just because" |
    | 📘 **Concept** | the syntax and a mental model, kept short |
    | 🔍 **Example** | run it, but **predict the output first**. A wrong prediction teaches you the most |
    | ⚠️ **Trap** | the mistake almost everyone makes once |
    | ✍️ **Task** 🟢🟡🔴 | write the code yourself: 🟢 warm-up, 🟡 core (exam/job level), 🔴 stretch |
    | ✅ `check("id")` | tells you right/wrong **and why**, and recognises typical mistakes |
    | 🏁 **Checkpoint** | a business question that mixes the part's skills. Answer in code **and in words** |

    **When you are stuck, climb the ladder (no AI needed).** Add a new cell (**+ Code**) right under the `check` cell and run:
    1. `cheat()`: the 📘 concept table for this task, shown right there. No scrolling up.
    2. `hint()`: a nudge. Run it again for a stronger hint.
    3. `compare()`: your result next to the expected one (first rows).
    4. `solution()`: read it, **close it, retype it from memory**, run `check` again.

    No task number needed: these refer to **the task cell you ran (or checked) last**. (`hint("3.2")` works too, for any task.)

    📋 `cheat()` also searches: `cheat("merge")`, `cheat("NaN")`, `cheat("KeyError")` show every line about it from all
    lessons. `cheat("Part 3")` shows one part, `cheat("all")` the full cheat sheet and error decoder.
    🌐 The same as a web page with search, to keep open next to the notebook (second screen, phone):
    **[📋 open the cheat sheet](https://stanislavsidorovich.github.io/pandas-analyst-path/cheatsheet.html)**

    `progress()` shows your score per part. The ✅ outputs stay in your saved copy as a record.

    **Rules that make it stick:** try for 10 minutes before hint #1 · type, don't paste · one part per sitting is plenty ·
    next day, redo the tasks you needed a solution for (spaced repetition is what makes it stick).
    """)
    b.md("""
    ## 🗺️ The path

    | Part | Story | You learn | ≈ Time |
    |---|---|---|---|
    | 0 | Start here | how it works, the data, where it comes from (SQL/BigQuery) | 15 min |
    | 1 | Week 1 · Mon: meet the data | `head` `info` `describe`, selecting columns, `value_counts`, sorting | 1.5 h |
    | 2 | Tue: find the right rows | boolean masks, `& | ~`, `isin`, `between`, `loc` / `iloc` | 1.5 h |
    | 3 | Wed: new columns | arithmetic, `np.where` / `np.select`, `map`, `cut` / `qcut`, `.str` | 2 h |
    | 4 | Thu: dates | `to_datetime`, `.dt`, durations, date filters | 1.5 h |
    | 5 | Fri: clean a messy file | `read_csv`, missing values, duplicates, types, outliers (IQR) | 2.5 h |
    | 6 | Week 2 · Mon: join tables | `merge` (inner/left/anti), row-count sanity, `concat` | 1.5 h |
    | 7 | Tue–Wed: aggregate | `groupby`, `agg`, named aggregation, `transform`, `pivot_table`, `crosstab` | 3 h |
    | 8 | Thu: charts | matplotlib anatomy, seaborn `histplot` `boxplot` `barplot` `lineplot` `scatterplot` `heatmap` | 2.5 h |
    | 9 | Fri: KPIs over time | monthly KPIs, `pct_change`, `shift`, `rolling`, YoY | 2 h |
    | 10 | Week 3: customers | customer table, Pareto, cohorts, RFM, **churn**, funnel | 4 h |
    | 11 | Final case | quarterly business review + findings memo | 2–3 h |
    | 12 | Bonus · Data Mining | correlation, `get_dummies`, scaling, k‑means segmentation | 2 h |
    | A | Appendix | exam drill, cheat sheet, error decoder, glossary EN→RU | n/a |

    ### What a data / BI analyst actually does, and where you practise it
    | At work | Here |
    |---|---|
    | Answer ad-hoc questions: "how many…?", "which…?", "what share…?" | Parts 1–4, 7 |
    | Check and clean data before trusting it | Part 5 |
    | Combine data from several tables (the SQL `JOIN` of pandas) | Part 6 |
    | Build KPI tables: revenue, orders, AOV, margin, return rate | Parts 7, 9 |
    | Explain trends: month over month, year over year | Part 9 |
    | Segment customers and products: Pareto/ABC, RFM | Part 10 |
    | Retention, cohorts, churn | Part 10 |
    | Conversion funnels (website → cart → purchase) | Part 10 |
    | Make a chart that proves one point | Part 8 |
    | Turn numbers into a recommendation | Parts 11 and every 🏁 |
    | Prepare data for models (Data Mining course) | Part 12 |
    """)
    b.md("""
    ## ☁️ Working in Colab (also on a phone or tablet)

    - **First time:** open the notebook from GitHub (the badge above) → **File → Save a copy in Drive**. From then on, open
      *your copy* from [colab.research.google.com](https://colab.research.google.com) → *Recent* or from Google Drive, on any device.
    - **Data needs no login.** By default it downloads a frozen snapshot (~10 MB) from GitHub. You only sign in to Google if you
      switch `DATA_SOURCE` to `bigquery` (see below).
    - **Colab forgets variables** when you close the tab or after ~90 min idle. Then: run **⚙️ Setup**, then the
      **▶ Part setup** cell of the part you're in. Every part can start in a fresh session.
    - Phone: fine for reading, examples and short tasks. Tablet + keyboard: fine for everything.

    ### Colab basics in 60 seconds
    | To… | Do this |
    |---|---|
    | run a cell | click ▶ on its left, or click inside it and press **Shift+Enter** |
    | know if a cell has run | `[ ]` = never run · `[5]` = ran (5th run) · spinning circle = running |
    | add your own cell (e.g. for `hint(...)`) | hover between two cells → **+ Code**, or the **+ Code** button at the top (inserts below the selected cell) |
    | jump to a part | **Table of contents** (☰ icon on the left) |
    | undo a deleted cell | **Edit → Undo** (Ctrl+Z / ⌘Z outside the cell) |

    ⚠️ **Writing code is not enough. The cell must be run.** Until you run it, Python doesn't know your variable, and `check` says
    "I can't find …". Order for every task: **write → run your cell → run the `check` cell under it.**
    """)


def setup_placeholder(b):
    b.code("# SETUP_PLACEHOLDER", hidden=True)


def meet_data(b):
    b.md("""
    ## 🏢 Meet TheLook and its data

    TheLook sells clothes online to customers worldwide. The data is Google's public demo dataset
    `bigquery-public-data.thelook_ecommerce`. The data is synthetic, but it is structured exactly like a real shop's database.
    Snapshot date: **`TODAY` = 2026‑10‑01** (data up to 30 Sep 2026).

    | Table | Rows | One row = | Key columns |
    |---|---|---|---|
    | `users` | ~98k | a registered customer | `user_id`, `age`, `gender`, `country`, `traffic_source` (how they found us), `created_at` (sign-up) |
    | `products` | ~29k | a product in the catalogue | `product_id`, `name`, `brand`, `category`, `department` (Men/Women), `cost` (what we pay), `retail_price` |
    | `orders` | ~121k | an order | `order_id`, `user_id`, `status`, `num_of_item`, `created_at`, `shipped_at`, `delivered_at`, `returned_at` |
    | `order_items` | ~176k | one item inside an order | `order_item_id`, `order_id`, `user_id`, `product_id`, `status`, `created_at`, `sale_price` |
    | `sessions` | ~41k | one website visit (Jul–Sep 2026) | `session_id`, `user_id` (empty for guests), `traffic_source`, `browser`, `started_at`, `n_events`, `viewed_product`, `added_to_cart`, `purchased` |

    ```
    users ──< orders ──< order_items >── products        ──<  means "one … to many …"
      │ user_id    order_id        product_id
      └──< sessions (user_id, only for logged-in visitors)
    ```
    Order **status** flow: `Processing → Shipped → Complete`, or the order ends as `Cancelled` / `Returned`.
    """)
    b.md("""
    ### Where the data comes from: SQL first, pandas second
    In most companies the data sits in a warehouse (BigQuery, Snowflake, SQL Server…). The analyst **pulls a slice with SQL**,
    then explores, combines and explains it in pandas. The snapshot was extracted with queries like this one:

    ```sql
    SELECT oi.id AS order_item_id, oi.order_id, oi.user_id, oi.product_id, oi.status,
           DATETIME(o.created_at) AS created_at, ROUND(oi.sale_price, 2) AS sale_price
    FROM `bigquery-public-data.thelook_ecommerce.order_items` AS oi
    JOIN `bigquery-public-data.thelook_ecommerce.orders`      AS o USING (order_id)
    WHERE o.created_at < TIMESTAMP('2026-10-01')
    ```

    **Want the live data instead?** In the ⚙️ Setup cell set `DATA_SOURCE = "bigquery"` and your `PROJECT_ID`
    (the free BigQuery sandbox is enough). Colab will ask you to sign in once per session. Live data changes every day, so
    the numbers in the texts will differ slightly. The checks still work, because they recompute expected answers from whatever data is loaded.

    In Colab you can also run SQL directly into a DataFrame:
    ```python
    %%bigquery top_countries --project my-project-2026-484105
    SELECT country, COUNT(*) AS users FROM `bigquery-public-data.thelook_ecommerce.users`
    GROUP BY country ORDER BY users DESC LIMIT 5
    ```
    """)


# =====================================================================================================
def part1(b):
    b.part("Part 1", "Meet the data · Week 1, Monday", """
        users, products, orders, order_items, sessions = fresh_data()
    """)
    b.md("""
    > 📨 **Ana:** *"Welcome aboard! Before you touch any metric, get to know our tables: how big they are, what's inside,
    > who our customers are. By the end of the day tell me: top countries, how people find us, typical age."*
    """)
    # 1.1 ----------------------------------------------------------------------------------------
    b.md("""
    ## 1.1 Anatomy of a DataFrame

    🎯 **Why:** the first 5 minutes with any dataset are always the same. Size, columns, types, a few rows, summary stats.
    Skipping this is how analysts end up reporting nonsense.

    📘 **Concept**
    - A **DataFrame** is a table. Each column is a **Series** (values + an **index** of row labels).
    - | Command | Answers |
      |---|---|
      | `df.shape` | (rows, columns): an attribute, **no brackets** |
      | `df.head(n)` / `df.tail(n)` / `df.sample(n)` | first / last / random n rows |
      | `df.columns`, `df.dtypes` | column names, their types |
      | `df.info()` | types + non-null counts + memory, all at once |
      | `df.describe()` | count, mean, std, min, quartiles, max of numeric columns |
      | `df.describe(include="all")` | the same + text columns (count, unique, top, freq) |
      | `df["col"].mean()` `.median()` `.min()` `.max()` `.sum()` `.std()` | one number from a column |
    - Types you'll meet: `int64`, `float64` (numbers), `object`/`str` (text), `bool`, `datetime64` (dates).
    """)
    b.code("""
    # 🔍 Predict first: how many rows and columns does `users` have? Then run.
    print(users.shape)
    users.head()
    """)
    b.code("""
    users.info()
    """)
    b.code("""
    # Summary statistics. Look at age: what are the min, median (50%) and max?
    users.describe()
    """)
    b.md("""
    ⚠️ **Trap:** `df.shape()` → `TypeError: 'tuple' object is not callable`. `shape` is an attribute (no brackets),
    `head()` is a method (brackets). Same for `df.columns` and `df.dtypes`.
    """)
    b.task("1.1", "How big is the catalogue?", """
        How many products are in `products`? Store the **number of rows** as an integer.
        """, "n_products", "n_products = products.shape[0]   # or len(products)",
        ["`shape` is a tuple (rows, columns). Take the first element with `[0]`.",
         "`n_products = products.shape[0]`  ·  `len(products)` works too."], level=1)
    b.task("1.2", "Column names", """
        Store the column names of `products` as a **Python list**, in their original order.
        """, "product_cols", "product_cols = list(products.columns)",
        ["`products.columns` gives an Index object. Wrap it in `list(...)`.",
         "`product_cols = list(products.columns)`  (or `products.columns.tolist()`)"], level=1)
    b.task("1.3", "Typical price", """
        What is the **average** (mean) `retail_price` of products? And then think: is the **median** lower or higher, and why?
        """, "avg_retail_price", "avg_retail_price = products['retail_price'].mean()",
        ["Select the column with `products['retail_price']`, then call a method on it.",
         "`.mean()`"], level=1,
        takeaway="Mean > median means a long right tail: a few very expensive items pull the mean up.")
    b.task("1.4", "Median age", """
        Store the **median** age of our users.
        """, "median_age", "median_age = users['age'].median()",
        ["Same pattern as 1.3, but a different statistic.", "`users['age'].median()`"], level=1,
        traps=[("median_age = users['age'].mean()", "that's the mean, the task asks for the median.")])

    # 1.2 ----------------------------------------------------------------------------------------
    b.md("""
    ## 1.2 Selecting columns

    📘 **Concept**
    - `df["col"]` → a **Series** (one column).
    - `df[["col1", "col2"]]` → a **DataFrame**. The outer brackets mean "select", the inner ones are a Python list.
    - `df.col` also works for simple names, but fails for names with spaces and clashes with methods. Prefer brackets.
    - `df.rename(columns={"old": "new"})` returns a renamed copy.
    """)
    b.code("""
    # 🔍 Predict: what is the type of each result?
    a = users["country"]
    b_ = users[["country", "age"]]
    print(type(a), a.shape)
    print(type(b_), b_.shape)
    """)
    b.task("1.5", "One column", """
        Store the `retail_price` column of `products` as a **Series**.
        """, "prices", "prices = products['retail_price']",
        ["One column → single brackets.", "`products['retail_price']`"], level=1)
    b.task("1.6", "A few columns", """
        Make a DataFrame with exactly the columns `name`, `brand`, `retail_price` (in that order).
        """, "product_info", "product_info = products[['name', 'brand', 'retail_price']]",
        ["Several columns → put a **list** of names inside the brackets.",
         "`products[['name', 'brand', 'retail_price']]` (two pairs of brackets)"], level=1)

    # 1.3 ----------------------------------------------------------------------------------------
    b.md("""
    ## 1.3 Counting categories: `value_counts`, `unique`, `nunique`

    🎯 **Why:** "How many of each?" is the most common question in analytics, from orders by status to customers by country.

    📘 **Concept**
    | Code | Returns |
    |---|---|
    | `s.value_counts()` | count per value, **sorted from most to least frequent** |
    | `s.value_counts(normalize=True)` | **share** (0–1) instead of count |
    | `s.value_counts(dropna=False)` | also counts missing values |
    | `s.unique()` / `s.nunique()` | the distinct values / **how many** distinct values |
    | `s.value_counts().idxmax()` | the most frequent value (also `.index[0]`) |

    💡 A boolean trick you'll use daily: `(s == "X").mean()` = **share of rows where s is X** (True=1, False=0).

    🧩 **A Series has two parts.** The result of `value_counts()` looks like a two-column table, but it is a Series:
    - the left column is the **index**: the *labels* (here: the traffic sources) → `.index`
    - the right column is the **values**: the *counts* → `.values`

    So "which ones?" questions (names, top 3, the biggest) are answered by the **index**, and "how many?" questions by
    the **values**. `.head(3)` keeps the first 3 rows, `.index` takes their labels, `list(...)` makes them a plain list
    (same trick as `list(products.columns)` in 1.2).
    """)
    b.code("""
    # 🔍 How do customers find us?
    print(users["traffic_source"].value_counts())
    print()
    print(users["traffic_source"].value_counts(normalize=True).round(3))
    print("Share from Search:", (users["traffic_source"] == "Search").mean())
    """)
    b.code("""
    # 🔍 Labels vs counts: the two parts of a value_counts() result
    vc = users["traffic_source"].value_counts()
    print("index  (labels):", list(vc.index))
    print("values (counts):", list(vc.values))
    print("most frequent label:", vc.index[0], "| its count:", vc.iloc[0])
    """)
    b.task("1.7", "How many countries?", """
        How many **distinct** countries appear in `users`?
        """, "n_countries", "n_countries = users['country'].nunique()",
        ["You need a count of distinct values, not the values themselves.", "`.nunique()`"], level=1,
        traps=[("n_countries = users['country'].count()", "`count()` counts non-empty rows, not distinct values.")])
    b.task("1.8", "Orders by status", """
        Count orders per `status` (a Series: status → number of orders, most frequent first).
        """, "orders_by_status", "orders_by_status = orders['status'].value_counts()",
        ["Which method counts each distinct value?", "`orders['status'].value_counts()`"], level=1,
        cmp={"ordered": True})
    b.task("1.9", "Status as shares", """
        Same as 1.8 but as **shares between 0 and 1** (they should sum to 1).
        """, "status_share", "status_share = orders['status'].value_counts(normalize=True)",
        ["`value_counts` has a parameter that turns counts into proportions.", "`normalize=True`"],
        traps=[("status_share = orders['status'].value_counts()", "these are counts. Add `normalize=True` to get shares."),
               ("status_share = orders['status'].value_counts(normalize=True) * 100",
                "that's percent. The task wants fractions (0–1). Multiply by 100 only when formatting a report.")])
    b.task("1.10", "The biggest category", """
        Which product `category` has the most products? Store its **name** (a string).
        """, "top_category", "top_category = products['category'].value_counts().idxmax()",
        ["Count categories first, then take the label of the largest count.",
         "`value_counts()` is sorted descending, so the first **index** label is the answer: `.index[0]` or `.idxmax()`."],
        traps=[("top_category = products['category'].value_counts().max()",
                "`.max()` gives the biggest *count*. You need the *label*: `.idxmax()`.")])

    # 1.4 ----------------------------------------------------------------------------------------
    b.md("""
    ## 1.4 Sorting and top‑N

    📘 **Concept**
    - `df.sort_values("col")` ascending; `ascending=False` for descending.
    - Several keys: `df.sort_values(["a", "b"], ascending=[True, False])`.
    - Top N: `df.sort_values("col", ascending=False).head(N)` or `df.nlargest(N, "col")`.
    - Sorting **returns a new DataFrame**. The original is unchanged unless you assign: `df = df.sort_values(...)`.
    """)
    b.code("""
    # 🔍 The 5 cheapest products: which columns would you show a manager?
    products.sort_values("retail_price").head(5)[["name", "category", "retail_price"]]
    """)
    b.task("1.11", "Top 10 most expensive", """
        A DataFrame with the **10 most expensive products** (all columns), most expensive first.
        """, "top10_expensive", "top10_expensive = products.sort_values('retail_price', ascending=False).head(10)",
        ["Sort by price descending, then keep the first 10 rows.",
         "`products.sort_values('retail_price', ascending=False).head(10)`  or  `products.nlargest(10, 'retail_price')`"],
        level=1, cmp={"cols": ["retail_price"], "ignore_index": True},
        traps=[("top10_expensive = products.sort_values('retail_price').head(10)",
                "you got the 10 *cheapest*. Sort with `ascending=False`.")])
    b.task("1.12", "Sort by two columns", """
        Sort `products` by `category` A→Z, and **within each category** by `retail_price` from high to low.
        Keep all rows and columns.
        """, "products_sorted",
        "products_sorted = products.sort_values(['category', 'retail_price'], ascending=[True, False])",
        ["Pass a list of columns and a list of directions.",
         "`sort_values(['category', 'retail_price'], ascending=[True, False])`"],
        cmp={"cols": ["category", "retail_price"], "ignore_index": True})

    b.md("""
    ## 🏁 Checkpoint 1: who are our customers?
    > 📨 **Ana:** *"Three quick facts for my slide: our top 3 countries, what share of customers come from Search, and their typical age."*
    """)
    b.task("1.C1", "Top 3 countries", """
        A **list** with the names of the 3 countries with the most users, biggest first.
        """, "top3_countries", "top3_countries = list(users['country'].value_counts().head(3).index)",
        ["You already have both pieces. 1.10: `value_counts()` is sorted biggest first, and the **names** sit in its "
         "`.index` (the counts are the values). 1.2: `list(...)` turns an Index into a plain Python list. "
         "No row filtering is needed here.",
         "Count countries with `value_counts()`, keep the first 3 rows with `.head(3)`, take their labels with `.index`, "
         "wrap it all in `list(...)`.",
         "`list(users['country'].value_counts().head(3).index)`"], cmp={"ordered": True},
        traps=[("top3_countries = users['country'].value_counts().head(3)",
                "that's a Series: country → **count**. You need only the names: take its `.index` and wrap it in `list(...)`.")])
    b.task("1.C2", "Share of Search", """
        The share of users (0–1) whose `traffic_source` is `"Search"`.
        """, "search_share", "search_share = (users['traffic_source'] == 'Search').mean()",
        ["Remember the boolean trick from 1.3.", "`(users['traffic_source'] == 'Search').mean()`"])
    b.md("""
    ✍️ **Write your answer to Ana** in 2 sentences in the cell below (double-click to edit). Use the numbers you found
    (median age from 1.4). Round sensibly: "about 35%", not "0.348712".

    *Your answer:* …
    """)


# =====================================================================================================
def part2(b):
    b.part("Part 2", "Find the right rows · Tuesday", """
        users, products, orders, order_items, sessions = fresh_data()
    """)
    b.md("""
    > 📨 **Ana:** *"Marketing wants a list of men's coats, ops wants the returned orders, and I want to know how many of our
    > products are 'mid-price'. Can you pull those?"*
    """)
    b.md("""
    ## 2.1 Boolean masks: the filter of pandas

    📘 **Concept**
    1. A condition on a column gives a Series of `True`/`False`: `products["retail_price"] > 100`.
    2. Put it inside `df[...]` and only the `True` rows stay: `products[products["retail_price"] > 100]`.
    3. Combine with `&` (and), `|` (or), `~` (not), and **each condition goes in parentheses**.

    | Need | Code |
    |---|---|
    | equals one of several values | `df["col"].isin(["A", "B"])` |
    | inside a range (both ends included) | `df["col"].between(10, 20)` |
    | text contains | `df["col"].str.contains("jean", case=False, na=False)` |
    | missing / not missing | `df["col"].isna()` / `df["col"].notna()` |
    | how many rows match | `mask.sum()` |
    | what share of rows match | `mask.mean()` |

    ⚠️ **Traps:** `and` / `or` → `ValueError: The truth value of a Series is ambiguous`. Use `&` / `|`.
    Missing parentheses: `df["a"] > 1 & df["b"] < 5` is evaluated in the wrong order → wrong rows or an error.
    """)
    b.code("""
    # 🔍 Predict: roughly how many products cost more than 500?
    mask = products["retail_price"] > 500
    print(mask.head(3))
    print("matches:", mask.sum(), "| share:", round(mask.mean(), 4))
    products[mask].head()
    """)
    b.code("""
    # Two conditions: women's dresses under 30
    cheap_dresses = products[(products["category"] == "Dresses") & (products["retail_price"] < 30)]
    print(len(cheap_dresses))
    """)
    b.task("2.1", "Returned orders", """
        All orders whose `status` is `"Returned"` (all columns).
        """, "returned_orders", "returned_orders = orders[orders['status'] == 'Returned']",
        ["Build the mask `orders['status'] == 'Returned'`, then put it inside `orders[...]`.",
         "`orders[orders['status'] == 'Returned']`"], level=1)
    b.task("2.2", "How many expensive products?", """
        The **number** of products with `retail_price` greater than 200.
        """, "n_expensive", "n_expensive = (products['retail_price'] > 200).sum()",
        ["You don't need the rows, only how many `True` values the mask has.", "`(mask).sum()` or `len(products[mask])`"],
        level=1, traps=[("n_expensive = (products['retail_price'] >= 200).sum()", "'greater than' is `>` not `>=`.")])
    b.task("2.3", "Men's outerwear", """
        Products where `department` is `"Men"` **and** `category` is `"Outerwear & Coats"`.
        """, "men_outerwear",
        "men_outerwear = products[(products['department'] == 'Men') & (products['category'] == 'Outerwear & Coats')]",
        ["Two conditions joined with `&`, each in parentheses.",
         "`products[(cond1) & (cond2)]`"])
    b.task("2.4", "Young or senior customers", """
        Users **under 18** or **65 and older**.
        """, "young_or_senior", "young_or_senior = users[(users['age'] < 18) | (users['age'] >= 65)]",
        ["'or' is `|`. Watch the boundaries: under 18 = `< 18`.", "`users[(users['age'] < 18) | (users['age'] >= 65)]`"],
        traps=[("young_or_senior = users[(users['age'] <= 18) | (users['age'] >= 65)]",
                "boundary: 'under 18' means `< 18`, 18-year-olds are not included."),
               ("young_or_senior = users[(users['age'] < 18) | (users['age'] > 65)]",
                "boundary: '65 and older' means `>= 65`.")])
    b.task("2.5", "Email or Facebook", """
        Users whose `traffic_source` is `"Email"` or `"Facebook"`. Use `isin`.
        """, "email_fb", "email_fb = users[users['traffic_source'].isin(['Email', 'Facebook'])]",
        ["`isin` takes a **list** of allowed values.", "`users[users['traffic_source'].isin(['Email', 'Facebook'])]`"])
    b.task("2.6", "Share of mid-price products", """
        What **share** (0–1) of products has `retail_price` between 50 and 100, both ends included?
        """, "share_mid_price", "share_mid_price = products['retail_price'].between(50, 100).mean()",
        ["`between(low, high)` includes both ends by default.", "Then use the `.mean()` trick on the boolean mask."],
        traps=[("share_mid_price = products['retail_price'].between(50, 100).sum()",
                "that's the *count*. The share is `.mean()` of the mask.")])
    b.task("2.7", "Items that really sold", """
        Rows of `order_items` whose status is **neither** `"Cancelled"` **nor** `"Returned"`.
        (This is the base for revenue later: cancelled and returned items earn nothing.)
        """, "sold_items", "sold_items = order_items[~order_items['status'].isin(['Cancelled', 'Returned'])]",
        ["'Not in a list' = `~` in front of an `isin` mask.",
         "`order_items[~order_items['status'].isin(['Cancelled', 'Returned'])]`"], level=3)

    b.md("""
    ## 2.2 `loc` and `iloc`: rows and columns together

    📘 **Concept**
    - `df.loc[rows, cols]` selects **by label** (index labels, column names, or a boolean mask for rows).
    - `df.iloc[rows, cols]` selects **by position** (0, 1, 2…), like a Python list.
    - `df.set_index("col")` makes a column the row labels, so `df.loc[label]` finds a row by, e.g., its id.
    - **Changing values:** `df.loc[mask, "col"] = value` sets the value only where the mask is True.

    ⚠️ **Biggest trap:** `loc[0:5]` **includes** 5 (labels), `iloc[0:5]` **excludes** 5 (positions).
    ⚠️ **Second trap:** `df[df["a"] > 1]["b"] = 0` does nothing useful (it changes a temporary copy, and pandas warns with
    `SettingWithCopyWarning`). Write `df.loc[df["a"] > 1, "b"] = 0`.
    """)
    b.code("""
    # 🔍 Predict the shapes before running
    print(orders.loc[0:4, ["order_id", "status"]].shape)    # labels 0..4 → ?
    print(orders.iloc[0:4, 0:2].shape)                      # positions 0..3 → ?

    p = products.set_index("product_id")
    print(p.loc[1, "name"], "|", p.loc[1, "retail_price"])  # product with id 1
    """)
    b.task("2.8", "First rows by position", """
        The **first 3 rows** of `orders` (by position), with only the columns `order_id` and `status`.
        """, "first_3_orders", "first_3_orders = orders.iloc[:3][['order_id', 'status']]",
        ["Positions → `iloc`. Then select the two columns.",
         "`orders.iloc[:3][['order_id', 'status']]`  or  `orders.loc[orders.index[:3], ['order_id', 'status']]`"], level=1)
    b.task("2.9", "Names of very cheap products", """
        A **Series** of product `name`s for products with `retail_price` below 5. Use `loc` with a mask and one column.
        """, "cheap_names", "cheap_names = products.loc[products['retail_price'] < 5, 'name']",
        ["`df.loc[mask, 'column']` returns one column for the matching rows.",
         "`products.loc[products['retail_price'] < 5, 'name']`"])
    b.task("2.10", "Find a product by id", """
        Make `p = products.set_index("product_id")` and use `loc` to get the `retail_price` of product **1000**.
        """, "price_1000", """
        p = products.set_index('product_id')
        price_1000 = p.loc[1000, 'retail_price']
        """,
        ["After `set_index`, the product ids are the row labels.", "`p.loc[1000, 'retail_price']`"],
        traps=[("price_1000 = products.iloc[1000]['retail_price']",
                "`iloc[1000]` is the 1001st *row position*, not product id 1000. Use `set_index` + `loc`.")])
    b.task("2.11", "Flag premium products", """
        Make a **copy** of `products` called `products_flagged`, add a column `is_premium` that is `False` everywhere,
        then set it to `True` with `loc` where `retail_price >= 100`.
        """, "products_flagged", """
        products_flagged = products.copy()
        products_flagged['is_premium'] = False
        products_flagged.loc[products_flagged['retail_price'] >= 100, 'is_premium'] = True
        """,
        ["Three lines: copy → new column with a default → `loc[mask, 'is_premium'] = True`.",
         "`products_flagged.loc[products_flagged['retail_price'] >= 100, 'is_premium'] = True`"], level=3,
        custom="""
        ok = isinstance(u, pd.DataFrame) and 'is_premium' in u.columns and len(u) == len(r) and (u['is_premium'].astype(bool).values == r['is_premium'].values).all()
        msg = '' if ok else "Check that products_flagged has all rows and an 'is_premium' column that is True exactly where retail_price >= 100."
        if ok and 'is_premium' in g['products'].columns:
            ok, msg = False, "You changed the original `products` too. Use products.copy()."
        """)
    b.md("""
    💡 **`query()`: an alternative you'll see in other people's code**
    `products.query("department == 'Men' and retail_price > 100")` is the same as the mask version. It's readable, but
    masks are the standard on exams and in most codebases, so learn masks first.

    ## 🏁 Checkpoint 2
    > 📨 **Ana:** *"What's the average price of women's jeans? And how many big orders (3+ items) did we actually ship or complete?"*
    """)
    b.task("2.C1", "Women's jeans", """
        Average `retail_price` of products with department `"Women"` and category `"Jeans"`.
        """, "women_jeans_avg",
        "women_jeans_avg = products.loc[(products['department'] == 'Women') & (products['category'] == 'Jeans'), 'retail_price'].mean()",
        ["Filter with two conditions, take the column, then `.mean()`.",
         "`products.loc[(cond1) & (cond2), 'retail_price'].mean()`"])
    b.task("2.C2", "Big delivered orders", """
        The number of orders with `num_of_item >= 3` whose `status` is `"Shipped"` or `"Complete"`.
        """, "n_big_orders",
        "n_big_orders = ((orders['num_of_item'] >= 3) & (orders['status'].isin(['Shipped', 'Complete']))).sum()",
        ["Combine a numeric condition and an `isin` condition with `&`.", "Then `.sum()` the mask."])


# =====================================================================================================
def part3(b):
    b.part("Part 3", "New columns · Wednesday", """
        users, products, orders, order_items, sessions = fresh_data()
        prod = products.copy()                      # our working copy: we will add columns to it
        prod["margin"] = prod["retail_price"] - prod["cost"]
        orders2 = orders.copy()
    """)
    b.md("""
    > 📨 **Ana:** *"Finance asks: what margin do we make per product, and can we split the catalogue into price tiers?"*

    ## 3.1 Calculated columns

    📘 **Concept**
    - `df["new"] = expression` creates (or overwrites) a column. The expression works on **whole columns at once**
      (vectorized), so no loops are needed: `df["total"] = df["price"] * df["qty"]`.
    - Use `.round(2)` for display, but keep the full precision for calculations.
    - Work on a copy (`prod = products.copy()`) when you don't want to change the original.
      `b = a` is **not** a copy, just a second name for the same table.
    """)
    b.code("""
    # 🔍 The Part setup already created prod["margin"] = retail_price - cost
    prod[["name", "cost", "retail_price", "margin"]].head()
    """)
    b.task("3.1", "Margin percent", """
        Add a column `margin_pct` to `prod`: margin as a **fraction** of `retail_price` (e.g. 0.45, not 45).
        """, 'prod["margin_pct"]', 'prod["margin_pct"] = prod["margin"] / prod["retail_price"]',
        ["Divide one column by another and assign to `prod['margin_pct']`.",
         "`prod['margin_pct'] = prod['margin'] / prod['retail_price']`"], level=1,
        traps=[('prod["margin_pct"] = prod["margin"] / prod["retail_price"] * 100', "the task asks for a fraction, not percent."),
               ('prod["margin_pct"] = prod["margin"] / prod["cost"]', "margin % is relative to the *selling* price (retail_price), not the cost. Margin on cost is called *markup*.")])
    b.task("3.2", "Most profitable product", """
        The **name** of the product with the largest absolute `margin` (in dollars).
        """, "most_profitable", "most_profitable = prod.loc[prod['margin'].idxmax(), 'name']",
        ["`idxmax()` gives the row **label** of the maximum. Then use it in `loc`.",
         "`prod.loc[prod['margin'].idxmax(), 'name']`"],
        traps=[("most_profitable = prod['margin'].max()", "that's the margin value. You need the product's *name*."),
               ("most_profitable = prod['margin'].idxmax()", "that's the row label. Use it in `prod.loc[label, 'name']`.")])

    b.md("""
    ## 3.2 Categories from conditions: `np.where`, `np.select`, `map`, `apply`

    📘 **Concept**
    | Situation | Tool |
    |---|---|
    | two outcomes | `np.where(condition, value_if_true, value_if_false)` |
    | several ordered rules | `np.select([cond1, cond2, ...], [val1, val2, ...], default=...)`: the **first** true condition wins |
    | translate values with a dictionary | `s.map({"old1": "new1", "old2": "new2"})`: unmapped values become NaN |
    | any custom Python function | `s.apply(func)`: flexible but **slow** (row-by-row), so use it as a last resort |
    """)
    b.code("""
    # 🔍 Example: sizes of orders
    orders2["size"] = np.where(orders2["num_of_item"] >= 3, "big", "small")
    print(orders2["size"].value_counts())

    conds = [orders2["num_of_item"] == 1, orders2["num_of_item"] == 2]
    orders2["size3"] = np.select(conds, ["single", "pair"], default="multi")
    print(orders2["size3"].value_counts())
    """)
    b.task("3.3", "Premium vs standard", """
        Add `prod["price_band"]`: `"premium"` if `retail_price >= 100`, otherwise `"standard"`. Use `np.where`.
        """, 'prod["price_band"]', 'prod["price_band"] = np.where(prod["retail_price"] >= 100, "premium", "standard")',
        ["`np.where(condition, if_true, if_false)`", "`np.where(prod['retail_price'] >= 100, 'premium', 'standard')`"], level=1)
    b.task("3.4", "Four price tiers", """
        Add `prod["tier"]` with `np.select`:
        `< 25` → `"budget"`, `< 75` → `"mid"`, `< 150` → `"upper"`, everything else → `"luxury"`.
        """, 'prod["tier"]', """
        conds = [prod["retail_price"] < 25, prod["retail_price"] < 75, prod["retail_price"] < 150]
        prod["tier"] = np.select(conds, ["budget", "mid", "upper"], default="luxury")
        """,
        ["The order of conditions matters: the first true one wins, so go from cheapest up.",
         "`np.select([c1, c2, c3], ['budget', 'mid', 'upper'], default='luxury')`"],
        traps=[("""
        conds = [prod["retail_price"] < 150, prod["retail_price"] < 75, prod["retail_price"] < 25]
        prod["tier"] = np.select(conds, ["upper", "mid", "budget"], default="luxury")
        """, "with `< 150` first, a $10 item is caught by it and becomes 'upper'. Order the rules from the narrowest.")])
    b.task("3.5", "Group the statuses", """
        Add `orders2["status_group"]` using `.map()` with this dictionary:
        `Complete → "done"`, `Shipped → "in_transit"`, `Processing → "in_transit"`, `Cancelled → "lost"`, `Returned → "lost"`.
        """, 'orders2["status_group"]', """
        status_map = {"Complete": "done", "Shipped": "in_transit", "Processing": "in_transit",
                      "Cancelled": "lost", "Returned": "lost"}
        orders2["status_group"] = orders2["status"].map(status_map)
        """,
        ["Write the dict first, then `orders2['status'].map(the_dict)`.",
         "If you see NaN in the result, a key is misspelled (case matters!)."])

    b.md("""
    ## 3.3 Binning numbers: `pd.cut` and `pd.qcut`

    📘 **Concept**
    - `pd.cut(s, bins=[0, 18, 35, 100], labels=["kid", "young", "adult"])`: **fixed edges** you choose.
      Intervals are right-closed by default: `(18, 35]` contains 35 but not 18.
    - `pd.qcut(s, q=4, labels=["Q1", "Q2", "Q3", "Q4"])`: **equal-sized groups** by quantiles (each ≈25% of rows).
    - The result is a *categorical* with a natural order, so `value_counts(sort=False)` keeps that order.
    """)
    b.code("""
    # 🔍 Age groups: which bin will a 18-year-old fall into?
    groups = pd.cut(users["age"], bins=[0, 17, 34, 54, 100], labels=["<18", "18-34", "35-54", "55+"])
    groups.value_counts(sort=False)
    """)
    b.task("3.6", "Marketing age groups", """
        Use `pd.cut` on `users["age"]` with bins `[0, 17, 24, 34, 44, 54, 64, 100]` and labels
        `["<18", "18-24", "25-34", "35-44", "45-54", "55-64", "65+"]`, then count users per group **in the label order**.
        """, "age_group_counts", """
        age_group = pd.cut(users["age"], bins=[0, 17, 24, 34, 44, 54, 64, 100],
                           labels=["<18", "18-24", "25-34", "35-44", "45-54", "55-64", "65+"])
        age_group_counts = age_group.value_counts(sort=False)
        """,
        ["`pd.cut(series, bins=[...], labels=[...])`", "Count with `.value_counts(sort=False)` to keep the age order."],
        cmp={"ordered": True})
    b.task("3.7", "Price quartiles", """
        Split `products["retail_price"]` into 4 equal-sized groups with `pd.qcut` (labels `Q1`…`Q4`).
        What is the **lowest price inside Q4**? (In business terms, the price where the top 25% of the catalogue starts.)
        """, "q4_min_price", """
        quartile = pd.qcut(products["retail_price"], 4, labels=["Q1", "Q2", "Q3", "Q4"])
        q4_min_price = products.loc[quartile == "Q4", "retail_price"].min()
        """,
        ["Create the quartile Series, then filter products where it equals 'Q4'.",
         "`products.loc[quartile == 'Q4', 'retail_price'].min()`"], level=3)

    b.md("""
    ## 3.4 Text columns: the `.str` accessor

    📘 **Concept:** `.str` applies string methods to every value of a column:
    `.str.lower()` `.str.upper()` `.str.title()` `.str.strip()` `.str.len()` `.str.contains("x", case=False, na=False)`
    `.str.startswith("x")` `.str.replace("a", "b")` `.str.split(" ")` → lists, `.str[0]` → first element / first character.

    ⚠️ **Trap:** `brand` has missing values. `str.contains` returns NaN for them and the mask fails with
    "Cannot mask with non-boolean array containing NA". Fix: `na=False`.
    """)
    b.code("""
    # 🔍 Which products mention "jacket"?
    m = products["name"].str.contains("jacket", case=False, na=False)
    print(m.sum())
    products.loc[m, "name"].head()
    """)
    b.task("3.8", "Levi's products", """
        How many products have a `brand` that contains `"levi"`, **ignoring case**?
        """, "n_levis", "n_levis = products['brand'].str.contains('levi', case=False, na=False).sum()",
        ["`str.contains` + two keyword arguments: one for case, one for missing values.",
         "`products['brand'].str.contains('levi', case=False, na=False).sum()`"], level=1,
        traps=[("n_levis = products['brand'].str.contains('levi', na=False).sum()",
                "case matters by default: 'Levi's' has a capital L. Add `case=False`.")])
    b.task("3.9", "First word of the name", """
        A Series with the **first word** of each product `name` (missing names stay missing).
        """, "first_word", "first_word = products['name'].str.split().str[0]",
        ["Split into words, then take element 0 of each list, both with `.str`.",
         "`products['name'].str.split().str[0]`"])

    b.md("""
    ## 🏁 Checkpoint 3
    > 📨 **Ana:** *"What share of our catalogue is 'luxury' tier, and is the margin % on luxury items higher than on budget ones?"*
    (Use the `tier` and `margin_pct` columns you made.)
    """)
    b.task("3.C1", "Luxury share", """
        Share (0–1) of products in `prod` whose `tier` is `"luxury"`.
        """, "luxury_share", "luxury_share = (prod['tier'] == 'luxury').mean()",
        ["Boolean mask + `.mean()`."], needs=["3.4"])
    b.task("3.C2", "Margin %: luxury minus budget", """
        Average `margin_pct` of luxury products **minus** average `margin_pct` of budget products
        (a positive number means luxury earns more per dollar).
        """, "margin_gap", """
        lux = prod.loc[prod['tier'] == 'luxury', 'margin_pct'].mean()
        bud = prod.loc[prod['tier'] == 'budget', 'margin_pct'].mean()
        margin_gap = lux - bud
        """,
        ["Two `loc` filters with `.mean()`, then subtract.", "`prod.loc[prod['tier'] == 'luxury', 'margin_pct'].mean()`"],
        needs=["3.1", "3.4"])
    b.md("*Your answer to Ana (1–2 sentences):* …")


# =====================================================================================================
def part4(b):
    b.part("Part 4", "Dates and durations · Thursday", """
        users, products, orders, order_items, sessions = fresh_data()
        o = orders.copy()
    """)
    b.md("""
    > 📨 **Ana:** *"Ops says delivery got slow. How long does it actually take from order to delivery? And when do people order?"*

    ## 4.1 Datetime basics

    📘 **Concept**
    - Text → dates: `pd.to_datetime(s)`. European `dd/mm/yyyy` needs `dayfirst=True` (or `format="%d/%m/%Y"`).
      Bad values → `errors="coerce"` turns them into `NaT` (missing date).
    - Parts of a date with the **`.dt`** accessor: `.dt.year` `.dt.month` `.dt.day_name()` `.dt.hour` `.dt.date`
      `.dt.to_period("M")` (a month like `2026-09`).
    - Subtracting dates gives a **Timedelta**: `.dt.days` (whole days) or `.dt.total_seconds() / 86400` (fractional days).
    - Compare with strings directly: `o["created_at"] >= "2026-01-01"`.
    """)
    b.code("""
    # 🔍 Parsing text dates: predict the month of each value
    raw = pd.Series(["03/04/2026", "15/04/2026", "not a date"])
    print(pd.to_datetime(raw, dayfirst=True, errors="coerce"))
    """)
    b.code("""
    print(o["created_at"].dtype)          # already datetime64: the parquet file keeps types
    year = o["created_at"].dt.year        # a separate Series; we don't add it to o
    year.value_counts().sort_index()
    """)
    b.code("""
    # Durations: hours from order to shipping
    ship_hours = (o["shipped_at"] - o["created_at"]).dt.total_seconds() / 3600
    ship_hours.describe()   # count < number of orders: not every order was shipped (NaT)
    """)
    b.task("4.1", "Orders in 2025", """
        How many orders were created in **2025**?
        """, "orders_2025", "orders_2025 = (o['created_at'].dt.year == 2025).sum()",
        ["`.dt.year` gives the year of each order.", "`(o['created_at'].dt.year == 2025).sum()`"], level=1)
    b.task("4.2", "Busiest weekday", """
        On which **day of the week** (e.g. `"Monday"`) were the most orders created? Store the name.
        """, "busiest_weekday", "busiest_weekday = o['created_at'].dt.day_name().value_counts().idxmax()",
        ["`.dt.day_name()` then `value_counts()`.", "`.idxmax()` gives the label of the biggest count."], level=1)
    b.task("4.3", "Average delivery time", """
        Average time from `created_at` to `delivered_at` in **days, as a decimal** (e.g. 3.4).
        Orders without a delivery date are skipped automatically by `.mean()`.
        """, "avg_days_to_deliver", """
        days_to_deliver = (o['delivered_at'] - o['created_at']).dt.total_seconds() / 86400
        avg_days_to_deliver = days_to_deliver.mean()
        """,
        ["Subtract the two columns → Timedelta. Convert to days with `.dt.total_seconds() / 86400`.",
         "`.dt.days` would cut 3.9 days down to 3. That's why total_seconds is used here."],
        traps=[("avg_days_to_deliver = (o['delivered_at'] - o['created_at']).dt.days.mean()",
                "`.dt.days` keeps only whole days (3.9 → 3). Use `.dt.total_seconds() / 86400`.")])
    b.task("4.4", "Delivered within 3 days", """
        Among **delivered** orders (`delivered_at` not missing), what share (0–1) was delivered within 3 days
        (≤ 3.0 days) of `created_at`?
        """, "share_fast", """
        delivered = o[o['delivered_at'].notna()]
        d = (delivered['delivered_at'] - delivered['created_at']).dt.total_seconds() / 86400
        share_fast = (d <= 3).mean()
        """,
        ["Filter delivered orders first. Otherwise NaN rows count as 'not fast' and drag the share down.",
         "Compute days as in 4.3, then `(days <= 3).mean()`."],
        traps=[("""
        d = (o['delivered_at'] - o['created_at']).dt.total_seconds() / 86400
        share_fast = (d <= 3).mean()
        """, "you included undelivered orders (NaN compares as False). Filter `delivered_at.notna()` first.")])
    b.md("""
    ## 4.2 Filtering by date ranges

    📘 Use **half-open intervals**: `start <= date < first day after the period`.

    ⚠️ **Trap:** `o["created_at"].between("2026-07-01", "2026-09-30")` stops at `2026-09-30 00:00:00`, so **almost the
    whole last day is lost**. Timestamps have hours.
    """)
    b.task("4.5", "Orders in Q3 2026", """
        All orders created from 1 July 2026 to 30 September 2026 **inclusive** (the full last day).
        """, "orders_q3", "orders_q3 = o[(o['created_at'] >= '2026-07-01') & (o['created_at'] < '2026-10-01')]",
        ["Use `>=` start and `<` the day after the end.", "`o[(o['created_at'] >= '2026-07-01') & (o['created_at'] < '2026-10-01')]`"],
        traps=[("orders_q3 = o[o['created_at'].between('2026-07-01', '2026-09-30')]",
                "`between(..., '2026-09-30')` stops at 30 Sep 00:00 and drops orders from that day. Use `< '2026-10-01'`.")])
    b.task("4.6", "Orders per month in 2026", """
        Number of orders per month for 2026, as a Series indexed by month (`Period` like `2026-01`), in calendar order.
        """, "monthly_orders_2026", """
        o26 = o[o['created_at'].dt.year == 2026]
        monthly_orders_2026 = o26['created_at'].dt.to_period('M').value_counts().sort_index()
        """,
        ["Filter 2026, convert dates to months with `.dt.to_period('M')`, count.",
         "`value_counts()` sorts by count, so add `.sort_index()` to get calendar order."], level=3,
        cmp={"ordered": True},
        traps=[("""
        o26 = o[o['created_at'].dt.year == 2026]
        monthly_orders_2026 = o26['created_at'].dt.to_period('M').value_counts()
        """, "`value_counts()` sorts by size. Add `.sort_index()` for calendar order.")])
    b.md("""
    ## 🏁 Checkpoint 4
    > 📨 **Ana:** *"Do bigger orders take longer to arrive?"* Compare the average delivery time (days, decimal) of delivered
    > **1‑item** orders vs delivered orders with **3 or more** items.
    """)
    b.task("4.C1", "Delivery time: big minus single", """
        `delivery_gap` = average delivery days of delivered orders with `num_of_item >= 3` **minus** that of orders with
        `num_of_item == 1`.
        """, "delivery_gap", """
        d = o[o['delivered_at'].notna()].copy()
        d['days'] = (d['delivered_at'] - d['created_at']).dt.total_seconds() / 86400
        delivery_gap = d.loc[d['num_of_item'] >= 3, 'days'].mean() - d.loc[d['num_of_item'] == 1, 'days'].mean()
        """,
        ["Make a delivered-only copy with a `days` column, then two filtered means.",
         "`d.loc[d['num_of_item'] >= 3, 'days'].mean() - d.loc[d['num_of_item'] == 1, 'days'].mean()`"])
    b.md("""
    *Your answer to Ana:* is the gap big enough to matter to a customer? (Hint: compare it with the average itself.) …
    """)
