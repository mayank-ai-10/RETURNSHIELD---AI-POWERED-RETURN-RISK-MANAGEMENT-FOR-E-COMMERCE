import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)

from xgboost import XGBClassifier


# Load data
df = pd.read_csv("data/return_risk_dataset.csv")

y = df["is_returned"]

X = df.drop(
    ["is_returned", "estimated_return_cost"],
    axis=1
)


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


# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
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
            "passthrough",
            numerical_features
        )
    ]
)

X_train_processed = preprocessor.fit_transform(X_train)
X_test_processed = preprocessor.transform(X_test)


# XGBoost
model = XGBClassifier(
    n_estimators=300,
    max_depth=5,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    eval_metric="logloss"
)

model.fit(
    X_train_processed,
    y_train
)


# Predictions
y_pred = model.predict(X_test_processed)


# Evaluation
print("\n===== XGBOOST MODEL =====")

print(
    f"Accuracy : {accuracy_score(y_test, y_pred):.4f}"
)

print(
    f"Precision: {precision_score(y_test, y_pred):.4f}"
)

print(
    f"Recall   : {recall_score(y_test, y_pred):.4f}"
)

print(
    f"F1 Score : {f1_score(y_test, y_pred):.4f}"
)

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))