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
from dash.dependencies import Input, Output, State
from dash import dash_table
from dash import ctx
import dash_bootstrap_components as dbc
from PIL import Image
from io import BytesIO
import requests
#%%


import random

def generate_data(value):
    # Genera una lista di 100 numeri casuali tra 0 e 100 per l'asse x
    x = [random.uniform(0, 100) for _ in range(100)]
    # Genera una lista di 100 numeri casuali tra 0 e 100 per l'asse y
    y = [random.uniform(0, 100) for _ in range(100)]
    return {'x': x, 'y': y}


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

# Opzioni per il menu a discesa di base
basic_options = {
    'Opzione 1': [{'label': 'Sotto-opzione 1.1', 'value': '1.1'}, {'label': 'Sotto-opzione 1.2', 'value': '1.2'}],
    'Opzione 2': [{'label': 'Sotto-opzione 2.1', 'value': '2.1'}, {'label': 'Sotto-opzione 2.2', 'value': '2.2'}],
    'Opzione 3': [{'label': 'Sotto-opzione 3.1', 'value': '3.1'}, {'label': 'Sotto-opzione 3.2', 'value': '3.2'}],
}


# Define app layout
app.layout = html.Div([
  
    #TITOLO   
        html.Div(html.H1('Tool PAC'), style={'margin-left': '20px', 'justify-content': 'center','display': 'flex', 'align-items': 'flex-end'}),
        html.Div(html.H2('Engineered by Monitoraggio & Analisi Prodotti di Investimento', 
                 style={'margin-top':'-10px','color': 'black', 'font-style': 'italic', 'font-weight': 'normal','font-size': '1.85vh', 'margin-left': '0px','margin-bottom':'20px', 'justify-content': 'center'}),
                 style={'margin-left': '20px', 'justify-content': 'center','display': 'flex', 'align-items': 'flex-end'}),
        
    #Selezione prodotti    
        dcc.Dropdown(
            id='basic-dropdown',
            options=[{'label': key, 'value': key} for key in basic_options.keys()],
            value='Opzione 1'  # valore iniziale
        ),
        #Selezione fondi 
        dcc.Dropdown(
            id='multi-dropdown',
            multi=True
        ),
        html.Table(id='my-table', children=[]),
        
        
        #Tabella input e dettaglio
        html.Div([
        html.Table([
            html.Tr([
                html.Th('Data Primo Versamento', style={'text-align': 'center','backgroundColor': 'royalblue',
                'color': 'white', 'fontSize':'0.75vw'}),
                html.Th('Versamento Iniziale', style={'text-align': 'center','backgroundColor': 'royalblue',
                'color': 'white', 'fontSize':'0.75vw'}),
                html.Th('Rata', style={'text-align': 'center','backgroundColor': 'royalblue',
                'color': 'white', 'fontSize':'0.75vw'}),
                html.Th('Frequenza', style={'text-align': 'center','backgroundColor': 'royalblue',
                'color': 'white', 'fontSize':'0.75vw'}),
                html.Th('Durata', style={'text-align': 'center','backgroundColor': 'royalblue',
                'color': 'white', 'fontSize':'0.75vw'}),
                html.Th('Deroga', style={'text-align': 'center','backgroundColor': 'royalblue',
                'color': 'white', 'fontSize':'0.75vw'}),
                html.Th('Deroga', style={'text-align': 'center','backgroundColor': 'royalblue',
                'color': 'white', 'fontSize':'0.75vw'}),
                html.Th('Tieni investimento a fine PAC', style={'text-align': 'center','backgroundColor': 'royalblue',
                'color': 'white', 'fontSize':'0.75vw'}),
            ], style={'border': '1px solid black'}),
            
            html.Tr([
                # DATA INIZIO
                html.Td(dcc.Dropdown(
                    id='start_date', 
                    options=[{'label': date, 'value': date} for date in [1,2,3]],
                    value=1), style={'text-align': 'center','border': '1px solid black', 'fontSize':'0.75vw'}),
                
                # IMPORTO
                html.Td(dcc.Input(
                    id='importo',
                    type='number',
                    min=0,style={'position': 'sticky', 'top': '0'} ), style={'text-align': 'center','border': '1px solid black', 'fontSize':'0.75vw'}),
               
                #RATA
                html.Td(dcc.Input(
                    id='rata',
                    type='number',
                    min=0,style={'position': 'sticky', 'top': '0'} ), style={'text-align': 'center','border': '1px solid black', 'fontSize':'0.75vw'}),
                                
               #FREQUENZA  
                html.Td(dcc.Dropdown(
                    id='frequenza', 
                    options=[{'label': date, 'value': date} for date in ['mensile','trimestrale','annuale']],
                    value=1), style={'text-align': 'center','border': '1px solid black', 'fontSize':'0.75vw'}),
                
                #DURATA
               html.Td(dcc.Dropdown(
                   id='durata_years', 
                   options=[{'label': date, 'value': date} for date in [1,2,3]],
                   value=1), style={'text-align': 'center','border': '1px solid black', 'fontSize':'0.75vw'}),
              
                #DEROGA 1            
               html.Td(dcc.Dropdown(
                   id='deroga_dropdown', 
                   options=[{'label': date, 'value': date} for date in [0.25,0.50,0.75,1.00]],
                   value=1), style={'text-align': 'center','border': '1px solid black', 'fontSize':'0.75vw'}),
               
               #DEROGA 2
              html.Td(dcc.Dropdown(
                  id='deroga_dropdown', 
                  options=[{'label': date, 'value': date} for date in ['Rata Iniziale','Intero piano']],
                  value=1), style={'text-align': 'center','border': '1px solid black', 'fontSize':'0.75vw'}),
              
              # FLAG TIENI INVESTIMENTO
              # # Input('tieni_investimento', 'value')
              # dcc.Checklist(
              #     id='tieni_investimento',
              #     options=[
              #         {'value': 'OP1'},

              #     ],
                  
              # ), 
               
              html.Td(dcc.Dropdown(
                  id='tieni_investimento', 
                  options=[{'label': date, 'value': date} for date in ['SI','NO']],
                  value=1), style={'text-align': 'center','border': '1px solid black', 'fontSize':'0.75vw'}),
                
              
            ],style={'border': '1px solid black'}),
            ],style={'width': '100%', 'table-layout': 'adaptive','marginTop': '0px','border': '1px solid black'})

            ], style={'display': 'flex', 'justify-content': 'center', 'margin-top': '10px'}), 
        
            #MESSAGGIO ROSSO/VERDE SOTTO TABELLA
            html.Div(id='output',style={'margin': 'auto', 'justify-content': 'center','display': 'flex'}),
            
            # Aggiungi questo nell'app.layout
            dcc.Tabs(id='tabs', children=[]),

 ]) 


