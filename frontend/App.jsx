import { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [form, setForm] = useState({
    order_amount: 8999,
    product_category: "Fashion",
    discount_percentage: 40,
    customer_order_count: 20,
    customer_return_count: 8,
    customer_return_rate: 0.4,
    previous_refunds: 5,
    delivery_days: 7,
    product_rating: 2.8,
    quantity: 3,
    payment_method: "Credit Card",
    customer_tenure_days: 500,
  });

  const [dashboard, setDashboard] = useState(null);
  const [performance, setPerformance] = useState(null);
  const [confusion, setConfusion] = useState(null);
  const [datasetProfile, setDatasetProfile] = useState(null);
  const [history, setHistory] = useState([]);
  const [reviewQueue, setReviewQueue] = useState([]);
  const [financialImpact, setFinancialImpact] = useState(null);
  const [apiConnected, setApiConnected] = useState(false);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  useEffect(() => {
  fetch("http://127.0.0.1:8000/dashboard")
    .then((response) => response.json())
    .then((data) => setDashboard(data))
    .catch((error) => {
      console.error("Dashboard metrics error:", error);
    });

  fetch("http://127.0.0.1:8000/model-performance")
    .then((response) => response.json())
    .then((data) => setPerformance(data))
    .catch((error) => {
      console.error("Model performance error:", error);
    });
    fetch("http://127.0.0.1:8000/confusion-matrix")
  .then((response) => response.json())
  .then((data) => setConfusion(data))
  .catch((error) => {
    console.error("Confusion matrix error:", error);
  });
  fetch("http://127.0.0.1:8000/dataset-profile")
  .then((response) => response.json())
  .then((data) => setDatasetProfile(data))
  .catch((error) => {
    console.error("Dataset profile error:", error);
  });
  fetch("http://127.0.0.1:8000/history")
  .then((response) => response.json())
  .then((data) => setHistory(data.predictions))
  .catch((error) => {
    console.error("Prediction history error:", error);
  });
  fetch("http://127.0.0.1:8000/review-queue")
  .then((response) => response.json())
  .then((data) => setReviewQueue(data.cases))
  .catch((error) => {
    console.error("Review queue error:", error);
  });
  fetch("http://127.0.0.1:8000/financial-impact")
  .then((response) => response.json())
  .then((data) => setFinancialImpact(data))
  .catch((error) => {
    console.error("Financial impact error:", error);
  });
  fetch("http://127.0.0.1:8000/health")
  .then((response) => {
    if (!response.ok) {
      throw new Error("API unavailable");
    }

    return response.json();
  })
  .then(() => {
    setApiConnected(true);
  })
  .catch(() => {
    setApiConnected(false);
  });
}, []);


  const handleChange = (e) => {
    const { name, value } = e.target;

    setForm({
      ...form,
      [name]: [
        "order_amount",
        "discount_percentage",
        "customer_order_count",
        "customer_return_count",
        "customer_return_rate",
        "previous_refunds",
        "delivery_days",
        "product_rating",
        "quantity",
        "customer_tenure_days",
      ].includes(name)
        ? Number(value)
        : value,
    });
  };

  const predictRisk = async (e) => {
    e.preventDefault();

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch("http://127.0.0.1:8000/predict", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(form),
      });

      if (!response.ok) {
        throw new Error("Prediction request failed");
      }

      const data = await response.json();

      setResult(data);
      const historyResponse = await fetch(
  "http://127.0.0.1:8000/history"
);

const historyData = await historyResponse.json();

setHistory(historyData.predictions);
const queueResponse = await fetch(
  "http://127.0.0.1:8000/review-queue"
);

const queueData = await queueResponse.json();

setReviewQueue(queueData.cases);
const financialResponse = await fetch(
  "http://127.0.0.1:8000/financial-impact"
);

const financialData = await financialResponse.json();

setFinancialImpact(financialData);
    } catch (err) {
      setError(
        "Unable to connect to ReturnShield API. Make sure FastAPI is running."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>ReturnShield AI</h1>
          <p>AI-powered return risk management</p>
        </div>

        <div className={`api-status ${apiConnected ? "connected" : "disconnected"}`}>
  <span className="status-dot"></span>
  {apiConnected ? "API Connected" : "API Offline"}
</div>
      </header>
{history.length > 0 && (
  <section className="history-section">

    <div className="history-header">
      <div>
        <h2>Recent Predictions</h2>
        <p>
          Local prediction audit trail
        </p>
      </div>

      <div className="history-actions">

  <span className="history-count">
    {history.length} predictions
  </span>

  <button
    className="clear-history"
    onClick={async () => {

      await fetch(
        "http://127.0.0.1:8000/history",
        {
          method: "DELETE"
        }
      );

      setHistory([]);
    }}
  >
    Clear History
  </button>

</div>
    </div>

    <div className="history-table-wrapper">

      <table className="history-table">

        <thead>
          <tr>
            <th>Time</th>
            <th>Order Amount</th>
            <th>Category</th>
            <th>Probability</th>
            <th>Risk</th>
            <th>Action</th>
            <th>Why Flagged</th>
            <th>Expected Loss</th>
          </tr>
        </thead>

        <tbody>

          {[...history]
            .reverse()
            .slice(0, 10)
            .map((item, index) => (

              <tr key={index}>

                <td>
                  {new Date(
                    item.timestamp
                  ).toLocaleTimeString()}
                </td>

                <td>
                  ₹{item.order_amount.toLocaleString("en-IN")}
                </td>

                <td>
                  {item.product_category}
                </td>

                <td>
                  {(item.return_probability * 100).toFixed(1)}%
                </td>

                <td>
                  <span
                    className={`history-risk ${item.risk_level.toLowerCase()}`}
                  >
                    {item.risk_level}
                  </span>
                </td>

                <td>
                  {item.recommendation.replace(
                    "_",
                    " "
                  )}
                </td>

                <td>
                  ₹{item.expected_loss.toFixed(2)}
                </td>

              </tr>

            ))}

        </tbody>

      </table>

    </div>

  </section>
)}
      <main className="container">
        {dashboard && (
  <section className="overview">
    <div className="overview-header">
      <div>
        <h2>Risk Overview</h2>
        <p>
          Model evaluation snapshot · 4,000 held-out orders
        </p>
      </div>

      <div className="threshold">
        Decision threshold:{" "}
        <strong>{dashboard.threshold}</strong>
      </div>
    </div>

    <div className="overview-grid">

      <div className="overview-card">
        <span>Orders Analyzed</span>
        <strong>
          {dashboard.orders_analyzed.toLocaleString()}
        </strong>
      </div>

      <div className="overview-card high-card">
        <span>High-Risk Orders</span>
        <strong>
          {dashboard.high_risk_orders.toLocaleString()}
        </strong>
        <small>
          {dashboard.high_risk_percentage}% of orders
        </small>
      </div>

      <div className="overview-card">
        <span>Average Return Probability</span>
        <strong>
          {(dashboard.average_return_probability * 100).toFixed(1)}%
        </strong>
      </div>

      <div className="overview-card exposure-card">
        <span>Portfolio Expected Loss</span>
        <strong>
          ₹{dashboard.portfolio_expected_loss.toLocaleString(
            "en-IN",
            {
              maximumFractionDigits: 0
            }
          )}
        </strong>
      </div>

    </div>
  </section>
)}
{performance && (
  <section className="performance-section">
    <div className="performance-header">
      <div>
        <h2>Model Performance</h2>
        <p>
          Evaluation on the held-out test set · 4,000 orders
        </p>
      </div>

      <div className="threshold">
        Threshold: <strong>{performance.threshold}</strong>
      </div>
    </div>

    <div className="performance-grid">

      <div className="performance-card">
        <span>Accuracy</span>
        <strong>
          {(performance.accuracy * 100).toFixed(2)}%
        </strong>
      </div>

      <div className="performance-card">
        <span>Precision</span>
        <strong>
          {(performance.precision * 100).toFixed(2)}%
        </strong>
      </div>

      <div className="performance-card">
        <span>Recall</span>
        <strong>
          {(performance.recall * 100).toFixed(2)}%
        </strong>
      </div>

      <div className="performance-card">
        <span>F1 Score</span>
        <strong>
          {(performance.f1_score * 100).toFixed(2)}%
        </strong>
      </div>

    </div>

    <div className="error-summary">
      <div>
        <span>False Positives</span>
        <strong>{performance.false_positives}</strong>
      </div>

      <div>
        <span>False Negatives</span>
        <strong>{performance.false_negatives}</strong>
      </div>

      <div>
        <span>FP Cost Assumption</span>
        <strong>
          ₹{performance.false_positive_cost_assumption}
        </strong>
      </div>

      <div>
        <span>Estimated Total Cost</span>
        <strong>
          ₹{performance.estimated_total_cost.toLocaleString("en-IN")}
        </strong>
      </div>
    </div>
  </section>
)}
{confusion && (
  <section className="confusion-section">

    <div className="confusion-header">
      <h2>Confusion Matrix</h2>

      <p>
        How the model performed on the held-out test set
      </p>
    </div>

    <div className="matrix-wrapper">

      <table className="confusion-table">

        <thead>
          <tr>
            <th></th>
            <th>Predicted No Return</th>
            <th>Predicted Return</th>
          </tr>
        </thead>

        <tbody>

          <tr>
            <th>Actual No Return</th>

            <td className="correct">
              <strong>
                {confusion.true_negative}
              </strong>
              <span>True Negative</span>
            </td>

            <td className="false">
              <strong>
                {confusion.false_positive}
              </strong>
              <span>False Positive</span>
            </td>
          </tr>

          <tr>
            <th>Actual Return</th>

            <td className="false">
              <strong>
                {confusion.false_negative}
              </strong>
              <span>False Negative</span>
            </td>

            <td className="correct">
              <strong>
                {confusion.true_positive}
              </strong>
              <span>True Positive</span>
            </td>
          </tr>

        </tbody>

      </table>

    </div>

    <div className="confusion-explanation">

      <div>
        <strong>856 False Positives</strong>
        <p>
          Legitimate orders flagged for review.
        </p>
      </div>

      <div>
        <strong>344 False Negatives</strong>
        <p>
          Returns the model failed to identify.
        </p>
      </div>

    </div>

  </section>
)}
{datasetProfile && (
  <section className="dataset-section">

    <div className="dataset-header">
      <div>
        <h2>Dataset Profile</h2>
        <p>
          Evaluation data and model assumptions
        </p>
      </div>
    </div>

    <div className="dataset-grid">

      <div className="dataset-card">
        <span>Test Orders</span>
        <strong>
          {datasetProfile.test_orders.toLocaleString()}
        </strong>
      </div>

      <div className="dataset-card">
        <span>Actual Returns</span>
        <strong>
          {datasetProfile.actual_returns.toLocaleString()}
        </strong>
        <small>
          {datasetProfile.return_percentage}%
        </small>
      </div>

      <div className="dataset-card">
        <span>Actual Non-Returns</span>
        <strong>
          {datasetProfile.actual_non_returns.toLocaleString()}
        </strong>
        <small>
          {datasetProfile.non_return_percentage}%
        </small>
      </div>

      <div className="dataset-card">
        <span>Decision Threshold</span>
        <strong>
          {datasetProfile.decision_threshold}
        </strong>
      </div>

    </div>

    <div className="dataset-note">
      <strong>⚠️ Important evaluation note</strong>
      <p>
        {datasetProfile.note}
      </p>
    </div>

  </section>
)}
{reviewQueue.length > 0 && (
  <section className="review-section">

    <div className="review-header">
      <div>
        <h2>Merchant Review Queue</h2>
        <p>
          Orders requiring verification or manual review
        </p>
      </div>

      <span className="review-count">
        {reviewQueue.length} active cases
      </span>
    </div>

    <div className="review-table-wrapper">

      <table className="review-table">

        <thead>
          <tr>
            <th>Order</th>
            <th>Category</th>
            <th>Probability</th>
            <th>Risk</th>
            <th>Action</th>
            <th>Expected Loss</th>
          </tr>
        </thead>

        <tbody>

          {reviewQueue.slice(0, 10).map((item, index) => (

            <tr key={index}>

              <td>
                ₹{item.order_amount.toLocaleString("en-IN")}
              </td>

              <td>
                {item.product_category}
              </td>

              <td>
                <strong>
                  {(item.return_probability * 100).toFixed(1)}%
                </strong>
              </td>

              <td>
                <span
                  className={`queue-risk ${item.risk_level.toLowerCase()}`}
                >
                  {item.risk_level}
                </span>
              </td>

              <td>
                <span className="queue-action">
                  {item.recommendation.replaceAll("_", " ")}
                </span>
              </td>
              <td>
  <div className="queue-factors">
    {item.risk_factors.slice(0, 2).map(
      (factor, factorIndex) => (
        <span key={factorIndex}>
          {factor}
        </span>
      )
    )}

    {item.risk_factors.length > 2 && (
      <small>
        +{item.risk_factors.length - 2} more
      </small>
    )}
  </div>
</td>

              <td>
                ₹{item.expected_loss.toFixed(2)}
              </td>

            </tr>

          ))}

        </tbody>

      </table>

    </div>

  </section>
)}
{financialImpact && (
  <section className="financial-section">

    <div className="financial-header">
      <div>
        <h2>Financial Impact</h2>
        <p>
          Estimated exposure from locally reviewed predictions
        </p>
      </div>
    </div>

    <div className="financial-grid">

      <div className="financial-card">
        <span>High-Risk Orders</span>
        <strong>
          {financialImpact.high_risk_orders}
        </strong>
      </div>

      <div className="financial-card">
        <span>Review Cases</span>
        <strong>
          {financialImpact.review_cases}
        </strong>
      </div>

      <div className="financial-card exposure">
        <span>High-Risk Exposure</span>
        <strong>
          ₹{financialImpact.high_risk_exposure.toLocaleString(
            "en-IN",
            { maximumFractionDigits: 0 }
          )}
        </strong>
      </div>

      <div className="financial-card loss">
        <span>Expected Loss</span>
        <strong>
          ₹{financialImpact.expected_loss.toLocaleString(
            "en-IN",
            { maximumFractionDigits: 0 }
          )}
        </strong>
      </div>

    </div>

    <div className="financial-summary">
      <span>Average Expected Loss per High-Risk Order</span>

      <strong>
        ₹{financialImpact.average_expected_loss.toLocaleString(
          "en-IN",
          { maximumFractionDigits: 2 }
        )}
      </strong>
    </div>

  </section>
)}
        <section className="hero">
          <h2>Predict Return Risk</h2>
          <p>
            Analyze an order and identify potential return-related risk before
            it becomes a merchant loss.
          </p>
        </section>

        <div className="grid">
          <section className="card">
            <h3>Order Information</h3>

            <form onSubmit={predictRisk}>
              <label>Order Amount (₹)</label>
              <input
                type="number"
                name="order_amount"
                value={form.order_amount}
                onChange={handleChange}
              />

              <label>Product Category</label>
              <select
                name="product_category"
                value={form.product_category}
                onChange={handleChange}
              >
                <option>Electronics</option>
                <option>Fashion</option>
                <option>Home</option>
                <option>Beauty</option>
                <option>Sports</option>
                <option>Books</option>
              </select>

              <label>Discount (%)</label>
              <input
                type="number"
                name="discount_percentage"
                value={form.discount_percentage}
                onChange={handleChange}
              />

              <label>Total Previous Orders</label>
              <input
                type="number"
                name="customer_order_count"
                value={form.customer_order_count}
                onChange={handleChange}
              />

              <label>Previous Returns</label>
              <input
                type="number"
                name="customer_return_count"
                value={form.customer_return_count}
                onChange={handleChange}
              />

              <label>Customer Return Rate</label>
              <input
                type="number"
                step="0.01"
                min="0"
                max="1"
                name="customer_return_rate"
                value={form.customer_return_rate}
                onChange={handleChange}
              />

              <label>Previous Refunds</label>
              <input
                type="number"
                name="previous_refunds"
                value={form.previous_refunds}
                onChange={handleChange}
              />

              <label>Delivery Days</label>
              <input
                type="number"
                name="delivery_days"
                value={form.delivery_days}
                onChange={handleChange}
              />

              <label>Product Rating</label>
              <input
                type="number"
                step="0.1"
                min="1"
                max="5"
                name="product_rating"
                value={form.product_rating}
                onChange={handleChange}
              />

              <label>Quantity</label>
              <input
                type="number"
                name="quantity"
                value={form.quantity}
                onChange={handleChange}
              />

              <label>Payment Method</label>
              <select
                name="payment_method"
                value={form.payment_method}
                onChange={handleChange}
              >
                <option>UPI</option>
                <option>Credit Card</option>
                <option>Debit Card</option>
                <option>Net Banking</option>
                <option>COD</option>
              </select>

              <label>Customer Tenure (days)</label>
              <input
                type="number"
                name="customer_tenure_days"
                value={form.customer_tenure_days}
                onChange={handleChange}
              />

              <button type="submit" disabled={loading}>
                {loading ? "Analyzing..." : "Analyze Return Risk"}
              </button>
            </form>
          </section>

          <section className="card result-card">
            {!result && !error && (
              <div className="empty">
                <div className="empty-icon">🛡️</div>
                <h3>Ready to Analyze</h3>
                <p>
                  Enter order information and click "Analyze Return Risk".
                </p>
              </div>
            )}

            {error && (
              <div className="error">
                <h3>Connection Error</h3>
                <p>{error}</p>
              </div>
            )}

            {result && (
              <div>
                <h3>Risk Assessment</h3>

                <div className="score">
  <div className="score-number">
    {(result.return_probability * 100).toFixed(1)}%
  </div>

  <div className="score-label">
    Return Probability
  </div>

  <div className="risk-meter">
    <div
      className="risk-meter-fill"
      style={{
        width: `${result.return_probability * 100}%`,
      }}
    ></div>
  </div>

  <div className="meter-labels">
    <span>Low</span>
    <span>High</span>
  </div>
</div>

                <div
                  className={`risk ${
  result.risk_level === "HIGH"
    ? "high"
    : result.risk_level === "MEDIUM"
    ? "medium"
    : "low"
}`}
                >
                  {result.risk_level} RISK
                </div>

                <div className="recommendation">
  <strong>Recommended Action</strong>
  <p>{result.recommendation.replace("_", " ")}</p>
</div>

<div className="financial-box">
  <div>
    <span>Estimated Return Cost</span>
    <strong>
      ₹{result.estimated_return_cost.toFixed(2)}
    </strong>
  </div>

  <div>
    <span>Expected Loss</span>
    <strong>
      ₹{result.expected_loss.toFixed(2)}
    </strong>
  </div>
</div>

                <div className="factors">
                  <h4>Risk Factors</h4>

                  {result.risk_factors.map(
                    (factor, index) => (
                      <div className="factor" key={index}>
                        <span>✓</span>
                        {factor}
                      </div>
                    )
                  )}
                </div>
              </div>
            )}
          </section>
        </div>
      </main>
    </div>
  );
}

export default App;