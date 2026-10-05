"""Parts 9-12 + Appendix."""
from content_b import ITEMS_SETUP

ORDER_REV = ITEMS_SETUP + """
# one row per PAID order: who, when, how much
order_rev = (sales.groupby(["order_id", "user_id"], as_index=False)
                  .agg(created_at=("created_at", "first"), revenue=("sale_price", "sum")))
"""

CUSTOMERS = ORDER_REV + """
customers = order_rev.groupby("user_id").agg(first_order=("created_at", "min"),
                                             last_order=("created_at", "max"),
                                             n_orders=("order_id", "nunique"),
                                             revenue=("revenue", "sum"))
rfm = pd.DataFrame({"recency": (TODAY - customers["last_order"]).dt.days,
                    "frequency": customers["n_orders"],
                    "monetary": customers["revenue"]})
"""


# =====================================================================================================
def part9(b):
    b.part("Part 9", "KPIs over time · Friday", ITEMS_SETUP + """
sales["month"] = sales["created_at"].dt.to_period("M")
""")
    b.md("""
    > 📨 **Ana:** *"Board meeting on Monday. I need the monthly KPI table (revenue, orders, customers, AOV), growth month over
    > month and year over year, and an honest answer: are we growing because we have more customers or because they spend more?"*

    ## 9.1 Grouping by time

    📘 **Concept**
    - Month key: `df["created_at"].dt.to_period("M")` (a `Period`, e.g. `2026-09`), then a normal `groupby`.
      Weeks: `"W"`, quarters: `"Q"`, years: `"Y"`.
    - Alternative: `df.set_index("created_at").resample("MS")["sale_price"].sum()` (time index required; `"MS"` = month start).
    - Compare periods with `pd.Period("2025-01", "M")`.
    - ⚠️ Our data ends on 30 Sep 2026, so September is complete. In real life, **the current month is always incomplete**.
      Cut it off or label it, or your chart shows a fake crash.
    """)
    b.task("9.1", "Monthly revenue", """
        Revenue per month (from `sales`, using the `month` column), in calendar order.
        """, "monthly_rev", 'monthly_rev = sales.groupby("month")["sale_price"].sum()',
        ["`groupby('month')` sorts months automatically."], level=1)
    b.task("9.2", "Monthly KPI table", """
        `kpi`: one row per month **from 2024-01 on**, columns `revenue`, `orders` (distinct), `customers` (distinct `user_id`),
        `aov` (= revenue / orders).
        """, "kpi", """
        recent = sales[sales["month"] >= pd.Period("2024-01", "M")]
        kpi = recent.groupby("month").agg(revenue=("sale_price", "sum"),
                                          orders=("order_id", "nunique"),
                                          customers=("user_id", "nunique"))
        kpi["aov"] = kpi["revenue"] / kpi["orders"]
        """,
        ["Filter months first, then named aggregation, then the ratio.",
         "`sales[sales['month'] >= pd.Period('2024-01', 'M')]`"], cmp={"allow_extra": True})
    b.md("""
    ## 9.2 Change over time

    📘 **Concept**
    | Code | Meaning |
    |---|---|
    | `s.diff()` | change vs previous row (absolute) |
    | `s.pct_change()` | change vs previous row (relative): **MoM** growth on monthly data |
    | `s.pct_change(12)` | vs 12 rows earlier: **YoY** on monthly data (removes seasonality) |
    | `s.shift(1)` | the previous row's value next to the current one (lag) |
    | `s.rolling(3).mean()` | 3-month moving average: smooths noise |
    | `s.cumsum()` | running total (year-to-date) |

    ⚠️ Rows must be **sorted by time** and have **no missing months**, otherwise `shift(12)` is not "a year ago".
    """)
    b.code("""
    # 🔍 Predict the first value of each column, then run
    demo = pd.Series([100, 110, 99, 120], index=pd.period_range("2026-01", periods=4, freq="M"))
    pd.DataFrame({"value": demo, "diff": demo.diff(), "mom": demo.pct_change().round(3),
                  "prev": demo.shift(1), "roll2": demo.rolling(2).mean(), "cum": demo.cumsum()})
    """)
    b.task("9.3", "MoM growth", """
        Add `kpi["mom"]`: month-over-month revenue growth (a fraction, e.g. 0.05 = +5%).
        """, 'kpi["mom"]', 'kpi["mom"] = kpi["revenue"].pct_change()',
        ["One method on the revenue column."], level=1, needs=["9.2"])
    b.task("9.4", "Smoothed revenue", """
        Add `kpi["rev_3m"]`: 3-month moving average of revenue.
        """, 'kpi["rev_3m"]', 'kpi["rev_3m"] = kpi["revenue"].rolling(3).mean()',
        ["`.rolling(window).mean()`"], needs=["9.2"])
    b.task("9.5", "YoY growth", """
        Add `kpi["yoy"]`: revenue growth vs the **same month one year earlier**. (The 2024 rows will be NaN. Why?)
        """, 'kpi["yoy"]', 'kpi["yoy"] = kpi["revenue"].pct_change(12)',
        ["`pct_change` takes a number of periods."], needs=["9.2"],
        traps=[('kpi["yoy"] = kpi["revenue"].pct_change()', "that's month over month. A year ago is 12 rows back.")])
    b.task("9.6", "Best month", """
        The month (the index label) with the highest revenue in `kpi`.
        """, "best_month", 'best_month = kpi["revenue"].idxmax()', ["`idxmax()`"], level=1, needs=["9.2"])
    b.task("9.7", "Year-to-date growth", """
        Revenue Jan–Sep 2026 vs Jan–Sep 2025 as growth (fraction): `ytd26 / ytd25 - 1`. Use `sales["created_at"]`.
        """, "ytd_growth", """
        d = sales["created_at"]
        ytd26 = sales.loc[(d >= "2026-01-01") & (d < "2026-10-01"), "sale_price"].sum()
        ytd25 = sales.loc[(d >= "2025-01-01") & (d < "2025-10-01"), "sale_price"].sum()
        ytd_growth = ytd26 / ytd25 - 1
        """,
        ["Two half-open date filters (Part 4!), two sums, one ratio.",
         "Comparing the same months removes seasonality. Comparing Jan–Sep with a full year would be unfair."],
        traps=[("""
        d = sales["created_at"]
        ytd_growth = sales.loc[d.dt.year == 2026, "sale_price"].sum() / sales.loc[d.dt.year == 2025, "sale_price"].sum() - 1
        """, "you compared 9 months of 2026 with 12 months of 2025. Compare the same months (Jan–Sep).")])
    b.task("9.8", "Running total 2026", """
        `cum_2026`: cumulative revenue by month for 2026 only (from `monthly_rev`).
        """, "cum_2026", "cum_2026 = monthly_rev[monthly_rev.index.year == 2026].cumsum()",
        ["A PeriodIndex has `.year`. Filter, then `.cumsum()`."], needs=["9.1"])
    b.md("""
    ## 🏁 Checkpoint 9: what drives the growth?
    Revenue = customers × orders per customer × AOV. Compare **September 2026 vs September 2025** in `kpi`.
    """)
    b.task("9.C1", "Customer growth", """
        Growth (fraction) of `customers` in Sep 2026 vs Sep 2025. Rows: `kpi.loc[pd.Period("2026-09", "M")]`.
        """, "customers_growth", """
        sep26, sep25 = kpi.loc[pd.Period("2026-09", "M")], kpi.loc[pd.Period("2025-09", "M")]
        customers_growth = sep26["customers"] / sep25["customers"] - 1
        """, ["`kpi.loc[period, 'customers']`"], needs=["9.2"])
    b.task("9.C2", "AOV growth", """
        Growth (fraction) of `aov` in Sep 2026 vs Sep 2025.
        """, "aov_growth", """
        aov_growth = kpi.loc[pd.Period("2026-09", "M"), "aov"] / kpi.loc[pd.Period("2025-09", "M"), "aov"] - 1
        """, ["Same pattern as 9.C1."], needs=["9.2"])
    b.code("""
    # Board chart: two lines on one axis would hide the smaller one. Use two panels.
    if "kpi" in globals():
        fig, axes = plt.subplots(1, 2, figsize=(13, 3.5))
        kpi["customers"].plot(ax=axes[0], title="Paying customers per month")
        kpi["aov"].plot(ax=axes[1], title="Average order value, $")
        plt.tight_layout(); plt.show()
    """)
    b.md("*Your answer to Ana: is growth driven by more customers or bigger baskets? One sentence with both numbers.* …")


