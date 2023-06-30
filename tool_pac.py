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

app = dash.Dash(__name__, title ='Tool PAC', external_stylesheets=[dbc.themes.BOOTSTRAP])



app.css.append_css({
    'external_url': '/assets/style.css'
})


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




app.layout = html.Div(className="container", children=[
    
    html.H1('Dashboard Piano PAC', style={'textAlign': 'center', 'width': '100%', 'marginTop': '40px'}),

    
    html.Div(className="row sezione", children=[
        
        # First column
        html.Div(className="col-6", children=[
            html.Div(className="input-group", children=[
                html.Div(className="col-6", children=html.P("Data Inizio:", className="label text-right")),
                html.Div(className="col-6", children=dcc.Dropdown(
                    id='data-inizio',
                    options=[{'label': str(date), 'value': str(date)} for date in datetime_index],
                    value=None
                ))
            ]),
            html.Div(className="input-group", children=[
                html.Div(className="col-6", children=html.P("Importo Rata:", className="label text-right")),
                html.Div(className="col-6", children=dcc.Input(
                    id='importo-rata',
                    type='text',
                    placeholder='Importo rata',
                    className='input-form form-control'
                ))
            ]),
            html.Div(className="input-group", children=[
                html.Div(className="col-6", children=html.P("Frequenza:", className="label text-right")),
                html.Div(className="col-6", children=dcc.Dropdown(
                    id='frequenza', 
                    options=[{'label': label, 'value': value} for label, value in frequenze.items()],
                    value='Mensile',
                ))
            ]),
            html.Div(className="input-group", children=[
                html.Div(className="col-6", children=html.P("Durata:", className="label text-right")),
                html.Div(className="col-6", children=dcc.Dropdown(
                    id='durata', 
                    options=[
                            {'label': '10 Anni', 'value': '10'},
                            {'label': '15 Anni', 'value': '15'},
                        ],
                    value='10',
                ))
            ]),
            html.Div(className="input-group", children=[
                html.Div(className="col-6", children=html.P("Deroga:", className="label text-right")),
                html.Div(className="col-6", children=dcc.Dropdown(
                    id='deroga',
                    options=[{'label': str(deroga), 'value': str(deroga)} for deroga in selezione_deroga],
                    value='Nessuna'
                ))
            ]),
            html.Div(className="input-group", children=[
                html.Div(className="col-6", children=html.P("Giorno Versamento:", className="label text-right")),
                html.Div(className="col-6", children=dcc.Dropdown(
                    id='gggggggggg', 
                    options=[
                            {'label': '8', 'value': '8'},
                            {'label': '28', 'value': '28'},
                        ],
                    value='10',
                ))
            ]),
            html.Div(className="input-group", children=[
                html.Div(className="col-6", children=html.P("Prodotto:", className="label text-right")),
                html.Div(className="col-6", children=dcc.Dropdown(
                    id='basic-dropdown',
                    options=[{'label': key, 'value': key} for key in basic_options.keys()],
                    value='Opzione 1',
                ))
            ]),
            html.Div(className="input-group", children=[
                html.Div(className="col-6", children=html.P("Fondo Comume:", className="label text-right")),
                html.Div(className="col-6", children=dcc.Dropdown(
                    id='multi-dropdown',
                    multi=True
                ))
            ]),
            
            
            html.Div(className="input-group", children=[
                html.Div(className="col-6"),
                html.Div(className="col-6", children=html.Button('Calcola', id='calcola', n_clicks=0, className="btn btn-primary btn-lg btn-block"))
            ]),
            
            
            
            
        ]),
        # Second column
        html.Div(className="col-6", children=[
            html.Table(id='my-table', children=[])
        ]),
    ]),
    
    
    
    
    html.Div(className="row", children=[
        
        html.Div(id='error-message'),
        
    ]),
    
    
    
    html.Div(className="row sezione", children=[
        
        # html.H3('Grafico della simulazione', style={'text-align': 'center', 'width': '100%'}),
        dcc.Graph(id='result-graph'),
        
    ]),
    
    
    
    
    html.Div(className="row align-vertical sezione", children=[
        
        html.H3('Valori alla data finale della simulazione', style={'text-align': 'center', 'width': '100%'}),
            
        html.Div(className="col-6 align-vertical", children=[
            html.Div(id='table-div'),
        ]),
        
        html.Div(className="col-6 align-vertical", children=[
           dcc.Graph(id='pie-chart'),
        ]),
        
    ]),
    
   
    
    html.Div(className="row sezione", children=[
        
        dcc.Tabs(id="my-tabs"),
        
    ]),
    


    

    
    html.Div(children=html.Div(id='dummy-output')),  # dummy component used for button callback
    html.Div(children=dcc.Store(id='store-inputs', data={})),  # storage component to store input values
    
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
                html.Td(className='col-3 peso-isin', children=value),
                html.Td(className='col', children=dcc.Input(
                    value=data.get(value, ""),
                    id={'type': 'dynamic-input', 'index': value},  # use value as id index
                    type='text',
                    className='input-form-pesi form-control'  # Add the full-width-input class here
                ))
            ])
            rows.append(row)
        return rows

    
    



