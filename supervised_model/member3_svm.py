"""MEMBER 3 - Support Vector Machine (classification task: will the booking be cancelled?).

Idea: find the boundary (hyperplane) that separates the two classes with the widest possible
margin. The RBF kernel lets the boundary curve. Training time grows roughly with n^2, so the
SVM is trained on a 15,000-row sample of the training data (tested on the full 20% test set).
"""

import time

from sklearn.pipeline import Pipeline
from sklearn.svm import SVC

from supervised_model import common

NAME = "svm"
TASK = "classification"
TRAIN_SAMPLE = 15000


def run(df=None, fast=False):
    """Fit an RBF-kernel SVM on a train sample, test on unseen data."""
    started = time.time()
    df = common.load_data() if df is None else df
    X_train, X_test, y_train, y_test = common.prepare(df, TASK, fast)

    n = min(TRAIN_SAMPLE, len(X_train))
    X_fit, y_fit = X_train.iloc[:n], y_train.iloc[:n]

    model = Pipeline([("prep", common.build_preprocessor(TASK, scale=True)),
                      ("model", SVC(kernel="rbf", C=1.0, gamma="scale"))])
    model.fit(X_fit, y_fit)

    pred = model.predict(X_test)
    score = model.decision_function(X_test)      # distance from the boundary (for ROC-AUC)
    metrics = common.classification_metrics(y_test, pred, score)
    common.plot_classification(NAME, "SVM (RBF kernel)", y_test, pred, score)

    result = common.make_result(
        NAME, TASK, metrics, {"kernel": "rbf", "C": 1.0, "gamma": "scale",
                              "train_rows": n}, started,
        notes=f"trained on {n:,} sampled train rows (SVM is slow on big data)")
    common.save_result(result)
    return result
