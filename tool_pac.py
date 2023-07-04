import pandas as pd


import plotly.graph_objs as go


import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, ALL
import dash_bootstrap_components as dbc



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
file_codifiche_prodotto = pd.read_excel("excel/codifiche.xlsx", index_col=0)
SGR = file_codifiche_prodotto['FAMIGLIA'].unique()


#lettura quote
file_quote = pd.read_excel("excel/DB_TOT_PROXY.xlsx", index_col=0)



#lettura file costi
file_costi = pd.read_excel('excel/costi.xlsx', index_col=0)



#%% VALORI CHE POPOLANO I VARI COMPONENTI



#FONDI E PRODOTTI PER MULTIDROPDOWN
df_options = pd.DataFrame({
    'OptionID': SGR,
    'OptionLabel': SGR,
})

df_suboptions = pd.DataFrame({
    'OptionID': file_codifiche_prodotto['FAMIGLIA'],
    'SubOptionLabel': file_codifiche_prodotto['NOME'],
    'SubOptionValue': file_codifiche_prodotto.index,
})

basic_options = {}
for _, row in df_options.iterrows():
    option_id = row['OptionID']
    option_label = row['OptionLabel']
    suboptions = df_suboptions[df_suboptions['OptionID'] == option_id]
    basic_options[option_label] = [{'label': r['SubOptionLabel'], 'value': r['SubOptionValue']} for _, r in suboptions.iterrows()]





