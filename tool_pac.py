import pandas as pd
import numpy as np

import plotly.graph_objs as go


import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, ALL
import dash_bootstrap_components as dbc





url = 'https://raw.githubusercontent.com/TurcanuDionisie/Dashboard_PAC/new_motore/'



#%% FUNZIONI MOTORE 
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
    file_costi = dati_input["file_costi"]
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
            if(importo_fondi[isin] < file_costi['RATA_MINIMA_MULTIFONDO'].loc[isin]):
                print("IMPORTO MINIMO NON RISPETTATO " + isin)
                return "ERRORE IMPORTO MINIMO"


    # CALCOLA COSTI SOTTOSCRIZIONE
    importo_totale = importo_totale_rate + investimento_iniziale
    isin = list(fondi)[0]
    costi_sottoscrizione = file_costi[fasciaCostiSottoscrizione(importo_totale, file_costi.loc[isin])].loc[isin]


    # CALCOLA DIRITTI FISSI INIZIALI E COSTANTI
    diritti_fissi = file_costi["DIRITTO_FISSO"].loc[isin]
    fascia_diritti_fissi = fasciaDirittiFissi(investimento_iniziale, file_costi.loc[isin])
    diritti_fissi_iniziali = file_costi[fascia_diritti_fissi].loc[isin]


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
    movimenti['movimenti'] = 0
    
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
    quote['costi_up1'] = np.nan
    
    # Trova gli indici dei movimenti
    movimenti_index = quote[quote['movimenti'] != 0].index
    
    # Applica la prima fetta
    quote.loc[movimenti_index[0], 'costi_up1'] = prima_fetta
    
    # Applica la seconda fetta sui successivi 6 movimenti
    for i in range(1, 7):
        if i < len(movimenti_index):  # Verifica che ci sia un movimento
            quote.loc[movimenti_index[i], 'costi_up1'] = seconda_fetta / 6
    
    # Applica la terza fetta sui movimenti rimanenti
    num_movimenti_rimanenti = len(movimenti_index) - 7
    for i in range(7, len(movimenti_index)):
        if i < len(movimenti_index):  # Verifica che ci sia un movimento
            quote.loc[movimenti_index[i], 'costi_up1'] = terza_fetta / num_movimenti_rimanenti
    
    
    
    
    
    
    
    # COSTI UP3
    
    quote['costi_up3'] = np.nan
    
    # Trova gli indici dei movimenti
    movimenti_index = quote[quote['movimenti'] != 0].index
    
    # Applica il diritto fisso iniziale
    quote.loc[movimenti_index[0], 'costi_up3'] = diritto_fisso_iniziale
    
    # Applica il diritto fisso a tutti gli altri movimenti
    for i in range(1, len(movimenti_index)):
        quote.loc[movimenti_index[i], 'costi_up3'] = diritto_fisso
        
        
        
    
    
        
    # MOVIMENTO NETTO
    quote["movimento_netto"] = quote["movimenti"] - quote["costi_up1"] - quote["costi_up3"]
    
    
    
    
    
    # CTV LORDO
    quote = quote.fillna(0)
    
    quote['ctv_lordo'] = np.nan
    
    # Trova gli indici dei movimenti
    movimenti_index = quote[quote['movimenti'] != 0].index
    
    # Applica il primo valore dei movimenti
    quote.loc[movimenti_index[0], 'ctv_lordo'] = quote.loc[movimenti_index[0], 'movimenti']
    
    # Calcola CTV_LORDO per tutte le altre righe
    for i in range(1, len(quote.index)):
        ctv_precedente = quote.loc[quote.index[i-1], 'ctv_lordo']
        quote_precedente = quote.loc[quote.index[i-1], quote.columns[0]]
        quote_corrispettivo = quote.loc[quote.index[i], quote.columns[0]]
        movimento_corrispettivo = quote.loc[quote.index[i], 'movimenti']
    
        quote.loc[quote.index[i], 'ctv_lordo'] = (ctv_precedente * quote_corrispettivo / quote_precedente) + movimento_corrispettivo
    
      
    
    
    # CTV NETTO
    quote['ctv_netto'] = np.nan
    
    # Trova gli indici dei movimenti
    movimenti_index = quote[quote['movimento_netto'] != 0].index
    
    # Applica il primo valore dei movimenti
    quote.loc[movimenti_index[0], 'ctv_netto'] = quote.loc[movimenti_index[0], 'movimento_netto']
    
    # Calcola CTV_LORDO per tutte le altre righe
    for i in range(1, len(quote.index)):
        ctv_precedente = quote.loc[quote.index[i-1], 'ctv_netto']
        quote_precedente = quote.loc[quote.index[i-1], quote.columns[0]]
        quote_corrispettivo = quote.loc[quote.index[i], quote.columns[0]]
        movimento_corrispettivo = quote.loc[quote.index[i], 'movimento_netto']
    
        quote.loc[quote.index[i], 'ctv_netto'] = (ctv_precedente * quote_corrispettivo / quote_precedente) + movimento_corrispettivo
        
        
        
        
    max_date = quote.index.max()
    quote['numeri'] = quote['movimenti'] * (max_date - quote.index).days
    
    
    
    totale_dovuto = importo_totale_rate + investimento_iniziale
    quote['ctv_complessivo'] = quote['ctv_netto'] + totale_dovuto - quote['movimento_netto'].cumsum()
    
    
    quote['vol'] = quote['ctv_complessivo'].pct_change()
    
    
    
    quote['max_dd'] = quote['ctv_netto'] / quote['movimento_netto'].cumsum() - 1
    
    
    
    
    volatilita = quote['ctv_complessivo'].resample('M').last().pct_change()
    
    totale_rate_versate = sum(quote['movimenti'])
    
    patrimonio_finale = quote['ctv_netto'].iloc[-1]
    
    plus = patrimonio_finale - totale_rate_versate
    
    mwrr = plus / (sum(quote['numeri']) / (quote.index[-1] - quote.index[0]).days)
    
    mwrr_annualizzato = ((1 + mwrr) ** (365 / (quote.index[-1] - quote.index[0]).days)) - 1
    
    volatilita_finale = np.std(volatilita) * np.sqrt(12)
    
    max_dd = min(quote['max_dd'])
    
    
    
    
    
    
    #COLONNA QUOTE
    quote["quote"] = quote['movimento_netto'] / quote[quote.columns[0]]


    #COLONNA QUOTE CUMULATE
    quote["quote_cumulate"] = quote["quote"].cumsum()



    # COLONNA PMC
    indici = quote.index.tolist()

    quote['pmc'] = np.nan
    quote.at[indici[0], 'pmc'] = quote.loc[indici[0], quote.columns[0]]

    for i in range(1, len(quote)):
        prev_pmc = quote.at[indici[i - 1], 'pmc']
        prev_cum_quote = quote.at[indici[i - 1], 'quote_cumulate']
        curr_val_quota = quote.at[indici[i], quote.columns[0]]
        curr_quote = quote.at[indici[i], 'quote']
        curr_cum_quote = quote.at[indici[i], 'quote_cumulate']
        quote.at[indici[i], 'pmc'] = ((prev_pmc * prev_cum_quote) + (curr_val_quota * curr_quote)) / curr_cum_quote



    # Applico np.where per sostituire i valori di VAL_QUOTA con NaN quando Movimenti è 0
    quote['val_quota_filtrati'] = np.where(quote['movimenti'] != 0, quote[quote.columns[0]], np.nan)

    # Calcolo la media cumulativa, ignorando i NaN
    quote['prezzo_medio'] = quote['val_quota_filtrati'].expanding().mean()


    
    
    risultato = {
        "totale_rate_versate": totale_rate_versate,
        "patrimonio_finale": patrimonio_finale,
        "plus": plus,
        "mwrr": mwrr,
        "mwrr_annualizzato": mwrr_annualizzato,
        "volatilita_finale": volatilita_finale,
        "max_dd": max_dd,
        
        #salvo tutti i passaggi perchè servono per altri calcoli
        "calcoli": quote
    }
    
    
    return risultato






