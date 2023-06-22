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
    html.Table(id='my-table', children=[]),
    html.Button('Get Input IDs and Values', id='get-input-ids-button', n_clicks=0),
    dcc.Store(id='input-values-store'),  # Store component to store input values
    html.Div(id='input-ids-output')
])

@app.callback(
    Output('multi-dropdown', 'options'),
    Output('multi-dropdown', 'value'),
    Input('basic-dropdown', 'value')
)
def update_multi_dropdown(selected_value):
    return basic_options.get(selected_value, []), []

@app.callback(
    Output('my-table', 'children'),
    Output('input-values-store', 'data'),  # Store input values in the Store component
    Input('multi-dropdown', 'value'),
    Input('basic-dropdown', 'value')
)
def update_table(selected_values, _):
    if selected_values is None or len(selected_values) == 0:
        # Se non è selezionato nulla, ritorna una tabella vuota
        return [], {}
    else:
        # Crea una lista di html.Tr per ciascun valore selezionato
        rows = []
        input_values = {}
        for value in selected_values:
            input_id = f'input-{value}'
            input_values[input_id] = ""
            row = html.Tr(children=[
                html.Td(children=value),
                html.Td(children=dcc.Input(value="", id=input_id, type='text'))
            ])
            rows.append(row)
        return rows, input_values

@app.callback(
    Output('input-ids-output', 'children'),
    Input('get-input-ids-button', 'n_clicks'),
    State('input-values-store', 'data')  # Retrieve input values from the Store component
)
def get_input_ids(n_clicks, input_values):
    if n_clicks > 0:
        input_info = [f"ID: {input_id}, Value: {input_value}" for input_id, input_value in input_values.items()]
        return html.Div(input_info)
    return ""

if __name__ == '__main__':
    app.run_server()

