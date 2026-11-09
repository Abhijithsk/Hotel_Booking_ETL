"""MEMBER 4 - Decision Tree (classification task: will the booking be cancelled?).

Idea: a flowchart of yes/no questions ("lead_time > 100 days?") learned from the data. Each
leaf gives a prediction. An unlimited tree memorises the training data (overfitting), so we
limit its depth and choose the depth with cross-validation.

STUB - Member 4 (Anaz) replaces this file with the real implementation
(see supervised_model/tasks/member4.md).
"""

NAME = "decision_tree"
TASK = "classification"


def run(df=None, fast=False):
    """Train, evaluate and save results; return the dictionary made by common.make_result()."""
    raise NotImplementedError("Member 4: implement run() - see supervised_model/tasks/member4.md")