# =====================================================================================================
def part10(b):
    b.part("Part 10", "Customer analytics: Pareto, cohorts, RFM, churn, funnel · Week 3", ORDER_REV + """
CHURN_DAYS = 365
""")
    b.md("""
    > 📨 **Ana:** *"Acquisition is expensive. I want to know our customers: who brings the money, do they come back,
    > who are we losing, and where do website visitors drop off?"*

    The Part setup built `order_rev`, **one row per paid order** (`order_id, user_id, created_at, revenue`). Customer analytics
    almost always starts by turning *events* (orders) into a **customer table** (one row per customer).

    ## 10.1 The customer table
    """)
    b.task("10.1", "One row per customer", """
        `customers`: index `user_id`, columns `first_order` (min created_at), `last_order` (max), `n_orders` (distinct orders),
        `revenue` (sum), from `order_rev`.
        """, "customers", """
        customers = order_rev.groupby("user_id").agg(first_order=("created_at", "min"),
                                                     last_order=("created_at", "max"),
                                                     n_orders=("order_id", "nunique"),
                                                     revenue=("revenue", "sum"))
        """,
        ["Named aggregation on `order_rev.groupby('user_id')`."], cmp={"allow_extra": True})
    b.task("10.2", "Repeat rate", """
        Share (0–1) of customers with **2 or more** orders.
        """, "repeat_rate", 'repeat_rate = (customers["n_orders"] >= 2).mean()', ["Boolean mask + mean."],
        level=1, needs=["10.1"])
    b.task("10.3", "Revenue per customer by traffic source", """
        Average customer `revenue` per `traffic_source`, highest first. Bring `traffic_source` from `users` with
        `customers.join(users.set_index("user_id")["traffic_source"])`. `join` merges on the index.
        """, "rev_by_source", """
        cust = customers.join(users.set_index("user_id")["traffic_source"])
        rev_by_source = cust.groupby("traffic_source")["revenue"].mean().sort_values(ascending=False)
        """,
        ["`join` adds the column by matching index labels (user_id).", "Then groupby + mean + sort."],
        cmp={"ordered": True}, needs=["10.1"])
    b.md("""
    ## 10.2 Pareto: do 20% of customers bring 80% of revenue?

    📘 Sort customers by revenue (desc), compute the cumulative share `s.cumsum() / s.sum()`, and read where the top 20% land.
    The same logic on products is **ABC analysis** (A = items making the first 80% of revenue, B = next 15%, C = the rest).
    """)
    b.task("10.4", "Top 20% share", """
        Share of total revenue that comes from the **top 20% of customers** by revenue. Use `n_top = int(len(customers) * 0.2)`.
        """, "top20_share", """
        rev_sorted = customers["revenue"].sort_values(ascending=False)
        n_top = int(len(rev_sorted) * 0.2)
        top20_share = rev_sorted.head(n_top).sum() / rev_sorted.sum()
        """,
        ["Sort descending, take the first `n_top`, divide their sum by the total."], needs=["10.1"])
    b.code("""
    # Pareto curve
    if "customers" in globals():
        s = customers["revenue"].sort_values(ascending=False)
        curve = s.cumsum() / s.sum()
        x = np.arange(1, len(s) + 1) / len(s)
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(x, curve.values)
        ax.axvline(0.2, ls="--", c="grey")
        ax.set_title("Cumulative revenue share by customer rank")
        ax.set_xlabel("Share of customers (best first)"); ax.set_ylabel("Share of revenue")
        plt.show()
    """)
    b.md("""
    ## 10.3 Cohorts and retention

    🎯 *"Of the customers who first bought in March, how many came back 1, 2, 3… months later?"* A cohort table separates
    "we got more customers" from "customers stay longer". The overall total mixes the two.

    📘 Steps: (1) each order's month; (2) each customer's **cohort** = month of their first order (`transform("min")`!);
    (3) **months since first order** = (year diff) × 12 + (month diff); (4) pivot: cohorts × months-since, counting distinct customers;
    (5) divide each row by its month-0 size.
    """)
    b.code("""
    # 🔍 Steps 1-3 (run this: the tasks build on it)
    order_rev["order_month"] = order_rev["created_at"].dt.to_period("M")
    order_rev["cohort"] = order_rev.groupby("user_id")["order_month"].transform("min")
    order_rev["months_since"] = ((order_rev["order_month"].dt.year - order_rev["cohort"].dt.year) * 12
                                 + (order_rev["order_month"].dt.month - order_rev["cohort"].dt.month))
    order_rev[["user_id", "order_month", "cohort", "months_since"]].sort_values("user_id").head(8)
    """, ctx=True)
    b.task("10.5", "Cohort counts", """
        `cohort_counts`: for cohorts **2025-01 … 2025-12** and `months_since` **0 … 6**, the number of **distinct** customers
        (rows = cohort, columns = months_since, missing = 0).
        """, "cohort_counts", """
        c25 = order_rev[(order_rev["cohort"] >= pd.Period("2025-01", "M"))
                        & (order_rev["cohort"] <= pd.Period("2025-12", "M"))
                        & (order_rev["months_since"] <= 6)]
        cohort_counts = c25.pivot_table(index="cohort", columns="months_since", values="user_id",
                                        aggfunc="nunique", fill_value=0)
        """,
        ["Filter cohorts and months_since first, then `pivot_table(..., aggfunc='nunique', fill_value=0)`."], level=3)
    b.task("10.6", "Retention matrix", """
        `retention`: each row of `cohort_counts` divided by its month-0 value (so column 0 is all 1.0).
        """, "retention", "retention = cohort_counts.div(cohort_counts[0], axis=0)",
        ["`df.div(series, axis=0)` divides row by row.", "`cohort_counts[0]` is the month-0 column."],
        needs=["10.5"], traps=[("retention = cohort_counts / cohort_counts[0]",
                                "plain `/` aligns the Series with the *columns*, not the rows. Use `.div(..., axis=0)`.")])
    b.task("10.7", "Average month-1 retention", """
        The mean of column `1` of `retention` (share of a cohort that buys again in the following month).
        """, "m1_retention", "m1_retention = retention[1].mean()", ["Select column 1, `.mean()`."], level=1, needs=["10.6"])
    b.code("""
    if "retention" in globals():
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.heatmap(retention.iloc[:, 1:], annot=True, fmt=".1%", cmap="Greens", ax=ax)
        ax.set_title("Share of each 2025 cohort buying again, by months since first order")
        plt.show()
    """)
    b.md("""
    ## 10.4 RFM segmentation

    📘 Three numbers per customer: **R**ecency (days since last order: lower is better), **F**requency (number of orders),
    **M**onetary (revenue). Score each 1–5 with `pd.qcut`, then name segments with rules (`np.select`).

    ⚠️ **Trap:** most customers have exactly 1 order, so `pd.qcut(frequency, 5)` fails with *"Bin edges must be unique"*.
    The standard fix: rank first, `pd.qcut(s.rank(method="first"), 5, ...)`. Be aware it splits tied customers arbitrarily.
    Another option is fixed bins with `pd.cut` (e.g. 1 / 2 / 3+ orders).
    For recency the labels go **reversed** (`[5, 4, 3, 2, 1]`): fewer days = better score.
    """)
    b.code("""
    try:
        pd.qcut(pd.Series([1, 1, 1, 1, 1, 1, 2, 3]), 4)
    except ValueError as e:
        print("ValueError:", e)
    """)
    b.task("10.8", "RFM table", """
        `rfm`: index `user_id`, columns `recency` (whole days from `last_order` to `TODAY`), `frequency` (`n_orders`),
        `monetary` (`revenue`).
        """, "rfm", """
        rfm = pd.DataFrame({"recency": (TODAY - customers["last_order"]).dt.days,
                            "frequency": customers["n_orders"],
                            "monetary": customers["revenue"]})
        """,
        ["`TODAY - customers['last_order']` is a Timedelta Series. `.dt.days` turns it into whole days."],
        cmp={"allow_extra": True}, needs=["10.1"])
    b.task("10.9", "R, F, M scores", """
        Add integer columns `R`, `F`, `M` (1–5) to `rfm`:
        `R = qcut(recency, 5, labels=[5,4,3,2,1])`, `F = qcut(frequency.rank(method="first"), 5, labels=[1..5])`,
        `M = qcut(monetary, 5, labels=[1..5])`, each converted with `.astype(int)`.
        """, 'rfm[["R", "F", "M"]]', """
        rfm["R"] = pd.qcut(rfm["recency"], 5, labels=[5, 4, 3, 2, 1]).astype(int)
        rfm["F"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
        rfm["M"] = pd.qcut(rfm["monetary"], 5, labels=[1, 2, 3, 4, 5]).astype(int)
        """,
        ["Three similar lines. Only F needs `.rank(method='first')` inside.", "Recency labels are reversed."],
        level=3, needs=["10.8"],
        traps=[("""
        rfm["R"] = pd.qcut(rfm["recency"], 5, labels=[1, 2, 3, 4, 5]).astype(int)
        rfm["F"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
        rfm["M"] = pd.qcut(rfm["monetary"], 5, labels=[1, 2, 3, 4, 5]).astype(int)
        """, "R is reversed: a SMALL recency (bought recently) must get the HIGH score 5.")])
    b.task("10.10", "Segments", """
        Add `rfm["segment"]` with `np.select` (first match wins), default `"Needs attention"`:
        `R>=4 & F>=4` → `"Champions"` · `R>=4 & F<=2` → `"New / promising"` · `R<=2 & F>=4` → `"At risk"` · `R<=2 & F<=2` → `"Lost"`.
        Then `segment_summary`: per segment `customers` (count), `avg_monetary` (mean monetary), `revenue` (sum monetary),
        sorted by revenue, highest first.
        """, "segment_summary", """
        conds = [(rfm["R"] >= 4) & (rfm["F"] >= 4), (rfm["R"] >= 4) & (rfm["F"] <= 2),
                 (rfm["R"] <= 2) & (rfm["F"] >= 4), (rfm["R"] <= 2) & (rfm["F"] <= 2)]
        rfm["segment"] = np.select(conds, ["Champions", "New / promising", "At risk", "Lost"], default="Needs attention")
        segment_summary = (rfm.groupby("segment")
                              .agg(customers=("monetary", "size"), avg_monetary=("monetary", "mean"),
                                   revenue=("monetary", "sum"))
                              .sort_values("revenue", ascending=False))
        """,
        ["`np.select(list_of_conditions, list_of_names, default=...)` (Part 3).",
         "Named aggregation, `size` counts rows."], needs=["10.9"], cmp={"ordered": True})
    b.md("""
    ## 10.5 Churn: who have we lost?

    🎯 Subscription businesses know the day a customer leaves (they cancel). **A shop doesn't.** A customer simply stops buying,
    so **churn is a definition you choose and defend**:

    > A customer is **churned** if they have made **no paid order in the last N days** before `TODAY`.

    **How to pick N?** Look at how long returning customers usually wait between orders. If N is shorter than a normal gap,
    you call loyal customers "churned".

    **Who can churn?** Only customers who have existed for at least N days. Someone whose first order was last week cannot have
    "stopped buying" yet. Including them makes churn look lower than it is. So: **eligible** = `first_order <= TODAY − N days`.

    Churn rate = churned eligible customers / all eligible customers. Then compare churn **between groups** to find levers.
    """)
    b.task("10.11", "Typical gap between orders", """
        For customers with 2+ orders: days between consecutive orders. Sort `order_rev` by `user_id, created_at`, take
        `groupby("user_id")["created_at"].diff()` in days, and store the **median** gap as `gap_median`.
        """, "gap_median", """
        g = order_rev.sort_values(["user_id", "created_at"])
        gaps = g.groupby("user_id")["created_at"].diff().dt.days
        gap_median = gaps.median()
        """,
        ["`diff()` inside a groupby works per customer; the first order of each customer gets NaN.",
         "`.dt.days`, then `.median()` (NaNs are skipped)."])
    b.md("""
    The median gap is several months. With **N = 180** we'd call many perfectly normal customers "churned".
    That's why the Part setup uses `CHURN_DAYS = 365`. (In fast-moving retail, like groceries, N can be 30–60 days.
    The data decides, not habit.)
    """)
    b.task("10.12", "Churn rate", """
        Using `customers` and `CHURN_DAYS`: `cutoff = TODAY - pd.Timedelta(days=CHURN_DAYS)`,
        `eligible` = customers with `first_order <= cutoff`, add `eligible["churned"] = eligible["last_order"] < cutoff`.
        Store the churn rate (0–1) in `churn_rate`.
        """, "churn_rate", """
        cutoff = TODAY - pd.Timedelta(days=CHURN_DAYS)
        eligible = customers[customers["first_order"] <= cutoff].copy()
        eligible["churned"] = eligible["last_order"] < cutoff
        churn_rate = eligible["churned"].mean()
        """,
        ["Three steps: cutoff date → filter eligible → boolean column → mean.",
         "Use `.copy()` when you filter and then add a column (avoids SettingWithCopyWarning)."], needs=["10.1"],
        traps=[("""
        cutoff = TODAY - pd.Timedelta(days=CHURN_DAYS)
        churn_rate = (customers["last_order"] < cutoff).mean()
        """, "you included customers who are too new to churn. Filter `first_order <= cutoff` first.")])
    b.task("10.13", "Churn by traffic source", """
        Churn rate per `traffic_source` among `eligible` customers (join it from `users` as in 10.3), highest first.
        """, "churn_by_source", """
        el = eligible.join(users.set_index("user_id")["traffic_source"])
        churn_by_source = el.groupby("traffic_source")["churned"].mean().sort_values(ascending=False)
        """, ["join → groupby → mean of the boolean → sort."], cmp={"ordered": True}, needs=["10.12"])
    b.task("10.14", "Churn by number of orders", """
        Churn rate among `eligible` by order-count group: `"1"`, `"2"`, `"3+"` (make the group with `np.select` or `pd.cut`).
        Store a Series indexed by those three labels.
        """, "churn_by_orders", """
        grp = np.select([eligible["n_orders"] == 1, eligible["n_orders"] == 2], ["1", "2"], default="3+")
        churn_by_orders = eligible.groupby(grp)["churned"].mean()
        """,
        ["You can group by an array that has the same length as the DataFrame.",
         "`eligible.groupby(grp)['churned'].mean()`"], level=3, needs=["10.12"])
    b.md("""
    🤔 **Think before you report:**
    1. Churn by traffic source is almost flat. That is a finding too: *where* customers come from doesn't explain who stays.
    2. Churn for 1-order customers is exactly **100%**. Why? (Their last order *is* their first order, and eligible
       customers' first order is older than the cutoff.) The metric is true by definition, so it tells you nothing new.
       The useful business question is **"how do we get a second order?"**. Customers with 2+ orders churn much less.
       **Recommendation shape:** a second-purchase campaign (e.g. a voucher 30–60 days after the first order).
    """)
    b.md("""
    ## 10.6 Conversion funnel (website sessions, Jul–Sep 2026)

    📘 A funnel counts how many sessions reach each step: **visit → product page → cart → purchase**.
    Step conversion = this step / previous step. Where the drop is biggest, there's the biggest opportunity.
    """)
    b.task("10.15", "Funnel counts", """
        `funnel`: a Series with index `["sessions", "viewed_product", "added_to_cart", "purchased"]` and the number of sessions
        reaching each step (from `sessions`).
        """, "funnel", """
        funnel = pd.Series({"sessions": len(sessions),
                            "viewed_product": sessions["viewed_product"].sum(),
                            "added_to_cart": sessions["added_to_cart"].sum(),
                            "purchased": sessions["purchased"].sum()})
        """,
        ["`pd.Series({'name': value, ...})` builds a Series from a dict.", "Summing a boolean column counts the Trues."],
        level=1, cmp={"ordered": True})
    b.task("10.16", "Step conversion", """
        `step_conv`: each step divided by the **previous** step (first value NaN).
        """, "step_conv", "step_conv = funnel / funnel.shift(1)", ["`shift(1)` moves values one row down."],
        needs=["10.15"], cmp={"ordered": True})
    b.task("10.17", "Guests vs logged-in visitors", """
        Purchase rate (share of sessions with `purchased`) for **logged-in** vs **guest** sessions.
        `conv_by_login`: a Series indexed by `True` (logged in: `user_id` not missing) / `False`.
        """, "conv_by_login", 'conv_by_login = sessions.groupby(sessions["user_id"].notna())["purchased"].mean()',
        ["Group by a boolean Series: `sessions['user_id'].notna()`."], needs=["10.15"])
    b.md("""
    🤔 Guests **never** purchase. Is that a broken checkout, or is login simply required to pay? An analyst doesn't guess.
    They ask the product team, and meanwhile report "guest → login" as a funnel step of its own.

    ## 🏁 Checkpoint 10: write 3 bullet points for Ana
    Pareto share, 1-month retention, churn and the 2nd-order insight, funnel's biggest drop. Each bullet: **number → meaning → action**.

    *Your bullets:* …
    """)


