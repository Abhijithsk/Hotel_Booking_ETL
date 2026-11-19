"""MEMBER 2 - Agglomerative (hierarchical) clustering.

Idea: start with every booking as its own cluster and repeatedly merge the two closest clusters
until k remain. With ``ward`` linkage the merge that increases the within-cluster variance
least is chosen (similar goal to K-Means).

Limit: the algorithm needs the distance between every pair of bookings (86,638 x 86,638 numbers
is about 60 GB), so we fit it on a random sample of 10,000 bookings and then give every other
booking the cluster of its nearest cluster centre.

We also compare linkage types. Average, complete and single linkage reach a higher silhouette
(0.53-0.64 against 0.37 for ward) but only because they put 95-99 percent of the bookings in
ONE huge cluster and a few outliers in the others - a good lesson that a high score alone
does not mean a useful clustering. The comparison is saved in
``agglomerative_linkage_comparison.csv``.

STUB - Member 2 (Farhan) replaces this file with the real implementation
(see unsupervised_model/tasks/member2.md).
"""

NAME = "agglomerative"


def run(df=None, fast=False):
    """Cluster, score, draw and save; return the dictionary made by common.make_result()."""
    raise NotImplementedError("Member 2: implement run() - see unsupervised_model/tasks/member2.md")
