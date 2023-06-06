import json
from timeit import default_timer

import polars as pl

from functime.cross_validation import train_test_split
from functime.feature_extraction import add_calendar_effects, add_holiday_effects
from functime.forecasting import AutoLightGBM
from functime.metrics import mase

start_time = default_timer()

# Load data
y = pl.read_parquet("https://bit.ly/commodities-data")
entity_col, time_col = y.columns[:2]
X = (
    y.select([entity_col, time_col])
    .pipe(add_calendar_effects(["month"]))
    .pipe(add_holiday_effects(country_codes=["US"], freq="1mo"))
    .collect()
)

print("🎯 Target variable (y):\n", y)
print("📉 Exogenous variables (X):\n", X)

# Train-test splits
test_size = 3
freq = "1mo"
y_train, y_test = train_test_split(test_size)(y)
X_train, X_test = train_test_split(test_size)(X)

# Univariate time-series fit
forecaster = AutoLightGBM(
    test_size=test_size,
    freq=freq,
    min_lags=3,
    max_lags=6,
    n_splits=3,
    time_budget=10
)
forecaster.fit(y=y_train)
# Predict
y_pred = forecaster.predict(fh=test_size, freq=freq)
# Score
scores = mase(y_true=y_test, y_pred=y_pred, y_train=y_train)
# Retrieve "artifacts"
artifacts = forecaster.state.artifacts

print("✅ Predictions (univariate):\n", y_pred.sort(entity_col))
print("💯 Scores (univariate):\n", scores)
print(f"✨ Best parameters (univariate):\n{json.dumps(artifacts['best_params'], indent=4)}")


# With exogenous features
forecaster = AutoLightGBM(
    test_size=test_size,
    freq=freq,
    min_lags=3,
    max_lags=6,
    n_splits=3,
    time_budget=10
)
forecaster.fit(y=y_train)
# Predict
y_pred = forecaster.predict(fh=test_size, freq=freq)
# Score
scores = mase(y_true=y_test, y_pred=y_pred, y_train=y_train)
# Retrieve "artifacts"
artifacts = forecaster.state.artifacts

print("✅ Predictions (with exogenous variables):\n", y_pred.sort(entity_col))
print("💯 Scores (with exogenous variables):\n", scores)
print(f"✨ Best parameters (with exogenous variables):\n{json.dumps(artifacts['best_params'], indent=4)}")

elapsed_time = default_timer() - start_time
print(f"⏱️ Elapsed time: {elapsed_time}")