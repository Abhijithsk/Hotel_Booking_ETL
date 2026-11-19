"""MEMBER 4 - HDBSCAN (density-based clustering).

Idea: find dense regions of bookings; the number of clusters is NOT chosen by us, and bookings
that do not belong to any dense region are labelled noise (-1). Good at ignoring outliers and
at finding clusters of any shape.

On this data it finds a few dense groups and labels a share of the bookings as noise (12
percent in our run, and 10-40 percent with other settings), because guests form a continuous
cloud rather than separate islands. That makes it a poor choice for splitting ALL guests into
segments and a good illustration of when density-based clustering does not fit. It runs on a
random sample of 15,000 bookings (the full data takes about 2.5 minutes) and is scored on that
sample.

STUB - Member 4 (Anaz) replaces this file with the real implementation
(see unsupervised_model/tasks/member4.md).
"""

NAME = "hdbscan"


def run(df=None, fast=False):
    """Cluster, score, draw and save; return the dictionary made by common.make_result()."""
    raise NotImplementedError("Member 4: implement run() - see unsupervised_model/tasks/member4.md")
