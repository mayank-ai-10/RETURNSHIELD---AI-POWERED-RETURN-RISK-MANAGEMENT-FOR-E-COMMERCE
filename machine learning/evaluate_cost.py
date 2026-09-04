import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression


# Load dataset
df = pd.read_csv("data/return_risk_dataset.csv")

y = df["is_returned"]

X = df.drop(
    ["is_returned", "estimated_return_cost"],
    axis=1
)

return_cost = df["estimated_return_cost"]


categorical_features = [
    "product_category",
    "payment_method"
]

numerical_features = [
    "order_amount",
    "discount_percentage",
    "customer_order_count",
    "customer_return_count",
    "customer_return_rate",
    "previous_refunds",
    "delivery_days",
    "product_rating",
    "quantity",
    "customer_tenure_days"
]


# Train/test split
X_train, X_test, y_train, y_test, cost_train, cost_test = train_test_split(
    X,
    y,
    return_cost,
    test_size=0.20,
    random_state=42,
    stratify=y
)


# Preprocessing
preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(handle_unknown="ignore"),
            categorical_features
        ),
        (
            "numerical",
            StandardScaler(),
            numerical_features
        )
    ]
)


# Model
model = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        (
            "classifier",
            LogisticRegression(
                max_iter=1000,
                random_state=42
            )
        )
    ]
)


model.fit(X_train, y_train)


# Probability predictions
probabilities = model.predict_proba(X_test)[:, 1]


# False-positive cost assumption
FP_COST = 100


results = []


# Test different thresholds
for threshold in [
    0.10,
    0.15,
    0.20,
    0.25,
    0.30,
    0.35,
    0.40,
    0.45,
    0.50,
    0.55,
    0.60,
    0.65,
    0.70,
    0.75,
    0.80,
    0.85,
    0.90
]:

    y_pred = (
        probabilities >= threshold
    ).astype(int)

    false_positive_mask = (
        (y_pred == 1) &
        (y_test == 0)
    )

    false_negative_mask = (
        (y_pred == 0) &
        (y_test == 1)
    )

    false_positives = false_positive_mask.sum()
    false_negatives = false_negative_mask.sum()

    fp_cost = (
        false_positives *
        FP_COST
    )

    fn_cost = cost_test[
        false_negative_mask
    ].sum()

    total_cost = fp_cost + fn_cost

    results.append({
        "threshold": threshold,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
        "fp_cost": fp_cost,
        "fn_cost": fn_cost,
        "total_cost": total_cost
    })


# Convert to DataFrame
results_df = pd.DataFrame(results)


# Sort by total cost
results_df = results_df.sort_values(
    "total_cost"
)


print("\n===== THRESHOLD OPTIMIZATION =====")

print(
    results_df.to_string(
        index=False
    )
)


# Best threshold
best = results_df.iloc[0]

print("\n===== BEST THRESHOLD =====")

print(
    f"Threshold: {best['threshold']:.2f}"
)

print(
    f"False Positives: {int(best['false_positives'])}"
)

print(
    f"False Negatives: {int(best['false_negatives'])}"
)

print(
    f"FP Cost: ₹{best['fp_cost']:.2f}"
)

print(
    f"FN Cost: ₹{best['fn_cost']:.2f}"
)

print(
    f"TOTAL COST: ₹{best['total_cost']:.2f}"
)