#DATE INIZIO SIMULAZIONE
data_inizio_simulazione = file_quote.index.strftime('%d/%m/%Y')




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
    'Totale 50%': 'Totale 50%',
    'Totale 75%': 'Totale 75%',
    'Totale 100%': 'Totale 100%',
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
                html.Div(className="col-4", children=html.P("Data Inizio:", className="label text-right")),
                html.Div(className="col-8", children=dcc.Dropdown(
                    id='data-inizio',
                    options=[{'label': str(date), 'value': str(date)} for date in data_inizio_simulazione],
                    value=None
                ))
            ]),
            html.Div(className="input-group", children=[
                html.Div(className="col-4", children=html.P("Importo Rata:", className="label text-right")),
                html.Div(className="col-8", children=dbc.InputGroup([
                    dcc.Input(
                        id='importo-rata',
                        type='text',
                        value=None,
                        placeholder='Importo rata',
                        className='input-form form-control'
                    ),
                    dbc.InputGroupText("€")
                ], className='input-group'))
                
                
            ]),
            html.Div(className="input-group", children=[
                html.Div(className="col-4", children=html.P("Frequenza:", className="label text-right")),
                html.Div(className="col-8", children=dcc.Dropdown(
                    id='frequenza', 
                    options=[{'label': label, 'value': value} for label, value in frequenze.items()],
                    value='Mensile',
                ))
            ]),
            html.Div(className="input-group", children=[
                html.Div(className="col-4", children=html.P("Durata:", className="label text-right")),
                html.Div(className="col-8", children=dcc.Dropdown(
                    id='durata', 
                    options=[
                            {'label': '10 Anni', 'value': '10'},
                            {'label': '15 Anni', 'value': '15'},
                        ],
                    value='10',
                ))
            ]),
            html.Div(className="input-group", children=[
                html.Div(className="col-4", children=html.P("Deroga:", className="label text-right")),
                html.Div(className="col-8", children=dcc.Dropdown(
                    id='deroga',
                    options=[{'label': str(deroga), 'value': str(deroga)} for deroga in selezione_deroga],
                    value='Nessuna'
                ))
            ]),
            html.Div(className="input-group", children=[
                html.Div(className="col-4", children=html.P("Giorno Versamento:", className="label text-right")),
                html.Div(className="col-8", children=dcc.Dropdown(
                    id='giorno_versamento', 
                    options=[
                            {'label': '8', 'value': '8'},
                            {'label': '28', 'value': '28'},
                        ],
                    value='8',
                ))
            ]),
            html.Div(className="input-group", children=[
                html.Div(className="col-4", children=html.P("Prodotto:", className="label text-right")),
                html.Div(className="col-8", children=dcc.Dropdown(
                    id='basic-dropdown',
                    options=[{'label': key, 'value': key} for key in basic_options.keys()],
                    value='MBB',
                ))
            ]),
            html.Div(className="input-group", children=[
                html.Div(className="col-4", children=html.P("Fondo Comume:", className="label text-right")),
                html.Div(className="col-8", children=dcc.Dropdown(
                    id='multi-dropdown',
                    value=None,
                    multi=True
                ))
            ]),
            
            
            html.Div(className="input-group", children=[
                html.Div(className="col-4"),
                html.Div(className="col-8", children=html.Button('Calcola', id='calcola', n_clicks=0, className="btn btn-primary btn-lg btn-block"))
            ]),
            
            
            
            
        ]),
        # Seconda colonna
        html.Div(className="col-6", children=[
            html.Div(id='table-title'),
            html.Table(id='my-table', children=[])
        ]),
    ]),
    
    
    
    
    #MESSAGGIO ERRORE
    html.Div(className="row", children=[
        
        html.H4(id='error-message', className="messaggio-errore")
        
        
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
            html.Div(id='table-div', style={'width': '100%'}),
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




#TITOLO TABELLA DEI PESI
@app.callback(
    Output('table-title', 'children'),
    [Input('my-table', 'children')]
)
def update_title(table_children):
    if table_children:  # if the table is not empty
        return html.H4('Inserisci Peso Percentuale')
    else:
        return "" 


#TABELLA DINAMICA CON I PESI
@app.callback(
    Output('my-table', 'children'),
    [Input('multi-dropdown', 'value'),
     Input('store-inputs', 'data')]
)
def update_table(selected_values, data):
    if selected_values is None or len(selected_values) == 0:
        return []
    else:
        rows = []
        for i, value in enumerate(selected_values):
            row = html.Tr(children=[
                html.Td(className='col', children=dbc.InputGroup([
                    dcc.Input(
                        value=data.get(value, ""),
                        id={'type': 'dynamic-input', 'index': value},
                        type='text',
                        className='form-control input-form-pesi'
                    ),
                    dbc.InputGroupText("%")
                ], className='input-group')),
                html.Td(className='col-8 peso-isin', children= file_codifiche_prodotto['NOME'].loc[value]),
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
    if data_inizio is None or importo_rata is None or frequenza is None or durata is None or deroga is None or giorno_versamento is None or (len(isin_selezionati) == 0) or (len(isin_peso) == 0):
        message = "Attenzione, non hai compilato tutti i campi"
        return fig, None, message, table, pie_chart, tabs
    
    
        
    #controlla che la somma dei pesi sia 100
    #ritorna false se l'utente non inserisce un numero valido
    if(controlloSommaPesi(isin_peso) == False):
        message = "Attenzione, la somma dei pesi non è 100"
        return fig, None, message, table, pie_chart, tabs
        
    
    
    

        
        
    # estrae e formatta input inseriti dall'utente   
    try:
        
        input_utente = {
            "isin_selezionati": isin_peso,
            "importo_rata": int(importo_rata),
            "frequenza": frequenza,
            "durata_anni": int(durata),
            "giorno_mese": int(giorno_versamento),
            "deroga": deroga,
            
            #dati letti da excel
            "file_quote": file_quote[file_quote.index >= data_inizio],
            "file_costi": file_costi
            
        }
        
        
    except:
        message = "Attenzione, errore in un campo in input"
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



    # VECCHIA VERSIONE DEL GRAFICO
    # fig = {
    #     'data': [
    #         go.Scatter(  # linea
    #             x=grafico_ptf['x'],
    #             y=grafico_ptf['y1'],
    #             mode='lines',
    #             name='Controvalore Netto',
    #             hovertemplate='%{y:.2f}',  # add this line
    #         ),
    #         go.Bar(  # barre
    #             x=df_bar['x'],
    #             y=df_bar['y2'],
    #             name='Importo Versato',
    #             width=3,
    #             hovertemplate='%{y:.2f}',  # add this line
    #         )
    #     ],
    #     'layout': go.Layout(
    #         title='Grafico della simulazione',
    #         title_font=dict(
    #         size=25,
    #         family="Verdana, bold"
    #     ),
    #         yaxis={'title': 'Valore'}
    #     )
    # }
    
    
    
    
    fig = {
        'data': [
            go.Scatter(  # linea
                x=grafico_ptf['x'],
                y=grafico_ptf['y1'],
                mode='lines',
                name='Controvalore Netto',
                hovertemplate='%{y:.2f}', 
            ),
            go.Bar(  # barre
                x=df_bar['x'],
                y=df_bar['y2'],
                name='Importo Versato',
                width=3,
                hovertemplate='%{y:.2f}', 
            )
        ],
        'layout': go.Layout(
            title={
                'text': 'Grafico della simulazione',  # use HTML-like syntax to apply bold
                'font': {
                    'family': "Verdana",
                    'size': 25,
                    # 'color': "black",
                },
                'y':0.9, #change position as per your requirement
                'x':0.5, #change position as per your requirement
                'xanchor': 'center',
                'yanchor': 'top'
            },
            yaxis={'title': 'Valore'},
            hovermode='x unified', 
            legend=dict(
                orientation="h",  
                yanchor="bottom",
                y=-0.2,  
                xanchor="center",
                x=0.5, 
                font=dict(
                    size=15,  
                    color="black"  
                )
            )
        )
    }







    
    #DATI DA METTERE NELLA TABELLA DELLE PERFORMANCE
    
    # Mappa la frequenza a un numero di mesi
    codifica_mesi = {
        'Mensile': 1,
        'Bimestrale': 2,
        'Trimestrale': 3,
        'Quadrimestrale': 4,
        'Semestrale': 6,
        'Annuale': 12,
    }
    
    num_mesi = codifica_mesi[frequenza]
    numero_rate = (12 / num_mesi) * int(durata)
    
    
    #LE CHIAVI SONO I TITOLI DELLA TABELLA
    dati_tabella_perf = {
        
        "Frequenza Rate": frequenza,
        "Numero Rate": numero_rate,
        "Importo Rata": "{:,}".format(int(importo_rata)).replace(",", ".") + "€",
        "Totale Rate Versate": "{:,}".format(int(risultati["portafoglio"]["totale_rate_versate"])).replace(",", ".") + "€",
        "Patrimonio Finale": "{:,}".format(int(risultati["portafoglio"]["patrimonio_finale"])).replace(",", ".") + "€",
        "Plus/Minus": "{:,}".format(int(risultati["portafoglio"]["plus"])).replace(",", ".") + "€",
        "MWRR Totale": "{:,.2f}".format(round(risultati["portafoglio"]["mwrr"] * 100 ,2)).replace(".", ",") + "%",
        "MWRR Annualizzato": "{:,.2f}".format(round(risultati["portafoglio"]["mwrr_annualizzato"] * 100 ,2)).replace(".", ",") + "%",
        "Volatilita": "{:,.2f}".format(round(risultati["portafoglio"]["volatilita_finale"] * 100 ,2)).replace(".", ",") + "%",
        "Max DD": "{:,.2f}".format(round(risultati["portafoglio"]["max_dd"] * 100 ,2)).replace(".", ",") + "%",
        
    }
    
    #TABELLA DELLE PERFORMANCE
    table = html.Table(className='my-table', style={'width': '100%'}, children=[
        html.Tbody([
            html.Tr([
                html.Div(className='row', children=[
                    html.Div(className='col-6 d-flex justify-content-end', children=[
                        html.Th(col)
                    ]),
                    html.Div(className='col-6 d-flex justify-content-center', children=[
                        html.Td(dati_tabella_perf[col])
                    ])
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
            
            
            tab = dcc.Tab(label=file_codifiche_prodotto['NOME'].loc[value], children=[
                
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