# per importo
@app.callback(
    Output('output', 'children'),
    Input('importo', 'value')
)
def check_amount(amount):
    if amount is not None and amount < 0:
        return 'Minimo investito deve essere almeno €0'




# per prodotti selezionati
@app.callback(
    Output('multi-dropdown', 'options'),
    Output('multi-dropdown', 'value'),  # Aggiungi questa riga per cancellare i valori selezionati nel Multi Dropdown
    Input('basic-dropdown', 'value')
)
def update_multi_dropdown(selected_value):
    return basic_options.get(selected_value, []), []  # Restituisce una lista vuota come nuovo valore per il Multi Dropdown

# per fondi selezionati
@app.callback(
    Output('my-table', 'children'),
    Input('multi-dropdown', 'value'),
    # Aggiungi questo input per resettare la tabella quando cambia il valore del Basic Dropdown
    Input('basic-dropdown', 'value')
)
def update_table(selected_values, _):
    if selected_values is None or len(selected_values) == 0:
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
    
    
# Callback per aggiornare i tab
@app.callback(
    Output('tabs', 'children'),
    Input('multi-dropdown', 'value'),
    # Aggiungi questo input per resettare i tab quando cambia il valore del Basic Dropdown
    Input('basic-dropdown', 'value')
)
def update_tabs(selected_values, _):
    if selected_values is None or len(selected_values) == 0:
        # Se non è selezionato nulla, ritorna una lista vuota
        return []
    else:
        # Crea un dcc.Tab per ciascun valore selezionato
        tabs = []
        for value in selected_values:
            # Assumendo che tu abbia una funzione generate_data che restituisce dati basati sul valore
            data = generate_data(value)

            tab = dcc.Tab(label=value, children=[
                # Aggiungi un grafico
                dcc.Graph(
                    id=f'graph-{value}',
                    figure={
                        'data': [
                            go.Scatter(
                                x = data['x'],  # Sostituisci con i tuoi dati
                                y = data['y'],  # Sostituisci con i tuoi dati
                                mode = 'lines+markers',
                                name = 'Grafico'
                            )
                        ],
                        'layout': go.Layout(
                            title = f'Grafico per {value}'
                        )
                    }
                )
            ])
            tabs.append(tab)
        return tabs
 

if __name__ == '__main__':
    app.run_server()



