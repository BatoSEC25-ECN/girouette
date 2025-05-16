import os
import sys
import random
import logging
from typing import List

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Set up logging
logger = logging.getLogger(__name__)


def _get_random_color() -> str:
    """Return a random color from a predefined palette."""
    colors = ["black", "mediumpurple", "orangered", "firebrick", "teal", "olive"]
    return random.choice(colors)


def _load_csv_file(filepath: str) -> pd.DataFrame:
    """Load a CSV file into a DataFrame and ensure content validity."""
    df = pd.read_csv(filepath)
    if df.empty or len(df.columns) < 1:
        raise ValueError(f"CSV file '{filepath}' is empty or has no columns.")
    return df


def check_df_consistency(dataframes: List[pd.DataFrame], filenames: List[str]) -> None:
    """Ensure all DataFrames have the same structure."""
    reference_columns = dataframes[0].columns
    for i, df in enumerate(dataframes[1:], start=1):
        if not reference_columns.equals(df.columns):
            logger.error("Inconsistent columns in file: %s", filenames[i])
            sys.exit(-1)


def build_figure(dataframes: List[pd.DataFrame], filenames: List[str]) -> go.Figure:
    """Create and return a plotly figure with subplots for each column of the dataframes."""
    column_names = dataframes[0].columns.tolist()
    fig = make_subplots(
        rows=len(column_names),
        cols=1,
        shared_xaxes=False,
        subplot_titles=column_names,
        vertical_spacing=0.06,
    )

    for index, df in enumerate(dataframes):
        filename = filenames[index].removesuffix(".csv", "")
        color = _get_random_color()

        for row, col_name in enumerate(column_names[1:], start=1):  # Skip 'Timestamp'
            fig.add_trace(
                go.Scatter(
                    x=df["Timestamp"],
                    y=df[col_name],
                    name=f"{col_name} - {filename}, measure {index}",
                    line=dict(color=color),
                ),
                row=row,
                col=1,
            )

    fig.update_layout(
        margin=dict(l=30, r=30),
        template="ggplot2",
    )
    return fig


def plot_collected_data(folder: str, filenames: List[str]) -> None:
    """
    Plot measurements from CSV files in subplots.
    Each subplot corresponds to a column in the data (excluding 'Timestamp').
    """
    csv_paths = []
    for file in filenames:
        if not file.endswith(".csv"):
            logger.error("File '%s' is not a CSV.", file)
            sys.exit(-1)
        csv_paths.append(os.path.join(folder, file))

    dataframes = [_load_csv_file(path) for path in csv_paths]
    check_df_consistency(dataframes, filenames)

    fig = build_figure(dataframes, filenames)
    fig.show()
