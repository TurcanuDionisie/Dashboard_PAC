import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import numpy as np


df = pd.read_excel("grafico.xlsx", index_col=0)

# Creazione di una serie di dati casuale
np.random.seed(0)
df = pd.DataFrame({
    'x': df.index,
    'y1': df["CTV_NETTO"],
    'y2': df["MOVIMENTI"]
})

df_bar = df.iloc[::10, :]

app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.H1(children='Grafico Misto con Dash'),
    dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                go.Scatter(  # linea
                    x=df['x'],
                    y=df['y1'],
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
    )
])

if __name__ == '__main__':
    app.run_server()
