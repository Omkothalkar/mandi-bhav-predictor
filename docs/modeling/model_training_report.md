# Model Training Report

## 1. Selected Crop-Mandi Pairs & Selection Methodology
We dynamically evaluated continuous mandis with high volumes and >60 months of data.

### Selected Pairs:
1. **Rice** in **Kerala - Alappuzha - Alappuzha** (Kerala, Alappuzha)
   - Dates: 2012-01-02 to 2017-06-19
   - Unique Months: 66, Total Obs: 5639
2. **Rice** in **Gujarat - Vadodara(Baroda) - Vadodara** (Gujarat, Vadodara(Baroda))
   - Dates: 2012-01-02 to 2017-06-21
   - Unique Months: 64, Total Obs: 4864
3. **Rice** in **Assam - Kamrup - P.O. Uparhali Guwahati** (Assam, Kamrup)
   - Dates: 2012-01-04 to 2017-06-21
   - Unique Months: 66, Total Obs: 4395
4. **Wheat** in **Gujarat - Junagarh - Mangrol** (Gujarat, Junagarh)
   - Dates: 2012-01-09 to 2017-06-22
   - Unique Months: 66, Total Obs: 4261
5. **Rice** in **Karnataka - Kolar - Chintamani** (Karnataka, Kolar)
   - Dates: 2012-01-01 to 2017-06-22
   - Unique Months: 63, Total Obs: 4181

## 2. Monthly Aggregation & Variety Handling
Data is aggregated monthly. `Modal Price` uses the **monthly median** for robustness against daily outliers. `Arrivals` uses the **monthly sum**.

### Rice - Kerala - Alappuzha - Alappuzha
**Varieties Present**: Basumathi, Ir-8, Jaya, Other, Ponni, Basmati Paddy
> [!WARNING]
> Multiple varieties exist. Since we are aggregating to a single monthly price, variety mix changes could introduce noise. This is a known limitation.
**Extreme Values**: 2228 observations found > ₹3162.50. These are retained as legitimate observations.

**Sample Sizes**:
- Total Monthly Observations (after reindex): 66
- Usable after lag creation (lag_12 drops first 12): 54
- Training Samples (2012-Jan to 2016-Jun): 42
- Testing Samples (2016-Jul to 2017-Jun): 12

**Model Comparison (One-Step Ahead Evaluation)**:
| Model | MAE | RMSE | MAPE (%) |
|---|---|---|---|
| Baseline_Naive | 73.96 | 121.35 | 2.16 |
| LinearRegression | 203.34 | 241.39 | 5.88 |
| RandomForest | 199.79 | 246.31 | 5.62 |
| HistGradientBoosting | 252.53 | 317.02 | 7.06 |

- **Best ML Model**: RandomForest
- **Overall Best / Selected Forecasting Strategy**: Baseline_Naive (Lowest MAE). Strategy identifier: `naive`.
- Model artifacts saved to `models\Rice_Kerala___Alappuzha___Alappuzha_best_model.joblib`.

### Rice - Gujarat - Vadodara(Baroda) - Vadodara
**Varieties Present**: Ir-8, Masuri, Other, Parmal
> [!WARNING]
> Multiple varieties exist. Since we are aggregating to a single monthly price, variety mix changes could introduce noise. This is a known limitation.
**Extreme Values**: 1217 observations found > ₹3162.50. These are retained as legitimate observations.

**Sample Sizes**:
- Total Monthly Observations (after reindex): 66
- Usable after lag creation (lag_12 drops first 12): 54
- Training Samples (2012-Jan to 2016-Jun): 42
- Testing Samples (2016-Jul to 2017-Jun): 12

**Model Comparison (One-Step Ahead Evaluation)**:
| Model | MAE | RMSE | MAPE (%) |
|---|---|---|---|
| Baseline_Naive | 100.00 | 227.30 | 3.04 |
| LinearRegression | 602.36 | 658.81 | 17.26 |
| RandomForest | 713.33 | 740.02 | 20.60 |
| HistGradientBoosting | 842.81 | 848.89 | 24.32 |

- **Best ML Model**: LinearRegression
- **Overall Best / Selected Forecasting Strategy**: Baseline_Naive (Lowest MAE). Strategy identifier: `naive`.
- Model artifacts saved to `models\Rice_Gujarat___VadodaraBaroda___Vadodara_best_model.joblib`.

### Rice - Assam - Kamrup - P.O. Uparhali Guwahati
**Varieties Present**: Coarse, Fine, Super Fine, Medium, Other, Common
> [!WARNING]
> Multiple varieties exist. Since we are aggregating to a single monthly price, variety mix changes could introduce noise. This is a known limitation.
**Extreme Values**: 1897 observations found > ₹3162.50. These are retained as legitimate observations.

**Sample Sizes**:
- Total Monthly Observations (after reindex): 66
- Usable after lag creation (lag_12 drops first 12): 54
- Training Samples (2012-Jan to 2016-Jun): 42
- Testing Samples (2016-Jul to 2017-Jun): 12

