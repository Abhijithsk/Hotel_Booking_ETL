"""MEMBER 4 - Random Forest (classification task: will the booking be cancelled?).

Idea: many decision trees, each trained on a random sample of the rows and a random subset of
the columns; the forest takes a majority vote. Averaging many different trees removes most of
a single tree's overfitting.
"""

import time

from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline

from supervised_model import common

NAME = "random_forest"
TASK = "classification"


def run(df=None, fast=False):
    """Fit a 200-tree forest and test on unseen data."""
    started = time.time()
    df = common.load_data() if df is None else df
    X_train, X_test, y_train, y_test = common.prepare(df, TASK, fast)

    params = {"n_estimators": 60 if fast else 200, "max_depth": 20,
              "min_samples_leaf": 3, "max_features": "sqrt"}
    model = Pipeline([("prep", common.build_preprocessor(TASK, scale=False)),
                      ("model", RandomForestClassifier(
                          random_state=common.SEED, n_jobs=-1, **params))])
    model.fit(X_train, y_train)

    pred = model.predict(X_test)
    score = model.predict_proba(X_test)[:, 1]
    metrics = common.classification_metrics(y_test, pred, score)

    names = common.feature_names(model)
    imp = model.named_steps["model"].feature_importances_
    common.plot_classification(NAME, "Random Forest", y_test, pred, score)
    common.plot_importance(NAME, "Random Forest", names, imp,
                           label="Importance (mean impurity decrease)")

    top = [names[i] for i in imp.argsort()[::-1][:3]]
    result = common.make_result(NAME, TASK, metrics, params, started,
                                notes="most important: " + ", ".join(top))
    common.save_result(result)
    return result
