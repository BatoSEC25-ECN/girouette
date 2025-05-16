import sys
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Colors for data from each CSV file.
REST_COLOR = "#25a18e"
WIND_COLOR = "#fb6f92"


def _load_csv(path: str):
    df = pd.read_csv(path)
    if len(df.columns) < 1:
        raise ValueError
    return df


def comparison_analysis(csv_1: str, csv_2: str):
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

    df1 = _load_csv(csv_1)
    df2 = _load_csv(csv_2)

    if len(df1.columns) != len(df2.columns):
        print("Measures dont use the same number of probes")
        sys.exit(-1)

    fig = make_subplots(
        rows=len(df1.columns),
        cols=1,
        shared_xaxes=False,
        subplot_titles=list(df1.columns.values.tolist()),
        vertical_spacing=0.06,
    )

    for index, col_name in enumerate(df1.columns.values.tolist()[1:], 1):

        # Plot PWM data (first channel, index 1)
        fig.add_trace(
            go.Scatter(
                x=df1["Timestamp"],
                y=df1[col_name],
                name=f"{col_name}_MEAS1",
                line=dict(color=REST_COLOR),
            ),
            row=index,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=df2["Timestamp"],
                y=df2[col_name],
                name=f"{col_name}_MEAS1",
                line=dict(color=WIND_COLOR),
            ),
            row=index,
            col=1,
        )

    # # Update axis labels.
    # # X-axis: time scale in µs.
    # fig.update_xaxes(title_text="Time (µs)", row=3, col=1)
    # for i in range(1, 4):
    #     fig.update_yaxes(title_text="Voltage (V)", row=i, col=1)

    # Update layout with title including frequency and holder components.
    fig.update_layout(
        margin=dict(l=30, r=30, t=80, b=30),
        title_text="Measures with and without wind.",
        template="ggplot2",
    )

    fig.show()
