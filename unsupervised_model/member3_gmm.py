"""MEMBER 3 - Gaussian Mixture Model (soft clustering).

Idea: assume the data is a mixture of k bell-shaped (Gaussian) groups and learn each group's
centre, spread and weight (EM algorithm). Unlike K-Means, every booking gets a PROBABILITY of
belonging to each cluster; we label it with the most probable one and also report the average
confidence of that choice.

The number of components is chosen with the same rule as K-Means. We also plot BIC (an
information score, lower is better); on this large data set BIC keeps falling as k grows, so
it cannot be used alone.

STUB - Member 3 (Keerthi) replaces this file with the real implementation
(see unsupervised_model/tasks/member3.md).
"""

NAME = "gmm"


def run(df=None, fast=False):
    """Cluster, score, draw and save; return the dictionary made by common.make_result()."""
    raise NotImplementedError("Member 3: implement run() - see unsupervised_model/tasks/member3.md")