def CalcolaPerformancePortafolgio(dati_input):

    risultati_performance = dati_input["risultati_performance"]
    importo_totale_rate = dati_input["importo_totale_rate"]
    investimento_iniziale = dati_input["investimento_iniziale"]


    indici = risultati_performance[next(iter(risultati_performance))]["calcoli"].index
    colonne = ['movimenti', 'movimento_netto', 'ctv_lordo', 'ctv_netto']


    portafolgio = pd.DataFrame(columns=colonne, index=indici).fillna(0)



    for isin in risultati_performance:
        portafolgio["movimenti"] += risultati_performance[isin]["calcoli"]["movimenti"]
        portafolgio["movimento_netto"] += risultati_performance[isin]["calcoli"]["movimento_netto"]
        portafolgio["ctv_lordo"] += risultati_performance[isin]["calcoli"]["ctv_lordo"]
        portafolgio["ctv_netto"] += risultati_performance[isin]["calcoli"]["ctv_netto"]




    max_date = portafolgio.index.max()
    portafolgio['numeri'] = portafolgio['movimenti'] * (max_date - portafolgio.index).days
    
    
    
    totale_dovuto = importo_totale_rate + investimento_iniziale
    portafolgio['ctv_complessivo'] = portafolgio['ctv_netto'] + totale_dovuto - portafolgio['movimento_netto'].cumsum()
    
    
    portafolgio['vol'] = portafolgio['ctv_complessivo'].pct_change()
    
    
    
    portafolgio['max_dd'] = portafolgio['ctv_netto'] / portafolgio['movimento_netto'].cumsum() - 1
    
    
    
    
    volatilita = portafolgio['ctv_complessivo'].resample('M').last().pct_change()
    
    totale_rate_versate = sum(portafolgio['movimenti'])
    
    patrimonio_finale = portafolgio['ctv_netto'].iloc[-1]
    
    plus = patrimonio_finale - totale_rate_versate
    
    mwrr = plus / (sum(portafolgio['numeri']) / (portafolgio.index[-1] - portafolgio.index[0]).days)
    
    mwrr_annualizzato = ((1 + mwrr) ** (365 / (portafolgio.index[-1] - portafolgio.index[0]).days)) - 1
    
    volatilita_finale = np.std(volatilita) * np.sqrt(12)
    
    max_dd = min(portafolgio['max_dd'])
    
    
    
    
    #Dati per grafico portafolgio
    grafico = pd.DataFrame()
    grafico["ctv_netto"] = portafolgio['ctv_netto']
    grafico["movimenti"] = portafolgio["movimenti"].cumsum()
    

    risultato = {
        "totale_rate_versate": totale_rate_versate,
        "patrimonio_finale": patrimonio_finale,
        "plus": plus,
        "mwrr": mwrr,
        "mwrr_annualizzato": mwrr_annualizzato,
        "volatilita_finale": volatilita_finale,
        "max_dd": max_dd,
        "calcoli": portafolgio,
        
        #dati per grafico portafoglio
        "grafico": grafico
    }
    

    
    return risultato

