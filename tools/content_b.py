"""Parts 5-8."""

ITEMS_SETUP = """
users, products, orders, order_items, sessions = fresh_data()
items = (order_items
         .merge(products, on="product_id", how="left")
         .merge(users[["user_id", "age", "gender", "country", "traffic_source"]], on="user_id", how="left"))
items["profit"] = items["sale_price"] - items["cost"]
sales = items[~items["status"].isin(["Cancelled", "Returned"])].copy()   # what we really earned
"""


# =====================================================================================================
def part5(b):
    b.part("Part 5", "Clean a messy file · Friday", """
        users, products, orders, order_items, sessions = fresh_data()
        print(CRM_PATH)    # the CRM export file, created by the Setup cell
    """)
    b.md("""
    > 📨 **Ana:** *"Marketing exported their CRM sign-ups from Excel. They want spend by country, but I don't trust that file.
    > Clean it first, and tell me what was wrong with it."*

    🎯 **Why:** a large share of real analyst time goes into cleaning. Every number you report later inherits the mistakes you
    don't fix now. **Rule:** never fix silently. Write down every rule you apply, so others can check it.

    ## 5.1 Reading files

    📘 `pd.read_csv(path, sep=",", decimal=".", encoding="utf-8", parse_dates=[...], dtype={...})`
    - European Excel exports often use `sep=";"` and `decimal=","` (Portugal too!).
    - Always look right after reading: `.head()`, `.shape`, `.dtypes`. Is a number column read as text? Did everything land in one column?
    - Excel: `pd.read_excel("file.xlsx", sheet_name="Sheet1")`. Saving: `df.to_csv("out.csv", index=False)`.
    """)
    b.code("""
    # 🔍 Look at the raw text first: what separates the columns? How are decimals written?
    with open(CRM_PATH, encoding="utf-8") as f:
        for _ in range(4):
            print(f.readline().rstrip())

    wrong = pd.read_csv(CRM_PATH)        # default sep=","
    print(wrong.shape)                   # predict: how many columns?
    """)
    b.task("5.1", "Read the export correctly", """
        Read `CRM_PATH` into `crm` with the right separator and decimal mark, so that `lifetime_spend` becomes a **float** column.
        """, "crm", 'crm = pd.read_csv(CRM_PATH, sep=";", decimal=",")',
        ["Two parameters of `read_csv`: `sep` and `decimal`.", "`pd.read_csv(CRM_PATH, sep=';', decimal=',')`"], level=1,
        traps=[('crm = pd.read_csv(CRM_PATH, sep=";")', "`lifetime_spend` is still text ('92,20'). Add `decimal=','`."),
               ("crm = pd.read_csv(CRM_PATH)", "everything landed in ONE column. The separator is `;`.")])
    b.code("""
    # 🔍 After task 5.1: what types did pandas choose? Which columns look wrong?
    if "crm" in globals():
        crm.info()
        display(crm.head(10))
    else:
        print("Do task 5.1 first (create `crm`).")
    """)
    b.md("""
    ## 5.2 Missing values

    📘 **Concept**
    | Code | Does |
    |---|---|
    | `df.isna().sum()` | missing values per column |
    | `df.isna().mean()` | share missing per column |
    | `df.dropna(subset=["col"])` | drop rows where *col* is missing |
    | `df["col"].fillna(value)` | fill missing, e.g. with `0`, `"Unknown"`, `df["col"].median()` |

    **Drop or fill?** Drop when few rows are affected and they're random. Fill when the value has a clear meaning
    (missing spend = no purchase → 0) or you'd lose too much data (age → median). Always say which you did.

    ⚠️ **Trap:** text like `"unknown"` or `""` in a number column is **not** NaN to pandas. It makes the whole column text (`object`).
    `isna()` won't count it, and you only see it after converting (5.4).
    """)
    b.task("5.2", "Missing per column", """
        Number of missing values in each column of `crm` (a Series: column → count).
        """, "missing_per_col", "missing_per_col = crm.isna().sum()",
        ["`isna()` gives True/False for every cell; summing counts the Trues per column."], level=1, needs=["5.1"])
    b.task("5.3", "Share missing, worst first", """
        Share (0–1) of missing values per column, sorted from highest to lowest.
        """, "missing_share", "missing_share = crm.isna().mean().sort_values(ascending=False)",
        ["Like 5.2, but `.mean()` instead of `.sum()`, then sort.", "`crm.isna().mean().sort_values(ascending=False)`"],
        cmp={"ordered": True}, needs=["5.1"])

    b.md("""
    ## 5.3 Duplicates

    📘 `df.duplicated()` marks rows that repeat an earlier row (all columns equal). `df.duplicated(subset=["id"])`
    compares only some columns. `df.drop_duplicates(subset=..., keep="first" | "last")` removes them.

    The export has **two kinds** of duplicates: exact copy-paste repeats, and customers exported **twice** whose later
    row has an updated spend. For those, the **last** row is the truth.
    """)
    b.task("5.4", "Exact duplicates", """
        How many rows of `crm` are exact duplicates of an earlier row?
        """, "n_dupes", "n_dupes = crm.duplicated().sum()",
        ["`duplicated()` returns a boolean Series."], level=1, needs=["5.1"])
    b.task("5.5", "One row per customer", """
        Make `crm_nodup`: first drop exact duplicates, then keep only the **last** row for each `customer_id`.
        """, "crm_nodup", 'crm_nodup = crm.drop_duplicates().drop_duplicates(subset="customer_id", keep="last")',
        ["Chain two `drop_duplicates` calls. The second one uses `subset` and `keep`.",
         "`crm.drop_duplicates().drop_duplicates(subset='customer_id', keep='last')`"],
        traps=[('crm_nodup = crm.drop_duplicates().drop_duplicates(subset="customer_id")',
                "`keep='first'` (the default) keeps the OLD row. Updated rows are at the end, so use `keep='last'`."),
               ("crm_nodup = crm.drop_duplicates()", "exact duplicates are gone, but some customers still appear twice.")],
        needs=["5.1"])
    b.md("""
    ## 5.4 Fixing text and types

    📘 **Concept**
    - Normalise text before comparing it: `s.str.strip().str.title()` (" united states" → "United States").
    - Unify spellings with `s.replace({"old": "new"})`. Values not in the dict stay as they are.
      `s.map(dict)` turns every unmapped value into NaN.
    - Text → numbers: `pd.to_numeric(s, errors="coerce")` turns junk ("unknown") into NaN instead of crashing.
    - Impossible values → NaN: `s.where(condition)` keeps values where the condition is True, NaN elsewhere.
    - Text → dates: `pd.to_datetime(s, dayfirst=True)`.
    """)
    b.code("""
    # 🔍 How many spellings of each country are there?
    if "crm_nodup" in globals():
        display(crm_nodup["country"].value_counts())
    else:
        print("Do task 5.5 first (create `crm_nodup`).")
    """)
    b.task("5.6", "One spelling per country", """
        Make `clean_country` from `crm_nodup["country"]`: strip spaces, title-case, then replace these variants:
        `{"Usa": "United States", "Us": "United States", "Uk": "United Kingdom", "Brasil": "Brazil", "España": "Spain"}`.
        Check the result with `value_counts()`. There should be exactly 7 countries.
        """, "clean_country", """
        country_fix = {"Usa": "United States", "Us": "United States", "Uk": "United Kingdom",
                       "Brasil": "Brazil", "España": "Spain"}
        clean_country = crm_nodup["country"].str.strip().str.title().replace(country_fix)
        """,
        ["Chain: `.str.strip()` → `.str.title()` → `.replace(dict)`.",
         "Why `title()` before the dict? It turns 'USA', 'usa' and 'Usa' into the same 'Usa', so one dict key is enough."],
        traps=[("""
        country_fix = {"Usa": "United States", "Us": "United States", "Uk": "United Kingdom",
                       "Brasil": "Brazil", "España": "Spain"}
        clean_country = crm_nodup["country"].str.strip().str.title().map(country_fix)
        """, "`.map(dict)` makes every country that isn't in the dict NaN. Use `.replace(dict)`.")], needs=["5.5"])
    b.task("5.7", "Clean age", """
        Make `age_clean`: convert `crm_nodup["age"]` to numbers (junk → NaN), then set ages **outside 12–100** to NaN.
        """, "age_clean", """
        age_num = pd.to_numeric(crm_nodup["age"], errors="coerce")
        age_clean = age_num.where(age_num.between(12, 100))
        """,
        ["Step 1: `pd.to_numeric(..., errors='coerce')`. Step 2: `.where(condition)`.",
         "`age_num.where(age_num.between(12, 100))`"],
        traps=[('age_clean = pd.to_numeric(crm_nodup["age"], errors="coerce")',
                "the junk is gone, but impossible ages (-1, 0, 150, 230) are still there. Use `.where(...between(12, 100))`.")],
        needs=["5.5"])
    b.task("5.8", "Parse sign-up dates", """
        Make `signup`: `crm_nodup["signup_date"]` as datetimes. The format is **day/month/year**.
        """, "signup", 'signup = pd.to_datetime(crm_nodup["signup_date"], dayfirst=True)',
        ["`pd.to_datetime` with one extra argument.", "`dayfirst=True` (or `format='%d/%m/%Y'`)"],
        traps=[('signup = pd.to_datetime(crm_nodup["signup_date"], format="%m/%d/%Y", errors="coerce")',
                "month/day order is swapped. 15/12/2025 is the 15th of December. Use `dayfirst=True`.")],
        needs=["5.5"])
    b.task("5.9", "Newsletter as True/False", """
        Make `newsletter_bool` from `crm_nodup["newsletter"]`: strip + lower-case, then map
        `yes`, `y`, `true` → `True` and `no`, `n`, `false` → `False`.
        """, "newsletter_bool", """
        yes_no = {"yes": True, "y": True, "true": True, "no": False, "n": False, "false": False}
        newsletter_bool = crm_nodup["newsletter"].str.strip().str.lower().map(yes_no)
        """,
        ["Normalise first, then a dict with `.map()`. Here `map` is right: every value *should* be in the dict.",
         "Check: `newsletter_bool.isna().sum()` should be 0."], needs=["5.5"])
    b.task("5.10", "One letter for gender", """
        Make `gender_clean`: `"F"` or `"M"` from values like `" f"`, `"Female"`, `"male"`.
        """, "gender_clean", 'gender_clean = crm_nodup["gender"].str.strip().str[0].str.upper()',
        ["Strip spaces, take the first character with `.str[0]`, upper-case it."], needs=["5.5"])
    b.task("5.11", "The clean table", """
        Assemble `crm_clean`, a DataFrame with these columns in this order:
        `customer_id`, `signup_date` (from 5.8), `country` (5.6), `age` (5.7 with missing filled by the **median** age),
        `gender` (5.10), `newsletter` (5.9), `lifetime_spend` (missing → 0, assuming "no spend recorded = no purchase").
        """, "crm_clean", """
        crm_clean = pd.DataFrame({
            "customer_id": crm_nodup["customer_id"],
            "signup_date": signup,
            "country": clean_country,
            "age": age_clean.fillna(age_clean.median()),
            "gender": gender_clean,
            "newsletter": newsletter_bool,
            "lifetime_spend": crm_nodup["lifetime_spend"].fillna(0),
        })
        """,
        ["`pd.DataFrame({'col': series, ...})` builds a table from Series that share the same index.",
         "Alternative: `crm_clean = crm_nodup.copy()` and overwrite columns one by one."], level=3,
        needs=["5.5", "5.6", "5.7", "5.8", "5.9", "5.10"])

    b.md("""
    ## 5.5 Outliers

    📘 **Concept**: the **IQR rule** (box-plot rule, a Data Mining exam favourite):
    `IQR = Q3 − Q1`, outliers are below `Q1 − 1.5·IQR` or above `Q3 + 1.5·IQR`.
    Quantiles: `s.quantile(0.25)`, `s.quantile(0.75)`.

    What to do with them? **Investigate first.** A $999 coat is real. An age of 230 is an error.
    Options: keep (and say so) · remove · **cap** (`s.clip(lower, upper)`, called winsorizing) · analyse separately.
    For modelling (Part 12) capping is common. For revenue reporting, you never delete real sales.
    """)
    b.code("""
    # 🔍 Where would you draw the line for "unusually expensive"?
    products["retail_price"].describe()
    """)
    b.task("5.12", "Upper fence", """
        The IQR upper fence for `products["retail_price"]`: `Q3 + 1.5 * (Q3 - Q1)`.
        """, "upper_fence", """
        q1 = products["retail_price"].quantile(0.25)
        q3 = products["retail_price"].quantile(0.75)
        upper_fence = q3 + 1.5 * (q3 - q1)
        """,
        ["Two quantiles first, then the formula.", "`products['retail_price'].quantile(0.75)`"])
    b.task("5.13", "How many outliers?", """
        Number of products priced **above** the upper fence.
        """, "n_price_outliers", 'n_price_outliers = (products["retail_price"] > upper_fence).sum()',
        ["Mask + `.sum()`."], needs=["5.12"])
    b.task("5.14", "Cap the prices", """
        A Series `price_capped`: `retail_price` with every value above the fence replaced by the fence.
        """, "price_capped", 'price_capped = products["retail_price"].clip(upper=upper_fence)',
        ["`clip` has `lower` and `upper` parameters."], needs=["5.12"])
    b.md("""
    ## 🏁 Checkpoint 5: a reusable data-quality report
    Analysts reuse small functions. Write `quality_report(df)` that returns a DataFrame with **one row per column of df**
    (index = column names) and these columns:
    `dtype` (as text), `n_missing`, `pct_missing` (0–1), `n_unique` (distinct non-missing values).
    """)
    b.task("5.C1", "quality_report()", """
        Define the function. The check calls `quality_report(crm)`.
        """, "quality_report(crm)", """
        def quality_report(df):
            return pd.DataFrame({
                "dtype": df.dtypes.astype(str),
                "n_missing": df.isna().sum(),
                "pct_missing": df.isna().mean(),
                "n_unique": df.nunique(),
            })
        """,
        ["Each of `df.dtypes`, `df.isna().sum()`, `df.isna().mean()`, `df.nunique()` is a Series indexed by column name.",
         "Put them into `pd.DataFrame({...})` and return it."], level=3, needs=["5.1"],
        starter="def quality_report(df):\n    ...")
    b.md("""
    *Your note to Ana: list the 5 problems you found in the export and the rule you applied for each.* …
    """)


