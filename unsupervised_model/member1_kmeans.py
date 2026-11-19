"""MEMBER 1 - K-Means clustering (the main model).

Idea: choose k centres, assign every booking to its nearest centre, move each centre to the
mean of its bookings, and repeat until nothing changes. Fast (about 2 seconds for 86,638 rows)
and easy to explain, which is why it is the main model of this part.

The number of clusters k is NOT given: we try k = 3..8 and pick the best by silhouette and
Davies-Bouldin (see ``common.choose_k``). k = 2 is excluded because it only splits off a small
group of repeat / company guests.

STUB - Member 1 (Abhijith) replaces this file with the real implementation
(see unsupervised_model/tasks/member1.md).
"""

NAME = "kmeans"


def run(df=None, fast=False):
    """Cluster, score, draw and save; return the dictionary made by common.make_result()."""
    raise NotImplementedError("Member 1: implement run() - see unsupervised_model/tasks/member1.md")