#%% MOTORE

class Motore:
    def __init__(self):
        # Mappa la frequenza a un numero di mesi
        self.frequenze = {
            'Mensile': 1,
            'Bimestrale': 2,
            'Trimestrale': 3,
            'Quadrimestrale': 4,
            'Semestrale': 6,
            'Annuale': 12,
        }
    
    
    
    
    
    def EseguiAnalisi (self,input_motore):
        
        
        # isin selezionati e corrispettivo peso
        fondi = {
            
        }
        
        
        
        #ESTRAZIONE DATI RICEVUTI IN INPUT
        
        file_quote = input_motore['file_quote']
        file_costi = input_motore['file_costi']
        
        #estrazione dati input utente (tutti)
        frequenza =  input_motore['frequenza']
        importo_rata = input_motore['importo_rata']
        durata_anni = input_motore['durata_anni']
        giorno_del_mese = input_motore['giorno_mese']
        
       
        
        deroga = input_motore['deroga']
        
        #DEROGA
        if deroga == 'Nessuna':
            deroga_iniziale = 1
            deroga_totale = 1
        elif deroga == 'Iniziale 25%':
            deroga_iniziale = 0.75
            deroga_totale = 1
        elif deroga == 'Iniziale 50%':
            deroga_iniziale = 0.5
            deroga_totale = 1
        elif deroga == 'Iniziale 75%':
            deroga_iniziale = 0.25
            deroga_totale = 1
        elif deroga == 'Iniziale 100%':
            deroga_iniziale = 0
            deroga_totale = 1
        elif deroga == 'Totale 25%':
            deroga_iniziale = 1
            deroga_totale = 0.75
        elif deroga == 'Totale 50%':
            deroga_iniziale = 1
            deroga_totale = 0.5
        elif deroga == 'Totale 75%':
            deroga_iniziale = 1
            deroga_totale = 0.25
        elif deroga == 'Totale 100%':
            deroga_iniziale = 1
            deroga_totale = 0
        
        
        
    
        
        #i pesi dei fondi inseriti dall'utente sono stringhe
        #trasformo pesi dei fondi da stringhe in float
        for isin in input_motore["isin_selezionati"]:
            fondi[isin] = float(input_motore["isin_selezionati"][isin])
        
        
        
        num_mesi = self.frequenze[frequenza]
    
        numero_rate = (12 / num_mesi) * durata_anni
    
        importo_rata_mensile = (importo_rata * (12 / num_mesi) * durata_anni) / (durata_anni * 12)
    
        investimento_iniziale = importo_rata_mensile * 12
    
        #escluso versamento iniziale
        importo_totale_rate = numero_rate * importo_rata
    
    
    
        dati_input_costi = {
                #fondi selezionati con corrispettivo peso
                "fondi": fondi,
                
                #file con tutte le fasce di costo
                "file_costi": file_costi,
                
                #dati input utente
                'importo_rata_mensile': importo_rata_mensile,
                'importo_totale_rate':importo_totale_rate,
                'investimento_iniziale': investimento_iniziale
        }
        
        
        #calcola costi
        costi = calcola_costi(dati_input_costi)
        
        print("COSTI")
        print(costi)
        
    
        
        #prima di calcolare performance controlla importo rata minima
        #se non rispettato chiudi
        if costi == "ERRORE RATA MENSILE":
            return "ERRORE RATA MENSILE"
        elif costi == "ERRORE IMPORTO MINIMO":
            return "ERRORE IMPORTO MINIMO"
        
        
        # se sono arrivato qua tutto apposto con le rate    
        
        
        
        #salvo le performance per ogni fondo selezionato
        #serviranno per il calcolo performance portafolgio e per le varie tabs
        risultati_performance = {}
    
    
        #per ogni fondo selezionato estraggo le quote e peso nel portafolgio
        for isin in fondi:
            quote = file_quote[isin]
            peso = fondi[isin]
            
            
            dati_input_performance = {
                
                #serie storica
                "quote" : quote,
                
                #quanto pesa nel portafolgio
                "peso" : peso,
                
                #costi
                "costi_sottoscrizione" : costi["costi_sottoscrizione"],
                "diritti_fissi_iniziali" : costi["diritti_fissi_iniziali"],
                "diritti_fissi" : costi["diritti_fissi"],
                
                #sconti
                "deroga_totale" : deroga_totale,
                "deroga_iniziale" : deroga_iniziale,
                "num_mesi" : num_mesi,
                
                #informazioni rata
                "giorno_del_mese" : giorno_del_mese,
                "numero_rate" : numero_rate,
                "importo_rata" : importo_rata,
                "durata_anni": durata_anni
                
            }
            
            
            
            #calcolo le performance del fondo
            
            risultati_performance[isin] = calcola_performance(dati_input_performance)
            
            
        
        
        #dati input per calcolo performance portafolgio
        dati_input_portafolgio = {
            
            "risultati_performance": risultati_performance,
            "importo_totale_rate": importo_totale_rate,
            "investimento_iniziale": investimento_iniziale,
        }
        
        
        # contiene tutti i dati elaborati del portafolgio
        elaborazione = CalcolaPerformancePortafolgio(dati_input_portafolgio)
        
        
    
        
        #SALVO CALCOLI SU EXCEL
        #ELIMINARE DOPO
        # with pd.ExcelWriter('test/output.xlsx') as writer:  
        #     for isin in fondi:
        #         temp_excel = risultati_performance[isin]['calcoli'].copy()
        #         temp_excel.replace(0, np.nan, inplace=True)
        #         temp_excel.to_excel(writer, sheet_name=isin)
                
                
        #     temp_excel = elaborazione['calcoli'].copy()
        #     temp_excel.replace(0, np.nan, inplace=True)
        #     temp_excel.to_excel(writer, sheet_name="PORTAFOLGIO")
            
    
        
    
        
        #contiene tutti i dati necessari per tutti i componenti
        risultato_motore = {
            
            #dati portafolgio
            "portafoglio": elaborazione,
            
            #dati singoli fondi
            "singoli_fondi": risultati_performance
        }
        
            
        
        return risultato_motore
    
    


