from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from pathlib import Path
import joblib
import pandas as pd
import json


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = (
    BASE_DIR /
    "models" /
    "return_risk_model.joblib"
)

HISTORY_PATH = (
    Path(__file__).resolve().parent /
    "prediction_history.json"
)


# ============================================================
# LOAD MODEL
# ============================================================

model = joblib.load(MODEL_PATH)


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="ReturnShield AI",
    description="AI-powered return risk management API",
    version="1.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# ORDER INPUT
# ============================================================

class Order(BaseModel):

    order_amount: float
    product_category: str
    discount_percentage: float
    customer_order_count: int
    customer_return_count: int
    customer_return_rate: float
    previous_refunds: int
    delivery_days: int
    product_rating: float
    quantity: int
    payment_method: str
    customer_tenure_days: int


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():

    return {
        "message": "ReturnShield AI API is running"
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "model": "loaded"
    }


# ============================================================
# DASHBOARD METRICS
# ============================================================

@app.get("/dashboard")
def dashboard():

    metrics_path = (
        BASE_DIR /
        "data" /
        "dashboard_metrics.json"
    )

    with open(
        metrics_path,
        "r"
    ) as file:

        metrics = json.load(file)

    return metrics


# ============================================================
# MODEL PERFORMANCE
# ============================================================

@app.get("/model-performance")
def model_performance():

    return {
        "dataset": "Held-out test set",
        "test_orders": 4000,
        "threshold": 0.55,
        "accuracy": 0.7000,
        "precision": 0.7378,
        "recall": 0.8750,
        "f1_score": 0.8006,
        "false_positives": 856,
        "false_negatives": 344,
        "false_positive_cost_assumption": 500,
        "estimated_total_cost": 552540.56
    }


# ============================================================
# CONFUSION MATRIX
# ============================================================

@app.get("/confusion-matrix")
def confusion_matrix():

    return {
        "true_negative": 391,
        "false_positive": 856,
        "false_negative": 344,
        "true_positive": 2409
    }


# ============================================================
# DATASET PROFILE
# ============================================================

@app.get("/dataset-profile")
def dataset_profile():

    return {
        "dataset_type": "Synthetic held-out test set",
        "test_orders": 4000,
        "actual_returns": 2753,
        "actual_non_returns": 1247,
        "return_percentage": 68.83,
        "non_return_percentage": 31.18,
        "decision_threshold": 0.55,
        "note": (
            "Class distribution is return-heavy and "
            "should not be interpreted as real merchant traffic."
        )
    }


# ============================================================
# PREDICTION HISTORY
# ============================================================

def load_history():

    if not HISTORY_PATH.exists():

        return []

    try:

        with open(
            HISTORY_PATH,
            "r"
        ) as file:

            return json.load(file)

    except (json.JSONDecodeError, OSError):

        return []


def save_history(history):

    with open(
        HISTORY_PATH,
        "w"
    ) as file:

        json.dump(
            history,
            file,
            indent=4
        )


# ============================================================
# GET HISTORY
# ============================================================

@app.get("/history")
def get_history():

    history = load_history()

    return {
        "count": len(history),
        "predictions": history
    }


# ============================================================
# CLEAR HISTORY
# ============================================================

@app.delete("/history")
def clear_history():

    save_history([])

    return {
        "message": "Prediction history cleared",
        "count": 0
    }

# ============================================================
# MERCHANT REVIEW QUEUE
# ============================================================

@app.get("/review-queue")
def review_queue():

    history = load_history()

    queue = []

    for item in history:

        if item["risk_level"] in ["HIGH", "MEDIUM"]:

            queue.append({
                "timestamp": item["timestamp"],
                "order_amount": item["order_amount"],
                "product_category": item["product_category"],
                "return_probability": item["return_probability"],
                "risk_level": item["risk_level"],
                "recommendation": item["recommendation"],
                "expected_loss": item["expected_loss"],
                "risk_factors": item["risk_factors"]
            })

    # Highest-risk orders first
    queue.sort(
        key=lambda x: x["return_probability"],
        reverse=True
    )

    return {
        "count": len(queue),
        "high_risk": sum(
            1 for item in queue
            if item["risk_level"] == "HIGH"
        ),
        "medium_risk": sum(
            1 for item in queue
            if item["risk_level"] == "MEDIUM"
        ),
        "cases": queue
    }
