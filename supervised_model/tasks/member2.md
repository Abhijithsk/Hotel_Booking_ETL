# Task card - Member 2 (Farhan): Logistic Regression

**Branch:** `feature/supervised-member2-logistic-regression`
**Your file(s):** `member2_logistic_regression.py` (inside `supervised_model/`)
**Your tests:** `test_ml_logistic_regression.py` (inside `supervised_model/tests/`)
**Shared helpers (read, do not edit):** `supervised_model/common.py`
**Merge position:** after the supervised_model scaffold PR (members may merge in any order)

## Goal
Predict whether a booking will be cancelled and see which inputs raise the cancellation odds.

## Steps
- [ ] 1. Split with `common.prepare(df, "classification")`
- [ ] 2. Pipeline: shared preprocessor + `LogisticRegression`
- [ ] 3. Tune the regularisation strength C with `GridSearchCV` (3-fold, scoring F1)
- [ ] 4. Predict classes and probabilities on the test set
- [ ] 5. Metrics with `common.classification_metrics`; confusion matrix + ROC; coefficient chart
- [ ] 6. Save with `common.make_result` and `common.save_result`

## Done when
- [ ] `flake8 .` is clean
- [ ] `test_ml_logistic_regression.py` pass (they skip while your file is still a stub)
- [ ] `python -m supervised_model.train_models --only logistic_regression` prints your row(s) with sensible metrics
- [ ] Pull request approved by a teammate and merged

## Be ready to explain in the review
- Why is it called regression but used for classification (sigmoid, probability, 0.5 threshold)?
- What does C control? What is regularisation?
- Why is accuracy alone misleading here (baseline 72%)? What do precision, recall and F1 add?
- What does ROC-AUC mean?
