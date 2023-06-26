# %% INIT

import pandas as pd
import numpy as np
import os


from funzioni import fasciaDirittiFissi, fasciaCostiSottoscrizione


folder_path = r"C:\Users\Dionisie.Turcanu\Documents\GitHub\Dashboard_PAC"
os.chdir(folder_path)


costi = pd.read_excel('costi.xlsx', index_col=0)


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
    "IT0005066896": 0.5,
    "IT0005066938": 0.5,
}


# Scegli tra: 'Mensile', 'Bimestrale', 'Trimestrale', 'Quadrimestrale', 'Semestrale', 'Annuale'
frequenza = 'Mensile'  
importo_rata = 500
durata_anni = 10



# %% ELABORAZIONE INPUT

num_mesi = frequenze[frequenza]

numero_rate = (12 / num_mesi) * durata_anni

importo_rata_mensile = (importo_rata * (12 / num_mesi) * durata_anni) / (durata_anni * 12)

investimento_iniziale = importo_rata_mensile * 12

#escluso versamento iniziale
importo_totale_rate = numero_rate * importo_rata



# %% VERIFICA IMPORTO MINIMO

# per qualsiasi fondo la rata minima deve essere di 150
if(importo_rata_mensile < 150):
    print("Errore importo minimo mensile: " + str(importo_rata_mensile))



importo_fondi = {}


for isin in fondi:
   importo_fondi[isin] = fondi[isin] * importo_rata_mensile
   


#se c'è più di un fondo selezionato
#controlla importi minimo
if(len(importo_fondi) > 1):
    for isin in importo_fondi:
        if(importo_fondi[isin] < costi['RATA_MINIMA_MULTIFONDO'].loc[isin]):
            print("IMPORTO MINIMO NON RISPETTATO " + isin)



# %% CALCOLA COSTI SOTTOSCRIZIONE

#calcolo importo totale rate e investimento iniziale
importo_totale = importo_totale_rate + investimento_iniziale


#prendo un isin a caso da quelli selezionati
#i fondi della stessa famiglia hanno le stesse caratteristiche
isin = list(fondi)[0]


#ritorna costi di sottoscrizione in percentuale
costi_sottoscrizione = costi[fasciaCostiSottoscrizione(importo_totale, costi.loc[isin])].loc[isin]



# %% CALCOLA DIRITTI FISSI INIZIALI E COSTANTI

#ritorna costi in euro
diritti_fissi_iniziali = costi["DIRITTO_FISSO"].loc[isin]



#fascia diritti fissi costanti
fascia_diritti_fissi = fasciaDirittiFissi(investimento_iniziale, costi.loc[isin])

#ritorna costi in euro
diritti_fissi = costi[fascia_diritti_fissi].loc[isin]

#se il costo è in percentuale allora trasformalo in euro
if (diritti_fissi == 0.001):
    diritti_fissi = investimento_iniziale * diritti_fissi




