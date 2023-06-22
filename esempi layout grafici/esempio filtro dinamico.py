import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State

# Sample data for investments
investments = {
    'Equity': ['AAPL', 'GOOGL', 'MSFT'],
    'FixedIncome': ['BND', 'AGG', 'TLT']
}

app = dash.Dash(__name__)

app.layout = html.Div([
    html.Label('Asset Class'),
    dcc.Dropdown(
        id='asset-dropdown',
        options=[
            {'label': 'Equity', 'value': 'Equity'},
            {'label': 'Fixed Income', 'value': 'FixedIncome'}
        ],
        value='Equity'
    ),
    
    html.Label('Investment'),
    dcc.Dropdown(id='investment-dropdown'),
    
    dcc.Graph(id='investment-graph'),
    
    html.Button('View Details', id='view-details-button', n_clicks=0),
    
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@app.callback(
    Output('investment-dropdown', 'options'),
    [Input('asset-dropdown', 'value')]
)
def update_investment_dropdown(asset_class):
    options = [{'label': investment, 'value': investment} for investment in investments.get(asset_class, [])]
    return options

@app.callback(
    Output('investment-graph', 'figure'),
    [Input('investment-dropdown', 'value')]
)
def update_investment_graph(selected_investment):
    # Add your graph creation code here based on the selected investment
    # This is just a placeholder example
    data = [{'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar'}]
    layout = {'title': f'Investment: {selected_investment}'}
    return {'data': data, 'layout': layout}

@app.callback(
    Output('url', 'pathname'),
    [Input('view-details-button', 'n_clicks')],
    [State('investment-dropdown', 'value')]
)
def view_details(n_clicks, selected_investment):
    if n_clicks > 0:
        return f'/details/{selected_investment}'
    return '/'

@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname.startswith('/details/'):
        selected_investment = pathname.split('/')[2]
        # Add your code to fetch the details data for the selected investment
        # This is just a placeholder example using dummy data
        details_data = [{'Date': '2023-06-01', 'Value': 100},
                       {'Date': '2023-06-02', 'Value': 110},
                       {'Date': '2023-06-03', 'Value': 120}]
        
        return html.Div([
            html.H2(f'Details for Investment: {selected_investment}'),
            dash_table.DataTable(
                data=details_data,
                columns=[{'name': 'Date', 'id': 'Date'}, {'name': 'Value', 'id': 'Value'}]
            )
        ])
    else:
        return html.H2('Select an investment and click "View Details"')

if __name__ == '__main__':
    app.run_server()
