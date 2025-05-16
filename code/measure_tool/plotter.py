import random
import os
import sys
import logging
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Set up logging
logger = logging.getLogger(__name__)


def _get_color() -> str:
    colors = ["black", "mediumpurple", "orangered", "firebrick", "teal", "olive"]
    return colors[random.randint(0, len(colors) - 1)]


def _extract_df_from_file(path: str):
    df = pd.read_csv(path)
    if len(df.columns) < 1:
        raise ValueError
    return df


def plot_collected_data(
    folder: str,
    files: list[str],
):
    """
    Plot acquired measures on three subplots:
      - PWM (first channel),
      - Sound (second channel),
      - MAX (third channel).

    Two vertical, draggable cursors are added to the Sound graph to measure a time range,
    and a custom fix marker is placed at x = 100 µs.
    Frequency is extracted from the first column of the CSV and displayed in the title.

    Note: For truly dynamic updates when dragging the cursors, you will need to set up callbacks
    (for example, within a Dash app or using Plotly events).
    """
    csv_file = []
    for file in files:
        if not file.endswith(".csv"):
            logger.error('File "%s" is not a CSV file.', file)
            sys.exit(-1)
        else:
            csv_file.append(os.path.join(folder, file))

    df_list = [_extract_df_from_file(df) for df in csv_file]

    # Ensure all dataframes have the same columns
    first_columns = df_list[0].columns
    for idx, df in enumerate(df_list[1:], start=1):
        if not first_columns.equals(df.columns):
            logger.error(
                'Measures in file "%s" do not use the same columns number', files[idx]
            )
            sys.exit(-1)

    # Extract the first dataframe for plotting
    fig = make_subplots(
        rows=len(df_list[0].columns),
        cols=1,
        shared_xaxes=False,
        subplot_titles=list(df_list[0].columns.values.tolist()),
        vertical_spacing=0.06,
    )

    for df_no, df in enumerate(df_list):

        f_name = files[df_no].removesuffix(".csv")
        data_color = _get_color()

        for col_no, col_name in enumerate(df.columns.values.tolist()[1:], 1):

            # Plot PWM data (first channel, index 1)

            fig.add_trace(
                go.Scatter(
                    x=df["Timestamp"],
                    y=df[col_name],
                    name=f" {col_name} - {f_name}, measure n°{df_no}",
                    line=dict(color=data_color),
                ),
                row=col_no,
                col=1,
            )

    # Update layout with title including frequency and holder components.
    fig.update_layout(
        margin=dict(l=30, r=30),
        template="ggplot2",
    )

    fig.show()
