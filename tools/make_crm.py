"""Generate the deliberately messy 'CRM export' used in Part 5 (data cleaning).

Problems baked in (all realistic):
  ; separator and decimal comma (European Excel export), dd/mm/yyyy dates,
  country spellings / stray spaces / case, ages stored as text ('unknown', '', -1, 230),
  inconsistent gender and yes/no flags, missing spend, exact duplicate rows,
  and customers exported twice with an updated spend (keep the LAST row).
"""
import os
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
N = 300

countries = {
    "United States": ["United States", "united states", " United States", "USA", "US", "usa"],
    "China": ["China", "china", "China "],
    "Brazil": ["Brasil", "Brazil", "brasil"],
    "Spain": ["Spain", "España", "spain "],
    "United Kingdom": ["United Kingdom", "UK", "united kingdom"],
    "France": ["France", "france"],
    "Germany": ["Germany", " Germany"],
}
c_names = list(countries)
c_probs = np.array([0.25, 0.30, 0.15, 0.08, 0.08, 0.07, 0.07])

rows = []
for i in range(N):
    true_c = rng.choice(c_names, p=c_probs)
    variants = countries[true_c]
    country = variants[0] if rng.random() < 0.6 else rng.choice(variants)
    signup = pd.Timestamp("2025-01-01") + pd.Timedelta(days=int(rng.integers(0, 600)))
    r = rng.random()
    if r < 0.05:
        age = "unknown"
    elif r < 0.09:
        age = ""
    elif r < 0.11:
        age = str(rng.choice([-1, 230, 0, 150]))
    else:
        age = str(int(rng.integers(16, 71)))
    g = rng.choice(["F", "M"])
    gender = g if rng.random() < 0.7 else rng.choice(
        {"F": ["f", "Female", "female ", " F"], "M": ["m", "Male", "male", " M"]}[g])
    nl = rng.random() < 0.4
    newsletter = (rng.choice(["yes", "Yes", "Y", "TRUE", " yes"]) if nl
                  else rng.choice(["no", "No", "N", "false", "no "]))
    spend = "" if rng.random() < 0.08 else f"{rng.gamma(2.0, 60.0):.2f}".replace(".", ",")
    rows.append([f"C{10001 + i}", signup.strftime("%d/%m/%Y"), country, age, gender, newsletter, spend])

df = pd.DataFrame(rows, columns=["customer_id", "signup_date", "country", "age", "gender",
                                 "newsletter", "lifetime_spend"])
# customers exported twice: the later row has a higher, updated spend
upd = df.sample(8, random_state=1).copy()
upd["lifetime_spend"] = [f"{rng.gamma(3.0, 70.0):.2f}".replace(".", ",") for _ in range(8)]
# exact duplicate rows (copy-paste accident)
dup = df.sample(10, random_state=2)
df = pd.concat([df, dup]).sample(frac=1, random_state=3)
# re-exported customers arrive at the end of the file, so keep="last" is the right rule
df = pd.concat([df, upd.sample(frac=1, random_state=4)])
out = os.path.join(os.path.dirname(__file__), "..", "data", "crm_signups_export.csv")
df.to_csv(out, sep=";", index=False)
print(df.shape, "->", out)
