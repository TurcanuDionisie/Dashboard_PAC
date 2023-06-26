# -*- coding: utf-8 -*-
"""
Created on Mon Jun 26 14:31:53 2023

@author: Dionisie.Turcanu
"""

import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State

app = dash.Dash(__name__)

app.layout = html.Div([
    html.Table([
        html.Tr([html.Td("Input 1:"), html.Td(dcc.Input(id='input-1', type='text'))]),
        html.Tr([html.Td("Input 2:"), html.Td(dcc.Input(id='input-2', type='text'))]),
        # Aggiungi ulteriori righe come questa per più input
    ]),
    html.Button('Controlla', id='button'),
    html.Div(id='error-message')
])

@app.callback(
    Output('error-message', 'children'),
    [Input('button', 'n_clicks')],
    [State('input-1', 'value'),
     State('input-2', 'value')]
    # Aggiungi più stati come questo per più input
)
def update_output(n_clicks, input1, input2):
    if n_clicks is None:
        # Non fare nulla finché il pulsante non viene premuto
        return ""
    error_message = ""
    if input1 != input1.lower():
        error_message += "L'input 1 deve essere in minuscolo. "
    if input2 != input2.lower():
        error_message += "L'input 2 deve essere in minuscolo. "
    # Aggiungi ulteriori controlli come questo per più input
    return error_message

if __name__ == '__main__':
    app.run_server()
