# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/model.ipynb.

# %% auto 0
__all__ = ['X_COLS', 'create_line_features', 'do_prepare_train_data_grp', 'prepare_train_data', 'df_to_x_y', 'train_model',
           'load_model', 'prepare_paragraph_from_txt_lines']

# %% ../nbs/model.ipynb 1
import os
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.base import ClassifierMixin
from joblib import dump, load
import numpy as np

# %% ../nbs/model.ipynb 2
def create_line_features(lines: list[str]) -> pd.DataFrame:
    line_lengths = [len(l) for l in lines]
    line_rows = [i for i, _ in enumerate(lines)]
    are_end_of_sent = [
        l.strip()[-1] in [".", "?", "!"] if len(l.strip()) > 0 else False for l in lines
    ]
    are_end_hyphen = [
        l.strip()[-1] in ["-"] if len(l.strip()) > 0 else False for l in lines
    ]
    # erreur car élimine des lignes. ils doit avoir une valeur else
    are_start_upper = [
        l.strip()[0].isupper() if len(l.strip()) > 0 else False for l in lines
    ]
    are_start_bullet = [
        l.strip().startswith(("-", "•", "o ")) if len(l.strip()) > 0 else False
        for l in lines
    ]

    # print(all_lines)
    lines_data = [
        (r, l, e, h, u, b, t)
        for r, t, l, e, h, u, b in iter(
            zip(
                line_rows,
                lines,
                line_lengths,
                are_end_of_sent,
                are_end_hyphen,
                are_start_upper,
                are_start_bullet,
            )
        )
    ]
    lines_df = pd.DataFrame(
        lines_data,
        columns=[
            "row",
            "txt_len",
            "end_with_end_sent",
            "end_with_hyphen",
            "start_with_upper",
            "start_with_bullet",
            "line_txt",
        ],
    )
    lines_df["diff_len_prev"] = lines_df.txt_len.diff()
    lines_df.diff_len_prev = lines_df.diff_len_prev.fillna(lines_df.txt_len)
    lines_df["diff_max_len"] = lines_df.txt_len.max() - lines_df.txt_len

    return lines_df


def do_prepare_train_data_grp(df: pd.DataFrame):
    lines = df.line_txt.values.tolist()
    lines_feats_df = create_line_features(lines)
    prepared_df = pd.concat(
        [lines_feats_df, df.new_paragraph.reset_index().new_paragraph], axis=1
    )
    return prepared_df


def prepare_train_data(lines_df: pd.DataFrame) -> pd.DataFrame:
    lines_df["line_txt"] = lines_df.line_txt.fillna("")
    df = lines_df.groupby("grp").apply(do_prepare_train_data_grp).reset_index()
    return df

# %% ../nbs/model.ipynb 4
from typing import Final

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


def train_model(train_df: pd.DataFrame, version: str = "1.0") -> ClassifierMixin:
    x, y = df_to_x_y(train_df)
    clf = GradientBoostingClassifier()
    clf.fit(x, y)

    model_dir = f"../models/paragraph_clf/{version}"
    os.makedirs(model_dir, exist_ok=True)
    dump(clf, f"{model_dir}/clf.joblib")

    return clf

# %% ../nbs/model.ipynb 10
def load_model(version: str) -> ClassifierMixin:
    clf = load(f"../models/paragraph_clf/{version}/clf.joblib")
    return clf

# %% ../nbs/model.ipynb 12
def prepare_paragraph_from_txt_lines(clf: ClassifierMixin, lines: list[str]) -> str:
    lines_df = create_line_features(lines)
    x = lines_df[X_COLS]
    preds = clf.predict(x).tolist()
    txt = ""
    for l, pred in zip(lines, preds):
        if len(l) > 0:
            if l[-1] == "-":
                l = l[:-1]

        if pred == 1:
            txt += "\n" + l
        else:
            txt += l
    return txt
