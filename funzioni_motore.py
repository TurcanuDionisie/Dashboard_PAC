import pandas as pd
import numpy as np
import os


folder_path = r"C:\Users\Dionisie.Turcanu\Documents\GitHub\Dashboard_PAC"
os.chdir(folder_path)



#funzione usata per estrarre fascia diritti fissi
def fasciaDirittiFissi(importo_iniziale, dataframe):
    for i in range(1,4):  # Per il numero di fasce (1-6)
        column_min = f"DIRITTO_FISSO_FASCIA_{i}_MIN"
        column_max = f"DIRITTO_FISSO_FASCIA_{i}_MAX"
        # Controlla se importo_iniziale rientra in questa fascia
        if dataframe[column_min].item() <= importo_iniziale <= dataframe[column_max].item():
            return f"DIRITTO_FISSO_FASCIA_{i}"
    return "Importo non rientra in nessuna fascia"





#funzione usata per estrarre fascia costi sottostcrzione
def fasciaCostiSottoscrizione(importo_iniziale, dataframe):
    for i in range(1,7):  # Per il numero di fasce (1-6)
        column_min = f"COM_FASCIA_{i}_MIN"
        column_max = f"COM_FASCIA_{i}_MAX"
        # Controlla se importo_iniziale rientra in questa fascia
        if dataframe[column_min].item() <= importo_iniziale <= dataframe[column_max].item():
            return f"COM_FASCIA_{i}"
    return "Importo non rientra in nessuna fascia"





#restituisce in un dizionario: costi sottoscrizione, diritti fissi iniziali e diritti fissi costanti
def calcola_costi(dati_input):
    
    #estrazione dati in input
    fondi = dati_input["fondi"]
    file_decodifiche = dati_input["file_decodifiche"]
    importo_rata_mensile = dati_input["importo_rata_mensile"]
    importo_totale_rate = dati_input["importo_totale_rate"]
    investimento_iniziale = dati_input["investimento_iniziale"]
    
    
    # VERIFICA IMPORTO MINIMO
    if(importo_rata_mensile < 150):
        print("Errore importo minimo mensile: " + str(importo_rata_mensile))
        return "ERRORE RATA MENSILE"
    
    
    #calcolo importo rata mensile per ogni fondo selezionato
    importo_fondi = {}
    for isin in fondi:
        #es trasforma 50 in 50%
        importo_fondi[isin] = (fondi[isin] / 100) * importo_rata_mensile
        
    
    # se c'è più di un fondo selezionato, controlla importi minimo
    if(len(importo_fondi) > 1):
        for isin in importo_fondi:
            if(importo_fondi[isin] < file_decodifiche['RATA_MINIMA_MULTIFONDO'].loc[isin]):
                print("IMPORTO MINIMO NON RISPETTATO " + isin)
                return "ERRORE IMPORTO MINIMO"


    # CALCOLA COSTI SOTTOSCRIZIONE
    importo_totale = importo_totale_rate + investimento_iniziale
    isin = list(fondi)[0]
    costi_sottoscrizione = file_decodifiche[fasciaCostiSottoscrizione(importo_totale, file_decodifiche.loc[isin])].loc[isin]


    # CALCOLA DIRITTI FISSI INIZIALI E COSTANTI
    diritti_fissi = file_decodifiche["DIRITTO_FISSO"].loc[isin]
    fascia_diritti_fissi = fasciaDirittiFissi(investimento_iniziale, file_decodifiche.loc[isin])
    diritti_fissi_iniziali = file_decodifiche[fascia_diritti_fissi].loc[isin]


    # se il costo è in percentuale allora trasformalo in euro
    if (diritti_fissi_iniziali == 0.001):
        diritti_fissi_iniziali = investimento_iniziale * diritti_fissi_iniziali
        
        
    costi_prodotti = { 
        "costi_sottoscrizione": costi_sottoscrizione, 
        "diritti_fissi_iniziali": diritti_fissi_iniziali, 
        "diritti_fissi": diritti_fissi      
    }
 

    return costi_prodotti








