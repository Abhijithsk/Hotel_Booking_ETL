# Task card - Member 3 (Keerthi): Gaussian Mixture Model

**Branch:** `feature/unsupervised-member3-gmm`
**Your file:** `member3_gmm.py` (inside `unsupervised_model/`)
**Your tests:** `test_um_gmm.py` (inside `unsupervised_model/tests/`)
**Shared helpers (read, do not edit):** `unsupervised_model/common.py`
**Merge position:** after the unsupervised_model scaffold PR (members may merge in any order)

## Goal
Cluster the bookings with a Gaussian mixture and report how confident each assignment is.

## Steps
- [ ] 1. Fit a GMM (full covariance) for 3..8 components
- [ ] 2. Choose the number of components with `common.choose_k`; draw the BIC chart
- [ ] 3. Predict labels, measure the average confidence (highest probability per booking)
- [ ] 4. Measure stability across random starts
- [ ] 5. Draw the cluster map and heat map, profile the clusters
- [ ] 6. Save with `common.make_result` and `common.save_result`

## Done when
- [ ] `flake8 .` is clean
- [ ] test_um_gmm.py passes (it skips while your file is still a stub)
- [ ] `python -m unsupervised_model.run_clustering --only gmm` prints your row
- [ ] Pull request approved by a teammate and merged

## Be ready to explain in the review
- How does a GMM differ from K-Means (probabilities, ellipse-shaped clusters, EM algorithm)?
- What is BIC and why can it not be used alone on 86,000 rows?
- Why is the GMM less stable than K-Means here?
- What does the average confidence tell you?
