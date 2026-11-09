"""MEMBER 1 - Linear Regression (regression task: predict the average daily rate).

Idea: price = b0 + b1*x1 + b2*x2 + ... The model learns one weight (coefficient) per input so
that the straight-line prediction is as close as possible to the real prices (least squares).
"""

import time

import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline

from supervised_model import common

NAME = "linear_regression"
TASK = "regression"


def run(df=None, fast=False):
    """Train on 80% of the bookings, test on the unseen 20%, save metrics and charts."""
    started = time.time()
    df = common.load_data() if df is None else df

    # 1. Same split as every other model (fixed seed) - target: avg_daily_rate
    X_train, X_test, y_train, y_test = common.prepare(df, TASK, fast)

    # 2. Pipeline = preprocessing + model, so the test data is transformed with the
    #    statistics learned on the TRAIN data only (no leakage)
    model = Pipeline([("prep", common.build_preprocessor(TASK, scale=True)),
                      ("model", LinearRegression())])
    model.fit(X_train, y_train)

    # 3. Predict on unseen data and measure the error
    pred = model.predict(X_test)
    metrics = common.regression_metrics(y_test, pred, y_train.mean())

    # 4. Which inputs push the price up or down? (coefficients of scaled inputs)
    names = common.feature_names(model)
    coefs = pd.Series(model.named_steps["model"].coef_, index=names)
    common.plot_regression(NAME, "Linear Regression", y_test, pred)
    common.plot_importance(NAME, "Linear Regression", coefs.index, coefs.values,
                           label="Coefficient (EUR per 1 std. dev. / category)")

    top = coefs.abs().sort_values(ascending=False).head(3).index.tolist()
    result = common.make_result(NAME, TASK, metrics, {"fit_intercept": True}, started,
                                notes="strongest inputs: " + ", ".join(top))
    common.save_result(result)
    return result
