# Task card - Member 1 (Abhijith): K-Means

**Branch:** `feature/unsupervised-member1-kmeans`
**Your file:** `member1_kmeans.py` (inside `unsupervised_model/`)
**Your tests:** `test_um_kmeans.py` (inside `unsupervised_model/tests/`)
**Shared helpers (read, do not edit):** `unsupervised_model/common.py`
**Merge position:** after the unsupervised_model scaffold PR (members may merge in any order)

## Goal
Find natural guest segments with K-Means and choose the number of clusters objectively.

## Steps
- [ ] 1. `common.prepare(df, fast)` removes the labels, builds and standardises the features
- [ ] 2. Fit K-Means for k = 3..8, collect inertia, silhouette, Davies-Bouldin
- [ ] 3. Choose k with `common.choose_k`, draw the k-selection chart
- [ ] 4. Fit the final model, score it, measure stability across 3 random starts
- [ ] 5. Profile the clusters (cancel rate is used only here) and draw the cluster map and heat map
- [ ] 6. Save with `common.make_result` and `common.save_result`

## Done when
- [ ] `flake8 .` is clean
- [ ] test_um_kmeans.py passes (it skips while your file is still a stub)
- [ ] `python -m unsupervised_model.run_clustering --only kmeans` prints your row
- [ ] Pull request approved by a teammate and merged

## Be ready to explain in the review
- Why must the label columns be removed before clustering, and where is `is_cancelled` used afterwards?
- How does K-Means work (assign, update, repeat) and what is inertia?
- Why scale the features? Why is k = 2 excluded?
- What do silhouette and Davies-Bouldin measure, and what does stability (ARI) tell you?
- What are the five segments and what would the hotel do with them?
