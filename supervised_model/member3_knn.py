"""MEMBER 3 - K-Nearest Neighbours (classification task: will the booking be cancelled?).

Idea: to classify a booking, find the k most similar bookings in the training data (smallest
distance) and take a majority vote of their labels. Distances need scaled inputs, which the
shared preprocessor provides.
"""

import time

from sklearn.model_selection import cross_val_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline

from supervised_model import common

NAME = "knn"
TASK = "classification"
K_VALUES = [3, 5, 9, 15, 25, 41]


def run(df=None, fast=False):
    """Choose k by 3-fold CV on a train sample (KNN is slow), then test on unseen data."""
    started = time.time()
    df = common.load_data() if df is None else df
    X_train, X_test, y_train, y_test = common.prepare(df, TASK, fast)

    def make(k):
        return Pipeline([("prep", common.build_preprocessor(TASK, scale=True)),
                         ("model", KNeighborsClassifier(n_neighbors=k, n_jobs=-1))])

    # Tune k on a 15,000-row sample of the TRAIN set only (the test set stays untouched)
    n = min(15000, len(X_train))
    Xs, ys = X_train.iloc[:n], y_train.iloc[:n]
    ks = [k for k in K_VALUES if k < n // 3]
    cv = [cross_val_score(make(k), Xs, ys, cv=3, scoring="f1").mean() for k in ks]
    best_k = ks[cv.index(max(cv))]
    common.plot_curve(NAME, "KNN: choosing k (3-fold CV on train sample)", ks, cv,
                      "k (number of neighbours)", "CV F1 score", best=best_k)

    model = make(best_k).fit(X_train, y_train)
    pred = model.predict(X_test)
    score = model.predict_proba(X_test)[:, 1]
    metrics = common.classification_metrics(y_test, pred, score)
    common.plot_classification(NAME, f"KNN (k={best_k})", y_test, pred, score)

    result = common.make_result(NAME, TASK, metrics, {"n_neighbors": best_k}, started,
                                notes="no feature importance - KNN has no coefficients")
    common.save_result(result)
    return result
