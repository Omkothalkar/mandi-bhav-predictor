# Mandi Bhav Predictor

An end-to-end web application for exploring historical Indian mandi prices and producing transparent price forecasts and sell/wait comparisons. The project uses Agmarknet data for Rice and Wheat (2012–June 2017), a FastAPI backend, and a React + TypeScript frontend.

> **Status:** In progress. This is a historical-data demonstration, not a live market-price service. Forecasts are estimates and must not be treated as financial or agricultural advice.

## Highlights

- Browse the supported crop–mandi combinations and their historical monthly prices.
- Produce recursive forecasts for a selected future horizon.
- Compare expected net returns after a user-supplied transport cost.
- Receive an explainable `SELL` or `WAIT` recommendation based on a configurable threshold.
- Review model evaluation, exploratory analysis, forecasts, and known limitations in `docs/`.
- Run automated backend and forecasting tests with pytest.

## Technology

- Python, Pandas, NumPy, scikit-learn, Joblib
- FastAPI, Uvicorn, Pydantic, Pytest
- React, TypeScript, Vite, Axios, Recharts, Lucide
- Matplotlib

## Data and modelling

The application works with the public Agmarknet Rice and Wheat files from 2012–2017. The downloaded and processed CSV files are deliberately not committed: the processed files are more than GitHub’s 100 MB single-file limit and can be reproduced locally.

The project evaluates a Naive baseline, Linear Regression, Random Forest, and HistGradientBoosting. For the verified mandi pairs, the Naive previous-month-price baseline achieved the best MAE and is the active forecast strategy. Full methodology and results are in [the model training report](docs/modeling/model_training_report.md).

## Project structure

```text
backend/       FastAPI routes, services, schemas, and API tests
data/          Downloaded source data and generated processed datasets (not tracked)
docs/          EDA, model, backend, and frontend reports with plots
frontend/      React + TypeScript + Vite interface
ml/            Data ingestion and cleaning code
models/        Small serialized model metadata/artifacts for supported mandis
scripts/       Dataset setup, EDA, diagnostics, training, and reporting scripts
tests/         Forecasting and ML-pipeline tests
```

## Run locally

### 1. Prepare Python and the data

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

python scripts/setup_and_download.py
python ml/preprocessing/ingest.py
python ml/preprocessing/cleaner.py
```

The data download uses the public Agmarknet source specified in `scripts/setup_and_download.py`. It requires an internet connection and produces the ignored CSV files under `data/`.

### 2. Start the API

```powershell
uvicorn backend.main:app --reload
```

The API runs at `http://localhost:8000`; interactive API documentation is available at `http://localhost:8000/docs`.

### 3. Start the frontend

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite (normally `http://localhost:3000`). The frontend expects the API on `http://localhost:8000/api`.

## Test

After preparing the data, run:

```powershell
pytest backend/tests tests
```

## Deploy the API on Render

Create a **Python web service** with this repository as its root directory.

```text
Build Command: python -m pip install -r requirements.txt && python scripts/prepare_deployment_data.py
Start Command: python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT
Health Check Path: /api/health
```

The build command downloads the public source files and runs the existing ingestion and cleaning pipeline. It verifies `data/processed/cleaned_dataset.csv` before deployment, while `.gitignore` continues to keep the generated files out of Git. No custom environment variables are required: Render provides `PORT`, and `.python-version` pins Python 3.11.

## Important limitations

- The historical source data ends in June 2017. This project does not provide live 2026 mandi prices.
- Multi-month forecasts are recursive; they never access future actual values.
- The current strategy is intentionally simple because it outperformed the tested ML models on the available validation data.
- Crop varieties are aggregated at mandi level, so changing variety mix can introduce noise.
- Transport distance and rate are supplied by the user; routing is not integrated.

## Documentation

- [Backend report](docs/backend/backend_report.md)
- [Frontend report](docs/frontend/frontend_report.md)
- [EDA report](docs/eda/eda_report.md)
- [Model training report](docs/modeling/model_training_report.md)

## Credits

Built by Om Kothalkar. Historical data is sourced through the public Agmarknet dataset repository referenced by the setup script.
