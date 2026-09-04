import joblib
import pandas as pd


# Load saved model
model = joblib.load(
    "models/return_risk_model.joblib"
)


# Example order
sample_order = pd.DataFrame([{
    "order_amount": 8999,
    "product_category": "Fashion",
    "discount_percentage": 40,
    "customer_order_count": 20,
    "customer_return_count": 8,
    "customer_return_rate": 0.40,
    "previous_refunds": 5,
    "delivery_days": 7,
    "product_rating": 2.8,
    "quantity": 3,
    "payment_method": "Credit Card",
    "customer_tenure_days": 500
}])


# Predict probability
probability = model.predict_proba(
    sample_order
)[0][1]


# Apply our chosen threshold
threshold = 0.55

risk_level = (
    "HIGH"
    if probability >= threshold
    else "LOW"
)


print("\n===== RETURNSHIELD AI TEST =====")

print(
    f"Return probability: {probability:.2%}"
)

print(
    f"Risk level: {risk_level}"
)

print("\nModel loaded and prediction successful!")