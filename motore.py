import pandas as pd
import numpy as np
import os


folder_path = r"C:\Users\Dionisie.Turcanu\Documents\GitHub\Dashboard_PAC"
os.chdir(folder_path)


file_decodifiche = pd.read_excel('costi.xlsx', index_col=0)
base_dati = pd.read_excel('DB_TOT_PROXY.xlsx', index_col=0)


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






def calcola_costi(dati_input):
    
    
    fondi = dati_input["fondi"]
    file_decodifiche = dati_input["file_decodifiche"]
    importo_rata_mensile = dati_input["importo_rata_mensile"]
    importo_totale_rate = dati_input["importo_totale_rate"]
    investimento_iniziale = dati_input["investimento_iniziale"]
    
    
    # VERIFICA IMPORTO MINIMO
    if(importo_rata_mensile < 150):
        print("Errore importo minimo mensile: " + str(importo_rata_mensile))
    
    
    importo_fondi = {}
    for isin in fondi:
        importo_fondi[isin] = fondi[isin] * importo_rata_mensile


    # se c'è più di un fondo selezionato, controlla importi minimo
    if(len(importo_fondi) > 1):
        for isin in importo_fondi:
            if(importo_fondi[isin] < file_decodifiche['RATA_MINIMA_MULTIFONDO'].loc[isin]):
                print("IMPORTO MINIMO NON RISPETTATO " + isin)


    # CALCOLA COSTI SOTTOSCRIZIONE
    importo_totale = importo_totale_rate + investimento_iniziale
    isin = list(fondi)[0]
    costi_sottoscrizione = file_decodifiche[fasciaCostiSottoscrizione(importo_totale, file_decodifiche.loc[isin])].loc[isin]


    # CALCOLA DIRITTI FISSI INIZIALI E COSTANTI
    diritti_fissi_iniziali = file_decodifiche["DIRITTO_FISSO"].loc[isin]
    fascia_diritti_fissi = fasciaDirittiFissi(investimento_iniziale, file_decodifiche.loc[isin])
    diritti_fissi = file_decodifiche[fascia_diritti_fissi].loc[isin]


    # se il costo è in percentuale allora trasformalo in euro
    if (diritti_fissi == 0.001):
        diritti_fissi = investimento_iniziale * diritti_fissi
        
        
    risultato = { 
        "costi_sottoscrizione": costi_sottoscrizione, 
        "diritti_fissi_iniziali": diritti_fissi_iniziali, 
        "diritti_fissi": diritti_fissi      
    }
 

    return risultato






