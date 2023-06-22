# -*- coding: utf-8 -*-
"""
Created on Wed Jun 21 11:49:57 2023

@author: Dionisie.Turcanu
"""

import dash
from dash import dcc, html
from dash.dependencies import Input, Output

app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Dropdown(
        id='my-dropdown',
        options=[
            {'label': 'Opzione 1', 'value': '1'},
            {'label': 'Opzione 2', 'value': '2'},
            {'label': 'Opzione 3', 'value': '3'},
            # Aggiungi tutte le opzioni necessarie
        ],
        multi=True
    ),
    html.Table(id='my-table', children=[])
])

@app.callback(
    Output('my-table', 'children'),
    Input('my-dropdown', 'value')
)
def update_table(selected_values):
    if selected_values is None:
        # Se non è selezionato nulla, ritorna una tabella vuota
        return []
    else:
        # Crea una lista di html.Tr per ciascun valore selezionato
        rows = []
        for value in selected_values:
            row = html.Tr(children=[
                html.Td(children=value),
                html.Td(children=dcc.Input(value="", id=f'input-{value}', type='text'))
            ])
            rows.append(row)
        return rows

if __name__ == '__main__':
    app.run_server()
