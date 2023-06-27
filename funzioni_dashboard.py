

def controlloSommaPesi(pesi):
    
    somma_pesi = 0
    
    try:
        for isin in pesi:
            somma_pesi += int(pesi[isin])
    
    except:
        return False
    
    
    if(somma_pesi < 100 | somma_pesi > 100):
        return False
    
    return True


