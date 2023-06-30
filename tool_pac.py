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


import motore



#%% FUNZIONI PER DASHBOARD


#Controlla che la somma dei pesi sia 100
def controlloSommaPesi(pesi):
    
    somma_pesi = 0
    
    try:
        for isin in pesi:
            somma_pesi += int(pesi[isin])
    
    except:
        return False
    
    if(somma_pesi != 100):
        return False
    
    return True


#%% LETTURA FILE EXCEL

#decodifiche FONDO - Prodotto
file_codifiche_prodotto = pd.read_excel("codifiche.xlsx", index_col=0)
SGR = file_codifiche_prodotto['FAMIGLIA'].unique()


#lettura quote
file_quote = pd.read_excel("DB_TOT_PROXY.xlsx", index_col=0)


#lettura file costi
file_costi = pd.read_excel('costi.xlsx', index_col=0)



#%% VALORI CHE POPOLANO I VARI COMPONENTI



#FONDI E PRODOTTI PER MULTIDROPDOWN
df_options = pd.DataFrame({
    'OptionID': SGR,
    'OptionLabel': SGR,
})

df_suboptions = pd.DataFrame({
    'OptionID': file_codifiche_prodotto['FAMIGLIA'],
    'SubOptionLabel': file_codifiche_prodotto.index,
    'SubOptionValue': file_codifiche_prodotto.index,
})

basic_options = {}
for _, row in df_options.iterrows():
    option_id = row['OptionID']
    option_label = row['OptionLabel']
    suboptions = df_suboptions[df_suboptions['OptionID'] == option_id]
    basic_options[option_label] = [{'label': r['SubOptionLabel'], 'value': r['SubOptionValue']} for _, r in suboptions.iterrows()]





#DATE INIZIO SIMULAZIONE
data_inizio_simulazione = file_quote.index




#FREQUENZE
frequenze = {
    'Mensile': 'Mensile',
    'Bimestrale': 'Bimestrale',
    'Trimestrale': 'Trimestrale',
    'Quadrimestrale': 'Quadrimestrale',
    'Semestrale': 'Semestrale',
    'Annuale': 'Annuale'
}




#DEROGHE
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


#CSS
app.css.append_css({
    'external_url': '/assets/style.css'
})