#%% FUNZIONI PER DASHBOARD


#Controlla che la somma dei pesi sia 100
def controlloSommaPesi(pesi):
    
    somma_pesi = 0
    
    try:
        for isin in pesi:
            somma_pesi += int(pesi[isin])
    
    except:
        return False
    
    if(somma_pesi != 100):
        return False
    
    return True



#%% LETTURA FILE EXCEL

#decodifiche FONDO - Prodotto
file_codifiche_prodotto = pd.read_excel(url+"excel/codifiche.xlsx", index_col=0)
SGR = file_codifiche_prodotto['FAMIGLIA'].unique()


#lettura quote
file_quote = pd.read_excel(url+"excel/DB_TOT_PROXY.xlsx", index_col=0)
file_quote.index = pd.to_datetime(file_quote.index, format='%d/%m/%Y')



#lettura file costi
file_costi = pd.read_excel(url+'excel/costi.xlsx', index_col=0)



#%% VALORI CHE POPOLANO I VARI COMPONENTI



#FONDI E PRODOTTI PER MULTIDROPDOWN
df_options = pd.DataFrame({
    'OptionID': SGR,
    'OptionLabel': SGR,
})

df_suboptions = pd.DataFrame({
    'OptionID': file_codifiche_prodotto['FAMIGLIA'],
    'SubOptionLabel': file_codifiche_prodotto['NOME'],
    'SubOptionValue': file_codifiche_prodotto.index,
})

basic_options = {}
for _, row in df_options.iterrows():
    option_id = row['OptionID']
    option_label = row['OptionLabel']
    suboptions = df_suboptions[df_suboptions['OptionID'] == option_id]
    basic_options[option_label] = [{'label': r['SubOptionLabel'], 'value': r['SubOptionValue']} for _, r in suboptions.iterrows()]





#DATE INIZIO SIMULAZIONE

data_inizio_simulazione = file_quote.index.strftime('%d/%m/%Y')




#FREQUENZE
frequenze = {
    'Mensile': 'Mensile',
    'Bimestrale': 'Bimestrale',
    'Trimestrale': 'Trimestrale',
    'Quadrimestrale': 'Quadrimestrale',
    'Semestrale': 'Semestrale',
    'Annuale': 'Annuale'
}




#DEROGHE
selezione_deroga = {
    'Nessuna': 'Nessuna',
    'Iniziale 25%': 'Iniziale 25%',
    'Iniziale 50%': 'Iniziale 50%',
    'Iniziale 75%': 'Iniziale 75%',
    'Iniziale 100%': 'Iniziale 75%',
    'Totale 25%': 'Totale 25%',
    'Totale 50%': 'Totale 50%',
    'Totale 75%': 'Totale 75%',
    'Totale 100%': 'Totale 100%',
}




