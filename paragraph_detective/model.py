# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/model.ipynb.

# %% auto 0
__all__ = ['MODEL_FILE_NAME', 'X_COLS', 'df_to_x_y', 'get_model', 'clean_doc_paragraphs']

# %% ../nbs/model.ipynb 1
import os
import pandas as pd
from typing import Final, Union
from sklearn.base import BaseEstimator
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.base import ClassifierMixin, BaseEstimator
from sklearn.model_selection import cross_val_score
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
import joblib
import yaml
import numpy as np
from pathlib import Path
from dataclasses import dataclass
from .data_prep import prepare_data_from_doc, create_line_features

# %% ../nbs/model.ipynb 2
MODEL_FILE_NAME: Final[str] = "clf.joblib"
X_COLS: Final[list[str]] = [
    "txt_len",
    "end_with_end_sent",
    "end_with_hyphen",
    "start_with_upper",
    "start_with_bullet",
    "diff_len_prev",
    "diff_max_len",
]


def df_to_x_y(train_df) -> tuple[np.ndarray, np.ndarray]:
    y_col = "new_paragraph"
    x = train_df[X_COLS]
    y = train_df[y_col]

    return x, y


def get_model() -> BaseEstimator:
    model_path = Path("../model") / MODEL_FILE_NAME
    clf = joblib.load(model_path)
    return clf

# %% ../nbs/model.ipynb 3
def clean_doc_paragraphs(clf: BaseEstimator, doc_path: Union[str, Path]) -> str:
    lines_df, lines = prepare_data_from_doc(doc_path)
    x = lines_df[X_COLS]
    preds = clf.predict(x).tolist()
    txt = ""
    for l, pred in zip(lines, preds):
        if len(l) > 0:
            if l[-1] == "-":
                l = l[:-1]

        # 1 is for new paragraph.
        if pred == 1:
            txt += "\n" + l
        else:
            txt += l
    return txt
