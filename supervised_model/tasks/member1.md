# Task card - Member 1 (Abhijith): Linear Regression

**Branch:** `feature/supervised-member1-linear-regression`
**Your file(s):** `member1_linear_regression.py` (inside `supervised_model/`)
**Your tests:** `test_ml_linear_regression.py` (inside `supervised_model/tests/`)
**Shared helpers (read, do not edit):** `supervised_model/common.py`
**Merge position:** after the supervised_model scaffold PR (members may merge in any order)

## Goal
Predict the average daily rate (price per night) of a booking from the other booking details.

## Steps
- [ ] 1. Split the data with `common.prepare(df, "regression")`
- [ ] 2. Build a Pipeline: shared preprocessor + `LinearRegression`
- [ ] 3. Fit on the train set, predict on the test set
- [ ] 4. Compute MAE, RMSE, R2 with `common.regression_metrics`
- [ ] 5. Plot actual vs predicted, residuals and the coefficients
- [ ] 6. Save with `common.make_result` and `common.save_result`

## Done when
- [ ] `flake8 .` is clean
- [ ] `test_ml_linear_regression.py` pass (they skip while your file is still a stub)
- [ ] `python -m supervised_model.train_models --only linear_regression` prints your row(s) with sensible metrics
- [ ] Pull request approved by a teammate and merged

## Be ready to explain in the review
- What is least squares and what does a coefficient mean?
- Why scale the inputs, and why fit the scaler on the train set only?
- What do R2, MAE and RMSE tell you? Is R2 = 0.62 good for this data?
- Why is `estimated_revenue` not allowed as an input here?
