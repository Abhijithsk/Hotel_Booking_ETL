"""MEMBER 2 - Logistic Regression (classification task: will the booking be cancelled?).

Idea: a linear score is squeezed through the S-shaped sigmoid function to give a probability
between 0 and 1. Probability >= 0.5 -> predict "cancelled".
"""

import time

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline

from supervised_model import common

NAME = "logistic_regression"
TASK = "classification"


def run(df=None, fast=False):
    """Tune the regularisation strength C with 3-fold CV, then test on unseen data."""
    started = time.time()
    df = common.load_data() if df is None else df
    X_train, X_test, y_train, y_test = common.prepare(df, TASK, fast)

    pipe = Pipeline([("prep", common.build_preprocessor(TASK, scale=True)),
                     ("model", LogisticRegression(max_iter=1000))])
    # Smaller C = stronger regularisation (simpler model). CV picks the best C on TRAIN data.
    search = GridSearchCV(pipe, {"model__C": [0.01, 0.1, 1, 10]}, cv=3, scoring="f1",
                          n_jobs=-1)
    search.fit(X_train, y_train)
    model = search.best_estimator_

    pred = model.predict(X_test)
    score = model.predict_proba(X_test)[:, 1]
    metrics = common.classification_metrics(y_test, pred, score)

    names = common.feature_names(model)
    coefs = model.named_steps["model"].coef_[0]
    common.plot_classification(NAME, "Logistic Regression", y_test, pred, score)
    common.plot_importance(NAME, "Logistic Regression", names, coefs,
                           label="Coefficient (+ raises cancellation odds)")

    top = np.array(names)[np.argsort(-np.abs(coefs))[:3]].tolist()
    result = common.make_result(NAME, TASK, metrics, search.best_params_, started,
                                notes="strongest inputs: " + ", ".join(top))
    common.save_result(result)
    return result