def calcola_performance(dati_input):
    
    
    peso = dati_input["peso"]
    #trasformo il peso in percentuale
    peso = peso / 100
    
    
    
    quote = dati_input["quote"]
    
    
    
    
    # espresso in percentuale
    costo_sottoscrizione = dati_input["costi_sottoscrizione"]
    
    
    #espresso in euro
    diritto_fisso_iniziale = dati_input["diritti_fissi_iniziali"]
    diritto_fisso = dati_input["diritti_fissi"]
    
    
    deroga_totale = dati_input["deroga_totale"]
    deroga_iniziale = dati_input["deroga_iniziale"]
    
    
    #ogni quanti mesi investe
    num_mesi = dati_input["num_mesi"]
    
    
    giorno_del_mese = dati_input["giorno_del_mese"]
    
    
    numero_rate = dati_input["numero_rate"]
    
    
    importo_rata = dati_input["importo_rata"] * peso
    
    
    durata_anni = dati_input["durata_anni"]
    
    
    
    
    
    #già pesata
    importo_rata_mensile = (importo_rata * (12 / num_mesi) * durata_anni) / (durata_anni * 12)
    
    investimento_iniziale = importo_rata_mensile * 12
    
    #escluso versamento iniziale
    importo_totale_rate = numero_rate * importo_rata
    
    
    
    
    
    # Vado a pesare i costi di competenza del fondo
    diritto_fisso_iniziale = diritto_fisso_iniziale * peso
    diritto_fisso = diritto_fisso * peso
    
    
    
    importo_costo_sottoscrizione = costo_sottoscrizione * (importo_totale_rate + investimento_iniziale)
    
    
    
    
    # Divido i costi in fette
    prima_fetta = importo_costo_sottoscrizione * 0.33 * deroga_totale * deroga_iniziale
    seconda_fetta = importo_costo_sottoscrizione * 0.19 * deroga_totale
    terza_fetta = importo_costo_sottoscrizione * 0.48 * deroga_totale
    
    
    
    # In quote ho lo storico, piano piano ci aggiungo le varie colonne
    
    # MOVIMENTI
    movimenti = pd.DataFrame(index=quote.index)
    movimenti['Movimenti'] = 0
    
    # Assegna l'investimento iniziale alla prima data
    movimenti.iloc[0] = investimento_iniziale
    
    # Crea una funzione per trovare la prossima data disponibile
    def trova_data(dates, target_day):
        for date in dates:
            if date.day >= target_day:
                return date
        return None
    
    # Itera per ogni mese e anno nel DataFrame
    mesi_anni = [(date.year, date.month) for date in quote.index]
    mesi_anni = list(set(mesi_anni))  # Rimuovi i duplicati
    mesi_anni.sort()  # Ordina la lista
    
    rate_added = 0
    current_month = None
    for year, month in mesi_anni:
        if current_month is None or ((month - current_month) % 12) >= num_mesi:
            # Trova tutte le date per quel mese e anno
            dates = quote.index[(quote.index.year == year) & (quote.index.month == month)]
            dates = dates.sort_values()  # Assicurati che le date siano ordinate
    
            # Trova la prossima data disponibile dopo il giorno_del_mese
            date = trova_data(dates, giorno_del_mese)
    
            # Aggiungi la rata se la data è valida e non abbiamo già aggiunto tutte le rate
            if date is not None and rate_added < numero_rate:
                movimenti.loc[date] += importo_rata
                rate_added += 1
                current_month = month
    
    # Unisci il DataFrame movimenti con il tuo DataFrame originale
    quote = pd.concat([quote, movimenti], axis=1)
    
    
    
    
    
    
    
    # COSTI UP1
    quote['COSTI UP1'] = np.nan
    
    # Trova gli indici dei movimenti
    movimenti_index = quote[quote['Movimenti'] != 0].index
    
    # Applica la prima fetta
    quote.loc[movimenti_index[0], 'COSTI UP1'] = prima_fetta
    
    # Applica la seconda fetta sui successivi 6 movimenti
    for i in range(1, 7):
        if i < len(movimenti_index):  # Verifica che ci sia un movimento
            quote.loc[movimenti_index[i], 'COSTI UP1'] = seconda_fetta / 6
    
    # Applica la terza fetta sui movimenti rimanenti
    num_movimenti_rimanenti = len(movimenti_index) - 7
    for i in range(7, len(movimenti_index)):
        if i < len(movimenti_index):  # Verifica che ci sia un movimento
            quote.loc[movimenti_index[i], 'COSTI UP1'] = terza_fetta / num_movimenti_rimanenti
    
    
    
    
    
    
    
    # COSTI UP3
    
    quote['COSTI UP3'] = np.nan
    
    # Trova gli indici dei movimenti
    movimenti_index = quote[quote['Movimenti'] != 0].index
    
    # Applica il diritto fisso iniziale
    quote.loc[movimenti_index[0], 'COSTI UP3'] = diritto_fisso_iniziale
    
    # Applica il diritto fisso a tutti gli altri movimenti
    for i in range(1, len(movimenti_index)):
        quote.loc[movimenti_index[i], 'COSTI UP3'] = diritto_fisso
        
        
        
    
    
        
    # MOVIMENTO NETTO
    quote["MOVIMENTO_NETTO"] = quote["Movimenti"] - quote["COSTI UP1"] - quote["COSTI UP3"]
    
    
    
    
    
    # CTV LORDO
    quote = quote.fillna(0)
    
    quote['CTV_LORDO'] = np.nan
    
    # Trova gli indici dei movimenti
    movimenti_index = quote[quote['Movimenti'] != 0].index
    
    # Applica il primo valore dei movimenti
    quote.loc[movimenti_index[0], 'CTV_LORDO'] = quote.loc[movimenti_index[0], 'Movimenti']
    
    # Calcola CTV_LORDO per tutte le altre righe
    for i in range(1, len(quote.index)):
        ctv_precedente = quote.loc[quote.index[i-1], 'CTV_LORDO']
        quote_precedente = quote.loc[quote.index[i-1], quote.columns[0]]
        quote_corrispettivo = quote.loc[quote.index[i], quote.columns[0]]
        movimento_corrispettivo = quote.loc[quote.index[i], 'Movimenti']
    
        quote.loc[quote.index[i], 'CTV_LORDO'] = (ctv_precedente * quote_corrispettivo / quote_precedente) + movimento_corrispettivo
    
      
    
    
    # CTV NETTO
    quote['CTV_NETTO'] = np.nan
    
    # Trova gli indici dei movimenti
    movimenti_index = quote[quote['MOVIMENTO_NETTO'] != 0].index
    
    # Applica il primo valore dei movimenti
    quote.loc[movimenti_index[0], 'CTV_NETTO'] = quote.loc[movimenti_index[0], 'MOVIMENTO_NETTO']
    
    # Calcola CTV_LORDO per tutte le altre righe
    for i in range(1, len(quote.index)):
        ctv_precedente = quote.loc[quote.index[i-1], 'CTV_NETTO']
        quote_precedente = quote.loc[quote.index[i-1], quote.columns[0]]
        quote_corrispettivo = quote.loc[quote.index[i], quote.columns[0]]
        movimento_corrispettivo = quote.loc[quote.index[i], 'MOVIMENTO_NETTO']
    
        quote.loc[quote.index[i], 'CTV_NETTO'] = (ctv_precedente * quote_corrispettivo / quote_precedente) + movimento_corrispettivo
        
        
        
        
    max_date = quote.index.max()
    quote['Numeri'] = quote['Movimenti'] * (max_date - quote.index).days
    
    
    
    totale_dovuto = importo_totale_rate + investimento_iniziale
    quote['CTV Complessivo'] = quote['CTV_NETTO'] + totale_dovuto - quote['MOVIMENTO_NETTO'].cumsum()
    
    
    quote['VOL'] = quote['CTV Complessivo'].pct_change()
    
    
    
    quote['MAX DD'] = quote['CTV_NETTO'] / quote['MOVIMENTO_NETTO'].cumsum() - 1
    
    
    
    
    volatilita = quote['CTV Complessivo'].resample('M').last().pct_change()
    
    totale_rate_versate = sum(quote['Movimenti'])
    
    patrimonio_finale = quote['CTV_NETTO'].iloc[-1]
    
    plus = patrimonio_finale - totale_rate_versate
    
    mwrr = plus / (sum(quote['Numeri']) / (quote.index[-1] - quote.index[0]).days)
    
    mwrr_annualizzato = ((1 + mwrr) ** (365 / (quote.index[-1] - quote.index[0]).days)) - 1
    
    volatilita_finale = np.std(volatilita) * np.sqrt(12)
    
    max_dd = min(quote['MAX DD'])
    
    
    
    
    
    
    #COLONNA QUOTE
    quote["Quote"] = quote['MOVIMENTO_NETTO'] / quote[quote.columns[0]]


    #COLONNA QUOTE CUMULATE
    quote["Quote Cumulate"] = quote["Quote"].cumsum()



    # COLONNA PMC
    indici = quote.index.tolist()

    quote['PMC'] = np.nan
    quote.at[indici[0], 'PMC'] = quote.loc[indici[0], quote.columns[0]]

    for i in range(1, len(quote)):
        prev_pmc = quote.at[indici[i - 1], 'PMC']
        prev_cum_quote = quote.at[indici[i - 1], 'Quote Cumulate']
        curr_val_quota = quote.at[indici[i], quote.columns[0]]
        curr_quote = quote.at[indici[i], 'Quote']
        curr_cum_quote = quote.at[indici[i], 'Quote Cumulate']
        quote.at[indici[i], 'PMC'] = ((prev_pmc * prev_cum_quote) + (curr_val_quota * curr_quote)) / curr_cum_quote



    # Applico np.where per sostituire i valori di VAL_QUOTA con NaN quando Movimenti è 0
    quote['VAL_QUOTA_FILT'] = np.where(quote['Movimenti'] != 0, quote[quote.columns[0]], np.nan)

    # Calcolo la media cumulativa, ignorando i NaN
    quote['Prezzo_medio'] = quote['VAL_QUOTA_FILT'].expanding().mean()


    
    
    risultato = {
        "Totale rate versate": totale_rate_versate,
        "patrimonio finale": patrimonio_finale,
        "plus": plus,
        "MWRR": mwrr,
        "MWRR_annualizzato": mwrr_annualizzato,
        "Volatilita_finale": volatilita_finale,
        "Max_DD": max_dd,
        
        #salvo tutti i passaggi perchè servono per altri calcoli
        "Calcoli": quote
    }
    
    
    return risultato






