# %% INIT

import pandas as pd
import numpy as np
import os


from funzioni import fasciaDirittiFissi, fasciaCostiSottoscrizione, calcola_costi, calcola_performance


folder_path = r"C:\Users\Dionisie.Turcanu\Documents\GitHub\Dashboard_PAC"
os.chdir(folder_path)


file_decodifiche = pd.read_excel('costi.xlsx', index_col=0)
base_dati = pd.read_excel('DB_TOT_PROXY.xlsx', index_col=0)


# Mappa la frequenza a un numero di mesi
frequenze = {
    'Mensile': 1,
    'Bimestrale': 2,
    'Trimestrale': 3,
    'Quadrimestrale': 4,
    'Semestrale': 6,
    'Annuale': 12,
}


# %% INPUT


# isin selezionati e corrispettivo peso
fondi = {
    "IE0004878744": 0.5,
    "IE0004460683": 0.5
}


# Scegli tra: 'Mensile', 'Bimestrale', 'Trimestrale', 'Quadrimestrale', 'Semestrale', 'Annuale'
frequenza = 'Mensile'  
importo_rata = 200
durata_anni = 10



# %% ELABORAZIONE INPUT

num_mesi = frequenze[frequenza]

numero_rate = (12 / num_mesi) * durata_anni

importo_rata_mensile = (importo_rata * (12 / num_mesi) * durata_anni) / (durata_anni * 12)

investimento_iniziale = importo_rata_mensile * 12

#escluso versamento iniziale
importo_totale_rate = numero_rate * importo_rata


giorno_del_mese = 8


deroga_iniziale = 1
deroga_totale = 1

 

# %% CALCOLA COSTI

dati_input = {
        "fondi": fondi,
        "file_decodifiche": file_decodifiche,
        'importo_rata_mensile': importo_rata_mensile,
        'importo_totale_rate':importo_totale_rate,
        'investimento_iniziale': investimento_iniziale
        }

costi = calcola_costi(dati_input)


# %% CALCOLA PERFORMANCE



risultati_performance = {}

for isin in fondi:
    quote = base_dati[isin]
    peso = fondi[isin]
    
    
    dati_input = {
        
        "quote" : quote,
        "peso" : peso,
        "costo_sottoscrizione" : costi["costi_sottoscrizione"],
        "diritto_fisso_iniziale" : costi["diritti_fissi_iniziali"],
        "diritto_fisso" : costi["diritti_fissi"],
        "deroga_totale" : deroga_totale,
        "deroga_iniziale" : deroga_iniziale,
        "num_mesi" : num_mesi,
        "giorno_del_mese" : giorno_del_mese,
        "numero_rate" : numero_rate,
        "importo_rata_mensile" : importo_rata_mensile,
        "importo_rata" : importo_rata,
        "importo_totale_rate" : importo_totale_rate,
        "investimento_iniziale" : investimento_iniziale
        }
    
    
    
    risultati_performance[isin] = calcola_performance(dati_input)
    


df_portafolgio = pd.DataFrame(columns=risultati_performance[isin]["Calcoli"].columns, index=risultati_performance[isin]["Calcoli"].index)

df_portafolgio = df_portafolgio.fillna(0)


for isin in risultati_performance:
    df_portafolgio["Movimenti"] += risultati_performance[isin]["Calcoli"]["Movimenti"]
    df_portafolgio["MOVIMENTO_NETTO"] += risultati_performance[isin]["Calcoli"]["MOVIMENTO_NETTO"]
    df_portafolgio["CTV_LORDO"] += risultati_performance[isin]["Calcoli"]["CTV_LORDO"]
    df_portafolgio["CTV_NETTO"] += risultati_performance[isin]["Calcoli"]["CTV_NETTO"]
    


max_date = quote.index.max()


df_portafolgio['Numeri'] = df_portafolgio['Movimenti'] * (max_date - df_portafolgio.index).days

totale_dovuto = importo_totale_rate + investimento_iniziale

df_portafolgio['CTV Complessivo'] = df_portafolgio['CTV_NETTO'] + totale_dovuto - df_portafolgio['MOVIMENTO_NETTO'].cumsum()

df_portafolgio['VOL'] = df_portafolgio['CTV Complessivo'].pct_change()

df_portafolgio['MAX DD'] = df_portafolgio['CTV_NETTO'] / df_portafolgio['MOVIMENTO_NETTO'].cumsum() - 1



# performance = 
