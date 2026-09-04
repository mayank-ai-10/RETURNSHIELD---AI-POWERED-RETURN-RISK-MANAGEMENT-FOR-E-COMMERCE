import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression


# Load dataset
df = pd.read_csv("data/return_risk_dataset.csv")

# Target
y = df["is_returned"]

# Features
X = df.drop(
    ["is_returned", "estimated_return_cost"],
    axis=1
)


# Feature columns
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


# Train on the complete dataset
model.fit(X, y)


# Save model
model_path = "models/return_risk_model.joblib"

joblib.dump(
    model,
    model_path
)


print("Model trained and saved successfully!")
print(f"Model path: {model_path}")
print(f"Training rows: {len(X)}")