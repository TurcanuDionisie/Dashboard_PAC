import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State

app = dash.Dash(__name__)

# Opzioni per il menu a discesa di base
basic_options = {
    'Opzione 1': [{'label': 'Sotto-opzione 1.1', 'value': '1.1'}, {'label': 'Sotto-opzione 1.2', 'value': '1.2'}],
    'Opzione 2': [{'label': 'Sotto-opzione 2.1', 'value': '2.1'}, {'label': 'Sotto-opzione 2.2', 'value': '2.2'}],
    'Opzione 3': [{'label': 'Sotto-opzione 3.1', 'value': '3.1'}, {'label': 'Sotto-opzione 3.2', 'value': '3.2'}],
}

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
    html.Table(id='my-table', children=[])
])

@app.callback(
    Output('multi-dropdown', 'options'),
    Output('multi-dropdown', 'value'),  # Aggiungi questa riga per cancellare i valori selezionati nel Multi Dropdown
    Input('basic-dropdown', 'value')
)
def update_multi_dropdown(selected_value):
    return basic_options.get(selected_value, []), []  # Restituisce una lista vuota come nuovo valore per il Multi Dropdown

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

if __name__ == '__main__':
    app.run_server()
