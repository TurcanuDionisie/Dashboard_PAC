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
from dash.dependencies import Input, Output, State
from dash import dash_table
from dash import ctx
import dash_bootstrap_components as dbc
from PIL import Image
from io import BytesIO
import requests

#%% IMPORTO E AGGIUSTO QUOTE STORICHE DEI FONDI NECESSARI ALL'ANALISI

url = 'https://raw.githubusercontent.com/TurcanuDionisie/Dashboard_PAC/main/'

quote = pd.read_excel(url+'input/DB_TOT_PROXY.xlsx')
quote = quote.set_index(quote.columns[0])
alfa= quote.iloc[:2].T

#DIZIONARIO ISIN TO NOMI
isin_name_dict = {alfa.iloc[i,1] : alfa.iloc[i,0] for i in range(len(alfa))}

quote.columns = quote.iloc[1]
quote = quote.iloc[2:]

#%%


