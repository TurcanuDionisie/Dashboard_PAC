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


import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.graph_objects as go


import funzioni_dashboard
import motore

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


#data inizio
datetime_index = quote.index




frequenze = {
    'Mensile': 'Mensile',
    'Bimestrale': 'Bimestrale',
    'Trimestrale': 'Trimestrale',
    'Quadrimestrale': 'Quadrimestrale',
    'Semestrale': 'Semestrale',
    'Annuale': 'Annuale'
}




selezione_deroga = {
    'Nessuna': 'Nessuna',
    'Iniziale 25%': 'Iniziale 25%',
    'Iniziale 50%': 'Iniziale 50%',
    'Iniziale 75%': 'Iniziale 75%',
    'Iniziale 100%': 'Iniziale 75%',
    'Totale 25%': 'Totale 25%',
    'Totale 50%': 'Iniziale 50%',
    'Totale 75%': 'Iniziale 75%',
    'Totale 100%': 'Iniziale 75%',
}




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
    
    
    #frequenza
    dcc.Dropdown(
    id='frequenza', 
    options=[{'label': label, 'value': value} for label, value in frequenze.items()],
    value='Mensile',  # Puoi impostare il valore predefinito qui
    ),
    
    
    #durata
    dcc.Dropdown(
    id='durata', 
    options=[
            {'label': '10 Anni', 'value': '10'},
            {'label': '15 Anni', 'value': '15'},
        ],
    value='10',  # Puoi impostare il valore predefinito qui
    ),
    
    
    #data inizio
    dcc.Dropdown(
        id='deroga',
        options=[{'label': str(deroga), 'value': str(deroga)} for deroga in selezione_deroga],
        value='Nessuna'
    ),
    
    
    dcc.Graph(id='result-graph'),
    
    html.Div(id='table-div'),
        
    
    dcc.Graph(id='pie-chart'),  # The new pie chart graph
    
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


@app.callback(
    [Output('result-graph', 'figure'),
     Output('dummy-output', 'children'),
     Output('error-message', 'children'),
     Output('table-div', 'children'),
     Output('pie-chart', 'figure')],
    [Input('calcola', 'n_clicks'),
     Input('data-inizio', 'value'),
     Input('importo-rata', 'value'),
     Input('frequenza', 'value'),
     Input('durata', 'value'),
     Input('deroga', 'value'),
     ],
    [State('store-inputs', 'data')]
)
def print_input_values(n_clicks, data_inizio, importo_rata, frequenza, durata, deroga, isin_selezionati):
    message = ""
    fig = {}
    table = {}

    if n_clicks > 0:

        #controlla che la somma dei pesi sia 100
        # if(funzioni_dashboard.controlloSommaPesi(isin_selezionati)):
        if(True):
                        
            
            #input inseriti dall'utente
            input_utente = {
                "isin_selezionati": isin_selezionati,
                "data_inizio": data_inizio,
                "importo_rata": importo_rata,
                "frequenza": frequenza,
                "durata_anni": durata,
                "giorno_mese":"8"
            }
            
            
            
            #passo tutti gli input utente al motore
            risultati = motore.EseguiAnalisi(input_utente)
            
            
            #controlla importo minimo rate
            if(risultati == "ERRORE RATA MENSILE"):
                message = "IMPORTO RATA NON RISPETTA IMPORTO MINIMO"
            elif(risultati == "ERRORE IMPORTO MINIMO"):
                message = "IMPORTO MINIMO SU UN FONDO NON RISPETTATO"
            
            else:
                
                grafico_ptf = risultati["Grafico"]
    
                grafico_ptf = pd.DataFrame({
                    'x': grafico_ptf.index,
                    'y1': grafico_ptf["CTV_NETTO"],
                    'y2': grafico_ptf["MOVIMENTI"]
                })
    
                df_bar = grafico_ptf.iloc[::10, :]
    
                fig = {
                    'data': [
                        go.Scatter(  # linea
                            x=grafico_ptf['x'],
                            y=grafico_ptf['y1'],
                            mode='lines',
                            name='Linea'
                        ),
                        go.Bar(  # barre
                            x=df_bar['x'],
                            y=df_bar['y2'],
                            name='Barre',
                            width=3
                        )
                    ],
                    'layout': go.Layout(
                        title='Linea e Barre su un Unico Grafico',
                        xaxis={'title': 'Data'},
                        yaxis={'title': 'Valore'}
                    )
                }
            
            
            
                dati_tabella_perf = {
                    
                    "Frequenza Rate": frequenza,
                    "Importo Rata": importo_rata,
                    "Totale Rate Versate": risultati["Totale rate versate"],
                    "Patrimonio Finale": round(risultati["patrimonio finale"],2),
                    "Plus/Minus": round(risultati["plus"] ,2),
                    "MWRR Totale": round(risultati["MWRR"] * 100 ,2),
                    "MWRR Annualizzato": round(risultati["MWRR_annualizzato"] * 100 ,2),
                    "Volatilita": round(risultati["Volatilita_finale"] * 100 ,2),
                    "Max DD": round(risultati["Max_DD"] * 100 ,2)
                    
                }
                
            
            
                # Code to create the table
                table = html.Table([
                    html.Thead(
                        html.Tr([html.Th(col) for col in dati_tabella_perf.keys()])
                    ),
                    html.Tbody([
                        html.Tr([html.Td(v) for v in dati_tabella_perf.values()])
                    ])
                ])
            
            

            pie_chart = go.Figure()

            labels = ["Versato", "Contributo Mercato"]
            values = [risultati["Totale rate versate"], (risultati["patrimonio finale"] - risultati["Totale rate versate"])]
    
            pie_chart.add_trace(go.Pie(labels=labels, values=values))
 
            

        else:
            message = "Errori nei pesi"

    return fig, None, message, table, pie_chart    # Returns figure to the graph, None to the 'dummy-output', and the error message to 'error-message'.







if __name__ == '__main__':
    app.run_server()


