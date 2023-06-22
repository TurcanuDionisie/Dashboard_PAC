import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_table
import pandas as pd

app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Dropdown(
        id='my-dropdown',
        options=[
            {'label': 'Opzione 1', 'value': '1'},
            {'label': 'Opzione 2', 'value': '2'},
            {'label': 'Opzione 3', 'value': '3'},
            # Aggiungi tutte le opzioni necessarie
        ],
        multi=True
    ),
    dash_table.DataTable(
        id='my-table',
        columns=[{"name": i, "id": i, "editable": (i == "Input")} for i in ["Valore Selezionato", "Input"]],
        # I dati iniziali saranno vuoti
        data=[]
    )
])

@app.callback(
    Output('my-table', 'data'),
    Input('my-dropdown', 'value')
)
def update_table(selected_values):
    if selected_values is None:
        # Se non è selezionato nulla, ritorna dati vuoti
        return []
    else:
        # Crea un dataframe con il numero di righe uguale al numero di valori selezionati
        # Inserisce i valori selezionati nella colonna "Valore Selezionato" e lascia vuota la colonna "Input"
        df = pd.DataFrame([{"Valore Selezionato": value, "Input": ""} for value in selected_values])
        return df.to_dict('records')

if __name__ == '__main__':
    app.run_server()