server = app.server

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

    
    #INPUT FORM
    html.Div(className="row sezione", children=[
        
        # Prima colonna
        html.Div(className="col-6", children=[
            html.Div(className="input-group", children=[
                html.Div(className="col-6", children=html.P("Data Inizio:", className="label text-right")),
                html.Div(className="col-6", children=dcc.Dropdown(
                    id='data-inizio',
                    options=[{'label': str(date), 'value': str(date)} for date in data_inizio_simulazione],
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
                    id='giorno_versamento', 
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
        # Seconda colonna
        html.Div(className="col-6", children=[
            html.Table(id='my-table', children=[])
        ]),
    ]),
    
    
    
    
    #MESSAGGIO ERRORE
    html.Div(className="row", children=[
        
        html.Div(id='error-message'),
        
    ]),
    
    
    
    #GRAFICO SIMULAZIONE
    html.Div(className="row sezione", children=[
        
        # html.H3('Grafico della simulazione', style={'text-align': 'center', 'width': '100%'}),
        dcc.Graph(id='result-graph'),
        
    ]),
    
    
    
    
    #TABELLA PERFORMANCE E GRAFICO A TORTA
    html.Div(className="row align-vertical sezione", children=[
        
        html.H3('Valori alla data finale della simulazione', style={'text-align': 'center', 'width': '100%'}),
            
        html.Div(className="col-6 align-vertical", children=[
            html.Div(id='table-div'),
        ]),
        
        html.Div(className="col-6 align-vertical", children=[
           dcc.Graph(id='pie-chart'),
        ]),
        
    ]),
    
   
    
    
    #TABS CON I VARI GRAFICI
    html.Div(className="row sezione", children=[
        
        dcc.Tabs(id="my-tabs"),
        
    ]),
    


    

    #COMPONENTI CHE CONSERVANO I PESI
    html.Div(children=html.Div(id='dummy-output')),  # dummy component used for button callback
    html.Div(children=dcc.Store(id='store-inputs', data={})),  # storage component to store input values
    
])




# %% CALLBACKS


# GESTISCE I DUE DROPDOWN
@app.callback(
    Output('store-inputs', 'data'),
    [Input({'type': 'dynamic-input', 'index': ALL}, 'value')],
    [Input({'type': 'dynamic-input', 'index': ALL}, 'id'),
     Input('store-inputs', 'data')]
)
def update_store(input_values, input_ids, data):
    data = {id['index']: value for value, id in zip(input_values, input_ids)}
    return data

@app.callback(
    Output('multi-dropdown', 'options'),
    Output('multi-dropdown', 'value'),
    [Input('basic-dropdown', 'value')]
)
def update_multi_dropdown(selected_value):
    return basic_options.get(selected_value, []), []




#GESTISCE TABELLA DINAMICA DEI PESI
@app.callback(
    Output('my-table', 'children'),
    [Input('multi-dropdown', 'value'),
     Input('store-inputs', 'data')]
    
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
                    id={'type': 'dynamic-input', 'index': value},  
                    type='text',
                    className='input-form-pesi form-control'  
                ))
            ])
            rows.append(row)
        return rows

    
    


#MOTORE
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
     Input('giorno_versamento', 'value'),
     
     #isin selezionati (solo isin)
     Input('multi-dropdown', 'value'),
     
     #dizionario dove ad ogni isin è associato il peso
     Input('store-inputs', 'data')
     ],
)
def print_input_values(n_clicks, data_inizio, importo_rata, frequenza, durata, deroga, giorno_versamento, isin_selezionati, isin_peso):
    message = ""
    fig = {}
    table = {}
    pie_chart = {}
    tabs = {}

    
    if n_clicks <= 0:
        return fig, None, message, table, pie_chart, tabs
        
    
    #controlla che i campi in input siano tutti compilati
    if data_inizio is None or importo_rata is None or isin_selezionati is None or isin_peso is None:
        message = "Attenzione, non hai compilato tutti i campi"
        return fig, None, message, table, pie_chart, tabs
    
    
        
    #controlla che la somma dei pesi sia 100
    #ritorna false se l'utente non inserisce un numero valido
    if(controlloSommaPesi(isin_peso) == False):
        message = "Attenzione, la somma dei pesi non è 0"
        return fig, None, message, table, pie_chart, tabs
        
    
    
    
    # input_utente = {
    #     "isin_selezionati": isin_peso,
    #     "data_inizio": data_inizio,
    #     "importo_rata": importo_rata,
    #     "frequenza": frequenza,
    #     "durata_anni": durata,
    #     "giorno_mese": giorno_versamento,
        
    #     #dati letti da excel
    #     "file_quote": file_quote,
    #     "file_costi": file_costi
        
    # }
    
    
    # print(input_utente)
    
        
        
    # estrae e formatta input inseriti dall'utente   
    try:
        input_utente = {
            "isin_selezionati": isin_peso,
            "data_inizio": data_inizio,
            "importo_rata": int(importo_rata),
            "frequenza": frequenza,
            "durata_anni": int(durata),
            "giorno_mese": int(giorno_versamento),
            
            #dati letti da excel
            "file_quote": file_quote,
            "file_costi": file_costi
            
        }
        
    except:
        message = "Attenzione, errore nei campi di input"
        return fig, None, message, table, pie_chart, tabs
    
    
    
    #passo tutti gli input utente al motore
    risultati = motore.EseguiAnalisi(input_utente)
    
    
    
    #controlla validità importo minimo rate
    if(risultati == "ERRORE RATA MENSILE"):
        message = "Attenzione, l'importo della rata è troppo piccolo"
        return fig, None, message, table, pie_chart, tabs
    elif(risultati == "ERRORE IMPORTO MINIMO"):
        message = "Attenzione, l'importo minimo su uno dei fondi è troppo piccolo"
        return fig, None, message, table, pie_chart, tabs
    
    

        
    #GRAFICO GRANDE CON LE PERFORMANCE
    grafico_ptf = risultati["portafoglio"]["grafico"]

    grafico_ptf = pd.DataFrame({
        'x': grafico_ptf.index,
        'y1': grafico_ptf["ctv_netto"],
        'y2': grafico_ptf["movimenti"]
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



    
    #DATI DA METTERE NELLA TABELLA DELLE PERFORMANCE
    #LE CHIAVI SONO I TITOLI DELLA TABELLA
    dati_tabella_perf = {
        
        "Frequenza Rate": frequenza,
        "Importo Rata": str(importo_rata) + "€",
        "Totale Rate Versate": str(risultati["portafoglio"]["totale_rate_versate"]) + "€",
        "Patrimonio Finale": str(int(risultati["portafoglio"]["patrimonio_finale"])) + "€",
        "Plus/Minus": str(int(risultati["portafoglio"]["plus"])) + "€",
        "MWRR Totale": str(round(risultati["portafoglio"]["mwrr"] * 100 ,2)) + "%",
        "MWRR Annualizzato": str(round(risultati["portafoglio"]["mwrr_annualizzato"] * 100 ,2)) + "%",
        "Volatilita": str(round(risultati["portafoglio"]["volatilita_finale"] * 100 ,2)) + "%",
        "Max DD": str(round(risultati["portafoglio"]["max_dd"] * 100 ,2)) + "%"
        
    }
    
    #TABELLA DELLE PERFORMANCE
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
    
    
    

    
    #GRAFICO A TORTA
    pie_chart = go.Figure()

    labels = ["Versato", "Contributo Mercato"]
    values = [risultati["portafoglio"]["totale_rate_versate"], (risultati["portafoglio"]["patrimonio_finale"] - risultati["portafoglio"]["totale_rate_versate"])]

    pie_chart.add_trace(go.Pie(labels=labels, values=values))
    
    
    
    
    
    #TABS CON I VARI GRAFICI
    if isin_selezionati is None or len(isin_selezionati) == 0:
        return []
    else:
        tabs = []
        for i, value in enumerate(isin_selezionati):
            
            # value = isin del fondo
                                     
            x_values = risultati["singoli_fondi"][value]["calcoli"].index
            y_values1 = risultati["singoli_fondi"][value]["calcoli"][value]
            y_values2 = risultati["singoli_fondi"][value]["calcoli"]["pmc"]
            y_values3 = risultati["singoli_fondi"][value]["calcoli"]["prezzo_medio"]
            
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
 

    return fig, None, message, table, pie_chart, tabs




if __name__ == '__main__':
    app.run_server()