# =====================================================================================================
def part6(b):
    b.part("Part 6", "Join tables · Week 2, Monday", """
        users, products, orders, order_items, sessions = fresh_data()
        month = orders["created_at"].dt.to_period("M").astype(str)
        jul, aug, sep = orders[month == "2026-07"], orders[month == "2026-08"], orders[month == "2026-09"]
    """)
    b.md("""
    > 📨 **Ana:** *"To see revenue by category or by country we need the item table together with products and customers.
    > Build me one table I can slice any way."*

    ## 6.1 `merge`: the SQL JOIN of pandas

    📘 **Concept**: `left.merge(right, on="key", how="left")`
    | `how=` | keeps |
    |---|---|
    | `"inner"` (default) | only keys present in **both** tables |
    | `"left"` | **all** rows of the left table; no match → NaN |
    | `"outer"` | everything from both |

    - Different key names: `left_on="user_id", right_on="id"`.
    - Same column name in both tables (not the key) → suffixes `_x`, `_y`. Name them: `suffixes=("_order", "_item")`.
    - `indicator=True` adds a `_merge` column: `both` / `left_only` / `right_only`. That's how you find rows without a match (an *anti-join*).

    ⚠️ **The #1 merge bug: row explosion.** If the key isn't unique on the side you think it is, rows multiply and your
    revenue doubles silently. **Always compare row counts before and after**, or let pandas check it:
    `validate="many_to_one"` raises an error if the right side has duplicate keys.
    """)
    b.code("""
    # 🔍 Toy example: predict the number of rows for each `how`
    shop_customers = pd.DataFrame({"user_id": [1, 2, 3], "name": ["Ana", "Rui", "Mia"]})
    shop_orders = pd.DataFrame({"order_id": [10, 11, 12, 13], "user_id": [1, 1, 3, 4]})
    for how in ["inner", "left", "outer"]:
        print(how, len(shop_customers.merge(shop_orders, on="user_id", how=how)))
    shop_customers.merge(shop_orders, on="user_id", how="left", indicator=True)
    """)
    b.task("6.1", "Items + products", """
        `items_prod`: `order_items` left-merged with `products` on `product_id`.
        It must have **exactly as many rows as `order_items`**. Check it with `len()`.
        """, "items_prod", 'items_prod = order_items.merge(products, on="product_id", how="left")',
        ["`order_items.merge(products, on=..., how=...)`",
         "Add `validate='many_to_one'` to let pandas prove each item matches at most one product."], level=1)
    b.task("6.2", "+ customers", """
        `items`: `items_prod` left-merged with the customer columns `user_id, age, gender, country, traffic_source`
        from `users` (only those 5 columns!).
        """, "items", """
        items = items_prod.merge(users[["user_id", "age", "gender", "country", "traffic_source"]],
                                 on="user_id", how="left")
        """,
        ["Select the 5 columns of users first, then merge on `user_id`.",
         "If you merge all of `users`, its `created_at` (sign-up date) collides with the order date → `created_at_x/_y`."],
        traps=[('items = items_prod.merge(users, on="user_id", how="left")',
                "you merged all user columns. The sign-up `created_at` clashed with the order date and became `created_at_x`/`created_at_y`.")],
        needs=["6.1"])
    b.task("6.3", "Registered but never ordered", """
        How many users have **no orders at all**? (anti-join: use `merge(..., indicator=True)` or `~isin`)
        """, "n_no_orders", 'n_no_orders = (~users["user_id"].isin(orders["user_id"])).sum()',
        ["Option A: `~users['user_id'].isin(orders['user_id'])` then `.sum()`.",
         "Option B: `users.merge(orders[['user_id']].drop_duplicates(), how='left', indicator=True)` and count `left_only`."])
    b.md("""
    ### 🐛 Spot the bug
    A colleague wanted one row per order item with the order's info attached, and wrote:
    ```python
    lines = orders.merge(order_items, on="user_id")
    ```
    Run it in your head: a customer with 3 orders and 5 items gets 3 × 5 = 15 rows. Every order is paired with every item
    of that customer.
    """)
    b.code("""
    lines_bad = orders.merge(order_items, on="user_id")
    print(f"{len(order_items):,} items, but the bad merge has {len(lines_bad):,} rows")
    """)
    b.task("6.4", "Fix the merge", """
        `order_lines`: one row per **order item**, with the order's columns attached. Use the right key and readable
        suffixes `("_order", "_item")`. The row count must equal `len(order_items)`.
        """, "order_lines", 'order_lines = orders.merge(order_items, on="order_id", suffixes=("_order", "_item"))',
        ["Which column really links an item to its order?", "`on='order_id'`"],
        custom="""
        ok = isinstance(u, pd.DataFrame) and len(u) == len(g['order_items']) and 'order_item_id' in u.columns
        msg = '' if ok else f"Expected {len(g['order_items']):,} rows (one per item), you have {len(u) if hasattr(u, '__len__') else '?'}. Join on the order key."
        """, level=3)
    b.md("""
    ## 6.2 `concat`: stacking tables

    📘 `pd.concat([df1, df2, df3], ignore_index=True)` puts tables **under each other** (same columns), for example monthly
    exports. `axis=1` puts them side by side (rare; prefer merge). `ignore_index=True` renumbers the rows 0…n−1.
    """)
    b.task("6.5", "Stack the quarter", """
        The Part setup made three monthly tables `jul`, `aug`, `sep`. Stack them into `q3_orders` with a fresh 0…n−1 index.
        """, "q3_orders", "q3_orders = pd.concat([jul, aug, sep], ignore_index=True)",
        ["`pd.concat` takes a **list** of DataFrames."], level=1, cmp={"ignore_index": True})
    b.md("""
    ## 🏁 Checkpoint 6
    > 📨 **Ana:** *"How much did we actually earn from customers in China?"* Revenue counts only items that were **not**
    > Cancelled or Returned (you did this mask in 2.7).
    """)
    b.task("6.C1", "Revenue from China", """
        Sum of `sale_price` in `items` for country `"China"`, excluding Cancelled and Returned items.
        """, "revenue_china", """
        ok_status = ~items["status"].isin(["Cancelled", "Returned"])
        revenue_china = items.loc[ok_status & (items["country"] == "China"), "sale_price"].sum()
        """,
        ["Two masks with `&`, then `loc[..., 'sale_price'].sum()`."], needs=["6.2"],
        traps=[('revenue_china = items.loc[items["country"] == "China", "sale_price"].sum()',
                "this includes cancelled and returned items, money we never kept.")])


