"""MEMBER 3 - K-Nearest Neighbours (classification task: will the booking be cancelled?).

Idea: to classify a booking, find the k most similar bookings in the training data (smallest
distance) and take a majority vote of their labels. Distances need scaled inputs, which the
shared preprocessor provides.

STUB - Member 3 (Keerthi) replaces this file with the real implementation
(see supervised_model/tasks/member3.md).
"""

NAME = "knn"
TASK = "classification"


def run(df=None, fast=False):
    """Train, evaluate and save results; return the dictionary made by common.make_result()."""
    raise NotImplementedError("Member 3: implement run() - see supervised_model/tasks/member3.md")