#%% DASHBOARD

external_stylesheets = [
    'https://raw.githubusercontent.com/TurcanuDionisie/Dashboard_ER/main/assets/style.css',
    dbc.themes.BOOTSTRAP
]

app = dash.Dash(__name__, title ='Tool PAC', external_stylesheets=external_stylesheets)

server = app.server

app.index_string = '''
    <!DOCTYPE html>
    <html>
        <head>           
            <link rel="shortcut icon" href="https://raw.githubusercontent.com/marzowill96/Monitoraggio_Analisi_Performance/main/favicon.ico"  type="image/x-icon">
            {%metas%}
            <title>{%title%}</title>
            {%favicon%}
            {%css%}
        </head>
        <body>
            {%app_entry%}
            <footer>
                {%config%}
                {%scripts%}
                {%renderer%}
            </footer>
        </body>
    </html>
'''




app.layout = html.Div(className="container", children=[
    

    html.Div(className="row intestazione", children=[
        # Colonna per l'immagine
        html.Div(className="col-5 d-flex align-items-center justify-content-end logo", children=[
            html.Img(src='assets/logo.png')  # Aggiungi qui l'immagine
        ]),
        # Colonna per il titolo
        html.Div(className="col-7 d-flex align-items-center titolo", children=[
            html.H1('Dashboard Piano PAC', style={'textAlign': 'left'})  # Il titolo
        ])
    ]),


    

    #INPUT FORM
    html.Div(className="row sezione", children=[
        
        # Prima colonna
        html.Div(className="col-6", children=[
            html.Div(className="input-group", children=[
                html.Div(className="col-4", children=html.P("Data Inizio:", className="label text-right")),
                html.Div(className="col-8", children=dcc.Dropdown(
                    id='data-inizio',
                    options=[{'label': str(date), 'value': str(date)} for date in data_inizio_simulazione],
                    value=None
                ))
            ]),
            html.Div(className="input-group", children=[
                html.Div(className="col-4", children=html.P("Importo Rata:", className="label text-right")),
                html.Div(className="col-8", children=dbc.InputGroup([
                    dcc.Input(
                        id='importo-rata',
                        type='text',
                        value=None,
                        placeholder='Importo rata',
                        className='input-form form-control'
                    ),
                    dbc.InputGroupText("€")
                ], className='input-group'))
                
                
            ]),
            html.Div(className="input-group", children=[
                html.Div(className="col-4", children=html.P("Frequenza:", className="label text-right")),
                html.Div(className="col-8", children=dcc.Dropdown(
                    id='frequenza', 
                    options=[{'label': label, 'value': value} for label, value in frequenze.items()],
                    value='Mensile',
                ))
            ]),
            html.Div(className="input-group", children=[
                html.Div(className="col-4", children=html.P("Durata:", className="label text-right")),
                html.Div(className="col-8", children=dcc.Dropdown(
                    id='durata', 
                    options=[
                            {'label': '10 Anni', 'value': '10'},
                            {'label': '15 Anni', 'value': '15'},
                        ],
                    value='10',
                ))
            ]),
            html.Div(className="input-group", children=[
                html.Div(className="col-4", children=html.P("Deroga:", className="label text-right")),
                html.Div(className="col-8", children=dcc.Dropdown(
                    id='deroga',
                    options=[{'label': str(deroga), 'value': str(deroga)} for deroga in selezione_deroga],
                    value='Nessuna'
                ))
            ]),
            html.Div(className="input-group", children=[
                html.Div(className="col-4", children=html.P("Giorno Versamento:", className="label text-right")),
                html.Div(className="col-8", children=dcc.Dropdown(
                    id='giorno_versamento', 
                    options=[
                            {'label': '8', 'value': '8'},
                            {'label': '28', 'value': '28'},
                        ],
                    value='8',
                ))
            ]),
            html.Div(className="input-group", children=[
                html.Div(className="col-4", children=html.P("Prodotto:", className="label text-right")),
                html.Div(className="col-8", children=dcc.Dropdown(
                    id='basic-dropdown',
                    options=[{'label': key, 'value': key} for key in basic_options.keys()],
                    value='MBB',
                ))
            ]),
            html.Div(className="input-group", children=[
                html.Div(className="col-4", children=html.P("Fondo Comume:", className="label text-right")),
                html.Div(className="col-8", children=dcc.Dropdown(
                    id='multi-dropdown',
                    value=None,
                    multi=True
                ))
            ]),
            
            
            html.Div(className="input-group", children=[
                html.Div(className="col-4"),
                html.Div(className="col-8", children=html.Button('Calcola', id='calcola', n_clicks=0, className="btn btn-primary btn-lg btn-block"))
            ]),
            
            
            
            
        ]),
        # Seconda colonna
        html.Div(className="col-6", children=[
            html.Div(id='table-title'),
            html.Table(id='my-table', children=[])
        ]),
    ]),
    
    
    
    
    #MESSAGGIO ERRORE
    html.Div(className="row", children=[
        
        html.H4(id='error-message', className="messaggio-errore")
        
        
    ]),
    
    
    
    
    #GRAFICO SIMULAZIONE
    html.Div(className="row sezione", children=[
        
        html.H3('Grafico della simulazione', style={'text-align': 'center', 'width': '100%'}),
        dcc.Graph(id='result-graph'),
        
    ]),
    
    
    
    
    #TABELLA PERFORMANCE E GRAFICO A TORTA
    html.Div(className="row align-vertical sezione", children=[
        
        html.H3('Valori alla data finale della simulazione', style={'text-align': 'center', 'width': '100%'}),
            
        html.Div(className="col-6 align-vertical", children=[
            html.Div(id='table-div', style={'width': '100%'}),
        ]),
        
        html.Div(className="col-6 align-vertical", children=[
           dcc.Graph(id='pie-chart'),
        ]),
        
    ]),

    
   
    
    
    #TABS CON I VARI GRAFICI
    html.Div(className="row sezione", children=[
        dcc.Tabs(id="my-tabs"),
        
    ]),
    
    
    #TABS CON I VARI GRAFICI DCA
    html.Div(className="row sezione", children=[
        dcc.Tabs(id="my-tabs-DCA"),
        
    ]),
    


    

    #COMPONENTI CHE CONSERVANO I PESI
    html.Div(children=html.Div(id='dummy-output')),  # dummy component used for button callback
    html.Div(children=dcc.Store(id='store-inputs', data={})),  # storage component to store input values
    
])