def calcola_performance(dati_input):
  
    
  quote = dati_input["quote"]
  peso = dati_input["peso"]
  costo_sottoscrizione = dati_input["costo_sottoscrizione"]
  diritto_fisso_iniziale = dati_input["diritto_fisso_iniziale"]
  diritto_fisso = dati_input["diritto_fisso"]
  deroga_totale = dati_input["deroga_totale"]
  deroga_iniziale = dati_input["deroga_iniziale"]
  num_mesi = dati_input["num_mesi"]
  giorno_del_mese = dati_input["giorno_del_mese"]
  numero_rate = dati_input["numero_rate"]
  importo_rata_mensile = dati_input["importo_rata_mensile"]
  importo_rata = dati_input["importo_rata"]
  importo_totale_rate = dati_input["importo_totale_rate"]
  investimento_iniziale = dati_input["investimento_iniziale"]
  

  diritto_fisso_iniziale = diritto_fisso_iniziale * peso
  diritto_fisso = diritto_fisso * peso



  importo_costo_sottoscrizione = costo_sottoscrizione * (importo_totale_rate + investimento_iniziale)


  prima_fetta = importo_costo_sottoscrizione * 0.33 * deroga_totale * deroga_iniziale
  seconda_fetta = importo_costo_sottoscrizione * 0.19 * deroga_totale
  terza_fetta = importo_costo_sottoscrizione * 0.48 * deroga_totale


  # %% MOVIMENTI



  # Crea un nuovo DataFrame per i movimenti
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



  # %% COSTI UP1


  # Crea una nuova colonna "COSTI UP1" con tutti valori NaN
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



  # %% COSTI UP2

  # Definisci le variabili


  # Crea una nuova colonna "COSTI UP3" con tutti valori NaN
  quote['COSTI UP3'] = np.nan

  # Trova gli indici dei movimenti
  movimenti_index = quote[quote['Movimenti'] != 0].index

  # Applica il diritto fisso iniziale
  quote.loc[movimenti_index[0], 'COSTI UP3'] = diritto_fisso_iniziale

  # Applica il diritto fisso a tutti gli altri movimenti
  for i in range(1, len(movimenti_index)):
      quote.loc[movimenti_index[i], 'COSTI UP3'] = diritto_fisso



  # %%


  quote["MOVIMENTO_NETTO"] = quote["Movimenti"] - quote["COSTI UP1"] - quote["COSTI UP3"]


  # %%


  quote = quote.fillna(0)



  # Crea una nuova colonna "CTV_LORDO" con tutti valori NaN
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




  # Crea una nuova colonna "CTV_LORDO" con tutti valori NaN
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



  # %% 


  max_date = quote.index.max()

  # Crea la colonna 'Numeri'
  quote['Numeri'] = quote['Movimenti'] * (max_date - quote.index).days



  # %%



  totale_dovuto = importo_totale_rate + investimento_iniziale


  # Calcola 'CTV Complessivo'
  quote['CTV Complessivo'] = quote['CTV_NETTO'] + totale_dovuto - quote['MOVIMENTO_NETTO'].cumsum()



  # %%

  quote['VOL'] = quote['CTV Complessivo'].pct_change()


  # %%

  quote['MAX DD'] = quote['CTV_NETTO'] / quote['MOVIMENTO_NETTO'].cumsum() - 1


  # %%

  volatilita = quote['CTV Complessivo'].resample('M').last().pct_change()


  totale_rate_versate = sum(quote['Movimenti'])

  patrimonio_finale = quote['CTV_NETTO'].iloc[-1]


  plus = patrimonio_finale - totale_rate_versate


  mwrr = plus / (sum(quote['Numeri']) / (quote.index[-1] - quote.index[0]).days)


  mwrr_annualizzato = ((1 + mwrr) ** (365 / (quote.index[-1] - quote.index[0]).days)) - 1


  volatilita_finale = np.std(volatilita) * np.sqrt(12)



  max_dd = min(quote['MAX DD'])
  
  
  risultato =  {
        "Totale rate versate": totale_rate_versate,
        "patrimonio finale": patrimonio_finale,
        "plus": plus,
        "MWRR": mwrr,
        "MWRR_annualizzato": mwrr_annualizzato,
        "Volatilita_finale": volatilita_finale,
        "Max_DD": max_dd,
        "Calcoli": quote
    }
  
  return risultato









