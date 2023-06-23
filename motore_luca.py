import pandas as pd
import numpy as np
import os


folder_path = r"C:\Users\Dionisie.Turcanu\Documents\GitHub\Dashboard_PAC"
os.chdir(folder_path)

quote = pd.read_excel('DB_TOT_PROXY.xlsx', index_col=0)

quote = quote["IE0004878744"]



# giorno in cui parte la rata è sempre un 8/28 di ogni mese. Se il giorno in cui deve partire la rata è un festivo, la rata parte il primo giorno lavorativo disponibile

# frequenza: mensile, bimestrale, trimestrale, quadrimestrale, semestrale, annuale

#le prime 12 rate vengono pagate il giorno della sottoscrizione, pago tutto subito

# il primo giorno utile 8/28 faccio partire la rata e la successiva la faccio partire a seconda della cadenza che ha scelto
# se è il giorno stesso allora la faccio partire dal mese dopo il primo giorno dispobibile


#sto parlando dei costi di sottoscrizione che pago sul totale (iniziale + rate)
# il 33% dei costi lo pago sul primo versamento
# il 19% sulle successive 6 rate e 48% su tutto il resto
# di 26k il 3% sono 792 di costi che si ripartono come scritto
#con la deroga totale sconto tutti e 3 le ripartizioni
#con la deroga iniziale sconto solo il 33% sul primo versamento


# %% PARAMETRI

numero_rate = 120

importo_rata = 200

#escluso versamento iniziale
importo_totale = numero_rate * importo_rata

investimento_iniziale = importo_rata * 12


costo_sottoscrizione = 0.03


diritto_fisso = 0.024


# %% MOVIMENTI

type(quote.index[0])


giorno_del_mese = 8  # Scegli tra 8 e 28
frequenza = 'Mensile'  # Scegli tra: 'Mensile', 'Bimestrale', 'Trimestrale', 'Quadrimestrale', 'Semestrale', 'Annuale'

# Mappa la frequenza a un numero di mesi
frequenze = {
    'Mensile': 1,
    'Bimestrale': 2,
    'Trimestrale': 3,
    'Quadrimestrale': 4,
    'Semestrale': 6,
    'Annuale': 12,
}

num_mesi = frequenze[frequenza]

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



importo_costo_sottoscrizione = costo_sottoscrizione * (importo_totale + investimento_iniziale)

prima_fetta = importo_costo_sottoscrizione * 0.33
seconda_fetta = importo_costo_sottoscrizione * 0.19
terza_fetta = importo_costo_sottoscrizione * 0.48


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
diritto_fisso_iniziale = 2.4
diritto_fisso = 1.54

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



totale_dovuto = importo_totale + investimento_iniziale


# Calcola 'CTV Complessivo'
quote['CTV Complessivo'] = quote['CTV_NETTO'] + totale_dovuto - quote['MOVIMENTO_NETTO'].cumsum()



# %%

quote['VOL'] = quote['CTV Complessivo'].pct_change()


# %%

quote['MAX DD'] = quote['CTV_NETTO'] / quote['MOVIMENTO_NETTO'].cumsum() - 1


# %%


volatilita = quote['CTV Complessivo'].resample('M').last().pct_change()

# quote.to_excel('prova.xlsx', index=True)

## %% 


numero_rate

importo_rata

totale_rate_versate = sum(quote['Movimenti'])

patrimonio_finale = quote['CTV_NETTO'].iloc[-1]


plus = patrimonio_finale - totale_rate_versate


mwrr = plus / (sum(quote['Numeri']) / (quote.index[-1] - quote.index[0]).days)


mwrr_annualizzato = ((1 + mwrr) ** (365 / (quote.index[-1] - quote.index[0]).days)) - 1


volatilita_finale = np.std(volatilita) * np.sqrt(12)


max_dd = min(quote['MAX DD'])

