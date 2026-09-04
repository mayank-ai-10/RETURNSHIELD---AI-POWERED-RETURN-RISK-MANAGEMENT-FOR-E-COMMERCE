import pandas as pd

df = pd.read_csv("data/return_risk_dataset.csv")

print("\n===== RETURN RATE BY FEATURE =====")

print("\nReturn rate by product category:")
print(
    df.groupby("product_category")["is_returned"]
    .mean()
    .sort_values(ascending=False)
)

print("\nReturn rate by payment method:")
print(
    df.groupby("payment_method")["is_returned"]
    .mean()
    .sort_values(ascending=False)
)

print("\nNumeric feature correlations:")
print(
    df.select_dtypes(include="number")
    .corr()["is_returned"]
    .sort_values(ascending=False)
)