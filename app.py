#!/usr/bin/env python
# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import pandas as pd
import plotly.graph_objs as go

from dataHandler import TimeData, spreadFrame

testdate = 20190614
testname = 'treasuryyields'

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


colors = {
    'background': '#E0E0E2',
    'text': '#050949'
}


df = TimeData(testdate, testname, lookback=252).frame()
pairs = [('10_yr', '2_yr'), ('10_yr', '6_mo'), ('5_yr', '2_yr')]
spreads = spreadFrame(df.copy(), pairs)
curves = df.set_index('date').tail().T

markdown_text = '''
### Dash and Markdown
Dash uses the [CommonMark](http://commonmark.org/)
Check out their [60 Second Markdown Tutorial](http://commonmark.org/help/)
'''

def generate_table(dataframe, max_rows=10):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(
        children='Treasury Yields',
        style={
            'textAlign': 'left',
            'color': colors['text']
        }
    ),

    html.Div(children='Yield Curves', style={
        'textAlign': 'center',
        'color': colors['text']
    }),

    dcc.Graph(
        id='all-yields',
        figure={
            'data': [
                go.Scatter(
                    x=df['date'],
                    y=df[i],
                    text=i.replace('_', ' '),
                    mode='lines',
                    opacity=0.7,
                    marker={
                        'size': 15,
                        'line': {'width': 0.5, 'color': 'white'}
                    },
                    name=i.replace('_', ' ')
                ) for i in df.columns if i != 'date'
            ],
            'layout': go.Layout(
                yaxis={'title': 'Yield (%)'},
                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                legend={'x': 0, 'y': 1},
                hovermode='closest'
            )
        }
    ),

    dcc.Graph(
        id='yields-spreads',
        figure={
            'data': [
                go.Scatter(
                    x=spreads['date'],
                    y=spreads[i],
                    text=i.replace('_', ' '),
                    mode='lines',
                    opacity=0.7,
                    marker={
                        'size': 15,
                        'line': {'width': 0.5, 'color': 'white'}
                    },
                    name=i.replace('_', ' ')
                ) for i in spreads.columns if i != 'date'
            ],
            'layout': go.Layout(
                yaxis={'title': 'Yield Spread (%)'},
                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                legend={'x': 0, 'y': 1},
                hovermode='closest'
            )
        }
    ),

    dcc.Graph(
        id='yield-curve',
        figure={
            'data': [
                go.Scatter(
                        x=[x.replace('_', ' ') for x in curves.index],
                    y=curves[i],
                    text=i.strftime('%b %d, %Y'),
                    mode='lines',
                    opacity=0.7,
                    marker={
                        'size': 15,
                        'line': {'width': 0.5, 'color': 'white'}
                    },
                    name=i.strftime('%b %d, %Y')
                ) for i in curves.columns
            ],
            'layout': go.Layout(
                xaxis={'title': 'Maturity'},
                yaxis={'title': 'Yield (%)'},
                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                legend={'x': 0, 'y': 1},
                hovermode='closest'
            )
        }
    ),
])

if __name__ == '__main__':
    app.run_server(debug=True)
