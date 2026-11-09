# supervised_model - machine learning on the cleaned hotel bookings

The ETL pipeline produces `output/analysis_ready_hotel_bookings.csv` (86,638 bookings x 46
columns). This folder trains **six supervised-learning algorithms** on it. Each member owns one
or two algorithms, in their own files, on their own branch.

| Member | Name | Algorithm | Task | Target | File |
|---|---|---|---|---|---|
| 1 | Abhijith (lead) | Linear Regression | regression | `avg_daily_rate` (price) | `member1_linear_regression.py` |
| 2 | Farhan | Logistic Regression | classification | `is_cancelled` | `member2_logistic_regression.py` |
| 3 | Keerthi | K-Nearest Neighbours | classification | `is_cancelled` | `member3_knn.py` |
| 3 | Keerthi | Support Vector Machine | classification | `is_cancelled` | `member3_svm.py` |
| 4 | Anaz | Decision Tree | classification | `is_cancelled` | `member4_decision_tree.py` |
| 4 | Anaz | Random Forest | classification | `is_cancelled` | `member4_random_forest.py` |
| Lead | Abhijith | shared helpers, runner, comparison | - | - | `common.py`, `train_models.py` |

Task cards: [tasks/member1.md](tasks/member1.md), [member2](tasks/member2.md),
[member3](tasks/member3.md), [member4](tasks/member4.md).

## How the pieces fit
```
output/analysis_ready_hotel_bookings.csv
        |  common.py : feature lists, no-leakage rule, preprocessing, 80/20 split, metrics, charts
        v
memberN_<algorithm>.py : run(df, fast) -> trains, evaluates, saves metrics + charts
        v
train_models.py : runs every model, writes results/model_comparison.csv + comparison chart
```
Every model uses the **same** features, the **same** train/test split (80/20, seed 42) and the
**same** metrics, so the comparison is fair.

## Data leakage rule
A model may only use what is known when the prediction is made. We never use
`reservation_status`, `reservation_status_date` (they contain the answer), `realized_revenue`,
`estimated_revenue` (computed from the price and the answer) or `assigned_room_type`,
`room_changed`, `parking_spaces` (only exist after arrival - a cancelled booking never gets
them). The list is `LEAKAGE` in `common.py` and a test enforces it.

## Metrics
* Classification (positive class = cancelled): **accuracy**, **precision** (of predicted
  cancellations, how many were real), **recall** (of real cancellations, how many were found),
  **F1** (balance of the two), **ROC-AUC** (ranking quality, 0.5 = random, 1 = perfect). Compare
  accuracy with `baseline_accuracy` (always predict "kept" = 72.3%).
* Regression: **MAE** and **RMSE** (average error in EUR), **R2** (share of price variation
  explained). Compare with `baseline_rmse` (always predict the average price).

## How to run (from the repository root)
```bash
pip install -r requirements-dev.txt                       # includes scikit-learn
python pipeline.py                                        # only if the cleaned CSV is missing
python -m supervised_model.train_models                   # all models, about 1.5 minutes
python -m supervised_model.train_models --only knn svm    # selected models
python -m supervised_model.train_models --fast            # 3,000-row demo
pytest                                                    # also runs supervised_model/tests
```
Outputs go to `supervised_model/results/`: `metrics/<model>.csv`, `model_comparison.csv`,
`charts/*.png`.