def CalcolaPerformancePortafolgio(dati_input):

    risultati_performance = dati_input["risultati_performance"]
    importo_totale_rate = dati_input["importo_totale_rate"]
    investimento_iniziale = dati_input["investimento_iniziale"]


    indici = risultati_performance[next(iter(risultati_performance))]["Calcoli"].index
    colonne = ['Movimenti', 'MOVIMENTO_NETTO', 'CTV_LORDO', 'CTV_NETTO']


    portafolgio = pd.DataFrame(columns=colonne, index=indici).fillna(0)



    for isin in risultati_performance:
        portafolgio["Movimenti"] += risultati_performance[isin]["Calcoli"]["Movimenti"]
        portafolgio["MOVIMENTO_NETTO"] += risultati_performance[isin]["Calcoli"]["MOVIMENTO_NETTO"]
        portafolgio["CTV_LORDO"] += risultati_performance[isin]["Calcoli"]["CTV_LORDO"]
        portafolgio["CTV_NETTO"] += risultati_performance[isin]["Calcoli"]["CTV_NETTO"]




    max_date = portafolgio.index.max()
    portafolgio['Numeri'] = portafolgio['Movimenti'] * (max_date - portafolgio.index).days


    totale_dovuto = importo_totale_rate + investimento_iniziale
    portafolgio['CTV Complessivo'] = portafolgio['CTV_NETTO'] + totale_dovuto - portafolgio['MOVIMENTO_NETTO'].cumsum()


    portafolgio['VOL'] = portafolgio['CTV Complessivo'].pct_change()

    portafolgio['MAX DD'] = portafolgio['CTV_NETTO'] / portafolgio['MOVIMENTO_NETTO'].cumsum() - 1


    volatilita = portafolgio['CTV Complessivo'].resample('M').last().pct_change()

    totale_rate_versate = sum(portafolgio['Movimenti'])

    patrimonio_finale = portafolgio['CTV_NETTO'].iloc[-1]

    plus = patrimonio_finale - totale_rate_versate

    mwrr = plus / (sum(portafolgio['Numeri']) / (portafolgio.index[-1] - portafolgio.index[0]).days)

    mwrr_annualizzato = ((1 + mwrr) ** (365 / (portafolgio.index[-1] - portafolgio.index[0]).days)) - 1

    volatilita_finale = np.std(volatilita) * np.sqrt(12)

    max_dd = min(portafolgio['MAX DD'])
    
    
    
    
    #Dati per grafico portafolgio
    grafico = pd.DataFrame()
    grafico["CTV_NETTO"] = portafolgio['CTV_NETTO']
    grafico["MOVIMENTI"] = portafolgio["Movimenti"].cumsum()
    

    risultato = {
        "Totale rate versate": totale_rate_versate,
        "patrimonio finale": patrimonio_finale,
        "plus": plus,
        "MWRR": mwrr,
        "MWRR_annualizzato": mwrr_annualizzato,
        "Volatilita_finale": volatilita_finale,
        "Max_DD": max_dd,
        "Grafico": grafico
    }
    
    return risultato
