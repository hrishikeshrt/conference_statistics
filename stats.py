#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 07 11:13:27 2022

@author: Hrishikesh Terdalkar
"""

###############################################################################

import sqlite3
from datetime import datetime as dt

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

###############################################################################

PAPERS_FILE = "Papers.csv"
DATABASE_FILE = "dasfaa22.db"
SELECT_QUERY = "SELECT * FROM submissions"

###############################################################################

SCHEMA = """
CREATE TABLE submissions
(
    id integer primary key,
    created datetime,
    modified datetime,
    title varchar(150),
    abstract varchar(2000),
    subj1 varchar(100),
    subj2 varchar(100),
    status char(2),
    metareviewer varchar(50),
    student varchar(3),
    sessionid integer default 0,
    sessiontitle varchar(100),
    slot integer,
    track integer
);
"""

###############################################################################

BIN_COUNTS = {
    "number_of_words_in_title": 5,
    "number_of_chars_in_title": 5,
    "number_of_words_in_abstract": 5,
    # "number_of_authors": 2,
    # "is_student_paper": 2,
    "submission_id": 5,
    "created_at": 5,
    # "modified_at": 5,
    # "country": 5,
}

VIEW_COLORS = {
    "all": "lightseagreen",
    "accept_all": "green",
    "accept_long": "seagreen",
    "accept_short": "palegreen",
    "reject": "indianred",
}

###############################################################################


def create_bins(df, bin_counts):
    bins = {}
    for column_name, bin_count in bin_counts.items():
        bins[column_name] = df.groupby(
            pd.cut(df[column_name], bin_count)
        ).size()
    return bins


def create_numpy_histograms(df, bin_counts):
    histograms = {}
    for column_name, bin_count in bin_counts.items():
        histograms[column_name] = np.histogram(df[column_name], bin_count)
    return histograms


###############################################################################


def sqlite_to_dataframe(input_file, sqlite_query):
    """Read Results of an SQLite Query into a Pandas DataFrame"""
    con = sqlite3.connect(input_file)
    df = pd.read_sql_query(sqlite_query, con)
    con.close()
    return df


###############################################################################


def plot_attribute(
    histograms, hist_name, is_normalized=False, plot_views=None
):
    fig, ax = plt.subplots()
    view_colors = VIEW_COLORS.copy()

    if plot_views is None and is_normalized:
        plot_views = [view for view in view_colors if view != "all"]

    if plot_views is not None:
        view_colors = {k: v for k, v in view_colors.items() if k in plot_views}

    curr_start = 0
    view_count = len(view_colors)

    for view_name, view_color in view_colors.items():
        print(histograms[hist_name][view_name])
        heights, bins = histograms[hist_name][view_name]
        width = (bins[1] - bins[0]) / (view_count + 1)
        ax.bar(
            bins[:-1] + curr_start,
            heights,
            width=width,
            facecolor=view_color,
            label=view_name,
        )
        curr_start += width

    plt.legend(title="View")
    plt.xlabel(hist_name)
    if is_normalized:
        plt.ylabel("Percentage")
        plt.title(f"Percentage per bin on '{hist_name}'", fontsize=16)
    else:
        plt.ylabel("Count")
        plt.title(f"Counts per bin on '{hist_name}'", fontsize=16)
    plt.show()


###############################################################################


def main():
    import argparse

    parser = argparse.ArgumentParser(description="DASFAA Statistics")
    parser.add_argument(
        "attribute", help="Attribute to plot", choices=list(BIN_COUNTS)
    )
    parser.add_argument(
        "--views", nargs="*", help="Views to plot", choices=list(VIEW_COLORS)
    )
    parser.add_argument(
        "--normalize", action="store_true", help="Normalize before plotting"
    )
    parser.add_argument("--bins", type=int, help="Number of bins")
    parser.add_argument(
        "--database", help="Database File", default=DATABASE_FILE
    )
    args = vars(parser.parse_args())

    # parse arguments
    database_file = args["database"]
    attribute = args["attribute"]
    normalize = args["normalize"]
    number_of_bins = args["bins"] or BIN_COUNTS[attribute]
    plot_views = args.get("views", None)


    # read into dataframe
    df = sqlite_to_dataframe(database_file, SELECT_QUERY)

    # prepare dataframe
    df["number_of_words_in_title"] = df["title"].apply(
        lambda x: len(x.split())
    )
    df["number_of_chars_in_title"] = df["title"].apply(
        lambda x: len("".join(x.split()))
    )
    df["number_of_words_in_abstract"] = df["abstract"].apply(
        lambda x: len(x.split())
    )
    df["is_student_paper"] = df["student"].apply(lambda x: x == "Yes")
    df["submission_id"] = df["id"]
    df["created_at"] = df["created"].apply(
        lambda x: dt.strptime(x, "%m/%d/%Y %H:%M:%S %p %z").timestamp()
    )
    df["modified_at"] = df["modified"].apply(
        lambda x: dt.strptime(x, "%m/%d/%Y %H:%M:%S %p %z").timestamp()
    )

    # # information about accepted papers
    # papers = pd.read_csv(PAPERS_FILE)
    # papers["number_of_authors"] = papers["Authors"].apply(
    #     lambda x: x.count(";") + 1
    # )
    # df.merge(papers, left_on="id", right_on="Paper ID", how="left")

    bin_counts = BIN_COUNTS.copy()
    bin_counts[attribute] = number_of_bins
    overall_histograms = create_numpy_histograms(df, bin_counts)

    # views
    views = {
        "accept_long": df.query("status == 'Long'"),
        "accept_short": df.query("status == 'Short'"),
        "accept_all": df.query("status in ['Long', 'Short']"),
        "reject": df.query("status in ['Reject', 'Desk Reject']"),
    }

    histograms = {}
    for hist_name, (_heights, _bins) in overall_histograms.items():
        histograms[hist_name] = {"all": (_heights, _bins)}
        for view_name, view_frame in views.items():
            histograms[hist_name][view_name] = np.histogram(
                view_frame[hist_name], bins=_bins
            )

    if normalize:
        normalized_histograms = {}
        for hist_name, view_histogram in histograms.items():
            normalized_histograms[hist_name] = {}
            for view_name, (_heights, _bins) in view_histogram.items():
                heights, bins = histograms[hist_name][view_name]
                all_heights, _ = histograms[hist_name]["all"]
                normalized_histograms[hist_name][view_name] = (
                    heights / all_heights,
                    bins
                )
        histograms = normalized_histograms

    plot_attribute(
        histograms, attribute, is_normalized=normalize, plot_views=plot_views
    )

    return 0


###############################################################################


if __name__ == "__main__":
    import sys

    sys.exit(main())