@app.callback(
    [Output('result-graph', 'figure'),
     Output('dummy-output', 'children'),
     Output('error-message', 'children'),
     Output('table-div', 'children'),
     Output('pie-chart', 'figure'),
     Output('my-tabs', 'children')],
    [Input('calcola', 'n_clicks'),
     Input('data-inizio', 'value'),
     Input('importo-rata', 'value'),
     Input('frequenza', 'value'),
     Input('durata', 'value'),
     Input('deroga', 'value'),
     Input('multi-dropdown', 'value'),
     Input('store-inputs', 'data')
     ],
)
def print_input_values(n_clicks, data_inizio, importo_rata, frequenza, durata, deroga, finestre, isin_selezionati):
    message = ""
    fig = {}
    table = {}
    pie_chart = {}
    tabs = {}

    if n_clicks > 0:
        
        if data_inizio is None or importo_rata is None or finestre is None or isin_selezionati is None:
            message = "Attenzione, non hai compilato tutti i campi"
        
        else:

            #controlla che la somma dei pesi sia 100
            if(funzioni_dashboard.controlloSommaPesi(isin_selezionati)):
    
                            
                
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
                    message = "Attenzione, l'importo della rata è troppo piccolo"
                elif(risultati == "ERRORE IMPORTO MINIMO"):
                    message = "Attenzione, l'importo minimo su uno dei fondi è troppo piccolo"
                
                else:
                    
                    grafico_ptf = risultati["portafoglio"]["Grafico"]
        
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
                                name='Controvalore Netto'
                            ),
                            go.Bar(  # barre
                                x=df_bar['x'],
                                y=df_bar['y2'],
                                name='Importo Versato',
                                width=3
                            )
                        ],
                        'layout': go.Layout(
                            title='Grafico della simulazione',
                            title_font=dict(
                            size=25,
                            family="Verdana, bold"
                        ),
                            yaxis={'title': 'Valore'}
                        )
                    }
                
                
                
                    dati_tabella_perf = {
                        
                        "Frequenza Rate": frequenza,
                        "Importo Rata": importo_rata,
                        "Totale Rate Versate": risultati["portafoglio"]["Totale rate versate"],
                        "Patrimonio Finale": round(risultati["portafoglio"]["patrimonio finale"],2),
                        "Plus/Minus": round(risultati["portafoglio"]["plus"] ,2),
                        "MWRR Totale": round(risultati["portafoglio"]["MWRR"] * 100 ,3),
                        "MWRR Annualizzato": round(risultati["portafoglio"]["MWRR_annualizzato"] * 100 ,3),
                        "Volatilita": round(risultati["portafoglio"]["Volatilita_finale"] * 100 ,3),
                        "Max DD": round(risultati["portafoglio"]["Max_DD"] * 100 ,3)
                        
                    }
                    
                
                
                    # Code to create the table
                    table = html.Table(className='my-table', children=[
                        html.Tbody([
                            html.Tr([
                                html.Div(className='row', children=[
                                    html.Div(className='col-6', children=[html.Th(col)]),
                                    html.Div(className='col-6', children=[html.Td(dati_tabella_perf[col])])
                                ])
                            ]) for col in dati_tabella_perf.keys()
                        ])
                    ])
                    
                    
                    

                    
    
                    pie_chart = go.Figure()
        
                    labels = ["Versato", "Contributo Mercato"]
                    values = [risultati["portafoglio"]["Totale rate versate"], (risultati["portafoglio"]["patrimonio finale"] - risultati["portafoglio"]["Totale rate versate"])]
            
                    pie_chart.add_trace(go.Pie(labels=labels, values=values))
                    
                    
                    if finestre is None or len(finestre) == 0:
                        return []
                    else:
                        tabs = []
                        for i, value in enumerate(finestre):
                            
                            # value = isin del fondo
                            
                            
                            
                           
                            # Your data
                            x_values = risultati["singoli_fondi"][value]["Calcoli"].index
                            y_values1 = risultati["singoli_fondi"][value]["Calcoli"][value]
                            y_values2 = risultati["singoli_fondi"][value]["Calcoli"]["PMC"]
                            y_values3 = risultati["singoli_fondi"][value]["Calcoli"]["Prezzo_medio"]
                            
                            trace1 = go.Scatter(x=x_values, y=y_values1, mode='lines', name='Prezzo')
                            trace2 = go.Scatter(x=x_values, y=y_values2, mode='lines', name='PMC')
                            trace3 = go.Scatter(x=x_values, y=y_values3, mode='lines', name='Prezzo medio')
                            
                            data = [trace1, trace2, trace3]
                            
                            
                            tab = dcc.Tab(label=value, children=[
                                
                                dcc.Graph(
                                    id={'type': 'dynamic-graph', 'index': value},
                                    figure={'data': data, 
                                           }
                                )
                            ])
                            tabs.append(tab)
     
    
            else:
                message = "Attenzione, la somma dei pesi non è 100"

    return fig, None, message, table, pie_chart, tabs    # Returns figure to the graph, None to the 'dummy-output', and the error message to 'error-message'.







if __name__ == '__main__':
    app.run_server()


