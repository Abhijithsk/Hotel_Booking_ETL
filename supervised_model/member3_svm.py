"""MEMBER 3 - Support Vector Machine (classification task: will the booking be cancelled?).

Idea: find the boundary (hyperplane) that separates the two classes with the widest possible
margin. The RBF kernel lets the boundary curve. Training time grows roughly with n^2, so the
SVM is trained on a 15,000-row sample of the training data (tested on the full 20% test set).

STUB - Member 3 (Keerthi) replaces this file with the real implementation
(see supervised_model/tasks/member3.md).
"""

NAME = "svm"
TASK = "classification"


def run(df=None, fast=False):
    """Train, evaluate and save results; return the dictionary made by common.make_result()."""
    raise NotImplementedError("Member 3: implement run() - see supervised_model/tasks/member3.md")