# =====================================================================================================
def part11(b):
    b.part("Part 11", "Final case: Q3 2026 business review", ORDER_REV + """
CHURN_DAYS = 365
""")
    b.md("""
    > 📨 **Ana:** *"Quarterly business review on Friday. I need six answers with numbers, and then your one-page memo.
    > No hand-holding this time. You've done every technique before."*

    Rules of the case: use `sales` for revenue and `items` for returns; quarters are half-open date ranges;
    hints exist, but try to finish without them. This is the closest thing here to an interview take-home.
    """)
    b.task("11.1", "Q3 revenue and growth", """
        `q3_rev`: revenue for 1 Jul – 30 Sep 2026. `q3_growth`: growth (fraction) vs 1 Jul – 30 Sep 2025.
        The check looks at `q3_growth`.
        """, "q3_growth", """
        d = sales["created_at"]
        q3_rev = sales.loc[(d >= "2026-07-01") & (d < "2026-10-01"), "sale_price"].sum()
        q3_rev_ly = sales.loc[(d >= "2025-07-01") & (d < "2025-10-01"), "sale_price"].sum()
        q3_growth = q3_rev / q3_rev_ly - 1
        """, ["Part 9.7 is the same pattern."])
    b.task("11.2", "Which categories drove the growth?", """
        `top_growth_cats`: a list of the 3 categories with the largest **absolute** revenue increase, Q3 2026 vs Q3 2025,
        biggest first.
        """, "top_growth_cats", """
        d = sales["created_at"]
        q = sales[((d >= "2025-07-01") & (d < "2025-10-01")) | ((d >= "2026-07-01") & (d < "2026-10-01"))].copy()
        q["year"] = q["created_at"].dt.year
        by_year = q.pivot_table(index="category", columns="year", values="sale_price", aggfunc="sum", fill_value=0)
        growth_abs = (by_year[2026] - by_year[2025]).sort_values(ascending=False)
        top_growth_cats = list(growth_abs.head(3).index)
        """,
        ["Filter both quarters, add a `year` column, pivot categories × year, subtract, sort.",
         "`by_year[2026] - by_year[2025]`"], level=3, cmp={"ordered": True})
    b.task("11.3", "Return problem", """
        `worst_return_cat`: among categories with **at least 200 items** ordered in Q3 2026 (from `items`, all statuses),
        the one with the highest return rate.
        """, "worst_return_cat", """
        d = items["created_at"]
        q3i = items[(d >= "2026-07-01") & (d < "2026-10-01")]
        st = q3i.groupby("category").agg(n=("order_item_id", "count"),
                                         return_rate=("status", lambda s: (s == "Returned").mean()))
        worst_return_cat = st[st["n"] >= 200]["return_rate"].idxmax()
        """,
        ["Aggregate count and return rate per category, filter n >= 200, `idxmax()`.",
         "Why the 200 filter? A category with 5 items and 2 returns has a 40% return rate, but that's noise, not a signal."])
    b.task("11.4", "New vs returning customers", """
        `new_rev_share`: share of Q3 2026 revenue from customers whose **first paid order ever** (in `order_rev`) is in Q3 2026.
        """, "new_rev_share", """
        first = order_rev.groupby("user_id")["created_at"].min()
        d = sales["created_at"]
        q3 = sales[(d >= "2026-07-01") & (d < "2026-10-01")]
        is_new = q3["user_id"].map(first) >= "2026-07-01"
        new_rev_share = q3.loc[is_new, "sale_price"].sum() / q3["sale_price"].sum()
        """,
        ["Each customer's first order date: `groupby('user_id')['created_at'].min()`.",
         "`q3['user_id'].map(first)` attaches that date to every Q3 row (a Series works as a lookup dict)."], level=3)
    b.task("11.5", "Best acquisition channel", """
        For users who **signed up in 2025** (`users.created_at`): average revenue per signed-up user (all-time, from `sales`,
        users without purchases count as 0) by `traffic_source`. `best_source`: the name of the best source.
        """, "best_source", """
        u25 = users[users["created_at"].dt.year == 2025].copy()
        rev_user = sales.groupby("user_id")["sale_price"].sum()
        u25["revenue"] = u25["user_id"].map(rev_user).fillna(0)
        best_source = u25.groupby("traffic_source")["revenue"].mean().idxmax()
        """,
        ["Revenue per user → `map` onto the 2025 sign-ups → `fillna(0)` → groupby source → mean → idxmax.",
         "Why `fillna(0)`? Dropping non-buyers would make every channel look better than it is."])
    b.task("11.6", "Churn of the H1 2025 cohort", """
        `churn_h1_2025`: among customers whose **first paid order** was in Jan–Jun 2025, the share with **no paid order in the
        last `CHURN_DAYS` days** before `TODAY`.
        """, "churn_h1_2025", """
        c = order_rev.groupby("user_id")["created_at"].agg(["min", "max"])
        h1 = c[(c["min"] >= "2025-01-01") & (c["min"] < "2025-07-01")]
        churn_h1_2025 = (h1["max"] < TODAY - pd.Timedelta(days=CHURN_DAYS)).mean()
        """,
        ["First and last order per customer, filter the cohort by first order, compare last order to the cutoff."])
    b.md("""
    ## 📝 Your memo (the most important cell in this notebook)

    Write it below as if Ana will forward it to the CEO. **Max one screen.** Template:

    > **Q3 2026 in one sentence:** …
    >
    > | # | Finding (with the number) | So what | Recommendation |
    > |---|---|---|---|
    > | 1 | Revenue +X% YoY, driven by … | … | … |
    > | 2 | … categories delivered most of the growth | … | … |
    > | 3 | Returns in … are … | … | … |
    > | 4 | New customers bring X% of revenue; X% of the H1-2025 cohort churned | … | … |
    > | 5 | Best channel per user: … | … | … |
    >
    > **Caveats:** data through 30 Sep 2026; revenue excludes cancelled/returned items; churn = no order in 365 days.

    **Self-review before sending:** every number has a unit and a period · no more than 2 decimals · each finding says "so what" ·
    recommendations are actions someone can own · definitions are stated · you would defend each number if asked "how did you compute it?"
    """)
    b.md("*Your memo:* …")


