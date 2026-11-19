# Task card - Member 2 (Farhan): Agglomerative clustering

**Branch:** `feature/unsupervised-member2-agglomerative`
**Your file:** `member2_agglomerative.py` (inside `unsupervised_model/`)
**Your tests:** `test_um_agglomerative.py` (inside `unsupervised_model/tests/`)
**Shared helpers (read, do not edit):** `unsupervised_model/common.py`
**Merge position:** after the unsupervised_model scaffold PR (members may merge in any order)

## Goal
Cluster the bookings hierarchically, show the dendrogram and compare linkage types.

## Steps
- [ ] 1. Fit ward linkage on a random sample of 10,000 bookings for k = 3..8 and choose k
- [ ] 2. Give every booking the cluster of the nearest sample-cluster centre
- [ ] 3. Compare ward / average / complete / single linkage (silhouette AND largest cluster share)
- [ ] 4. Draw the dendrogram, the cluster map and the heat map
- [ ] 5. Measure stability over different samples and agreement with K-Means (ARI)
- [ ] 6. Save with `common.make_result` and `common.save_result`

## Done when
- [ ] `flake8 .` is clean
- [ ] test_um_agglomerative.py passes (it skips while your file is still a stub)
- [ ] `python -m unsupervised_model.run_clustering --only agglomerative` prints your row
- [ ] Pull request approved by a teammate and merged

## Be ready to explain in the review
- How does bottom-up (agglomerative) clustering work, and what does ward linkage minimise?
- How do you read a dendrogram and where do you cut it?
- Why is a sample needed, and why is propagating labels to the other bookings acceptable?
- Why do average / complete / single linkage score a higher silhouette but give useless clusters?
- How similar are the K-Means and agglomerative clusters?
