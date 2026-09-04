import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder


# Load dataset
df = pd.read_csv("data/return_risk_dataset.csv")

# Target
y = df["is_returned"]

# Keep return cost separately for later financial evaluation
return_cost = df["estimated_return_cost"]

# Remove target and cost from ML features
X = df.drop(
    ["is_returned", "estimated_return_cost"],
    axis=1
)


# Categorical features
categorical_features = [
    "product_category",
    "payment_method"
]


# Numerical features
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
            "passthrough",
            numerical_features
        )
    ]
)


# Fit ONLY on training data
X_train_processed = preprocessor.fit_transform(X_train)

# Transform held-out test data
X_test_processed = preprocessor.transform(X_test)


print("Data preparation complete!")

print("\nOriginal training data:", X_train.shape)
print("Original test data:", X_test.shape)

print("\nProcessed training data:", X_train_processed.shape)
print("Processed test data:", X_test_processed.shape)

print("\nTraining returns:")
print(y_train.value_counts())

print("\nTest returns:")
print(y_test.value_counts())

print("\nAverage test return cost:")
print(f"₹{cost_test.mean():.2f}")