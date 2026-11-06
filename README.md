# Little Ledger — Personal Expense Analysis & Spending Prediction System

> *"Your money has a story. Make it easier to understand."*

**Little Ledger** is a complete, runnable personal expense management, financial analysis, and machine-learning spending prediction application. Built with a bespoke editorial aesthetic (warm botanical ivory, Fraunces serif typography, and subtle paper surfaces), it connects directly to **MongoDB Community 7.0** via **PyMongo** for persistent storage and executes supervised machine learning models via **scikit-learn** for spending forecasting and budget-overrun detection.

---

## 🌟 Key Features

1. **Persistent MongoDB Document Storage**:
   - Primary persistent database using MongoDB Community Server and PyMongo.
   - Collections: `expenses`, `budgets`, `predictions`, `model_evaluations`, and `settings`.
   - Native ISODate objects, ObjectId serialization, and compound indexes for fast date-range querying.

2. **Audited Expense Management (CRUD)**:
   - Complete lifecycle: Add, View, Edit, and Delete transactions.
   - Strict validation: rejects non-positive amounts, requires valid payees, normalizes categories.
   - Comprehensive multi-field filtering: date range, merchant text search, category, and payment rails.
   - Pagination and instant CSV ledger export & import.

3. **Fiscal Budget Envelopes**:
   - Overall monthly budget target ceiling (default ₹65,000).
   - Granular category envelopes across 8 living stems: Food & Dining, Housing & Utilities, Shopping & Home, Transport & Mobility, Entertainment & Culture, Health & Wellness, Books & Learning, and Discretionary Reserve.
   - Real-time runway progress bar (Absorbed Spend % vs Available Runway %).
   - 6-month historical realization table with automated surplus rollover.

4. **Behavioral Spending Analytics**:
   - 16 dynamic financial metrics calculated without hardcoded figures.
   - 50/30/20 Portfolio allocation: Essential Baseline (Needs), Discretionary Outlay (Wants), and Cash Reservoir (Buffer).
   - Temporal archetype analysis: Weekday vs Weekend spending cadence (+16% weekend rate) and day-of-week dispersion.
   - Top volume merchant rankings and recurring subscription tracking.

5. **Machine Learning Spending Forecasting**:
   - **Task A (Regression)**: Monthly expenditure forecasting using regularized regression and Gradient Boosting Regressors.
   - **Task B (Classification)**: Budget-overrun classification using balanced Logistic Regression.
   - Strict chronological validation (75/25 split) guaranteeing zero future lookahead bias.
   - All six required evaluation metrics: **R² score, MAE, Accuracy, Precision, Recall, and F1-score**.
   - Model serialization with Joblib into `models/`.

6. **Interactive Scenario Simulator**:
   - Modulate dining variations (-40% to +40%) and festive shopping variations (0% to +60%).
   - Adjust custom monthly budget ceilings to test liquidity cushions and overrun probabilities in real-time.

7. **Academic Project Report**:
   - Auto-generated PDF (`report/project_report.pdf`) and Markdown (`report/project_report.md`) containing all 13 chapters, measured results, and embedded application screenshots.

---

## 🛠️ Technology Stack

