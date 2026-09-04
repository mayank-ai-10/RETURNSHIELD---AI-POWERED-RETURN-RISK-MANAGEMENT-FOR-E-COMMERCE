import json
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression


# ============================================================
# SETTINGS
# ============================================================

THRESHOLD = 0.55


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(
    "data/return_risk_dataset.csv"
)


# ============================================================
# FEATURES / TARGET / COST
# ============================================================

y = df["is_returned"]

X = df.drop(
    [
        "is_returned",
        "estimated_return_cost"
    ],
    axis=1
)

return_cost = df[
    "estimated_return_cost"
]


# ============================================================
# FEATURES
# ============================================================

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


# ============================================================
# HELD-OUT TEST SET
# ============================================================

(
    X_train,
    X_test,
    y_train,
    y_test,
    cost_train,
    cost_test
) = train_test_split(
    X,
    y,
    return_cost,
    test_size=0.20,
    random_state=42,
    stratify=y
)


# ============================================================
# PREPROCESSING
# ============================================================

preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(
                handle_unknown="ignore"
            ),
            categorical_features
        ),
        (
            "numerical",
            StandardScaler(),
            numerical_features
        )
    ]
)


# ============================================================
# MODEL
# ============================================================

model = Pipeline(
    steps=[
        (
            "preprocessor",
            preprocessor
        ),
        (
            "classifier",
            LogisticRegression(
                max_iter=1000,
                random_state=42
            )
        )
    ]
)


# ============================================================
# TRAIN
# ============================================================

model.fit(
    X_train,
    y_train
)


# ============================================================
# PREDICTIONS
# ============================================================

probabilities = model.predict_proba(
    X_test
)[:, 1]


predictions = (
    probabilities >= THRESHOLD
).astype(int)


# ============================================================
# PORTFOLIO METRICS
# ============================================================

total_orders = len(X_test)

high_risk_orders = int(
    predictions.sum()
)

low_risk_orders = int(
    total_orders - high_risk_orders
)

average_probability = float(
    probabilities.mean()
)

total_estimated_exposure = float(
    cost_test[predictions == 1].sum()
)

expected_loss = float(
    (
        probabilities *
        cost_test
    ).sum()
)

actual_return_orders = int(
    y_test.sum()
)


# ============================================================
# CREATE METRICS OBJECT
# ============================================================

metrics = {

    "dataset": {
        "type": "held_out_test_set",
        "orders": total_orders
    },

    "threshold": THRESHOLD,

    "orders_analyzed": total_orders,

    "high_risk_orders": high_risk_orders,

    "low_risk_orders": low_risk_orders,

    "actual_return_orders": actual_return_orders,

    "high_risk_percentage": round(
        (
            high_risk_orders /
            total_orders
        ) * 100,
        2
    ),

    "average_return_probability": round(
        average_probability,
        4
    ),

    "estimated_exposure_high_risk": round(
        total_estimated_exposure,
        2
    ),

    "portfolio_expected_loss": round(
        expected_loss,
        2
    )
}


# ============================================================
# SAVE
# ============================================================

output_path = (
    "data/dashboard_metrics.json"
)

with open(
    output_path,
    "w"
) as file:

    json.dump(
        metrics,
        file,
        indent=4
    )


# ============================================================
# DISPLAY
# ============================================================

print("\n==============================================")
print("       RETURNSHIELD DASHBOARD METRICS")
print("==============================================")

print(
    f"\nOrders analyzed      : {total_orders}"
)

print(
    f"High-risk orders     : {high_risk_orders}"
)

print(
    f"Low-risk orders      : {low_risk_orders}"
)

print(
    f"Actual returns       : {actual_return_orders}"
)

print(
    f"High-risk percentage : "
    f"{metrics['high_risk_percentage']:.2f}%"
)

print(
    f"Average probability  : "
    f"{average_probability:.2%}"
)

print(
    f"High-risk exposure   : "
    f"₹{total_estimated_exposure:,.2f}"
)

print(
    f"Portfolio expected loss: "
    f"₹{expected_loss:,.2f}"
)

print("\nMetrics saved to:")
print(output_path)

print("\n==============================================")