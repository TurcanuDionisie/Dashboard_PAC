import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    html.Button('Open Details', id='open-details-btn'),
    dcc.Graph(
        id='graph',
        figure={
            'data': [{
                'x': [1, 2, 3],
                'y': [4, 1, 2],
                'type': 'bar'
            }]
        }
    ),
    dbc.Modal(
        [
            dbc.ModalHeader('Details'),
            dbc.ModalBody(id='details-container'),
            dbc.ModalFooter(
                dbc.Button('Close', id='close-details-btn', className='ml-auto')
            ),
        ],
        id='details-modal',
        size='lg',
    ),
])

@app.callback(
    Output('details-modal', 'is_open'),
    [Input('open-details-btn', 'n_clicks'), Input('close-details-btn', 'n_clicks')],
    [State('details-modal', 'is_open')]
)
def toggle_modal(open_clicks, close_clicks, is_open):
    if open_clicks or close_clicks:
        return not is_open
    return is_open

@app.callback(
    Output('details-container', 'children'),
    [Input('open-details-btn', 'n_clicks')]
)
def display_details(n_clicks):
    if n_clicks:
        # Replace the following code with your logic to generate the table
        table_data = [
            {'Name': 'John', 'Age': 25},
            {'Name': 'Jane', 'Age': 30},
            {'Name': 'Bob', 'Age': 35}
        ]

        table_rows = [html.Tr([html.Th(col) for col in table_data[0].keys()])]
        for row in table_data:
            table_rows.append(html.Tr([html.Td(row[col]) for col in row.keys()]))

        table = html.Table(table_rows)
        return table
    else:
        return ''

if __name__ == '__main__':
    app.run_server()