# =====================================================================================================
def part12(b):
    b.part("Part 12", "Bonus for the Data Mining exam: correlation, encoding, scaling, k-means", CUSTOMERS)
    b.md("""
    🎯 Data Mining courses (like NOVA IMS's) build on everything above: **EDA → preprocessing → modelling → interpretation**.
    The typical project is a **customer segmentation**. Here is its skeleton on our `rfm` table (rebuilt by the Part setup).

    ## 12.1 Correlation

    📘 `df.corr()` gives a Pearson matrix (linear relationships, sensitive to outliers). `df.corr(method="spearman")` uses
    ranks, so it handles monotonic relationships and is robust to outliers. Values run from −1 to 1. **Correlation ≠ causation.**
    """)
    b.task("12.1", "Correlation matrix", """
        Pearson correlation matrix of `rfm`'s three columns.
        """, "corr_matrix", 'corr_matrix = rfm[["recency", "frequency", "monetary"]].corr()',
        ["`.corr()` on the 3-column DataFrame."], level=1)
    b.code("""
    if "corr_matrix" in globals():
        fig, ax = plt.subplots(figsize=(4.5, 3.5))
        sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="RdBu_r", vmin=-1, vmax=1, ax=ax)
        ax.set_title("RFM correlations"); plt.show()
    """)
    b.md("""
    ## 12.2 Encoding categorical variables

    📘 Models need numbers.
    - **Nominal** (no order: country, traffic source) → **one-hot**: `pd.get_dummies(df, columns=[...], drop_first=True)`.
      `drop_first` avoids a redundant column, which matters for linear models.
    - **Ordinal** (has order: S < M < L) → `map({"S": 1, "M": 2, "L": 3})`.
    """)
    b.task("12.2", "One-hot encoding", """
        `user_features`: `pd.get_dummies` of `users[["age", "gender", "traffic_source"]]`, encoding `gender` and
        `traffic_source`, with `drop_first=True`.
        """, "user_features",
        'user_features = pd.get_dummies(users[["age", "gender", "traffic_source"]], columns=["gender", "traffic_source"], drop_first=True)',
        ["`pd.get_dummies(df, columns=[...], drop_first=True)`"])
    b.md("""
    ## 12.3 Scaling

    📘 Distance-based methods (k-means, kNN) get dominated by the column with the biggest numbers (monetary in $ vs frequency 1–4).
    - **Standardisation (z-score):** `(x − mean) / std` → mean 0, std 1. `StandardScaler` uses the population std (**`ddof=0`**),
      while pandas' `.std()` defaults to `ddof=1`. With 60k rows you won't see the difference, but on a 5-row exam example you will.
    - **Min-max:** `(x − min) / (max − min)` → 0…1.
    - Skewed money columns: apply `np.log1p` first (log of 1 + x), or the clusters will just split big spenders from everyone else.
    """)
    b.task("12.3", "Standardise RFM", """
        `rfm_scaled`: a DataFrame with the 3 RFM columns where `monetary` is first transformed with `np.log1p`,
        then **every** column is standardised with `ddof=0`.
        """, "rfm_scaled", """
        X = rfm[["recency", "frequency", "monetary"]].copy()
        X["monetary"] = np.log1p(X["monetary"])
        rfm_scaled = (X - X.mean()) / X.std(ddof=0)
        """,
        ["Copy, transform one column, then one vectorised line for all columns.",
         "Check: `rfm_scaled.mean().round(6)` → 0, `rfm_scaled.std(ddof=0)` → 1."],
        traps=[("""
        X = rfm[["recency", "frequency", "monetary"]]
        rfm_scaled = (X - X.mean()) / X.std(ddof=0)
        """, "you forgot `np.log1p` on monetary.")])
    b.md("""
    ## 12.4 k-means segmentation

    📘 `KMeans(n_clusters=k, n_init=10, random_state=42).fit_predict(X)` assigns each customer to the nearest of k centres.
    Choose k with the **elbow** of the inertia curve (plus business sense: can marketing run 4 campaigns? 10?).
    Then **profile** the clusters by averaging the *unscaled* features per cluster, and **name** them.
    """)
    b.code("""
    from sklearn.cluster import KMeans
    if "rfm_scaled" in globals():
        sample = rfm_scaled.sample(10000, random_state=0)          # a sample keeps the elbow loop fast
        inertia = {k: KMeans(n_clusters=k, n_init=10, random_state=42).fit(sample).inertia_ for k in range(2, 9)}
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.plot(list(inertia), list(inertia.values()), marker="o")
        ax.set_title("Elbow: where does adding clusters stop helping?"); ax.set_xlabel("k"); ax.set_ylabel("inertia")
        plt.show()
    """)
    b.task("12.4", "Fit k-means", """
        Fit `KMeans(n_clusters=4, n_init=10, random_state=42)` on `rfm_scaled` and store the labels in `rfm["cluster"]`.
        """, 'rfm["cluster"]', """
        from sklearn.cluster import KMeans
        km = KMeans(n_clusters=4, n_init=10, random_state=42)
        rfm["cluster"] = km.fit_predict(rfm_scaled)
        """,
        ["`km.fit_predict(rfm_scaled)` returns one label per row."], needs=["12.3"],
        custom="""
        ok = hasattr(u, '__len__') and len(u) == len(r) and pd.Series(u).nunique() == 4
        msg = '' if ok else 'Expected one label per customer and exactly 4 different clusters.'
        """)
    b.task("12.5", "Profile the clusters", """
        `cluster_profile`: mean `recency`, `frequency`, `monetary` per `cluster` (original units, not scaled).
        Then name each cluster in a markdown cell (e.g. "recent big spenders", "one-time, long ago").
        """, "cluster_profile",
        'cluster_profile = rfm.groupby("cluster")[["recency", "frequency", "monetary"]].mean()',
        ["groupby cluster → three columns → mean."], needs=["12.4"],
        custom="""
        exp = g['rfm'].groupby('cluster')[['recency', 'frequency', 'monetary']].mean()
        ok = isinstance(u, pd.DataFrame) and u.shape == exp.shape and np.allclose(u.values, exp.values)
        msg = '' if ok else 'Expected the mean recency, frequency and monetary of each of YOUR clusters (shape 4×3).'
        """)
    b.code("""
    # Do the k-means clusters agree with the rule-based RFM segments? (needs the segment rules from Part 10)
    if "cluster" in rfm.columns:
        r_ = pd.qcut(rfm["recency"], 5, labels=[5, 4, 3, 2, 1]).astype(int)
        f_ = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
        seg = np.select([(r_ >= 4) & (f_ >= 4), (r_ >= 4) & (f_ <= 2), (r_ <= 2) & (f_ >= 4), (r_ <= 2) & (f_ <= 2)],
                        ["Champions", "New / promising", "At risk", "Lost"], default="Needs attention")
        display(pd.crosstab(rfm["cluster"], seg, normalize="index").round(2))
    """)
    b.md("""
    **Exam checklist for a segmentation project:** describe the data → treat missing values and outliers (and justify) →
    choose features → transform skewed ones → scale → pick k (elbow/silhouette + business sense) → fit → profile and name
    clusters → recommend an action per cluster → state limitations.
    """)


