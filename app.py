#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Central script for running Dash app.
date: 20190618
author: spencerbraun
"""

import argparse
import datetime

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import pandas as pd
import plotly.graph_objs as go
from textwrap import dedent

import dash_wrappers as dw
from dataHandler import TimeData, spreadFrame

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
colors = {"background": "#E0E0E2", "text": "#050949"}

def main():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "-d",
        "--date",
        type=str,
        help="an integer for the accumulator"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="sum the integers (default: find the max)",
    )
    args = parser.parse_args()

    if not args.date:
        date = datetime.datetime.today()


    df = TimeData(date, 'treasuryyields', lookback=252).frame()
    pairs = [("10_yr", "2_yr"), ("10_yr", "6_mo"), ("5_yr", "2_yr")]
    spreads = spreadFrame(df.copy(), pairs)
    curves = df.set_index("date").tail().T


    app.layout = html.Div(
        style={"backgroundColor": colors["background"]},
        children=[
            html.H1(
                children="Treasury Yields",
                style={"textAlign": "left", "color": colors["text"]},
            ),
            dcc.Markdown(
                dedent('''
                \n\n
                ##### Historical Yields
                Access Treasury yields across all maturities. All data is pulled from the Treasury's
                EOD [published](https://www.treasury.gov/resource-center/data-chart-center/interest-rates/pages/textview.aspx?data=yield)
                yield curve rates.
                ''')
            ),
            dcc.Dropdown(
                id="maturity-select",
                options=[
                    {"label": name.replace("_", " "), "value": name}
                    for name in df.columns
                    if name != "date"
                ],
                multi=True,
                value=[name for name in df.columns if name != "date"],
            ),
            dcc.Graph(id="all-yields"),
            dcc.Markdown(
                dedent('''
                \n\n
                ##### Yield Spreads
                Plots the spread between different maturities in the yield curve on a given date.
                A value below 0 indicates an inversion in the maturity pair selected.
                ''')
            ),
            dcc.Dropdown(
                id="maturity-spread-select",
                options=[
                    {"label": name.replace("_", " "), "value": name}
                    for name in spreads.columns
                    if name != "date"
                ],
                multi=True,
                value=[name for name in spreads.columns if name != "date"],
            ),
            dcc.Graph(id="custom-yield-spreads"),
            dcc.Markdown(
                dedent('''
                \n\n
                ##### Yield Curve
                Plots the yield curve on a selected date. The yields used are EOD and are
                published by the Treasury.
                ''')
            ),
            dcc.Graph(
                id="yield-curve",
                figure={
                    "data": [
                        go.Scatter(
                            x=[x.replace("_", " ") for x in curves.index],
                            y=curves[i],
                            text=i.strftime("%b %d, %Y"),
                            mode="lines",
                            opacity=0.7,
                            marker={"size": 15, "line": {"width": 0.5, "color": "white"}},
                            name=i.strftime("%b %d, %Y"),
                        )
                        for i in curves.columns
                    ],
                    "layout": dw.layout("Maturity", "Yield (%)"),
                },
            ),
        ],
    )


    @app.callback(
        Output("custom-yield-spreads", "figure"), [Input("maturity-spread-select", "value")]
    )
    def updateYieldSpreads(selectedSpreads):
        filtered_df = spreads[["date"] + selectedSpreads]
        traces = []
        for spread in selectedSpreads:
            traces.append(
                go.Scatter(
                    x=filtered_df["date"],
                    y=filtered_df[spread],
                    text=spread.replace("_", " "),
                    mode="lines",
                    opacity=0.7,
                    marker={"size": 15, "line": {"width": 0.5, "color": "white"}},
                    name=spread.replace("_", " "),
                )
            )

        return {"data": traces, "layout": dw.layout("Date", "Yield Spread (%)")}


    @app.callback(Output("all-yields", "figure"), [Input("maturity-select", "value")])
    def updateAllYields(maturities):
        filtered_df = df[["date"] + maturities]
        traces = []
        for term in maturities:
            traces.append(
                go.Scatter(
                    x=filtered_df["date"],
                    y=filtered_df[term],
                    text=term.replace("_", " "),
                    mode="lines",
                    opacity=0.7,
                    marker={"size": 15, "line": {"width": 0.5, "color": "white"}},
                    name=term.replace("_", " "),
                )
            )

        return {"data": traces, "layout": dw.layout("Date", "Yield (%)")}

    app.run_server(debug=args.debug)


if __name__ == "__main__":
    main()
