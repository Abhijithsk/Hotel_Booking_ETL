# unsupervised_model - clustering the hotel bookings

Unsupervised learning has **no target to predict**. Here we ask: *do the bookings fall into
natural groups (guest segments)?* Four clustering algorithms are tried on the cleaned dataset
(`output/analysis_ready_hotel_bookings.csv`, 86,638 bookings) and compared fairly. Each member
owns one algorithm, in their own file, on their own branch.

| Member | Name | Algorithm | File |
|---|---|---|---|
| 1 | Abhijith (lead) | **K-Means** (main model) | `member1_kmeans.py` |
| 2 | Farhan | **Agglomerative** (hierarchical, ward) | `member2_agglomerative.py` |
| 3 | Keerthi | Gaussian Mixture (soft clustering) | `member3_gmm.py` |
| 4 | Anaz | HDBSCAN (density based) | `member4_hdbscan.py` |
| Lead | Abhijith | shared helpers, runner, comparison | `common.py`, `run_clustering.py` |

Task cards: [tasks/member1.md](tasks/member1.md), [member2](tasks/member2.md),
[member3](tasks/member3.md), [member4](tasks/member4.md).

## Step 1 - the labelled data is removed BEFORE clustering
The dataset contains columns that describe the **outcome** of a booking. A clustering model must
not see them, otherwise the clusters would simply copy the answer:

| Removed before clustering (`LABEL_COLUMNS`) | Why |
|---|---|
| `is_cancelled` | the cancellation label |
| `reservation_status`, `reservation_status_date` | contain the cancellation outcome |
| `realized_revenue`, `estimated_revenue` | computed from the price and the outcome |

`common.prepare()` drops them first and then **asserts** that none of them is a feature; a test
changes the labels and checks that the feature matrix does not change. The removed
`is_cancelled` column is used only **after** clustering, to describe each cluster
("what share of this cluster cancelled?"). It never decides which booking joins which cluster.

## Step 2 - features
13 numeric booking-behaviour features: lead time (log), total nights, daily rate, total guests,
has children, special requests, booking changes, previous cancellations (log), previous
bookings kept (log), repeat guest, has agent, has company, waiting days (log).
Skewed counts are log-transformed and every feature is standardised (mean 0, std 1) because
clustering is distance based and a column measured in euros would otherwise dominate one
measured in 0/1.

We tested adding one-hot encoded text columns: the silhouette fell from 0.37 to 0.27, because
0/1 dummy columns dominate the distances. Text columns (hotel, market segment) are therefore
used only in the cluster profile. Post-arrival columns such as `parking_spaces` are not used.

## Step 3 - choosing the number of clusters (k)
We try k = 3 ... 8 and rank each k by **silhouette** (higher is better) and **Davies-Bouldin**
(lower is better); the smallest rank sum wins (`common.choose_k`). k = 2 is excluded: it only
separates a small group of repeat / company guests from everyone else (silhouette 0.50, but
not useful). K-Means picks **k = 5**.

## Step 4 - how a clustering is judged without labels
| Score | Meaning |
|---|---|
| Silhouette (-1 to 1) | how much closer a booking is to its own cluster than to the next one |
| Davies-Bouldin (lower is better) | how compact and well separated the clusters are |
| Calinski-Harabasz (higher is better) | between-cluster versus within-cluster spread |
| Stability (ARI, 1 = identical) | do different random starts give the same clusters? |
| Smallest / largest cluster share | guards against one giant cluster plus crumbs |

**A high silhouette alone is not proof of a good clustering.** Average, complete and single
linkage reach 0.53-0.64 but put 95-99 % of all bookings in one cluster
(`agglomerative_linkage_comparison.csv`).

## Results (our run on all 86,638 bookings)
| Model | Clusters | Silhouette | Davies-Bouldin | Stability | Notes |
|---|---|---|---|---|---|
| **K-Means** | 5 | 0.369 | 1.18 | 1.00 | 15 s; best overall: simple, stable, useful segments |
| Agglomerative (ward) | 6 | 0.373 | 1.14 | 0.84 | fitted on a 10,000 sample, others assigned to the nearest centre |
| Gaussian Mixture | 4 | 0.362 | 1.22 | 0.64 | soft probabilities, but least stable |
| HDBSCAN | 4 | 0.365 | 0.98 | - | 12 % of bookings are noise; scored on a 15,000 sample without noise |

K-Means and Agglomerative are almost tied on the scores. K-Means wins on stability, speed and
because every booking can be labelled directly. Agglomerative cannot handle all 86,638 rows at
once (the distance table would need about 60 GB).

## The five K-Means segments
| # | Segment | Share | What defines it | Cancel rate* |
|---|---|---|---|---|
| 1 | Standard agent bookings | 75 % | couples (1.9 guests), no children, booked through an agent | 29 % |
| 2 | Families | 10 % | 92 % with children, 3.4 guests, highest price (EUR 157) | 35 % |
| 3 | Loyal repeat guests | 4 % | 94 % repeat guests, short lead time (18 days), cheap | 8 % |
| 4 | Long-wait bookings | 1 % | on the waiting list about 47 days, books 182 days ahead | 35 % |
| 5 | Direct / company bookers | 10 % | almost no agent, 38 % company, 38-day lead time | 14 % |

\* the cancellation label was **not** used for clustering; the clear differences (8 % to 35 %)
show the segments are meaningful.

## How to run (from the repository root)
```bash
pip install -r requirements-dev.txt
python pipeline.py                                          # only if the cleaned CSV is missing
python -m unsupervised_model.run_clustering                 # all models, about 2 minutes
python -m unsupervised_model.run_clustering --only kmeans   # selected models
python -m unsupervised_model.run_clustering --fast          # 3,000-row demo
pytest                                                      # also runs unsupervised_model/tests
```
Outputs go to `unsupervised_model/results/`: `metrics/`, `profiles/` (one table per model),
`charts/` (cluster map, profile heat map, k selection, dendrogram, comparison) and
`model_comparison.csv`.
