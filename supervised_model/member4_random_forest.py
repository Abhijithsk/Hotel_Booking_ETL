"""MEMBER 4 - Random Forest (classification task: will the booking be cancelled?).

Idea: many decision trees, each trained on a random sample of the rows and a random subset of
the columns; the forest takes a majority vote. Averaging many different trees removes most of
a single tree's overfitting.

STUB - Member 4 (Anaz) replaces this file with the real implementation
(see supervised_model/tasks/member4.md).
"""

NAME = "random_forest"
TASK = "classification"


def run(df=None, fast=False):
    """Train, evaluate and save results; return the dictionary made by common.make_result()."""
    raise NotImplementedError("Member 4: implement run() - see supervised_model/tasks/member4.md")
