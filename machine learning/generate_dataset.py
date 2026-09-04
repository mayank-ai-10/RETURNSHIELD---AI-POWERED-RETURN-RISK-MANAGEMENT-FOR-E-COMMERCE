import numpy as np
import pandas as pd

np.random.seed(42)

N = 20000

# -----------------------------
# Basic order information
# -----------------------------

order_amount = np.round(
    np.random.lognormal(mean=7.5, sigma=0.8, size=N),
    2
)
order_amount = np.clip(order_amount, 200, 50000)

product_categories = [
    "Electronics",
    "Fashion",
    "Home",
    "Beauty",
    "Sports",
    "Books"
]

product_category = np.random.choice(
    product_categories,
    size=N,
    p=[0.20, 0.25, 0.18, 0.12, 0.12, 0.13]
)

discount_percentage = np.round(
    np.random.uniform(0, 70, N), 1
)

customer_order_count = np.random.randint(1, 51, N)

customer_return_count = np.minimum(
    np.random.poisson(3, N),
    customer_order_count
)

customer_return_rate = np.round(
    customer_return_count / customer_order_count,
    3
)

previous_refunds = np.minimum(
    np.random.poisson(2, N),
    customer_return_count
)

delivery_days = np.random.randint(1, 11, N)

product_rating = np.round(
    np.random.uniform(2.0, 5.0, N), 1
)

quantity = np.random.randint(1, 6, N)

payment_methods = [
    "UPI",
    "Credit Card",
    "Debit Card",
    "Net Banking",
    "COD"
]

payment_method = np.random.choice(
    payment_methods,
    size=N,
    p=[0.35, 0.25, 0.15, 0.10, 0.15]
)

customer_tenure_days = np.random.randint(
    30, 2000, N
)

# -----------------------------
# Product category risk
# -----------------------------

category_risk = {
    "Electronics": 0.05,
    "Fashion": 0.30,
    "Home": 0.10,
    "Beauty": 0.08,
    "Sports": 0.15,
    "Books": 0.02
}

category_component = np.array([
    category_risk[c]
    for c in product_category
])

# -----------------------------
# Return-risk score
# -----------------------------

risk_score = (
    3.5 * customer_return_rate
    + 0.020 * discount_percentage
    + 0.20 * previous_refunds
    + 0.18 * (delivery_days >= 7)
    + 0.35 * (product_rating < 3)
    + 0.20 * (quantity >= 4)
    + category_component
    - 0.00008 * customer_tenure_days
    - 0.015 * np.log1p(customer_order_count)
)

# Convert score to probability
probability = 1 / (1 + np.exp(-(risk_score - 1.0)))

probability = np.clip(
    probability,
    0.03,
    0.92
)

# Generate target
is_returned = np.random.binomial(
    1,
    probability
)

# -----------------------------
# Estimated merchant loss
# -----------------------------

reverse_shipping = np.random.uniform(
    50, 250, N
)

processing_cost = np.random.uniform(
    20, 120, N
)

restocking_rate = np.random.uniform(
    0.02, 0.08, N
)

restocking_loss = (
    order_amount * restocking_rate
)

estimated_return_cost = np.round(
    reverse_shipping
    + processing_cost
    + restocking_loss,
    2
)

# -----------------------------
# Create DataFrame
# -----------------------------

df = pd.DataFrame({
    "order_amount": order_amount,
    "product_category": product_category,
    "discount_percentage": discount_percentage,
    "customer_order_count": customer_order_count,
    "customer_return_count": customer_return_count,
    "customer_return_rate": customer_return_rate,
    "previous_refunds": previous_refunds,
    "delivery_days": delivery_days,
    "product_rating": product_rating,
    "quantity": quantity,
    "payment_method": payment_method,
    "customer_tenure_days": customer_tenure_days,
    "estimated_return_cost": estimated_return_cost,
    "is_returned": is_returned
})

# Save
output_path = "data/return_risk_dataset.csv"

df.to_csv(
    output_path,
    index=False
)

print("Dataset created successfully!")
print(f"Rows: {len(df)}")
print(f"Columns: {len(df.columns)}")
print(f"Saved to: {output_path}")

print("\nReturn distribution:")
print(df["is_returned"].value_counts())

print("\nReturn percentage:")
print(
    df["is_returned"]
    .value_counts(normalize=True)
    .mul(100)
    .round(2)
)

print("\nAverage estimated return cost:")
print(
    f"₹{df['estimated_return_cost'].mean():.2f}"
)

print("\nFirst 5 rows:")
print(df.head())