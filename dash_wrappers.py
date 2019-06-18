#!/usr/bin/env python
# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import plotly.graph_objs as go


def generate_html_table(dataframe, max_rows=10):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])]
        +
        # Body
        [
            html.Tr([html.Td(dataframe.iloc[i][col]) for col in dataframe.columns])
            for i in range(min(len(dataframe), max_rows))
        ]
    )


def layout(xtitle=None, ytitle=None):
    return go.Layout(
        xaxis={"title": xtitle},
        yaxis={"title": ytitle},
        margin={"l": 40, "b": 40, "t": 10, "r": 10},
        legend={"x": 0, "y": 1},
        hovermode="closest",
    )
