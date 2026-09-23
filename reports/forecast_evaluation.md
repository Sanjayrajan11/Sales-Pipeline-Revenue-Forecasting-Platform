# Forecast evaluation

Calculated from the generated dataset.

Selected on validation WAPE: Seasonal naive + 0% pipeline. Held-out six-month WAPE: 14.12%; MAE: ₹16,23,71,924; RMSE: ₹16,67,66,836; bias: -₹16,23,71,924.

See forecast_metrics.csv for every candidate and backtest.csv for every origin. Validation is the first six of the final twelve complete historical months; test is the later six. Each origin uses only earlier closed outcomes and stage entries. WAPE gives an aggregate business-scale error; MAPE excludes zero actual months and is reported with their count. The future horizon is twelve months; only one-month forecasts are backtested. Range width uses the validation 80th percentile absolute error and square-root horizon scaling; it is indicative, not a calibrated confidence guarantee. Future variance is undefined until actuals exist. Closed-won future contribution is zero because these are future complete months. Pipeline blends are genuine candidates, but a history-only model may win; current pipeline remains a separately reported commercial cross-check. Revenue means booked net contract value, not recognized accounting revenue or collected cash.
