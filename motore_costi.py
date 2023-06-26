import pandas as pd
import numpy as np
import os


folder_path = r"C:\Users\Dionisie.Turcanu\Documents\GitHub\Dashboard_PAC"
os.chdir(folder_path)


# %% FUNZIONI

def fasciaDirittiFissi(importo_iniziale, dataframe):
    for i in range(1,4):  # Per il numero di fasce (1-6)
        column_min = f"DIRITTO_FISSO_FASCIA_{i}_MIN"
        column_max = f"DIRITTO_FISSO_FASCIA_{i}_MAX"
        # Controlla se importo_iniziale rientra in questa fascia
        if dataframe[column_min].item() <= importo_iniziale <= dataframe[column_max].item():
            return f"DIRITTO_FISSO_FASCIA_{i}"
    return "Importo non rientra in nessuna fascia"



def fasciaCostiSottoscrizione(importo_iniziale, dataframe):
    for i in range(1,7):  # Per il numero di fasce (1-6)
        column_min = f"COM_FASCIA_{i}_MIN"
        column_max = f"COM_FASCIA_{i}_MAX"
        # Controlla se importo_iniziale rientra in questa fascia
        if dataframe[column_min].item() <= importo_iniziale <= dataframe[column_max].item():
            return f"COM_FASCIA_{i}"
    return "Importo non rientra in nessuna fascia"



#%% INPUT

costi = pd.read_excel('costi.xlsx', index_col=0)


pesi = {
    "IE0004457085": 0.40,
    "IE0004460683": 0.60,
}


importo_rata = 2000

durata_anni = 10


# Mappa la frequenza a un numero di mesi
frequenze = {
    'Mensile': 1,
    'Bimestrale': 2,
    'Trimestrale': 3,
    'Quadrimestrale': 4,
    'Semestrale': 6,
    'Annuale': 12,
}



#ogni quanti mesi investe
frequenza = 'Mensile'  # Scegli tra: 'Mensile', 'Bimestrale', 'Trimestrale', 'Quadrimestrale', 'Semestrale', 'Annuale'
num_mesi = frequenze[frequenza]


numero_rate = (12 / num_mesi) * durata_anni



importo_rata_mensile = (importo_rata * (12 / num_mesi) * durata_anni) / (durata_anni * 12)

investimento_iniziale = importo_rata_mensile * 12



#escluso versamento iniziale
importo_totale = numero_rate * importo_rata




# %% CALCOLA IMPORTO MINIMO


# per qualsiasi fondo la rata minima deve essere di 150
if(importo_rata_mensile < 150):
    print("Errore importo minimo mensile: " + str(importo_rata_mensile))



importo_fondi = {}


for isin in pesi:
   importo_fondi[isin] = pesi[isin] * importo_rata_mensile
   


#se c'è più di un fondo selezionato
#controlla importi minimo
if(len(importo_fondi) > 1):
    for isin in importo_fondi:
        if(importo_fondi[isin] < costi['RATA_MINIMA_MULTIFONDO'].loc[isin]):
            print("Errore importo minimo " + isin)


print("(ESCLUSO VERSAMENTO INIZIALE) IL cliente verserà in totale " + str(importo_totale))



# %% CALCOLA COSTI SOTTOSCRIZIONE


#calcolo importo totale aggiungendo iporto iniziale
importo_totale = importo_totale + investimento_iniziale


#prendo un isin a caso della categoria, tanto hanno tutti lo stesso costo
#passo in input il costo totale della categoria
#ritorna costi in percentuale
isin = "IE0004457085"
costi_sottoscrizione = costi[fasciaCostiSottoscrizione(importo_totale, costi.loc[isin])].loc[isin]




# %% CALCOLA DIRITTI FISSI


fascia_diritti_fissi_iniziale = fasciaDirittiFissi(investimento_iniziale, costi.loc[isin])

#costi diritti fissi in euro
costi_diritti_fissi = costi[fascia_diritti_fissi_iniziale].loc[isin]

#unico caso particolare dove il costo è in percentuale
if (costi_diritti_fissi == 0.001):
    costi_diritti_fissi = investimento_iniziale * costi_diritti_fissi


print("IMPORTO RATE: " + str(importo_rata))
print("DIRITTO FISSO: " + str(costi["DIRITTO_FISSO"].loc[isin]))
print("FASCIA: " + str(fascia_diritti_fissi_iniziale))
print("RANGE MIN: " + str(costi[fascia_diritti_fissi_iniziale + "_MIN"].loc[isin]))
print("RANGE MIN: " + str(costi[fascia_diritti_fissi_iniziale + "_MAX"].loc[isin]))
print("DIRITTI INIZIALI: " + str(costi_diritti_fissi))

