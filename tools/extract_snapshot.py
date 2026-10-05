"""Pull a frozen snapshot of bigquery-public-data.thelook_ecommerce into data/*.parquet.

Usage:  python tools/extract_snapshot.py --project YOUR_GCP_PROJECT --cutoff 2026-10-01
Needs:  pip install google-cloud-bigquery db-dtypes pyarrow  +  gcloud auth application-default login
The same SQL is used by the notebook when DATA_SOURCE = "bigquery".
"""
import argparse, os
import pandas as pd

D = "bigquery-public-data.thelook_ecommerce"


def queries(cutoff: str) -> dict:
    """cutoff: 'YYYY-MM-DD' literal date (exclusive upper bound for created_at)."""
    c = f"TIMESTAMP('{cutoff}')"
    return {
        "users": f"""
            SELECT id AS user_id, age, gender, country, traffic_source,
                   DATETIME(created_at) AS created_at
            FROM `{D}.users`
            WHERE created_at < {c}
            ORDER BY user_id""",
        "products": f"""
            SELECT id AS product_id, name, brand, category, department,
                   ROUND(cost, 2) AS cost, ROUND(retail_price, 2) AS retail_price
            FROM `{D}.products`
            ORDER BY product_id""",
        "orders": f"""
            SELECT order_id, user_id, status, num_of_item,
                   DATETIME(created_at)   AS created_at,
                   DATETIME(shipped_at)   AS shipped_at,
                   DATETIME(delivered_at) AS delivered_at,
                   DATETIME(returned_at)  AS returned_at
            FROM `{D}.orders`
            WHERE created_at < {c}
            ORDER BY order_id""",
        "order_items": f"""
            SELECT oi.id AS order_item_id, oi.order_id, oi.user_id, oi.product_id, oi.status,
                   DATETIME(o.created_at) AS created_at, ROUND(oi.sale_price, 2) AS sale_price
            FROM `{D}.order_items` oi
            JOIN `{D}.orders` o USING (order_id)
            WHERE o.created_at < {c}
            ORDER BY order_item_id""",
        "sessions": f"""
            -- one row per browsing session that STARTED in the 3 months before the cutoff
            SELECT session_id,
                   MAX(user_id)                       AS user_id,
                   ANY_VALUE(traffic_source)          AS traffic_source,
                   ANY_VALUE(browser)                 AS browser,
                   DATETIME(MIN(created_at))          AS started_at,
                   COUNT(*)                           AS n_events,
                   LOGICAL_OR(event_type = 'product') AS viewed_product,
                   LOGICAL_OR(event_type = 'cart')    AS added_to_cart,
                   LOGICAL_OR(event_type = 'purchase') AS purchased
            FROM `{D}.events`
            WHERE created_at >= TIMESTAMP(DATE_SUB(DATE '{cutoff}', INTERVAL 3 MONTH)) - INTERVAL 1 DAY
              AND created_at < {c}
            GROUP BY session_id
            HAVING MIN(created_at) >= TIMESTAMP(DATE_SUB(DATE '{cutoff}', INTERVAL 3 MONTH))
            ORDER BY started_at""",
    }


def normalize(df: pd.DataFrame) -> pd.DataFrame:
    """BigQuery returns nullable Int64/boolean/dbdate dtypes; turn them into plain numpy ones."""
    df = df.copy()
    for col in df.columns:
        s = df[col]
        if isinstance(s.dtype, pd.Int64Dtype):
            df[col] = s.astype("int64") if s.notna().all() else s.astype("float64")
        elif isinstance(s.dtype, pd.BooleanDtype):
            df[col] = s.fillna(False).astype(bool)
        elif pd.api.types.is_datetime64_any_dtype(s):
            df[col] = pd.to_datetime(s).astype("datetime64[ns]")
        elif pd.api.types.is_string_dtype(s) and not pd.api.types.is_object_dtype(s):
            df[col] = s.astype(object)
    return df


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--cutoff", default="2026-10-01")
    ap.add_argument("--only", nargs="*", help="extract only these tables")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "data"))
    a = ap.parse_args()
    from google.cloud import bigquery
    client = bigquery.Client(project=a.project)
    os.makedirs(a.out, exist_ok=True)
    for name, sql in queries(a.cutoff).items():
        if a.only and name not in a.only:
            continue
        df = normalize(client.query(sql).to_dataframe())
        path = os.path.join(a.out, f"{name}.parquet")
        df.to_parquet(path, index=False, compression="zstd")
        print(f"{name:12s} {df.shape}  {os.path.getsize(path)/1e6:.1f} MB")
