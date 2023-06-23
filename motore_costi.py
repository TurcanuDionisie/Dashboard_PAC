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
    "IE0004621052": 0.40,
    "IE0004879379": 0.60,
}


importo_rata = 2000

durata_anni = 10

#paga 2 volte all'anno (frequenza semestrale)
frequenza = 2


importo_totale_ex_iniziale = importo_rata * frequenza * durata_anni

importo_mensile = importo_totale_ex_iniziale / (durata_anni * 12)


# %% CALCOLA IMPORTO MINIMO


if(importo_mensile < 150):
    print("Errore importo minimo mensile: " + str(importo_mensile))


importo_fondi = {}


for isin in pesi:
   importo_fondi[isin] = pesi[isin] * importo_mensile
   


#se c'è più di un fondo selezionato
#controlla importi minimo
if(len(importo_fondi) > 1):
    for isin in importo_fondi:
        if(importo_fondi[isin] < costi['RATA_MINIMA_MULTIFONDO'].loc[isin]):
            print("Errore importo minimo " + isin)


print("(ESCLUSO VERSAMENTO INIZIALE) IL cliente verserà in totale " + str(importo_totale_ex_iniziale))



# %% CALCOLA COSTI SOTTOSCRIZIONE


#calcolo importo totale
importo_totale = importo_totale_ex_iniziale + (importo_mensile * 12)


totale_fondi = {}


for isin in pesi:
    totale_fondi[isin] = pesi[isin] * importo_totale



costi_sottoscrizione = {}

for isin in totale_fondi:
    costi_sottoscrizione[isin] = costi[fasciaCostiSottoscrizione(totale_fondi[isin], costi.loc[isin])].loc[isin]




# %% CALCOLA DIRITTI FISSI


fascia_diritti_fissi_iniziale = fasciaDirittiFissi(importo_iniziale, costi.loc[isin])

costi_diritti_fissi = costi[fascia_diritti_fissi_iniziale].loc[isin]



print("IMPORTO RATE: " + str(importo_rata))
print("DIRITTO FISSO: " + str(costi["DIRITTO_FISSO"].loc[isin]))
print("FASCIA: " + str(fascia_diritti_fissi_iniziale))
print("RANGE MIN: " + str(costi[fascia_diritti_fissi_iniziale + "_MIN"].loc[isin]))
print("RANGE MIN: " + str(costi[fascia_diritti_fissi_iniziale + "_MAX"].loc[isin]))
print("DIRITTI INIZIALI: " + str(costi_diritti_fissi))

