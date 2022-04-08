#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Conference Statistics
---------------------
Generate and plot statistics about papers at a conference

@author: Hrishikesh Terdalkar
"""

###############################################################################

import sqlite3
from datetime import datetime as dt

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator

###############################################################################

PAPERS_FILE = "papers.csv"
DATABASE_FILE = "submissions.db"
SELECT_QUERY = "SELECT * FROM submissions"

###############################################################################
# Default Configurations

BIN_COUNTS = {
    "created_at": 5,
    "submission_id": 5,
    "number_of_authors": 5,
    "number_of_words_in_title": 5,
    "number_of_chars_in_title": 5,
    "number_of_words_in_abstract": 5,
    "is_student_paper": 2,
    # "modified_at": 5,
    # "country": 5,
}

VIEW_COLORS = {
    "all": "lightseagreen",
    "accept_short": "palegreen",
    "accept_long": "seagreen",
    "accept": "green",
    "reject": "indianred",
}

###############################################################################


def sqlite_to_dataframe(input_file, sqlite_query):
    """Read Results of an SQLite Query into a Pandas DataFrame"""
    con = sqlite3.connect(input_file)
    df = pd.read_sql_query(sqlite_query, con)
    con.close()
    return df


###############################################################################


def create_numpy_histograms(df, bin_counts):
    histograms = {}
    for column_name, bin_count in bin_counts.items():
        histograms[column_name] = np.histogram(df[column_name], bin_count)
    return histograms


###############################################################################


def plot_attribute(
    histograms, hist_name, is_normalized=False, plot_views=None
):
    """Plot histogram of the specified attribute"""
    fig, ax = plt.subplots()
    view_colors = VIEW_COLORS.copy()

    if plot_views is None and is_normalized:
        plot_views = [view for view in view_colors if view != "all"]

    if plot_views is not None:
        view_colors = {k: v for k, v in view_colors.items() if k in plot_views}

    curr_start = 0
    view_count = len(view_colors)

    for view_name, view_color in view_colors.items():
        print(
            f"histograms[{hist_name}][{view_name}]:",
            histograms[hist_name][view_name],
        )
        heights, bins = histograms[hist_name][view_name]
        width = (bins[1] - bins[0]) / (view_count + 1)
        rects = ax.bar(
            bins[:-1] + curr_start,
            heights,
            width=width,
            facecolor=view_color,
            label=view_name,
        )
        for rect in rects:
            height = rect.get_height()
            ax.text(
                rect.get_x() + rect.get_width() / 2.0,
                height * 1.01,
                f"{height:.1f}",
                fontsize=6,
                ha="center",
                va="bottom",
                alpha=0.5,
            )

        curr_start += width

    if hist_name in ["created_at", "modified_at"]:
        xticks = [
            dt.fromtimestamp(x).strftime("%Y-%m-%d %H:%M")
            for x in ax.get_xticks()
        ]
        ax.xaxis.set_major_locator(FixedLocator(ax.get_xticks()))
        ax.set_xticklabels(xticks, fontsize=6, rotation=30)
        plt.subplots_adjust(bottom=0.15)

    if hist_name in ["is_student_paper"]:
        ax.xaxis.set_major_locator(FixedLocator([0.15, 0.65]))
        ax.set_xticklabels(["No", "Yes"], fontsize=8)

    plt.legend(title="View", fontsize=8)
    if is_normalized:
        plt.ylabel("Percentage")
        plt.title(f"Percentages per bin on '{hist_name}'", fontsize=10)
    else:
        plt.ylabel("Count")
        plt.title(f"Counts per bin on '{hist_name}'", fontsize=10)

    plt.show()


###############################################################################


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Conference Statistics")
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
    parser.add_argument(
        "--papers", help="List of all papers", default=PAPERS_FILE
    )
    args = vars(parser.parse_args())

    # ----------------------------------------------------------------------- #
    # parse arguments

    database_file = args["database"]
    papers_file = args["papers"]
    attribute = args["attribute"]
    normalize = args["normalize"]
    number_of_bins = args["bins"] or BIN_COUNTS[attribute]
    plot_views = args.get("views", None)

    # ----------------------------------------------------------------------- #
    # read into dataframe
    df = sqlite_to_dataframe(database_file, SELECT_QUERY)

    # ----------------------------------------------------------------------- #
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

    # read papers file for authors details
    papers = pd.read_csv(papers_file)
    papers["number_of_authors"] = papers["Authors"].apply(
        lambda x: x.count(";") + 1
    )
    df = df.merge(papers, left_on="id", right_on="Paper ID", how="left")

    # ----------------------------------------------------------------------- #
    # views

    views = {
        "accept_long": df.query("status == 'Long'"),
        "accept_short": df.query("status == 'Short'"),
        "accept": df.query("status in ['Long', 'Short']"),
        "reject": df.query("status in ['Reject', 'Desk Reject']"),
    }

    # ----------------------------------------------------------------------- #
    # generate histograms

    bin_counts = BIN_COUNTS.copy()
    bin_counts[attribute] = number_of_bins
    overall_histograms = create_numpy_histograms(df, bin_counts)

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
                    heights / all_heights * 100,
                    bins,
                )
        histograms = normalized_histograms

    # ----------------------------------------------------------------------- #
    # plot

    plot_attribute(
        histograms,
        hist_name=attribute,
        is_normalized=normalize,
        plot_views=plot_views,
    )

    return 0


###############################################################################


if __name__ == "__main__":
    import sys

    sys.exit(main())
