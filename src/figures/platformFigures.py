import pandas as pd
import numpy as np
import plotly.graph_objects as go

from plotly.subplots import make_subplots


class PlatformForcesFigure:
    def __init__(
        self, title: str, y_label: str = "Force (N)", x_label: str = "Time (s)"
    ) -> None:
        self.figure = make_subplots(
            rows=3,
            cols=1,
            shared_xaxes=True,
            subplot_titles=(
                "Vertical forces (z axis)",
                "Horizontal forces (x axis)",
                "Horizontal forces (y axis)",
            ),
        )
        self.title = title
        self.x_label = x_label
        self.y_label = y_label

        # Plot style variables
        self.colors = [
            "#ff0000",
            "#00ff00",
            "#0000ff",
            "#ff00cc",
            "#ffcc00",
        ]
        self.markers = [
            "circle",
            "square",
            "diamond",
            "triangle-up",
            "hexagon",
        ]
        self.line_width = 1
        self.total_line_width = 2

    def buildTraces(self) -> None:
        default_sum_force = go.Scatter(
            x=[0],
            y=[0],
            mode="lines",
            line=dict(color="red", width=self.total_line_width),
            name="Total force",
        )

    def getFigure(
        self,
        fx_values: pd.Series | pd.DataFrame,
        fy_values: pd.Series | pd.DataFrame,
        fz_values: pd.Series | pd.DataFrame,
        x_values: pd.Series,
    ) -> go.Figure:

        num_markers = 10

        # Get indexes for even markers in figure
        marker_indexes = np.arange(len(x_values))
        if len(x_values) > num_markers:
            marker_indexes = np.linspace(
                0, len(x_values) - 1, num=num_markers, dtype=int
            )

        for i, values in enumerate([fz_values, fx_values, fy_values]):
            if isinstance(values, pd.Series):
                values = values.to_frame()

            if values.empty:
                continue

            for j, column in enumerate(values.columns):
                self.figure.add_trace(
                    go.Scatter(
                        x=x_values,
                        y=values[column],
                        mode="lines",
                        line=dict(
                            color=self.colors[j % len(self.colors)],
                            width=self.line_width,
                        ),
                        name=column,
                        showlegend=False,
                    ),
                    row=i + 1,
                    col=1,
                )
                if marker_indexes.any():
                    self.figure.add_trace(
                        go.Scatter(
                            x=x_values.iloc[marker_indexes],
                            y=values[column].iloc[marker_indexes],
                            mode="markers",
                            marker=dict(
                                symbol=self.markers[i % len(self.markers)],
                                color=self.colors[j % len(self.colors)],
                                size=10,
                            ),
                            name=column,
                        ),
                        row=i + 1,
                        col=1,
                    )

            self.figure.update_traces(
                x=x_values,
                y=values.sum(axis=1),
                selector="Total force",
                row=i + 1,
                col=1,
            )

        self.figure.update_layout(
            title=self.title,
            xaxis1=dict(
                showgrid=True,
                showline=True,
            ),
            xaxis2=dict(
                showgrid=True,
                showline=True,
            ),
            xaxis3=dict(
                title=self.x_label,
                showgrid=True,
                showline=True,
            ),
            yaxis=dict(
                title=self.y_label,
                showgrid=True,
                showline=True,
            ),
            yaxis2=dict(
                title=self.y_label,
                showgrid=True,
                showline=True,
            ),
            yaxis3=dict(
                title=self.y_label,
                showgrid=True,
                showline=True,
            ),
            height=700,
        )
        return self.figure


class PlatformCOPFigure:
    def __init__(self, title: str) -> None:
        self.figure = go.Figure()
        self.title = title
        self.x_label = "Medio-Lateral (mm)"
        self.y_label = "Anterior-Posterior (mm)"

        self.buildTraces()

    def buildTraces(self) -> None:
        default_ellipse_trace = go.Scatter(
            x=[0],
            y=[0],
            mode="lines",
            line=dict(color="red", width=2),
            fill="toself",
            fillcolor="rgba(255,0,0,0.3)",
            name="LMS ellipse",
        )
        default_cop_trace = go.Scatter(
            x=[0],
            y=[0],
            mode="lines",
            line=dict(color="blue"),
            name="COP",
        )
        default_ellipse_text_trace = go.Scatter(
            x=[0],
            y=[0],
            mode="text",
            name="COP area",
            text=["Area"],
            textposition="middle center",
            textfont=dict(size=14, color="white"),
            showlegend=False,
        )

        self.figure.add_trace(default_cop_trace)
        self.figure.add_trace(default_ellipse_trace)
        self.figure.add_trace(default_ellipse_text_trace)

    def getFigure(
        self,
        y_values: pd.Series,
        x_values: pd.Series,
        ellipy_values: pd.Series,
        ellipx_values: pd.Series,
        area: float,
    ) -> go.Figure:

        self.figure.update_traces(
            x=x_values,
            y=y_values,
            selector=dict(name="COP"),
        )
        self.figure.update_traces(
            x=ellipx_values,
            y=ellipy_values,
            selector=dict(name="LMS ellipse"),
        )
        self.figure.update_traces(
            text=[f"Área: {area:.2f} cm2"],
            selector=dict(name="COP area"),
        )

        self.figure.update_layout(
            title=self.title,
            xaxis=dict(
                title=self.x_label,
                showgrid=True,
                zeroline=True,
                zerolinewidth=2,
                showline=True,
            ),
            yaxis=dict(
                title=self.y_label,
                showgrid=True,
                zeroline=True,
                zerolinewidth=2,
                showline=True,
            ),
        )
        return self.figure