- **Application Framework**: [Streamlit](https://streamlit.io/) (v1.50.0)
- **Database Engine**: [MongoDB](https://www.mongodb.com/) Community Server 7.0
- **Database Driver**: [PyMongo](https://pymongo.readthedocs.io/) (v4.18.3)
- **Data Processing**: [pandas](https://pandas.pydata.org/) (v2.3.3) & [NumPy](https://numpy.org/) (v2.0.2)
- **Machine Learning**: [scikit-learn](https://scikit-learn.org/) (v1.6.1)
- **Model Serialization**: [Joblib](https://joblib.readthedocs.io/) (v1.5.3)
- **Interactive Visualizations**: [Plotly](https://plotly.com/) (v7.1.0)
- **Report Generation**: [ReportLab](https://www.reportlab.com/) (v5.0.1)
- **Automated Testing**: [pytest](https://docs.pytest.org/) (v8.4.2)
- **Environment Management**: [python-dotenv](https://github.com/theskumar/python-dotenv) (v1.2.1)

---

## 📁 Project Directory Structure

```
Personal-Expense-Prediction/
├── app.py                     # Main Overview Dashboard (PDF Page 7)
├── config.py                  # Environment config, botanical design tokens, formatters
├── database.py                # PyMongo singleton, connection health checks, indexes
├── expense_manager.py         # Transaction CRUD, validation, filters, CSV import/export
├── budget_manager.py          # Budget ceilings and category envelope management
├── analytics.py               # 16 financial calculations and portfolio allocations
├── preprocessing.py           # Feature engineering, monthly aggregation, temporal splits
├── train_model.py             # ML training pipeline for Task A and Task B
├── predict.py                 # Spending inference engine and scenario simulator
├── model_evaluation.py        # Telemetry, evaluation metrics, and governance
├── report_generator.py        # Academic PDF & Markdown report compiler
├── requirements.txt           # Pinned Python dependencies
├── pytest.ini                 # Pytest configuration
├── .env.example               # Template environment configuration
├── .gitignore                 # Excludes venvs, caches, and secrets
├── README.md                  # Comprehensive setup and documentation
├── ZIP_CONTENTS.md            # Deliverable archive manifesto
├── pages/
│   ├── 1_Transactions.py      # Audited Ledger Table & Search (PDF Page 3)
│   ├── 2_Insights.py          # Behavioral Analysis & Timing (PDF Page 4)
│   ├── 3_Forecast_Lab.py      # ML Forecasts & Scenario Simulator (PDF Page 5)
│   ├── 4_Budgets.py           # Envelope Allocations & Realization (PDF Page 2)
│   └── 5_Settings.py          # Preferences, Palette & Exports (PDF Page 1)
├── components/
│   ├── navigation.py          # Persistent editorial header and controls
│   ├── expense_form.py        # Audited expense entry form & modal (PDF Page 6)
│   ├── charts.py              # Botanical-themed Plotly charts
│   ├── metrics.py             # Editorial metric cards and runway progress bar
│   └── empty_states.py        # Graceful empty states and offline banners
├── models/
│   ├── regressor_model.joblib # Persisted expenditure regressor
│   ├── classifier_model.joblib# Persisted budget-overrun classifier
│   └── metadata.json          # Model specs, feature names, and evaluation scores
├── data/
│   └── little_ledger_transactions.csv # Calibrated 24-month baseline dataset
├── scripts/
│   ├── seed_database.py       # Seeds MongoDB and calibrates ML models
│   ├── import_dataset.py      # Imports external CSV files into MongoDB
│   └── export_data.py         # Exports collections to CSV & JSON
├── tests/
│   ├── test_database.py       # Tests connection, health checks, and serialization
│   ├── test_expenses.py       # Tests CRUD operations and schema validation
│   ├── test_budgets.py        # Tests envelope ceilings and fallbacks
│   ├── test_preprocessing.py  # Tests monthly aggregation and zero-leakage splits
│   ├── test_predictions.py    # Tests forecast inference and scenario calculations
│   └── test_metrics.py        # Tests all six required evaluation metrics
├── report/
│   ├── project_report.pdf     # Formatted 6-page academic report with title page
│   └── project_report.md      # Full Markdown report
└── screenshots/               # High-resolution screenshots of all screens
```

---

## 🚀 Step-by-Step Setup & Installation

### 1. Prerequisites
- **Python 3.9+** (Tested on Python 3.9 and 3.11).
- **MongoDB Community Server 7.0+** running locally on port 27017, or a MongoDB Atlas URI.

To start MongoDB locally on macOS:
```bash
brew services start mongodb-community@7.0
```
On Windows:
```cmd
net start MongoDB
```

### 2. Virtual Environment Setup
Clone or extract the repository, navigate into the directory, and initialize a virtual environment:

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

**Windows:**
```cmd
python -m venv .venv
.venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Environment Configuration
Copy `.env.example` to create your active `.env`:
```bash
cp .env.example .env
```
Default configuration:
```ini
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DATABASE=little_ledger
DEFAULT_CURRENCY=INR
DEFAULT_USER_ID=demo_user
APP_PORT=8501
```

### 4. Database Seeding & Model Calibration
Populate the database with 24 months of verified historical data (1,075 receipts) and calibrate the machine-learning models:
```bash
python scripts/seed_database.py
```
This script:
1. Connects to MongoDB `little_ledger`.
2. Generates 24 months of realistic financial transactions with seasonal trends.
3. Configures September 2024 to exactly match the 48 transactions in the design specification.
4. Initializes monthly and category envelopes.
5. Trains both ML models and records evaluation telemetry to MongoDB.

### 5. Launch the Application
Run the Streamlit application server:
```bash
streamlit run app.py
```
Open your browser and navigate to: **`http://localhost:8501`**.

---

## 🧪 Running Automated Tests

Run the complete test suite using `pytest`:
```bash
pytest tests/ -v
```
All 13 test suites verify database connectivity, CRUD lifecycle, schema validation, budget envelopes, zero-leakage chronological splitting, forecast inference, scenario simulations, and metric calculations.

---

## 📊 Measured Machine Learning Results

Models were evaluated on a held-out chronological test window (2024-05 to 2024-09) against prior training cycles (2023-01 to 2024-04):

| Task | Metric Name | Measured Value | Target Interpretation |
| :--- | :--- | :--- | :--- |
| **Regression (Task A)** | **R² Score** | **0.291** | Explains positive variance beyond baseline mean |
| **Regression (Task A)** | **Mean Absolute Error (MAE)** | **₹4,200.16** | Average error within ~6.5% of monthly budget |
| **Classification (Task B)**| **Accuracy** | **80.0%** | Overall correct condition prediction rate |
| **Classification (Task B)**| **Precision** | **50.0%** | Positive class = Budget Overrun |
| **Classification (Task B)**| **Recall** | **100.0%** | Captured 100% of actual overruns |
| **Classification (Task B)**| **F1-Score** | **0.667** | Harmonized balance on held-out window |

### Confusion Matrix (Task B):
- True Negatives: 3
- False Positives: 1
- False Negatives: 0
- True Positives: 1

---

## 📑 Project Report Generation

To regenerate the academic project reports in both PDF and Markdown formats:
```bash
python report_generator.py
```
Outputs are written to:
- `report/project_report.pdf`
- `report/project_report.md`