# =====================================================================================================
def part7(b):
    b.part("Part 7", "groupby: the heart of analytics · Tuesday–Wednesday", ITEMS_SETUP)
    b.md("""
    > 📨 **Ana:** *"Now the real work: a category scorecard. Revenue, orders, margin, returns, all on one page."*

    ### 📏 Metric definitions (agree on these before computing anything)
    | Metric | Definition here | pandas |
    |---|---|---|
    | **Revenue** | sum of `sale_price` of items **not** Cancelled/Returned (`sales` table) | `sales["sale_price"].sum()` |
    | **Orders** | number of **distinct** orders | `sales["order_id"].nunique()` |
    | **AOV** (average order value) | revenue / orders | ratio of the two above |
    | **Profit** | `sale_price − cost` | `sales["profit"].sum()` |
    | **Margin %** | profit / revenue | ratio |
    | **Return rate** | returned items / all items (in `items`) | `items["status"].eq("Returned").mean()` |

    The Part setup created `items` (all items, every status) and `sales` (only items we kept the money for).

    ## 7.1 split → apply → combine

    📘 `df.groupby("key")["value"].agg_function()` = *split* rows into groups by key, *apply* a function to each group's values,
    *combine* into a result indexed by the key.

    ```
    category  sale_price          groupby("category")["sale_price"].sum()
    Jeans        100     ─┐
    Jeans         50     ─┴─► Jeans   150
    Socks         10     ───► Socks    10
    ```
    | Function | Counts / computes |
    |---|---|
    | `.sum()` `.mean()` `.median()` `.min()` `.max()` | as usual, per group |
    | `.count()` | non-missing values per group |
    | `.size()` | rows per group (including missing) |
    | `.nunique()` | **distinct** values per group (e.g. orders, customers) |

    ⚠️ **Trap:** one order has several items, so `count()` on `order_id` counts *items*. Number of orders = `nunique()`.
    """)
    b.code("""
    # 🔍 Predict which department earns more, then run
    print(sales.groupby("department")["sale_price"].sum())
    print()
    # as_index=False / reset_index() give a normal table instead of an indexed Series:
    sales.groupby("department", as_index=False)["sale_price"].sum()
    """)
    b.task("7.1", "Revenue by category", """
        Revenue per `category` from `sales`, highest first.
        """, "revenue_by_category",
        'revenue_by_category = sales.groupby("category")["sale_price"].sum().sort_values(ascending=False)',
        ["groupby category → take sale_price → sum → sort.", "`.sort_values(ascending=False)` at the end"], level=1,
        cmp={"ordered": True},
        traps=[('revenue_by_category = items.groupby("category")["sale_price"].sum().sort_values(ascending=False)',
                "you used `items`: it includes cancelled and returned items. Revenue comes from `sales`.")])
    b.task("7.2", "Orders by country", """
        Number of **distinct orders** per `country` (from `sales`), highest first.
        """, "orders_by_country",
        'orders_by_country = sales.groupby("country")["order_id"].nunique().sort_values(ascending=False)',
        ["Which function counts distinct values?", "`['order_id'].nunique()`"], cmp={"ordered": True},
        traps=[('orders_by_country = sales.groupby("country")["order_id"].count().sort_values(ascending=False)',
                "`count()` counts items (rows). An order with 3 items counts 3 times. Use `nunique()`.")])
    b.task("7.3", "Average item price by department", """
        Mean `sale_price` per `department` (from `sales`).
        """, "avg_price_by_dept", 'avg_price_by_dept = sales.groupby("department")["sale_price"].mean()',
        ["Same pattern, `.mean()`."], level=1)

    b.md("""
    ## 7.2 Several metrics at once: `agg` and **named aggregation**

    📘 **Concept**
    ```python
    sales.groupby("category").agg(
        revenue=("sale_price", "sum"),      # new_column=(source_column, function)
        orders=("order_id", "nunique"),
        items=("order_item_id", "count"),
    )
    ```
    Named aggregation gives clean column names. Ratios (AOV, margin) are computed **after** aggregating:
    `kpis["aov"] = kpis["revenue"] / kpis["orders"]`.

    ⚠️ **Trap:** the *average of ratios* ≠ the *ratio of totals*. AOV is total revenue / total orders, not the mean of item prices.
    """)
    b.code("""
    # 🔍 KPIs per department
    dept = sales.groupby("department").agg(revenue=("sale_price", "sum"),
                                           orders=("order_id", "nunique"),
                                           customers=("user_id", "nunique"))
    dept["aov"] = dept["revenue"] / dept["orders"]
    dept.round(1)
    """)
    b.task("7.4", "Category KPIs", """
        `cat_kpis`: one row per `category` with columns `revenue` (sum of sale_price), `orders` (distinct order_id),
        `items` (count of order_item_id), `avg_item_price` (mean sale_price), sorted by revenue, highest first.
        """, "cat_kpis", """
        cat_kpis = (sales.groupby("category")
                         .agg(revenue=("sale_price", "sum"),
                              orders=("order_id", "nunique"),
                              items=("order_item_id", "count"),
                              avg_item_price=("sale_price", "mean"))
                         .sort_values("revenue", ascending=False))
        """,
        ["Named aggregation: `.agg(revenue=('sale_price', 'sum'), ...)`.", "Then `.sort_values('revenue', ascending=False)`."],
        cmp={"ordered": True, "allow_extra": True})
    b.task("7.5", "AOV per category", """
        Add a column `aov` to `cat_kpis` = revenue / orders.
        """, 'cat_kpis["aov"]', 'cat_kpis["aov"] = cat_kpis["revenue"] / cat_kpis["orders"]',
        ["A new column computed from two existing ones."], level=1, needs=["7.4"],
        traps=[('cat_kpis["aov"] = cat_kpis["avg_item_price"]', "that's the average *item* price. AOV is per *order*: revenue / orders.")])
    b.task("7.6", "Top 10 brands (with enough volume)", """
        `brand_top`: brands with **at least 50 items sold**, top 10 by revenue, highest first.
        Columns: `revenue`, `items`.
        """, "brand_top", """
        brand_stats = sales.groupby("brand").agg(revenue=("sale_price", "sum"), items=("order_item_id", "count"))
        brand_top = brand_stats[brand_stats["items"] >= 50].sort_values("revenue", ascending=False).head(10)
        """,
        ["Aggregate first, **then** filter the aggregated table (like SQL `HAVING`), then sort and take 10.",
         "`brand_stats[brand_stats['items'] >= 50]`"], level=3, cmp={"ordered": True})

    b.md("""
    ## 7.3 Several keys and `unstack`

    📘 `groupby(["a", "b"])` gives a result with a two-level (Multi)Index. `.unstack()` moves the inner level into columns,
    turning a long list into a readable matrix. `.stack()` does the reverse.
    """)
    b.task("7.7", "Revenue by department × traffic source", """
        Revenue (from `sales`) grouped by `department` **and** `traffic_source`, as a Series with a 2-level index.
        """, "rev_dept_source", 'rev_dept_source = sales.groupby(["department", "traffic_source"])["sale_price"].sum()',
        ["Pass a list of two columns to groupby."])
    b.task("7.8", "As a matrix", """
        Turn `rev_dept_source` into a DataFrame: departments as rows, traffic sources as columns.
        """, "rev_matrix", "rev_matrix = rev_dept_source.unstack()",
        ["One method call."], level=1, needs=["7.7"])

    b.md("""
    ## 7.4 `transform`: group values back on every row

    📘 `agg` gives **one row per group**. `transform` gives **one value per original row** (the group's result repeated),
    so you can compare each row to its group:
    ```python
    sales["cat_avg"] = sales.groupby("category")["sale_price"].transform("mean")
    sales["share_of_cat"] = sales["sale_price"] / sales.groupby("category")["sale_price"].transform("sum")
    ```
    Use it for: share within a group, difference from the group average, ranking inside groups.
    """)
    b.task("7.9", "Category share inside its department", """
        `share_in_dept`: for every (department, category) pair, the category's share (0–1) of its **department's** revenue.
        Steps: revenue by `["department", "category"]` → divide by the department total, computed with
        `groupby(level="department").transform("sum")`.
        """, "share_in_dept", """
        cat_rev = sales.groupby(["department", "category"])["sale_price"].sum()
        share_in_dept = cat_rev / cat_rev.groupby(level="department").transform("sum")
        """,
        ["`cat_rev.groupby(level='department')` groups by an index level instead of a column.",
         "Sanity check: `share_in_dept.groupby(level=0).sum()` should give 1.0 for both departments."], level=3,
        traps=[("""
        cat_rev = sales.groupby(["department", "category"])["sale_price"].sum()
        share_in_dept = cat_rev / cat_rev.sum()
        """, "that's the share of the TOTAL revenue. The task wants the share within the department.")])
    b.task("7.10", "Items priced above their category average", """
        How many rows of `sales` have a `sale_price` **above the average sale_price of their own category**?
        """, "n_above", """
        cat_avg = sales.groupby("category")["sale_price"].transform("mean")
        n_above = (sales["sale_price"] > cat_avg).sum()
        """,
        ["`transform('mean')` gives each row its category's average.", "Compare, then `.sum()`."])

    b.md("""
    ## 7.5 `pivot_table` and `crosstab`

    📘 **Concept**
    - `df.pivot_table(index="a", columns="b", values="v", aggfunc="sum", fill_value=0, margins=False)` is the Excel pivot
      table: groupby on two keys + unstack in one call.
    - `pd.crosstab(df["a"], df["b"])` counts combinations. `normalize="index"` gives shares per row (each row sums to 1).

    💡 **Rate trick:** the mean of a boolean column is a rate:
    `items.assign(is_returned=items["status"].eq("Returned")).groupby("category")["is_returned"].mean()`
    """)
    b.code("""
    # 🔍 Items by department and status
    items.pivot_table(index="department", columns="status", values="order_item_id", aggfunc="count", margins=True)
    """)
    b.task("7.11", "Status mix per category", """
        `status_pivot`: from `items` (all statuses), rows = `category`, columns = `status`, values = number of items
        (`count` of `order_item_id`), missing combinations = 0.
        """, "status_pivot", """
        status_pivot = items.pivot_table(index="category", columns="status", values="order_item_id",
                                         aggfunc="count", fill_value=0)
        """,
        ["`pivot_table(index=..., columns=..., values=..., aggfunc=..., fill_value=0)`"])
    b.task("7.12", "Return rate by category", """
        `return_rate_by_cat`: share (0–1) of items with status `"Returned"` per category (from `items`), highest first.
        """, "return_rate_by_cat", """
        return_rate_by_cat = (items.assign(is_returned=items["status"].eq("Returned"))
                                   .groupby("category")["is_returned"].mean()
                                   .sort_values(ascending=False))
        """,
        ["Make a boolean column (`assign` or a new column), then groupby + mean.",
         "Without a new column: `items['status'].eq('Returned').groupby(items['category']).mean()`"],
        cmp={"ordered": True},
        traps=[("""
        return_rate_by_cat = (sales.assign(is_returned=sales["status"].eq("Returned"))
                                   .groupby("category")["is_returned"].mean().sort_values(ascending=False))
        """, "`sales` contains no returned items by definition. Use `items`.")])
    b.task("7.13", "Gender mix per traffic source", """
        `source_gender`: `pd.crosstab` of `users["traffic_source"]` (rows) × `users["gender"]` (columns), as shares per row.
        """, "source_gender", 'source_gender = pd.crosstab(users["traffic_source"], users["gender"], normalize="index")',
        ["`normalize='index'` makes each row sum to 1."], level=1)

    b.md("""
    ## 🏁 Checkpoint 7: the category scorecard
    > 📨 **Ana:** *"One table, one row per category: revenue, profit, orders, margin and return rate, biggest revenue first.
    > Then tell me which big category worries you."*
    """)
    b.task("7.C1", "Scorecard", """
        `scorecard` with index `category` and columns in this order: `revenue`, `profit`, `orders` (from `sales`),
        `margin` = profit / revenue, `return_rate` (from `items`, as in 7.12). Sort by revenue, highest first.
        """, "scorecard", """
        scorecard = sales.groupby("category").agg(revenue=("sale_price", "sum"),
                                                  profit=("profit", "sum"),
                                                  orders=("order_id", "nunique"))
        scorecard["margin"] = scorecard["profit"] / scorecard["revenue"]
        scorecard["return_rate"] = items["status"].eq("Returned").groupby(items["category"]).mean()
        scorecard = scorecard.sort_values("revenue", ascending=False)
        """,
        ["Named agg for the three sums/counts, then two derived columns, then sort.",
         "Assigning a Series indexed by category to `scorecard[...]` aligns on the index automatically."], level=3,
        cmp={"ordered": True})
    b.code("""
    # Format for humans (only for display; keep the raw numbers for calculations)
    scorecard.style.format({"revenue": "{:,.0f}", "profit": "{:,.0f}", "orders": "{:,}",
                            "margin": "{:.1%}", "return_rate": "{:.1%}"}) if "scorecard" in globals() else None
    """)
    b.md("*Your answer: which category has high revenue AND a high return rate? What would you suggest?* …")


