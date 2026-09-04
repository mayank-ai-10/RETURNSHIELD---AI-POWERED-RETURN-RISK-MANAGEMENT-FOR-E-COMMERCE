import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression


# ============================================================
# 1. LOAD DATA
# ============================================================

df = pd.read_csv("data/return_risk_dataset.csv")


# ============================================================
# 2. SEPARATE FEATURES, TARGET AND RETURN COST
# ============================================================

y = df["is_returned"]

X = df.drop(
    ["is_returned", "estimated_return_cost"],
    axis=1
)

return_cost = df["estimated_return_cost"]


# ============================================================
# 3. FEATURE COLUMNS
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
# 4. TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test, cost_train, cost_test = train_test_split(
    X,
    y,
    return_cost,
    test_size=0.20,
    random_state=42,
    stratify=y
)


# ============================================================
# 5. PREPROCESSING
# ============================================================

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


# ============================================================
# 6. LOGISTIC REGRESSION MODEL
# ============================================================

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


# ============================================================
# 7. TRAIN MODEL
# ============================================================

model.fit(X_train, y_train)


# ============================================================
# 8. GET PROBABILITY PREDICTIONS
# ============================================================

probabilities = model.predict_proba(X_test)[:, 1]


# ============================================================
# 9. COST SCENARIOS
# ============================================================

FP_COSTS = [
    100,
    250,
    500,
    750,
    1000
]


# Thresholds to test
THRESHOLDS = [
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
]


# ============================================================
# 10. RUN COST SENSITIVITY ANALYSIS
# ============================================================

all_results = []


for fp_cost_value in FP_COSTS:

    for threshold in THRESHOLDS:

        # Convert probabilities to predictions
        y_pred = (
            probabilities >= threshold
        ).astype(int)


        # False positive
        false_positive_mask = (
            (y_pred == 1) &
            (y_test == 0)
        )


        # False negative
        false_negative_mask = (
            (y_pred == 0) &
            (y_test == 1)
        )


        # Counts
        false_positives = int(
            false_positive_mask.sum()
        )

        false_negatives = int(
            false_negative_mask.sum()
        )


        # Financial costs
        total_fp_cost = (
            false_positives *
            fp_cost_value
        )


        total_fn_cost = (
            cost_test[
                false_negative_mask
            ].sum()
        )


        total_cost = (
            total_fp_cost +
            total_fn_cost
        )


        # Save result
        all_results.append({
            "fp_cost_assumption": fp_cost_value,
            "threshold": threshold,
            "false_positives": false_positives,
            "false_negatives": false_negatives,
            "fp_cost": total_fp_cost,
            "fn_cost": total_fn_cost,
            "total_cost": total_cost
        })


# ============================================================
# 11. CREATE RESULTS TABLE
# ============================================================

results_df = pd.DataFrame(
    all_results
)


# ============================================================
# 12. DISPLAY BEST THRESHOLD FOR EACH COST
# ============================================================

print("\n==============================================")
print("       COST SENSITIVITY ANALYSIS")
print("==============================================")

print(
    "\nFalse-positive cost assumptions:"
)

print(
    [f"₹{x}" for x in FP_COSTS]
)


for fp_cost_value in FP_COSTS:

    scenario = results_df[
        results_df["fp_cost_assumption"]
        == fp_cost_value
    ].sort_values(
        "total_cost"
    )

    best = scenario.iloc[0]

    print("\n----------------------------------------------")
    print(
        f"FALSE-POSITIVE COST = ₹{fp_cost_value}"
    )
    print("----------------------------------------------")

    print(
        f"Best threshold      : "
        f"{best['threshold']:.2f}"
    )

    print(
        f"False positives     : "
        f"{int(best['false_positives'])}"
    )

    print(
        f"False negatives     : "
        f"{int(best['false_negatives'])}"
    )

    print(
        f"False-positive cost : "
        f"₹{best['fp_cost']:.2f}"
    )

    print(
        f"False-negative cost : "
        f"₹{best['fn_cost']:.2f}"
    )

    print(
        f"TOTAL COST          : "
        f"₹{best['total_cost']:.2f}"
    )


# ============================================================
# 13. SAVE COMPLETE RESULTS
# ============================================================

results_df.to_csv(
    "data/cost_sensitivity_results.csv",
    index=False
)


print("\n==============================================")
print("Analysis complete!")
print("Results saved to:")
print("data/cost_sensitivity_results.csv")
print("==============================================")