**Model Comparison (One-Step Ahead Evaluation)**:
| Model | MAE | RMSE | MAPE (%) |
|---|---|---|---|
| Baseline_Naive | 54.17 | 101.04 | 1.89 |
| LinearRegression | 415.07 | 424.26 | 14.76 |
| RandomForest | 68.24 | 84.21 | 2.40 |
| HistGradientBoosting | 362.60 | 492.39 | 12.95 |

- **Best ML Model**: RandomForest
- **Overall Best / Selected Forecasting Strategy**: Baseline_Naive (Lowest MAE). Strategy identifier: `naive`.
- Model artifacts saved to `models\Rice_Assam___Kamrup___P.O._Uparhali_Guwahati_best_model.joblib`.

### Wheat - Gujarat - Junagarh - Mangrol
**Varieties Present**: Lok-1, Milbar, Rajasthan Tukdi, Other
> [!WARNING]
> Multiple varieties exist. Since we are aggregating to a single monthly price, variety mix changes could introduce noise. This is a known limitation.
**Extreme Values**: 3 observations found > ₹3162.50. These are retained as legitimate observations.

**Sample Sizes**:
- Total Monthly Observations (after reindex): 66
- Usable after lag creation (lag_12 drops first 12): 54
- Training Samples (2012-Jan to 2016-Jun): 42
- Testing Samples (2016-Jul to 2017-Jun): 12

**Model Comparison (One-Step Ahead Evaluation)**:
| Model | MAE | RMSE | MAPE (%) |
|---|---|---|---|
| Baseline_Naive | 74.17 | 110.35 | 3.96 |
| LinearRegression | 112.70 | 138.92 | 6.49 |
| RandomForest | 91.51 | 122.44 | 4.92 |
| HistGradientBoosting | 111.04 | 142.26 | 5.85 |

- **Best ML Model**: RandomForest
- **Overall Best / Selected Forecasting Strategy**: Baseline_Naive (Lowest MAE). Strategy identifier: `naive`.
- Model artifacts saved to `models\Wheat_Gujarat___Junagarh___Mangrol_best_model.joblib`.

### Rice - Karnataka - Kolar - Chintamani
**Varieties Present**: Broken Rice, Hansa, Sona
> [!WARNING]
> Multiple varieties exist. Since we are aggregating to a single monthly price, variety mix changes could introduce noise. This is a known limitation.
**Extreme Values**: 1232 observations found > ₹3162.50. These are retained as legitimate observations.

**Sample Sizes**:
- Total Monthly Observations (after reindex): 66
- Usable after lag creation (lag_12 drops first 12): 54
- Training Samples (2012-Jan to 2016-Jun): 42
- Testing Samples (2016-Jul to 2017-Jun): 12

**Model Comparison (One-Step Ahead Evaluation)**:
| Model | MAE | RMSE | MAPE (%) |
|---|---|---|---|
| Baseline_Naive | 16.67 | 35.36 | 0.70 |
| LinearRegression | 117.86 | 129.59 | 4.87 |
| RandomForest | 57.91 | 66.06 | 2.38 |
| HistGradientBoosting | 36.65 | 42.03 | 1.51 |

- **Best ML Model**: HistGradientBoosting
- **Overall Best / Selected Forecasting Strategy**: Baseline_Naive (Lowest MAE). Strategy identifier: `naive`.
- Model artifacts saved to `models\Rice_Karnataka___Kolar___Chintamani_best_model.joblib`.

## Methodologies & Checks
- **Selection Criterion**: MAE is prioritized as the primary error metric. RMSE is used as a secondary tie-breaker. MAPE provides interpretability. The Naive baseline is actively included in the selection rule.
- **Feature Definitions**: Engineered lags (1, 2, 3, 6, 12), rolling stats (3, 6) applied to past prices only, cyclical month, year, and lag-1 arrivals.
- **Chronological Split**: Strictly trained on data before July 2016, tested on July 2016 to June 2017.
- **Leakage Prevention**: Rolling window features are calculated on `lag_1_price` to prevent current month data from polluting the current month's features. Train and test sets were explicitly asserted for disjoint indices.
- **Evaluation Mode**: The metrics above represent **One-Step-Ahead** forecasting (where the true `lag_1` is available for predicting the next month). This simulates predicting month $T$ when month $T-1$ just concluded.

## Key Empirical Findings
> [!IMPORTANT]
> The Naive previous-month-price baseline outperformed the tested ML models on several/all selected Crop-Mandi series. This indicates strong month-to-month persistence in the available historical data and demonstrates why baseline comparison is essential. It is an empirical result of the dataset, and selecting the Naive strategy ensures maximum accuracy.

## Critical Recursive Forecast Verification
For eventual backend integration, the forecasting service will perform **Recursive Multi-Step Forecasting** when predicting future months where actual prices are unavailable.
1. The first step forecast will use the latest known actual price as its `lag_1_price`.
2. Subsequent step forecasts will feed back previous predictions as the input for `lag_1_price` (and updating rolling stats/lags accordingly).
3. The forecasting service **must NOT** require future actual prices.