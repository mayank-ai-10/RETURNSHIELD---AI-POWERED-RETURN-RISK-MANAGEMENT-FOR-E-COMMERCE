import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)


# ============================================================
# 1. SETTINGS
# ============================================================

THRESHOLD = 0.55
FP_COST = 500


# ============================================================
# 2. LOAD DATA
# ============================================================

df = pd.read_csv("data/return_risk_dataset.csv")


# ============================================================
# 3. FEATURES / TARGET / COST
# ============================================================

y = df["is_returned"]

X = df.drop(
    ["is_returned", "estimated_return_cost"],
    axis=1
)

return_cost = df["estimated_return_cost"]


# ============================================================
# 4. FEATURE COLUMNS
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
# 5. HELD-OUT TEST SET
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
# 6. PREPROCESSING
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
# 7. MODEL
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
# 8. TRAIN
# ============================================================

model.fit(
    X_train,
    y_train
)


# ============================================================
# 9. PROBABILITY PREDICTIONS
# ============================================================

probabilities = model.predict_proba(
    X_test
)[:, 1]


# ============================================================
# 10. APPLY BUSINESS THRESHOLD
# ============================================================

y_pred = (
    probabilities >= THRESHOLD
).astype(int)


# ============================================================
# 11. CLASSIFICATION METRICS
# ============================================================

accuracy = accuracy_score(
    y_test,
    y_pred
)

precision = precision_score(
    y_test,
    y_pred
)

recall = recall_score(
    y_test,
    y_pred
)

f1 = f1_score(
    y_test,
    y_pred
)

matrix = confusion_matrix(
    y_test,
    y_pred
)


# ============================================================
# 12. FALSE POSITIVE / FALSE NEGATIVE
# ============================================================

false_positive_mask = (
    (y_pred == 1) &
    (y_test == 0)
)

false_negative_mask = (
    (y_pred == 0) &
    (y_test == 1)
)


false_positives = int(
    false_positive_mask.sum()
)

false_negatives = int(
    false_negative_mask.sum()
)


# ============================================================
# 13. FINANCIAL COST
# ============================================================

fp_cost = (
    false_positives *
    FP_COST
)

fn_cost = (
    cost_test[
        false_negative_mask
    ].sum()
)

total_cost = (
    fp_cost +
    fn_cost
)


# ============================================================
# 14. PRINT FINAL REPORT
# ============================================================

print("\n")
print("================================================")
print("          RETURNSHIELD AI")
print("          FINAL MODEL EVALUATION")
print("================================================")

print(f"\nModel                : Logistic Regression")
print(f"Decision threshold   : {THRESHOLD}")
print(f"FP cost assumption   : ₹{FP_COST}")

print("\n--------------- CLASSIFICATION ----------------")

print(f"Accuracy             : {accuracy:.4f}")
print(f"Precision            : {precision:.4f}")
print(f"Recall               : {recall:.4f}")
print(f"F1 Score             : {f1:.4f}")

print("\n--------------- CONFUSION MATRIX --------------")

print(matrix)

print("\n--------------- ERROR ANALYSIS ----------------")

print(f"False Positives      : {false_positives}")
print(f"False Negatives      : {false_negatives}")

print("\n--------------- FINANCIAL IMPACT --------------")

print(f"False-positive cost  : ₹{fp_cost:,.2f}")
print(f"False-negative cost  : ₹{fn_cost:,.2f}")
print(f"TOTAL ESTIMATED COST : ₹{total_cost:,.2f}")

print("\n================================================")
print("Evaluation complete.")
print("================================================")