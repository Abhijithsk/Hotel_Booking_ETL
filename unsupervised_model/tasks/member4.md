# Task card - Member 4 (Anaz): HDBSCAN

**Branch:** `feature/unsupervised-member4-hdbscan`
**Your file:** `member4_hdbscan.py` (inside `unsupervised_model/`)
**Your tests:** `test_um_hdbscan.py` (inside `unsupervised_model/tests/`)
**Shared helpers (read, do not edit):** `unsupervised_model/common.py`
**Merge position:** after the unsupervised_model scaffold PR (members may merge in any order)

## Goal
Try a density-based method, report the noise points and explain why it fits this data less well.

## Steps
- [ ] 1. Take a random sample of 15,000 bookings
- [ ] 2. Run HDBSCAN with min_cluster_size = 2% of the sample
- [ ] 3. Score the clustered points (noise excluded) and report the noise percentage
- [ ] 4. Draw the cluster map (noise in grey) and the heat map, profile the clusters
- [ ] 5. Save with `common.make_result` and `common.save_result`

## Done when
- [ ] `flake8 .` is clean
- [ ] test_um_hdbscan.py passes (it skips while your file is still a stub)
- [ ] `python -m unsupervised_model.run_clustering --only hdbscan` prints your row
- [ ] Pull request approved by a teammate and merged

## Be ready to explain in the review
- How does density-based clustering work and what is noise (label -1)?
- Why does HDBSCAN not need k, and what does min_cluster_size control?
- Why are 12 % of bookings noise here, and why does that make it a weaker fit than K-Means?
- Why are its scores not directly comparable with the others?
