"""MEMBER 4 - Decision Tree (classification task: will the booking be cancelled?).

Idea: a flowchart of yes/no questions ("lead_time > 100 days?") learned from the data. Each
leaf gives a prediction. An unlimited tree memorises the training data (overfitting), so we
limit its depth and choose the depth with cross-validation.
"""

import time

from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier

from supervised_model import common

NAME = "decision_tree"
TASK = "classification"


def run(df=None, fast=False):
    """Tune max_depth and min_samples_leaf with 3-fold CV, then test on unseen data."""
    started = time.time()
    df = common.load_data() if df is None else df
    X_train, X_test, y_train, y_test = common.prepare(df, TASK, fast)

    # Trees do not need scaled inputs, but one shared preprocessor keeps things simple
    pipe = Pipeline([("prep", common.build_preprocessor(TASK, scale=False)),
                     ("model", DecisionTreeClassifier(random_state=common.SEED))])
    grid = {"model__max_depth": [4, 6, 8, 12, 16], "model__min_samples_leaf": [5, 20]}
    search = GridSearchCV(pipe, grid, cv=3, scoring="f1", n_jobs=-1)
    search.fit(X_train, y_train)
    model = search.best_estimator_

    pred = model.predict(X_test)
    score = model.predict_proba(X_test)[:, 1]
    metrics = common.classification_metrics(y_test, pred, score)

    names = common.feature_names(model)
    imp = model.named_steps["model"].feature_importances_
    common.plot_classification(NAME, "Decision Tree", y_test, pred, score)
    common.plot_importance(NAME, "Decision Tree", names, imp,
                           label="Importance (share of impurity reduction)")

    top = [names[i] for i in imp.argsort()[::-1][:3]]
    params = {k.replace("model__", ""): v for k, v in search.best_params_.items()}
    result = common.make_result(NAME, TASK, metrics, params, started,
                                notes="most important: " + ", ".join(top))
    common.save_result(result)
    return result