# =====================================================================================================
def part8(b):
    b.part("Part 8", "Charts that make a point · Thursday", ITEMS_SETUP + """
sns.set_theme(style="whitegrid")
""")
    b.md("""
    > 📨 **Ana:** *"Tables are fine for me, but the board wants pictures. Each chart should answer one question."*

    ## 8.1 Anatomy: figure, axes, and who draws what

    📘 **Concept**
    - **matplotlib** is the engine. A **Figure** is the canvas, an **Axes** (`ax`) is one chart on it.
      Standard start: `fig, ax = plt.subplots(figsize=(8, 4))`.
    - **pandas** plots straight from data: `series.plot(kind="bar", ax=ax)`. Fast for quick looks.
    - **seaborn** draws statistical charts from a DataFrame with column names:
      `sns.histplot(data=df, x="col", hue="group", ax=ax)`. It returns the `ax`.
    - Finish every chart: `ax.set_title(...)`, `ax.set_xlabel(...)`, `ax.set_ylabel(...)`.
      Many graders and managers mark a chart down when the labels are missing.

    In the tasks below, keep your chart in a variable called **`ax`**. The check reads it (number of bars, title, labels…).
    `show_me("8.x")` draws a reference chart.
    """)
    b.code("""
    # 🔍 Same data, three ways
    rev = sales.groupby("department")["sale_price"].sum()

    fig, axes = plt.subplots(1, 3, figsize=(13, 3.5))
    axes[0].bar(rev.index, rev.values)                         # pure matplotlib
    axes[0].set_title("matplotlib")
    rev.plot(kind="bar", ax=axes[1], title="pandas .plot")      # pandas
    sns.barplot(x=rev.index, y=rev.values, ax=axes[2])          # seaborn
    axes[2].set_title("seaborn")
    plt.tight_layout()
    plt.show()
    """)
    b.md("""
    ## 8.2 Distributions: histogram and box plot

    📘 *"What do typical values look like? Is it skewed? Outliers?"*
    - `sns.histplot(data=df, x="col", bins=30)`. Add `hue="group"` to compare groups, `stat="density", common_norm=False`
      to compare shapes of groups of different sizes, `log_scale=True` for long right tails (prices, revenue).
    - `sns.boxplot(data=df, x="group", y="col")`: median, quartiles, IQR whiskers, outliers as dots (Part 5 rule!).
    """)
    b.code("""
    fig, ax = plt.subplots(figsize=(8, 3.5))
    sns.histplot(data=products, x="retail_price", bins=40, ax=ax)
    ax.set_title("Most products are cheap, with a long tail of expensive ones")
    ax.set_xlabel("Retail price, $")
    plt.show()
    """)
    b.task("8.1", "Age histogram", """
        Histogram of `users["age"]` with **30 bins**, a title and an x-axis label. Keep the chart in `ax`.
        """, "ax", """
        fig, ax = plt.subplots(figsize=(8, 3.5))
        sns.histplot(data=users, x="age", bins=30, ax=ax)
        ax.set_title("Age of our customers")
        ax.set_xlabel("Age, years")
        """,
        ["`fig, ax = plt.subplots()` → `sns.histplot(..., bins=30, ax=ax)` → `ax.set_title(...)`, `ax.set_xlabel(...)`."],
        level=1, plot={"patches": 30, "title": True, "xlabel": True})
    b.task("8.2", "Prices by department", """
        Histogram of `sales["sale_price"]` with **50 bins**, split by `department` with `hue`, on a **log** x-axis
        (`log_scale=True`), plus a title.
        """, "ax", """
        fig, ax = plt.subplots(figsize=(8, 3.5))
        sns.histplot(data=sales, x="sale_price", hue="department", bins=50, log_scale=True, ax=ax)
        ax.set_title("Item prices by department (log scale)")
        """,
        ["`sns.histplot(data=sales, x='sale_price', hue='department', bins=50, log_scale=True, ax=ax)`"],
        plot={"min_patches": 50, "legend": True, "title": True})
    b.task("8.3", "Box plot", """
        Box plot of `sale_price` (y) by `department` (x) from `sales`, with a title.
        """, "ax", """
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.boxplot(data=sales, x="department", y="sale_price", ax=ax)
        ax.set_title("Sale price by department")
        """,
        ["`sns.boxplot(data=..., x=..., y=..., ax=ax)`"], level=1, plot={"xticks": ["Men", "Women"], "title": True})
    b.md("""
    ## 8.3 Comparing categories: bar charts

    📘 **Aggregate first, then plot** (pandas does the math, the chart only shows it).
    - Many categories or long names → **horizontal** bars, **sorted**, biggest on top.
      With `.plot.barh()` the first row is drawn at the bottom, so sort ascending first: `s.sort_values().plot.barh(ax=ax)`.
    - `sns.countplot(data=df, y="col", order=df["col"].value_counts().index)` counts rows for you.
    - Bars must start at 0, otherwise small differences look huge.
    """)
    b.task("8.4", "Top 10 categories by revenue", """
        A **horizontal** bar chart of the 10 categories with the highest revenue (from `sales`),
        **longest bar on top**, with a title and an x-label.
        """, "ax", """
        top10 = sales.groupby("category")["sale_price"].sum().nlargest(10)
        fig, ax = plt.subplots(figsize=(8, 4))
        top10.sort_values().plot.barh(ax=ax)
        ax.set_title("Top 10 categories by revenue")
        ax.set_xlabel("Revenue, $")
        ax.set_ylabel("")
        """,
        ["Compute the top 10 Series first (`nlargest(10)`).",
         "`.sort_values().plot.barh(ax=ax)` puts the biggest bar at the top."],
        plot={"patches": 10, "biggest_on_top": True, "title": True, "xlabel": True})
    b.md("""
    ## 8.4 Relationships: scatter and heatmap

    📘 `sns.scatterplot(data=df, x="a", y="b", alpha=0.3, s=10)`: with many points, use transparency (`alpha`) or a sample
    (`df.sample(5000, random_state=0)`). `sns.heatmap(matrix, annot=True, fmt=".2f", cmap="Blues")` colours a table,
    for example a correlation matrix (`df[cols].corr()`) or a pivot table.
    """)
    b.task("8.5", "Cost vs price", """
        Scatter plot of `products`: x = `cost`, y = `retail_price`, with `alpha=0.3`, title and both axis labels.
        """, "ax", """
        fig, ax = plt.subplots(figsize=(6, 5))
        sns.scatterplot(data=products, x="cost", y="retail_price", alpha=0.3, s=10, ax=ax)
        ax.set_title("Price grows with cost")
        ax.set_xlabel("Cost, $")
        ax.set_ylabel("Retail price, $")
        """,
        ["`sns.scatterplot(data=products, x='cost', y='retail_price', alpha=0.3, ax=ax)`"],
        plot={"points": 1000, "title": True, "xlabel": True, "ylabel": True})
    b.task("8.6", "Heatmap of average item price", """
        `pivot_table` of `sales`: rows = `traffic_source`, columns = `department`, values = mean `sale_price`.
        Draw it with `sns.heatmap(..., annot=True, fmt=".1f")` and a title.
        """, "ax", """
        pt = sales.pivot_table(index="traffic_source", columns="department", values="sale_price", aggfunc="mean")
        fig, ax = plt.subplots(figsize=(5, 4))
        sns.heatmap(pt, annot=True, fmt=".1f", cmap="Blues", ax=ax)
        ax.set_title("Average item price, $")
        """,
        ["Build the pivot first, then `sns.heatmap(pt, annot=True, fmt='.1f', ax=ax)`."],
        plot={"heatmap": True, "annot": True, "title": True})
    b.md("""
    ## 8.5 Trends: line charts

    📘 Time on the x-axis → a line. Aggregate per month first (Part 9 goes deeper):
    `monthly = sales.groupby(sales["created_at"].dt.to_period("M"))["sale_price"].sum()`.
    Drop the **incomplete current month**. A half month always looks like a crash.
    """)
    b.task("8.7", "Monthly revenue since 2024", """
        Line chart of monthly revenue (from `sales`) from **January 2024** on, with a title and a y-label.
        """, "ax", """
        monthly = sales.groupby(sales["created_at"].dt.to_period("M"))["sale_price"].sum()
        monthly = monthly[monthly.index >= pd.Period("2024-01", "M")]
        fig, ax = plt.subplots(figsize=(9, 3.5))
        monthly.plot(ax=ax, marker="o")
        ax.set_title("Revenue has been accelerating since early 2026")
        ax.set_ylabel("Revenue, $")
        ax.set_xlabel("")
        """,
        ["Group by month with `.dt.to_period('M')`, filter `>= pd.Period('2024-01', 'M')`, then `.plot(ax=ax)`."],
        plot={"lines": True, "title": True, "ylabel": True})
    b.md("""
    ## 8.6 Choosing the chart and making it honest

    | Question | Chart |
    |---|---|
    | How are values distributed? | histogram, box plot |
    | Which category is biggest? | sorted (horizontal) bar |
    | How does it change over time? | line |
    | Are two numbers related? | scatter (+ correlation) |
    | Two categorical dimensions at once | heatmap of a pivot table |
    | Parts of a whole | stacked bar, or a pie with **≤ 4** slices |

    **Checklist before sending:** the title states the insight ("Returns doubled in Q3"), not just the topic ("Returns") ·
    units on axes · sorted bars · bars start at zero · no incomplete periods · readable labels (`rotation=45` or horizontal bars) ·
    `plt.tight_layout()`.

    ## 🏁 Checkpoint 8: a two-panel slide
    """)
    b.task("8.C1", "Two charts, one figure", """
        `fig, axes = plt.subplots(1, 2, figsize=(13, 4))`. **Left:** revenue by department (bar). **Right:** monthly revenue
        line since 2025‑01. Give each chart a title. The check reads `axes`.
        """, "axes", """
        fig, axes = plt.subplots(1, 2, figsize=(13, 4))
        sales.groupby("department")["sale_price"].sum().plot.bar(ax=axes[0], rot=0)
        axes[0].set_title("Men's slightly ahead of women's")
        m = sales.groupby(sales["created_at"].dt.to_period("M"))["sale_price"].sum()
        m[m.index >= pd.Period("2025-01", "M")].plot(ax=axes[1])
        axes[1].set_title("Monthly revenue keeps growing")
        plt.tight_layout()
        """,
        ["`axes[0]` and `axes[1]` are two separate Axes. Pass `ax=axes[0]` to the first plot, etc."], level=3,
        plot={"n_axes": 2, "any_content": True, "title": True})
