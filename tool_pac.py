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


import funzioni_pac

#%% CALCOLI INIZIALI


def generate_data(value):
    # Genera una lista di 100 numeri casuali tra 0 e 100 per l'asse x
    x = [random.uniform(0, 100) for _ in range(100)]
    # Genera una lista di 100 numeri casuali tra 0 e 100 per l'asse y
    y = [random.uniform(0, 100) for _ in range(100)]
    return {'x': x, 'y': y}


#decodifiche FONDO - SGR
codifiche = pd.read_excel("codifiche.xlsx", index_col=0)
SGR = codifiche['FAMIGLIA'].unique()




#FONDI DA INSIERIRE NEL MULTIDROPDOWN
df_options = pd.DataFrame({
    'OptionID': SGR,
    'OptionLabel': SGR,
})

df_suboptions = pd.DataFrame({
    'OptionID': codifiche['FAMIGLIA'],
    'SubOptionLabel': codifiche.index,
    'SubOptionValue': codifiche.index,
})


# Opzioni per il menu a discesa di base
basic_options = {}
for _, row in df_options.iterrows():
    option_id = row['OptionID']
    option_label = row['OptionLabel']
    suboptions = df_suboptions[df_suboptions['OptionID'] == option_id]
    basic_options[option_label] = [{'label': r['SubOptionLabel'], 'value': r['SubOptionValue']} for _, r in suboptions.iterrows()]




#lettura quote


quote = pd.read_excel("DB_TOT_PROXY.xlsx", index_col=0)
datetime_index = quote.index


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
    html.Div(id='dummy-output'),  # componente "dummy" usato per il callback del pulsante
    dcc.Store(id='store-inputs', data={}),  # componente di storage per conservare i valori di input
    
    
    #data inizio
    dcc.Dropdown(
        id='data-inizio',
        options=[{'label': str(date), 'value': str(date)} for date in datetime_index],
        value=None
    ),
    
    
    #importo rata
    dcc.Input(
    id='importo-rata',
    type='text',
    placeholder='Importo rata'
    ),
    
    
    html.Button('Stampa valori', id='calcola', n_clicks=0),  # aggiungi il pulsante
    html.Div(id='error-message')
])





# Aggiungi un callback per ogni input generato dinamicamente
@app.callback(
    Output('store-inputs', 'data'),
    [Input({'type': 'dynamic-input', 'index': ALL}, 'value')],
    [Input({'type': 'dynamic-input', 'index': ALL}, 'id')],
    [State('store-inputs', 'data')]
)
def update_store(input_values, input_ids, data):
    data = {id['index']: value for value, id in zip(input_values, input_ids)}
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
    [Input('multi-dropdown', 'value')],
    [State('store-inputs', 'data')]
)
def update_table(selected_values, data):
    if selected_values is None or len(selected_values) == 0:
        data.clear()
        return []
    else:
        rows = []
        for i, value in enumerate(selected_values):
            row = html.Tr(children=[
                html.Td(children=value),
                html.Td(children=dcc.Input(
                    value=data.get(value, ""),
                    id={'type': 'dynamic-input', 'index': value},  # usa il valore come indice dell'id
                    type='text'
                ))
            ])
            rows.append(row)
        return rows


# Stampare i valori quando si preme il pulsante
@app.callback(
    [Output('dummy-output', 'children'),
     Output('error-message', 'children'),   
     ],
    [Input('calcola', 'n_clicks'),
     Input('data-inizio', 'value'),
     Input('importo-rata', 'value')],
    [State('store-inputs', 'data'),
     ]
)

def print_input_values(n_clicks, data_inizio, importo_rata, pesi):
    
    message = ""
    
    if n_clicks > 0:
        
        print(data_inizio)
        
        print(importo_rata)
        
        #controlla che i pesi inseriti siano giusti
        if(funzioni_pac.controlloSommaPesi(pesi)):
            print(pesi)
            
        else:
            message = "Errori nei pesi"
            
            
    
    return None, message




if __name__ == '__main__':
    app.run_server()