# %% CALLBACKS


# GESTISCE I DUE DROPDOWN
@app.callback(
    Output('store-inputs', 'data'),
    [Input({'type': 'dynamic-input', 'index': ALL}, 'value')],
    [Input({'type': 'dynamic-input', 'index': ALL}, 'id'),
     Input('store-inputs', 'data')]
)
def update_store(input_values, input_ids, data):
    data = {id['index']: value for value, id in zip(input_values, input_ids)}
    return data

@app.callback(
    Output('multi-dropdown', 'options'),
    Output('multi-dropdown', 'value'),
    [Input('basic-dropdown', 'value')]
)
def update_multi_dropdown(selected_value):
    return basic_options.get(selected_value, []), []




#TITOLO TABELLA DEI PESI
@app.callback(
    Output('table-title', 'children'),
    [Input('my-table', 'children')]
)
def update_title(table_children):
    if table_children:  # if the table is not empty
        return html.H4('Inserisci Peso Percentuale')
    else:
        return "" 


#TABELLA DINAMICA CON I PESI
@app.callback(
    Output('my-table', 'children'),
    [Input('multi-dropdown', 'value'),
     Input('store-inputs', 'data')]
)
def update_table(selected_values, data):
    if selected_values is None or len(selected_values) == 0:
        return []
    else:
        rows = []
        for i, value in enumerate(selected_values):
            row = html.Tr(children=[
                html.Td(className='col', children=dbc.InputGroup([
                    dcc.Input(
                        value=data.get(value, ""),
                        id={'type': 'dynamic-input', 'index': value},
                        type='text',
                        className='form-control input-form-pesi'
                    ),
                    dbc.InputGroupText("%")
                ], className='input-group')),
                html.Td(className='col-8 peso-isin', children= file_codifiche_prodotto['NOME'].loc[value]),
            ])
            rows.append(row)
        return rows
    
    


