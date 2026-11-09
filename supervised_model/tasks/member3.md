# Task card - Member 3 (Keerthi): KNN and SVM

**Branch:** `feature/supervised-member3-knn-and-svm`
**Your file(s):** `member3_knn.py` and `member3_svm.py` (inside `supervised_model/`)
**Your tests:** `test_ml_knn.py` and `test_ml_svm.py` (inside `supervised_model/tests/`)
**Shared helpers (read, do not edit):** `supervised_model/common.py`
**Merge position:** after the supervised_model scaffold PR (members may merge in any order)

## Goal
Predict cancellations with two distance/margin-based models and explain why they need scaled data.

## Steps
- [ ] 1. KNN: pipeline with the shared preprocessor + `KNeighborsClassifier`
- [ ] 2. KNN: choose k with 3-fold CV on a 15,000-row train sample, plot CV F1 against k
- [ ] 3. KNN: refit on the full train set, evaluate on the test set
- [ ] 4. SVM: `SVC(kernel="rbf")` trained on a 15,000-row train sample (it is slow on big data)
- [ ] 5. SVM: use `decision_function` as the score for ROC-AUC
- [ ] 6. Metrics, confusion matrix + ROC, save results for both models

## Done when
- [ ] `flake8 .` is clean
- [ ] `test_ml_knn.py` and `test_ml_svm.py` pass (they skip while your file is still a stub)
- [ ] `python -m supervised_model.train_models --only knn svm` prints your row(s) with sensible metrics
- [ ] Pull request approved by a teammate and merged

## Be ready to explain in the review
- Why do KNN and SVM need scaled inputs?
- How does the choice of k change underfitting and overfitting?
- What is the margin, and what does the RBF kernel add?
- Why is SVM trained on a sample and why is that acceptable (and tested on the full test set)?