# =====================================================================================================
def appendix(b):
    b.part("Appendix", "Exam drill, cheat sheet, error decoder, glossary", ITEMS_SETUP)
    b.md("""
    ## 🎯 A.1 Exam drill: mixed, no theory in front of you
    Real exams and interviews mix topics, so you first have to recognise **which tool** the question needs.
    Do these a few days after finishing Part 10. Aim for under 5 minutes each.
    """)
    b.task("A.1", "Oldest customers (big countries only)", """
        Among countries with **at least 1,000 users**, which one has the highest average user age? (name)
        """, "oldest_country", """
        st = users.groupby("country")["age"].agg(["mean", "size"])
        oldest_country = st[st["size"] >= 1000]["mean"].idxmax()
        """, ["agg mean + size, filter, idxmax."])
    b.task("A.2", "Cancellation rate 2025", """
        Share of orders created in 2025 whose status is `"Cancelled"`.
        """, "cancel_rate_2025", """
        o25 = orders[orders["created_at"].dt.year == 2025]
        cancel_rate_2025 = (o25["status"] == "Cancelled").mean()
        """, ["Filter the year, then boolean mean."], level=1)
    b.task("A.3", "Median price per department, as a table", """
        A **DataFrame** with columns `department` and `sale_price` (median from `sales`), one row per department, index 0…n−1.
        """, "dept_median", 'dept_median = sales.groupby("department", as_index=False)["sale_price"].median()',
        ["`as_index=False` or `.reset_index()`."], level=1)
    b.task("A.4", "Brand with the most customers", """
        Name of the brand bought by the most **distinct customers** (from `sales`).
        """, "top_brand", 'top_brand = sales.groupby("brand")["user_id"].nunique().idxmax()', ["nunique + idxmax."])
    b.task("A.5", "2026 sign-ups who ordered", """
        How many users who **signed up in 2026** have placed at least one order (any status)?
        """, "n_new_buyers", """
        u26 = users[users["created_at"].dt.year == 2026]
        n_new_buyers = u26["user_id"].isin(orders["user_id"]).sum()
        """, ["Filter, then `isin`."])
    b.task("A.6", "Items per order", """
        Average number of items per order, computed from `order_items` (not from `num_of_item`).
        """, "items_per_order", 'items_per_order = order_items.groupby("order_id").size().mean()',
        ["`size()` per order, then mean."], level=1)
    b.task("A.7", "Best category in each department", """
        A Series: department → name of its highest-revenue category (from `sales`).
        """, "best_cat", """
        r = sales.groupby(["department", "category"])["sale_price"].sum().reset_index()
        best_cat = r.loc[r.groupby("department")["sale_price"].idxmax()].set_index("department")["category"]
        """,
        ["Revenue per (department, category) as a flat table → `groupby('department')['sale_price'].idxmax()` gives row labels → `loc`."],
        level=3)
    b.task("A.8", "Weakest month of 2025", """
        The month (Period) of 2025 with the lowest revenue (from `sales`).
        """, "worst_month_2025", """
        m = sales["created_at"].dt.to_period("M")
        rev25 = sales[m.dt.year == 2025].groupby(m)["sale_price"].sum()
        worst_month_2025 = rev25.idxmin()
        """, ["to_period → filter 2025 → groupby → sum → idxmin."])
    b.task("A.9", "Lost at the cart", """
        Among sessions that **added to cart**, the share that did **not** purchase.
        """, "cart_abandon", """
        cart = sessions[sessions["added_to_cart"]]
        cart_abandon = (~cart["purchased"]).mean()
        """, ["Filter with a boolean column directly, then `~` and mean."], level=1)
    b.task("A.10", "Margin leader", """
        Among products with `retail_price >= 50`, the **name** of the product with the highest margin % (`(retail_price - cost) / retail_price`).
        """, "margin_leader", """
        p = products[products["retail_price"] >= 50].copy()
        p["margin_pct"] = (p["retail_price"] - p["cost"]) / p["retail_price"]
        margin_leader = p.loc[p["margin_pct"].idxmax(), "name"]
        """, ["filter → new column → idxmax → loc."])
    b.md("""
    ## 📋 A.2 Cheat sheet

    | Task | Code |
    |---|---|
    | look | `df.shape` `df.head()` `df.info()` `df.describe()` `df["c"].value_counts(normalize=True)` |
    | select | `df["c"]` `df[["a","b"]]` `df.loc[mask, "c"]` `df.iloc[:5, :3]` |
    | filter | `df[(df.a > 1) & (df.b.isin(["x","y"]))]` · `~` not · `.between(a, b)` · `.str.contains("x", case=False, na=False)` |
    | sort / top | `df.sort_values("c", ascending=False).head(10)` · `df.nlargest(10, "c")` |
    | new column | `df["n"] = df.a / df.b` · `np.where(cond, x, y)` · `np.select(conds, vals, default)` · `s.map(dict)` |
    | bins | `pd.cut(s, bins, labels)` · `pd.qcut(s, 4, labels)` |
    | dates | `pd.to_datetime(s, dayfirst=True)` · `.dt.year/.month/.day_name()/.to_period("M")` · `(d2 - d1).dt.days` |
    | missing | `df.isna().sum()` · `dropna(subset=[...])` · `fillna(value)` |
    | duplicates | `df.duplicated().sum()` · `drop_duplicates(subset=[...], keep="last")` |
    | types | `pd.to_numeric(s, errors="coerce")` · `s.astype(int)` · `s.str.strip().str.title()` |
    | outliers | `q1, q3 = s.quantile([.25, .75])` · fence `q3 + 1.5*(q3-q1)` · `s.clip(upper=...)` |
    | join | `a.merge(b, on="key", how="left", validate="many_to_one")` · `pd.concat([a, b], ignore_index=True)` |
    | group | `df.groupby("k")["v"].sum()` · `.agg(name=("col","func"))` · `.transform("mean")` · `.nunique()` |
    | pivot | `df.pivot_table(index, columns, values, aggfunc, fill_value=0)` · `pd.crosstab(a, b, normalize="index")` · `.unstack()` |
    | time | `groupby(dt.to_period("M"))` · `pct_change()` · `pct_change(12)` · `shift()` · `rolling(3).mean()` · `cumsum()` |
    | charts | `fig, ax = plt.subplots()` · `sns.histplot / boxplot / barplot / countplot / lineplot / scatterplot / heatmap(..., ax=ax)` · `ax.set_title()` |
    | ML prep | `df.corr()` · `pd.get_dummies(df, columns=[...], drop_first=True)` · `(X - X.mean()) / X.std(ddof=0)` · `KMeans(...).fit_predict(X)` |

    ## 🩺 A.3 Error decoder: "why didn't it work?"

    | You see | It means | Fix |
    |---|---|---|
    | `KeyError: 'Revenue'` | no such column (typo, case, or it was never created) | `df.columns.tolist()`; column names are case-sensitive |
    | `NameError: name 'x' is not defined` | the cell defining `x` wasn't run (Colab restarted?) | run ⚙️ Setup + ▶ Part setup + your earlier cells |
    | `ValueError: The truth value of a Series is ambiguous` | `and`/`or`/`if` on a whole column | `&`, `|`, and parentheses around each condition |
    | `TypeError: '>' not supported between 'str' and 'int'` | a "number" column is actually text | `pd.to_numeric(s, errors="coerce")` |
    | `TypeError: 'tuple' object is not callable` | `df.shape()` | `df.shape` (no brackets) |
    | `SettingWithCopyWarning` | you changed a filtered *view* | `.copy()` after filtering, or `df.loc[mask, "c"] = v` |
    | `ValueError: Bin edges must be unique` | `qcut` on a column with many equal values | `s.rank(method="first")` first, or `pd.cut` |
    | `ValueError: cannot mask with non-boolean array containing NA` | `str.contains` on a column with NaN | `na=False` |
    | `MergeError ... not a many-to-one merge` | the right table has duplicate keys | dedupe or aggregate the right table before merging |
    | numbers suddenly 2–10× too big after a merge | row explosion (non-unique key) | check `len()` before/after, use `validate=` |
    | column full of `NaN` after `map` | the dict didn't cover those values (case? spaces?) | normalise text first, or use `replace` |
    | chart drops at the end | incomplete last period | filter it out or label it |

    ## 🔤 A.4 Glossary EN → RU

    | EN | RU |
    |---|---|
    | DataFrame / Series / index | таблица / столбец (одномерный массив с метками) / индекс (метки строк) |
    | boolean mask | булева маска (True/False для каждой строки) |
    | missing value (NaN, NaT) | пропуск (числовой / дата) |
    | outlier / IQR / to cap (clip, winsorize) | выброс / межквартильный размах / ограничить «потолком» |
    | to merge / join / anti-join | объединить таблицы / соединение / «строки без пары» |
    | row explosion | «размножение» строк при неуникальном ключе |
    | aggregate / named aggregation | агрегировать / именованная агрегация |
    | revenue / profit / margin | выручка / прибыль / маржа (доля прибыли в выручке) |
    | AOV (average order value) | средний чек |
    | return rate / cancellation rate | доля возвратов / доля отмен |
    | MoM / YoY / YTD | к прошлому месяцу / к прошлому году / с начала года |
    | moving (rolling) average | скользящее среднее |
    | cohort / retention / churn | когорта / удержание / отток |
    | repeat rate | доля повторных покупателей |
    | RFM (recency, frequency, monetary) | давность, частота, деньги |
    | funnel / conversion | воронка / конверсия |
    | Pareto / ABC analysis | принцип Парето / ABC-анализ |
    | one-hot encoding | one-hot кодирование (дамми-переменные) |
    | standardisation / normalisation (min-max) | стандартизация (z-score) / нормализация к 0…1 |
    | clustering / centroid / inertia | кластеризация / центр кластера / сумма квадратов расстояний |
    | insight / finding / recommendation | инсайт / вывод / рекомендация |

    ## 🚀 A.5 What next
    - **SQL** is the other half of the job: the same questions in SQL (your Quaera / StrataSQL tracks).
    - **BI**: rebuild the Part 7 scorecard and the Part 9 KPI chart in Power BI or Looker Studio (BigQuery connects directly).
    - **Portfolio**: publish your Part 11 memo + notebook on GitHub. It's a ready-made take-home example for applications.
    - **Next topics**: A/B tests (t-test, proportions), forecasting basics, `statsmodels`, `plotly` for interactive charts.

    Run `progress()` to see your score. Then come back in 3 days and redo every task you needed `solution()` for. 💪
    """)
    b.code("progress()")
