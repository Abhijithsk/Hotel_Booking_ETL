# Task card - Member 4 (Anaz): Decision Tree and Random Forest

**Branch:** `feature/supervised-member4-tree-models`
**Your file(s):** `member4_decision_tree.py` and `member4_random_forest.py` (inside `supervised_model/`)
**Your tests:** `test_ml_decision_tree.py` and `test_ml_random_forest.py` (inside `supervised_model/tests/`)
**Shared helpers (read, do not edit):** `supervised_model/common.py`
**Merge position:** after the supervised_model scaffold PR (members may merge in any order)

## Goal
Predict cancellations with a single tree and with a forest of trees, and show which features matter most.

## Steps
- [ ] 1. Decision Tree: tune `max_depth` and `min_samples_leaf` with `GridSearchCV`
- [ ] 2. Decision Tree: metrics, confusion matrix + ROC, feature-importance chart
- [ ] 3. Random Forest: `RandomForestClassifier` (200 trees, max_depth 20)
- [ ] 4. Random Forest: metrics, confusion matrix + ROC, feature-importance chart
- [ ] 5. Save results for both models

## Done when
- [ ] `flake8 .` is clean
- [ ] `test_ml_decision_tree.py` and `test_ml_random_forest.py` pass (they skip while your file is still a stub)
- [ ] `python -m supervised_model.train_models --only decision_tree random_forest` prints your row(s) with sensible metrics
- [ ] Pull request approved by a teammate and merged

## Be ready to explain in the review
- What is overfitting, and how does limiting the depth fight it?
- Why is a forest better than one tree (bagging, random feature subsets, voting)?
- How are feature importances computed and what are their limits?
- Why do trees not need scaled inputs?