def GraficoPortafolgio(risultati_performance, isin, totale_dovuto):
    df_portafolgio = pd.DataFrame(columns=risultati_performance[isin]["Calcoli"].columns, index=risultati_performance[isin]["Calcoli"].index)

    df_portafolgio = df_portafolgio.fillna(0)


    for isin in risultati_performance:
        df_portafolgio["Movimenti"] += risultati_performance[isin]["Calcoli"]["Movimenti"]
        df_portafolgio["MOVIMENTO_NETTO"] += risultati_performance[isin]["Calcoli"]["MOVIMENTO_NETTO"]
        df_portafolgio["CTV_LORDO"] += risultati_performance[isin]["Calcoli"]["CTV_LORDO"]
        df_portafolgio["CTV_NETTO"] += risultati_performance[isin]["Calcoli"]["CTV_NETTO"]
        


    max_date = df_portafolgio.index.max()


    df_portafolgio['Numeri'] = df_portafolgio['Movimenti'] * (max_date - df_portafolgio.index).days


    df_portafolgio['CTV Complessivo'] = df_portafolgio['CTV_NETTO'] + totale_dovuto - df_portafolgio['MOVIMENTO_NETTO'].cumsum()

    df_portafolgio['VOL'] = df_portafolgio['CTV Complessivo'].pct_change()

    df_portafolgio['MAX DD'] = df_portafolgio['CTV_NETTO'] / df_portafolgio['MOVIMENTO_NETTO'].cumsum() - 1
    
    
    
    grafico = pd.DataFrame()
    grafico["CTV_NETTO"] = df_portafolgio['CTV_NETTO']
    grafico["MOVIMENTI"] = df_portafolgio["Movimenti"].cumsum()
    
    
    
    volatilita = df_portafolgio['CTV Complessivo'].resample('M').last().pct_change()


    totale_rate_versate = sum(df_portafolgio['Movimenti'])

    patrimonio_finale = df_portafolgio['CTV_NETTO'].iloc[-1]


    plus = patrimonio_finale - totale_rate_versate


    mwrr = plus / (sum(df_portafolgio['Numeri']) / (df_portafolgio.index[-1] - df_portafolgio.index[0]).days)


    mwrr_annualizzato = ((1 + mwrr) ** (365 / (df_portafolgio.index[-1] - df_portafolgio.index[0]).days)) - 1


    volatilita_finale = np.std(volatilita) * np.sqrt(12)



    max_dd = min(df_portafolgio['MAX DD'])
    
    
    risultato =  {
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
    

    






# Mappa la frequenza a un numero di mesi
frequenze = {
    'Mensile': 1,
    'Bimestrale': 2,
    'Trimestrale': 3,
    'Quadrimestrale': 4,
    'Semestrale': 6,
    'Annuale': 12,
}



def Motore (input_motore):
    
    
    # isin selezionati e corrispettivo peso
    fondi = {
        
    }
    
    
    #estrazione dati input
    frequenza =  input_motore['frequenza']
    importo_rata = float(input_motore['importo_rata'])
    durata_anni = int(input_motore['durata_anni'])
    giorno_del_mese = int(input_motore['giorno_mese'])
    
    #non ancora gestito
    data_inizio = input_motore['data_inizio']
    
    
    
    #trasformo pesi dei fondi da stringhe in float
    for isin in input_motore["isin_selezionati"]:
        fondi[isin] = float(input_motore["isin_selezionati"][isin])
    
    
    
    num_mesi = frequenze[frequenza]

    numero_rate = (12 / num_mesi) * durata_anni

    importo_rata_mensile = (importo_rata * (12 / num_mesi) * durata_anni) / (durata_anni * 12)

    investimento_iniziale = importo_rata_mensile * 12

    #escluso versamento iniziale
    importo_totale_rate = numero_rate * importo_rata


    #deroga ancora da gestire
    deroga_iniziale = 1
    deroga_totale = 1
    

    dati_input_costi = {
            "fondi": fondi,
            "file_decodifiche": file_decodifiche,
            'importo_rata_mensile': importo_rata_mensile,
            'importo_totale_rate':importo_totale_rate,
            'investimento_iniziale': investimento_iniziale
    }
    
    
    #calcola costi
    costi = calcola_costi(dati_input_costi)

    
    
    
    
    
    # calcola performance per ogni fondo
    risultati_performance = {}

    for isin in fondi:
        quote = base_dati[isin]
        peso = fondi[isin]
        
        
        dati_input_performance = {
            
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
        
        
        risultati_performance[isin] = calcola_performance(dati_input_performance)
    
    
    
    # in realtà contiene tutto
    grafico = GraficoPortafolgio(risultati_performance, isin, (importo_totale_rate + investimento_iniziale))
    
    
    
    return grafico
    
    