#MOTORE
@app.callback(
    [Output('result-graph', 'figure'),
     Output('dummy-output', 'children'),
     Output('error-message', 'children'),
     Output('table-div', 'children'),
     Output('pie-chart', 'figure'),
     Output('my-tabs', 'children'),
     Output('my-tabs-DCA', 'children')],
    [Input('calcola', 'n_clicks'),
     Input('data-inizio', 'value'),
     Input('importo-rata', 'value'),
     Input('frequenza', 'value'),
     Input('durata', 'value'),
     Input('deroga', 'value'),
     Input('giorno_versamento', 'value'),
     
     #isin selezionati (solo isin)
     Input('multi-dropdown', 'value'),
     
     #dizionario dove ad ogni isin è associato il peso
     Input('store-inputs', 'data')
     ],
)
def print_input_values(n_clicks, data_inizio, importo_rata, frequenza, durata, deroga, giorno_versamento, isin_selezionati, isin_peso):
    
    
    
    message = ""
    fig = {}
    table = {}
    pie_chart = {}
    tabs = {}
    tabs_DCA = {}
    

    
    if n_clicks <= 0:
        return fig, None, message, table, pie_chart, tabs
        
    
    #controlla che i campi in input siano tutti compilati
    if data_inizio is None or importo_rata is None or frequenza is None or durata is None or deroga is None or giorno_versamento is None or (len(isin_selezionati) == 0) or (len(isin_peso) == 0):
        message = "Attenzione, non hai compilato tutti i campi"
        return fig, None, message, table, pie_chart, tabs
    
    
        
    #controlla che la somma dei pesi sia 100
    #ritorna false se l'utente non inserisce un numero valido
    if(controlloSommaPesi(isin_peso) == False):
        message = "Attenzione, la somma dei pesi non è 100"
        return fig, None, message, table, pie_chart, tabs
        
    
    
    

        
        
    # estrae e formatta input inseriti dall'utente   
    try:
        
        input_utente = {
            "isin_selezionati": isin_peso,
            "importo_rata": int(importo_rata),
            "frequenza": frequenza,
            "durata_anni": int(durata),
            "giorno_mese": int(giorno_versamento),
            "deroga": deroga,
            
            #dati letti da excel
            "file_quote": file_quote[file_quote.index >= pd.to_datetime(data_inizio, format='%d/%m/%Y')],
            "file_costi": file_costi
            
        }
        
        
    except:
        message = "Attenzione, errore in un campo in input"
        return fig, None, message, table, pie_chart, tabs
    
    
    
    #passo tutti gli input utente al motore
    motore = Motore()
    risultati = motore.EseguiAnalisi(input_utente)
    
    
    
    #controlla validità importo minimo rate
    if(risultati == "ERRORE RATA MENSILE"):
        message = "Attenzione, l'importo della rata è troppo piccolo"
        return fig, None, message, table, pie_chart, tabs
    elif(risultati == "ERRORE IMPORTO MINIMO"):
        message = "Attenzione, l'importo minimo su uno dei fondi è troppo piccolo"
        return fig, None, message, table, pie_chart, tabs
    
    

        
    #GRAFICO GRANDE CON LE PERFORMANCE
    grafico_ptf = risultati["portafoglio"]["grafico"]

    grafico_ptf = pd.DataFrame({
        'x': grafico_ptf.index,
        'y1': grafico_ptf["ctv_netto"],
        'y2': grafico_ptf["movimenti"]
    })

    df_bar = grafico_ptf.iloc[::10, :]



    # VECCHIA VERSIONE DEL GRAFICO
    # fig = {
    #     'data': [
    #         go.Scatter(  # linea
    #             x=grafico_ptf['x'],
    #             y=grafico_ptf['y1'],
    #             mode='lines',
    #             name='Controvalore Netto',
    #             hovertemplate='%{y:.2f}',  # add this line
    #         ),
    #         go.Bar(  # barre
    #             x=df_bar['x'],
    #             y=df_bar['y2'],
    #             name='Importo Versato',
    #             width=3,
    #             hovertemplate='%{y:.2f}',  # add this line
    #         )
    #     ],
    #     'layout': go.Layout(
    #         title='Grafico della simulazione',
    #         title_font=dict(
    #         size=25,
    #         family="Verdana, bold"
    #     ),
    #         yaxis={'title': 'Valore'}
    #     )
    # }
    
    
    
    
    fig = {
        'data': [
            go.Scatter(  # linea
                x=grafico_ptf['x'],
                y=grafico_ptf['y1'],
                mode='lines',
                name='Controvalore Netto',
                hovertemplate='%{y:.2f}', 
                line=dict(color='#002060') 
            ),
            go.Bar(  # barre
                x=df_bar['x'],
                y=df_bar['y2'],
                name='Importo Versato',
                width=3,
                hovertemplate='%{y:.2f}', 
                marker=dict(color='#86cbe7')
            )
        ],
        'layout': go.Layout(
        yaxis={
            'title': 'Valore',
            'titlefont': {'size': 15, 'color': '#002060', 'family': 'Verdana'},
            'tickfont': {'size': 12, 'color': '#002060', 'family': 'Verdana'}
        },
        xaxis={
            'titlefont': {'size': 15, 'color': '#002060', 'family': 'Verdana'},
            'tickfont': {'size': 12, 'color': '#002060', 'family': 'Verdana'}
        },
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5,
            font=dict(size=15, color="#002060", family="Verdana")
        ),
        margin=dict(l=50, r=20, t=20, b=20)
    )
}






    
    #DATI DA METTERE NELLA TABELLA DELLE PERFORMANCE
    
    # Mappa la frequenza a un numero di mesi
    codifica_mesi = {
        'Mensile': 1,
        'Bimestrale': 2,
        'Trimestrale': 3,
        'Quadrimestrale': 4,
        'Semestrale': 6,
        'Annuale': 12,
    }
    
    num_mesi = codifica_mesi[frequenza]
    numero_rate = (12 / num_mesi) * int(durata)
    
    
    #LE CHIAVI SONO I TITOLI DELLA TABELLA
    dati_tabella_perf = {
        
        "Frequenza Rate": frequenza,
        "Numero Rate": numero_rate,
        "Importo Rata": "{:,}".format(int(importo_rata)).replace(",", ".") + "€",
        "Totale Rate Versate": "{:,}".format(int(risultati["portafoglio"]["totale_rate_versate"])).replace(",", ".") + "€",
        "Patrimonio Finale": "{:,}".format(int(risultati["portafoglio"]["patrimonio_finale"])).replace(",", ".") + "€",
        "Plus/Minus": "{:,}".format(int(risultati["portafoglio"]["plus"])).replace(",", ".") + "€",
        "MWRR Totale": "{:,.2f}".format(round(risultati["portafoglio"]["mwrr"] * 100 ,2)).replace(".", ",") + "%",
        "MWRR Annualizzato": "{:,.2f}".format(round(risultati["portafoglio"]["mwrr_annualizzato"] * 100 ,2)).replace(".", ",") + "%",
        "Volatilita": "{:,.2f}".format(round(risultati["portafoglio"]["volatilita_finale"] * 100 ,2)).replace(".", ",") + "%",
        "Max DD": "{:,.2f}".format(round(risultati["portafoglio"]["max_dd"] * 100 ,2)).replace(".", ",") + "%",
        
    }
    
    #TABELLA DELLE PERFORMANCE
    table = html.Table(className='my-table', style={'width': '100%'}, children=[
        html.Tbody([
            html.Tr([
                html.Div(className='row', children=[
                    html.Div(className='col-6 d-flex justify-content-end', children=[
                        html.Th(col)
                    ]),
                    html.Div(className='col-6 d-flex justify-content-center', children=[
                        html.Td(dati_tabella_perf[col])
                    ])
                ])
            ]) for col in dati_tabella_perf.keys()
        ])
    ])

    
    

    
    #GRAFICO A TORTA
    pie_chart = go.Figure()
    
    labels = ["Versato", "Contributo Mercato"]
    values = [risultati["portafoglio"]["totale_rate_versate"], (risultati["portafoglio"]["patrimonio_finale"] - risultati["portafoglio"]["totale_rate_versate"])]
    
    pie_chart.add_trace(go.Pie(
        labels=labels, 
        values=values,
        marker=dict(colors=['#3568a1', '#6fbfe1']),  # Imposta i colori delle fette
        textinfo='percent',  # Mostra solo le percentuali
        insidetextfont=dict(size=16, color='white'),  # Imposta dimensione e colore del testo
        hoverinfo='label+value+percent'  # Informazioni mostrate al passaggio del mouse
    ))
    
    
    
    
    
    #TABS CON I VARI GRAFICI
    if isin_selezionati is None or len(isin_selezionati) == 0:
        return []
    else:
        tabs = []
        for i, value in enumerate(isin_selezionati):
            
            # value = isin del fondo
                                     
            x_values = risultati["singoli_fondi"][value]["calcoli"].index
            y_values1 = risultati["singoli_fondi"][value]["calcoli"][value]
            y_values2 = risultati["singoli_fondi"][value]["calcoli"]["pmc"]
            y_values3 = risultati["singoli_fondi"][value]["calcoli"]["prezzo_medio"]
            
            
            trace1 = trace1 = go.Scatter(
                x=x_values, 
                y=y_values1, 
                mode='lines', 
                name='Prezzo',
                line=dict(color='#002060')  # Imposta il colore della linea
            )
            trace2 = go.Scatter(x=x_values, y=y_values2, mode='lines', name='PMC')
            trace3 = go.Scatter(x=x_values, y=y_values3, mode='lines', name='Prezzo medio')
            
            data = [trace1, trace2, trace3]
            
            
            tab = dcc.Tab(label=file_codifiche_prodotto['NOME'].loc[value], children=[
                
                dcc.Graph(
                    id={'type': 'dynamic-graph', 'index': value},
                    figure={'data': data, 
                           }
                )
            ])
            
            tabs.append(tab)
            
            
            
            
            #TABS CON I VARI GRAFICI
            if isin_selezionati is None or len(isin_selezionati) == 0:
                return []
            else:
                tabs_DCA = []
                for i, value in enumerate(isin_selezionati):
                    
                    # value = isin del fondo
                                             
                    x_values = risultati["singoli_fondi"][value]["calcoli"].index
                    y_values1 = risultati["singoli_fondi"][value]["calcoli"]["pmc"] / risultati["singoli_fondi"][value]["calcoli"]["prezzo_medio"] - 1

                                        
                    trace1 = trace1 = go.Scatter(
                        x=x_values, 
                        y=y_values1, 
                        mode='lines', 
                        name='Dollar Cost Averaging',
                        line=dict(color='#002060')  # Imposta il colore della linea
                    )

                    
                    data = [trace1]
                    
                    
                    tab = dcc.Tab(label=file_codifiche_prodotto['NOME'].loc[value], children=[
                        
                        dcc.Graph(
                            id={'type': 'dynamic-graph', 'index': value},
                            figure={'data': data, 
                                   }
                        )
                    ])
                    
                    tabs_DCA.append(tab)
 

    return fig, None, message, table, pie_chart, tabs, tabs_DCA




if __name__ == '__main__':
    app.run_server()


