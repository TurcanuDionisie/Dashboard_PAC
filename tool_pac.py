import pandas as pd
import numpy as np
import os
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt
import plotly.graph_objs as go
import math

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, ALL
from dash import dash_table
from dash import ctx
import dash_bootstrap_components as dbc
from PIL import Image
from io import BytesIO
import requests
import random

#%% CALCOLI INIZIALI


def generate_data(value):
    # Genera una lista di 100 numeri casuali tra 0 e 100 per l'asse x
    x = [random.uniform(0, 100) for _ in range(100)]
    # Genera una lista di 100 numeri casuali tra 0 e 100 per l'asse y
    y = [random.uniform(0, 100) for _ in range(100)]
    return {'x': x, 'y': y}


#decodifiche FONDO - SGR
codifiche = pd.read_excel("codifiche.xlsx", index_col=0)
SGR = codifiche['SGR'].unique()




#FONDI DA INSIERIRE NEL MULTIDROPDOWN
df_options = pd.DataFrame({
    'OptionID': SGR,
    'OptionLabel': SGR,
})

df_suboptions = pd.DataFrame({
    'OptionID': codifiche['SGR'],
    'SubOptionLabel': codifiche['FONDO'],
    'SubOptionValue': codifiche['FONDO'],
})


# Opzioni per il menu a discesa di base
basic_options = {}
for _, row in df_options.iterrows():
    option_id = row['OptionID']
    option_label = row['OptionLabel']
    suboptions = df_suboptions[df_suboptions['OptionID'] == option_id]
    basic_options[option_label] = [{'label': r['SubOptionLabel'], 'value': r['SubOptionValue']} for _, r in suboptions.iterrows()]







#%% DASHBOARD

app = dash.Dash(__name__, 
                title ='Tool PAC')
server = app.server

# Add the following line to set the favicon

#use href="/assets/favicon.ico" to get favicon from local folder (named 'assets' and subdirectory) instead of github

app.index_string = '''
    <!DOCTYPE html>
    <html>
        <head>           
            <link rel="shortcut icon" href="https://raw.githubusercontent.com/marzowill96/Monitoraggio_Analisi_Performance/main/favicon.ico"  type="image/x-icon">
            {%metas%}
            <title>{%title%}</title>
            {%favicon%}
            {%css%}
        </head>
        <body>
            {%app_entry%}
            <footer>
                {%config%}
                {%scripts%}
                {%renderer%}
            </footer>
        </body>
    </html>
'''


app.layout = html.Div([
    dcc.Dropdown(
        id='basic-dropdown',
        options=[{'label': key, 'value': key} for key in basic_options.keys()],
        value='Opzione 1'  # valore iniziale
    ),
    dcc.Dropdown(
        id='multi-dropdown',
        multi=True
    ),
    html.Table(id='my-table', children=[]),
    html.Button('Stampa valori', id='print-button', n_clicks=0),  # aggiungi il pulsante
    html.Div(id='dummy-output'),  # componente "dummy" usato per il callback del pulsante
    dcc.Store(id='store-inputs', data={})  # componente di storage per conservare i valori di input
])

# Aggiungi un callback per ogni input generato dinamicamente
@app.callback(
    Output('store-inputs', 'data'),
    [Input({'type': 'dynamic-input', 'index': ALL}, 'value')],
    [Input({'type': 'dynamic-input', 'index': ALL}, 'id')],
    [State('store-inputs', 'data')]
)
def update_store(input_values, input_ids, data):
    for value, id in zip(input_values, input_ids):
        data[id['index']] = value
    return data

# Aggiorna le opzioni del multi-dropdown in base al valore del basic-dropdown
@app.callback(
    Output('multi-dropdown', 'options'),
    Output('multi-dropdown', 'value'),
    [Input('basic-dropdown', 'value')]
)
def update_multi_dropdown(selected_value):
    return basic_options.get(selected_value, []), []

# Aggiorna la tabella con i nuovi input ogni volta che si modifica il valore del dropdown
@app.callback(
    Output('my-table', 'children'),
    [Input('multi-dropdown', 'value')]
)
def update_table(selected_values):
    if selected_values is None or len(selected_values) == 0:
        return []
    else:
        rows = []
        for i, value in enumerate(selected_values):
            row = html.Tr(children=[
                html.Td(children=value),
                html.Td(children=dcc.Input(
                    value="",
                    id={'type': 'dynamic-input', 'index': value},  # usa il valore come indice dell'id
                    type='text'
                ))
            ])
            rows.append(row)
        return rows

# Stampare i valori quando si preme il pulsante
@app.callback(
    Output('dummy-output', 'children'),
    [Input('print-button', 'n_clicks')],
    [State('store-inputs', 'data')]
)
def print_input_values(n_clicks, data):
    if n_clicks > 0:
        for key, value in data.items():
            print(f'Value for {key}: {value}')
    return None


if __name__ == '__main__':
    app.run_server()