@app.get("/financial-impact")
def financial_impact():

    history = load_history()

    high_risk = [
        item for item in history
        if item["risk_level"] == "HIGH"
    ]

    medium_risk = [
        item for item in history
        if item["risk_level"] == "MEDIUM"
    ]

    total_exposure = sum(
        item["estimated_return_cost"]
        for item in high_risk
    )

    total_expected_loss = sum(
        item["expected_loss"]
        for item in high_risk
    )

    total_review_cases = (
        len(high_risk) +
        len(medium_risk)
    )

    average_expected_loss = (
        total_expected_loss / len(high_risk)
        if high_risk
        else 0
    )

    return {
        "high_risk_orders": len(high_risk),
        "medium_risk_orders": len(medium_risk),
        "review_cases": total_review_cases,
        "high_risk_exposure": round(
            total_exposure,
            2
        ),
        "expected_loss": round(
            total_expected_loss,
            2
        ),
        "average_expected_loss": round(
            average_expected_loss,
            2
        )
    }
# ============================================================
# PREDICT
# ============================================================

@app.post("/predict")
def predict(order: Order):

    # --------------------------------------------------------
    # Prepare model input
    # --------------------------------------------------------

    input_data = pd.DataFrame([{

        "order_amount":
            order.order_amount,

        "product_category":
            order.product_category,

        "discount_percentage":
            order.discount_percentage,

        "customer_order_count":
            order.customer_order_count,

        "customer_return_count":
            order.customer_return_count,

        "customer_return_rate":
            order.customer_return_rate,

        "previous_refunds":
            order.previous_refunds,

        "delivery_days":
            order.delivery_days,

        "product_rating":
            order.product_rating,

        "quantity":
            order.quantity,

        "payment_method":
            order.payment_method,

        "customer_tenure_days":
            order.customer_tenure_days
    }])


    # --------------------------------------------------------
    # ML prediction
    # --------------------------------------------------------

    probability = model.predict_proba(
        input_data
    )[0][1]


    # --------------------------------------------------------
    # Business decision
    # --------------------------------------------------------

    threshold = 0.55


    if probability >= 0.55:

        risk_level = "HIGH"

        recommendation = "MANUAL_REVIEW"

    elif probability >= 0.30:

        risk_level = "MEDIUM"

        recommendation = "VERIFY_ORDER"

    else:

        risk_level = "LOW"

        recommendation = "NORMAL_PROCESSING"


    # --------------------------------------------------------
    # Risk factors
    # --------------------------------------------------------

    risk_factors = []


    if order.customer_return_rate >= 0.30:

        risk_factors.append(
            "High customer return rate"
        )


    if order.previous_refunds >= 3:

        risk_factors.append(
            "Multiple previous refunds"
        )


    if order.discount_percentage >= 30:

        risk_factors.append(
            "High discount percentage"
        )


    if order.product_rating < 3:

        risk_factors.append(
            "Low product rating"
        )


    if order.delivery_days >= 7:

        risk_factors.append(
            "Long delivery time"
        )


    if order.quantity >= 4:

        risk_factors.append(
            "Large quantity"
        )


    if order.product_category == "Fashion":

        risk_factors.append(
            "Fashion category has higher historical return rate"
        )


    if not risk_factors:

        risk_factors.append(
            "No major risk factors detected"
        )


    # --------------------------------------------------------
    # Financial exposure
    # --------------------------------------------------------

    estimated_return_cost = (
        120 +
        (order.order_amount * 0.05)
    )


    expected_loss = (
        probability *
        estimated_return_cost
    )


    # --------------------------------------------------------
    # Create prediction record
    # --------------------------------------------------------

    prediction_record = {

        "timestamp":
            datetime.now().isoformat(
                timespec="seconds"
            ),

        "order_amount":
            order.order_amount,

        "product_category":
            order.product_category,

        "return_probability":
            round(
                float(probability),
                4
            ),

        "risk_level":
            risk_level,

        "recommendation":
            recommendation,

        "estimated_return_cost":
            round(
                float(estimated_return_cost),
                2
            ),

        "expected_loss":
            round(
                float(expected_loss),
                2
            ),

        "risk_factors":
            risk_factors
    }


    # --------------------------------------------------------
    # Save prediction
    # --------------------------------------------------------

    history = load_history()

    history.append(
        prediction_record
    )

    save_history(history)


    # --------------------------------------------------------
    # API response
    # --------------------------------------------------------

    return {

        "return_probability":
            round(
                float(probability),
                4
            ),

        "risk_level":
            risk_level,

        "recommendation":
            recommendation,

        "estimated_return_cost":
            round(
                float(estimated_return_cost),
                2
            ),

        "expected_loss":
            round(
                float(expected_loss),
                2
            ),

        "risk_factors":
            risk_factors
    }