# 🎣 Phishing URL Detector

An end-to-end **MLOps phishing detection system** that uses a multi-layered analysis pipeline to determine whether a given URL is a phishing site or legitimate. The project combines real-time threat intelligence, domain forensics, HTML/JS heuristic inspection, and machine learning predictions into a single cumulative risk score.

Built with **Streamlit**, **DVC**, **Jenkins**, and **Docker** for a fully automated CI/CD and Continuous Training workflow.

---

## Table of Contents

- [How a Site Gets Flagged as Phishing](#how-a-site-gets-flagged-as-phishing)
  - [Layer 1 — PhishTank Database Lookup](#layer-1--phishtank-database-lookup)
  - [Layer 2 — Domain Age & SSL Certificate Inspection](#layer-2--domain-age--ssl-certificate-inspection)
  - [Layer 3 — HTML & JavaScript Content Inspection](#layer-3--html--javascript-content-inspection)
  - [Layer 4 — Machine Learning Prediction](#layer-4--machine-learning-prediction)
  - [Final Verdict](#final-verdict)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running the App](#running-the-app)
  - [Running with Docker](#running-with-docker)
- [ML Training Pipeline](#ml-training-pipeline)
  - [Pipeline Stages](#pipeline-stages)
  - [Reproducing the Pipeline](#reproducing-the-pipeline)
  - [Trained Models](#trained-models)
- [CI/CD with Jenkins](#cicd-with-jenkins)
- [Tech Stack](#tech-stack)

---

## How a Site Gets Flagged as Phishing

The system runs every submitted URL through **4 sequential analysis layers**. Each layer contributes to a **cumulative risk score** (out of 100). If the total score reaches **≥ 45 points**, the site is flagged as **PHISHING**. Otherwise, it is considered **LEGITIMATE**.

> **Exception:** If the URL is found in the PhishTank database, it is **instantly flagged** with a score of 100 — no further analysis is needed.

### Scoring Breakdown

| Layer | What It Checks | Max Points |
|---|---|---|
| 1. PhishTank Lookup | Known phishing database | **100** (instant override) |
| 2. Domain & SSL | Domain age, SSL certificate | **50** |
| 3. Content Inspection | Hidden forms, obfuscated JS, cross-domain form actions | **40** |
| 4. ML Prediction | URL feature-based classification | **15** |
| **Threshold** | | **≥ 45 = Phishing** |

---

### Layer 1 — PhishTank Database Lookup

The URL is checked against the [PhishTank](https://phishtank.org/) crowdsourced database via their API.

- If the URL **exists in PhishTank** and is **verified** as phishing → the site is **instantly flagged** with a risk score of **100**. All subsequent layers are skipped.
- If the URL is **not found** → proceed to the next layers.

### Layer 2 — Domain Age & SSL Certificate Inspection

The system performs WHOIS and SSL lookups on the domain to check for suspicious patterns commonly associated with phishing sites:

| Signal | Condition | Risk Points |
|---|---|---|
| **New domain** | Domain age < 30 days | **+30** |
| **Short-lived free SSL** | SSL expiry < 90 days AND issued by a free provider (Let's Encrypt, ZeroSSL, Cloudflare) | **+20** |

**Why this matters:** Phishing sites are typically registered recently and use free, short-lived SSL certificates to appear legitimate before getting taken down.

### Layer 3 — HTML & JavaScript Content Inspection

The system fetches the live page and inspects its HTML source code for phishing heuristics:

| Signal | What It Detects | Risk Points |
|---|---|---|
| **Hidden login form** | A `<form>` with `display:none` or `visibility:hidden` that contains a password field | **+15** |
| **Suspicious form action** | A form that submits data to a completely different domain than the page | **+15** |
| **Obfuscated JavaScript** | Use of `eval()`, `unescape()`, `String.fromCharCode`, or extremely long single-line scripts (>500 chars) | **+10** |

**Why this matters:** Phishing pages often hide credential-harvesting forms, send data to attacker-controlled servers, and obfuscate their malicious scripts to evade detection.

### Layer 4 — Machine Learning Prediction

A trained ML model analyzes **17 numerical features** extracted from the URL structure:

| Feature | Description |
|---|---|
| `dom_len` | Length of the domain name |
| `is_ip` | Whether the URL uses an IP address instead of a domain |
| `tld_len` | Length of the top-level domain |
| `subdom_cnt` | Number of subdomains |
| `digit_cnt` | Count of digits in the URL |
| `qm_cnt` | Count of `?` characters |
| `amp_cnt` | Count of `&` characters |
| `dot_cnt` | Count of `.` characters |
| `dash_cnt` | Count of `-` characters |
| `under_cnt` | Count of `_` characters |
| `letter_ratio` | Ratio of letters to URL length |
| `digit_ratio` | Ratio of digits to URL length |
| `spec_ratio` | Ratio of special characters to URL length |
| `is_https` | Whether the URL uses HTTPS |
| `slash_cnt` | Count of `/` characters |
| `path_len` | Length of the URL path |
| `query_len` | Length of the query string |

If the model predicts phishing → **+15 risk points** are added.

**Available models:** RandomForest, XGBoost, LightGBM, LogisticRegression, DecisionTree. All models are trained with **GridSearchCV** hyperparameter tuning and evaluated on F1-score.

### Final Verdict

After all 4 layers execute, the cumulative risk score determines the outcome:

```
Risk Score ≥ 45  →  🚨 PHISHING DETECTED
Risk Score < 45  →  ✅ LEGITIMATE SITE
```

**Example scenarios:**

| Scenario | PhishTank | Domain/SSL | Content | ML | Total | Verdict |
|---|---|---|---|---|---|---|
| Known phishing site | +100 | — | — | — | 100 | 🚨 Phishing |
| Brand new domain + free SSL + suspicious form | — | +50 | +15 | +15 | 80 | 🚨 Phishing |
| New domain + obfuscated JS | — | +30 | +10 | +15 | 55 | 🚨 Phishing |
| Established domain, clean page | — | +0 | +0 | +0 | 0 | ✅ Legitimate |

---

## Project Structure

```
phishing-detection/
├── app.py                      # Streamlit web application
├── main.py                     # Entry point placeholder
├── test_sites.py               # Script to batch-test URLs
├── config.yaml                 # Project configuration & metadata
│
├── pipeline/                   # ML training pipeline (DVC stages)
│   ├── data_ingestion.py       # Load raw dataset
│   ├── data_cleaning.py        # Drop text cols, nulls, correlated features
│   ├── data_splitting.py       # 80/20 stratified train-test split
│   ├── data_resampling.py      # SMOTE oversampling for class balance
│   ├── model_training.py       # Train 5 models with GridSearchCV
│   ├── inference.py            # End-to-end inference pipeline
│   └── show_eval.py            # Pretty-print model metrics (used by Jenkins)
│
├── utils/                      # Runtime detection utilities
│   ├── phishtank_checker.py    # PhishTank API client
│   ├── domain_ssl_checker.py   # WHOIS & SSL certificate analysis
│   ├── content_inspector.py    # HTML/JS heuristic scanner
│   └── feature_extractor.py    # 17-feature URL feature extractor
│
├── models/                     # Trained model artifacts (.joblib)
├── data/                       # Dataset files (managed by DVC)
├── analysis/                   # EDA scripts and outputs
│
├── dvc.yaml                    # DVC pipeline definition
├── dvc.lock                    # DVC pipeline lockfile
├── Dockerfile                  # Multi-stage Docker build
├── docker-compose.yml          # App + Jenkins services
├── Jenkinsfile                 # CI/CD pipeline with human-in-the-loop
├── pyproject.toml              # Python project metadata & dependencies
└── uv.lock                     # Dependency lockfile (uv)
```

---

## Getting Started

### Prerequisites

- **Python 3.14+**
- [**uv**](https://docs.astral.sh/uv/) — fast Python package manager
- **Docker** & **Docker Compose** (optional, for containerized deployment)

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/legit-os/phishing-detection.git
   cd phishing-detection
   ```

2. **Install dependencies with uv:**

   ```bash
   uv sync
   ```

3. **Pull data and models from DagsHub (optional, requires DVC auth):**

   ```bash
   uv run dvc pull
   ```

### Running the App

Launch the Streamlit web application:

```bash
uv run streamlit run app.py
```

Then open [http://localhost:8501](http://localhost:8501) in your browser.

**How to use the app:**

1. Enter any URL in the text input field (e.g., `https://example.com`).
2. Optionally select a different ML model from the sidebar (default: RandomForest).
3. Optionally enter a [PhishTank API key](https://phishtank.org/api_info.php) for authenticated lookups.
4. Click **"Analyze URL"** and watch each detection layer execute in real time.
5. View the final verdict and cumulative risk score at the bottom.

### Running with Docker

Build and run using Docker Compose:

```bash
docker-compose up -d --build
```

| Service | URL |
|---|---|
| Streamlit App | [http://localhost:8502](http://localhost:8502) |
| Jenkins | [http://localhost:8080](http://localhost:8080) |

---

## ML Training Pipeline

### Pipeline Stages

The training pipeline is managed by [DVC](https://dvc.org/) and runs through 5 stages:

```
ingestion → cleaning → splitting → resampling → training
```

| Stage | Script | Description |
|---|---|---|
| **Ingestion** | `data_ingestion.py` | Loads raw CSV dataset |
| **Cleaning** | `data_cleaning.py` | Drops text columns (`url`, `dom`, `tld`), nulls, and highly correlated features (`entropy`, `eq_cnt`, `letter_cnt`, `special_cnt`, `url_len`) |
| **Splitting** | `data_splitting.py` | 80/20 stratified train-test split |
| **Resampling** | `data_resampling.py` | SMOTE oversampling to balance phishing vs. legitimate classes |
| **Training** | `model_training.py` | Trains 5 models with GridSearchCV (optimized on F1-score), saves `.joblib` artifacts and a `models_registry.json` |

### Reproducing the Pipeline

```bash
uv run dvc repro
```

This will re-run only the stages whose inputs have changed.

### Trained Models

All models are saved as timestamped `.joblib` files in the `models/` directory. A `models_registry.json` file tracks each model's best hyperparameters and test set metrics (accuracy, precision, recall, F1).

| Model | Description |
|---|---|
| LogisticRegression | Linear baseline |
| DecisionTree | Single tree classifier |
| RandomForest | Ensemble of decision trees |
| XGBoost | Gradient-boosted trees |
| LightGBM | Light gradient-boosted trees |

---

## CI/CD with Jenkins

The project includes a fully automated [Jenkinsfile](Jenkinsfile) pipeline that triggers on every push to `main`:

| Stage | What Happens |
|---|---|
| **Clean Workspace** | Purges Jenkins workspace for a clean build |
| **Checkout** | Clones the latest code from GitHub |
| **Install Dependencies** | Installs system packages, `uv`, and Python deps |
| **DVC Auth & Pull** | Authenticates with DagsHub and pulls data/models |
| **DVC Reproduce & Approve** | Re-trains models, displays metrics, and waits for **human approval** (up to 3 retries) |
| **Push to DagsHub** | Pushes updated data and models back to DagsHub |
| **Commit Lockfile** | Commits `dvc.lock` back to GitHub |
| **Build Docker Image** | Builds a production Docker image |
| **Deploy** | Deploys the updated app via Docker Compose |

> **Human-in-the-loop:** After each training run, the pipeline pauses and displays model metrics. A human reviewer must **approve** the model performance before deployment proceeds. If rejected, training re-runs (up to 3 attempts).

---

## Tech Stack

| Category | Technology |
|---|---|
| **Web App** | Streamlit |
| **ML Models** | Scikit-learn, XGBoost, LightGBM |
| **Data Balancing** | imbalanced-learn (SMOTE) |
| **Feature Engineering** | tldextract, python-whois |
| **Content Analysis** | BeautifulSoup4, Requests |
| **Data Versioning** | DVC + DagsHub |
| **Package Management** | uv |
| **Containerization** | Docker, Docker Compose |
| **CI/CD** | Jenkins |
| **Language** | Python 3.14+ |