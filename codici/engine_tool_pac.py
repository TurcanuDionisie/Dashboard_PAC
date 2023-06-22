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

#%% AGGIORNO DATI-...... DA FINIRE
# directory_universi = r'I:\Documenti\File PMC\In Corso'

# ch = pd.read_excel(directory_universi +'\par - universo ch mif sintesi.xlsx', sheet_name='Q.ta Pubblicata')
# mbb = pd.read_excel(directory_universi + '\par - universo mbb mif sintesi.xlsx', sheet_name='Q.ta Pubblicata')
# mif = pd.read_excel(directory_universi + '/a&p - universo mgf italiani.xlsx', sheet_name='Quota Pubb Rettificata')

# # FILE ADJUSTMENTS
# ch = ch.iloc[1:] 
# ch.iloc[0,0] = 'Date' 
# ch.columns = ch.loc[1]
# ch = ch.iloc[1:].set_index('Date') 
# for s in ch.columns:
#     ch[s] = pd.to_numeric(ch[s])
# ch = ch.replace(0,np.nan)
# ch.fillna(method='ffill', inplace=True)

# mbb = mbb.iloc[1:] 
# mbb.iloc[0,0] = 'Date' 
# mbb.columns = mbb.loc[1]
# mbb = mbb.iloc[1:].set_index('Date') 
# for s in mbb.columns:
#     mbb[s] = pd.to_numeric(mbb[s])
# mbb = mbb.replace(0,np.nan)
# mbb.fillna(method='ffill', inplace=True)

# mif = mif.iloc[2:] 
# mif = mif.rename(columns={mif.columns[0] : 'Date'}) 
# mif = mif.iloc[1:].set_index('Date') 
# for s in mif.columns:
#     mif[s] = pd.to_numeric(mif[s])
# mif = mif.replace(0,np.nan)
# mif.fillna(method='ffill', inplace=True)


# isin = quote.columns[0]

# quote.index = quote.index.append(ch[ch.index > quote.index[-1]].index)

# for isin in quote.columns:
    
#     if isin.startswith('IE') and isin_name_dict[isin].startswith('Challenge'):
#         quote[isin] = quote[isin].append(ch[isin][ch.index > quote.index[-1]].T)
        
#     elif isin.startswith('IE') and isin_name_dict[isin].startswith('Mediolanum'):
#         quote[isin].append(mbb[isin][mbb.index > quote.index[-1]])
        
# else:
#     quote[isin].append(mif[isin][mif.index > quote.index[-1]])
        
#%%         
        