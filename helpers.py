 
import tabula
import numpy as np
import pandas as pd

def cleanup_trainschedule(df):
    df = df.astype(str)
    df = df.replace('\.', ':', regex=True)
    df = df.replace('–', np.NaN)
    df = df.astype(str)
    for col in df.columns: # remove unwanted characters
        df[col] = df[col].str.replace('[^0-9:]', '', regex=True) # Removes non numeric characters or :
        df[col] = df[col].str.replace(r'(:\d)$', r'\g<1>0', regex=True) # Adds missing 0 at the end of a time
    df = df.replace('', np.NaN)
    #df = df.replace('nan', np.NaN)
    return df

# Definim una funció que converteix una hora en minuts
def hora_a_minuts(hora):
    h, m = hora.split(":")
    return int(h) * 60 + int(m)

def hora_a_segons(hora):
    if hora.count(":") == 1:
        h, m = hora.split(":")
        s = 0
    else:
        h, m, s = hora.split(":")
    return int(h) * 3600 + int(m) * 60 + int(s)

def busca_estacions(df, hora, row, inverse=False):
    train = df.iloc[row]

    # If the row is empty (train doesn't stop), skip it
    if train.isna().all():
        return f"Train {row} does not stop."
    
    # Convert the time to seconds
    segons = hora_a_segons(hora)

    firsttrain = train.loc[train.first_valid_index()]
    lasttrain = train.loc[train.last_valid_index()]

    seg_firsttrain = hora_a_segons(firsttrain)
    seg_lasttrain = hora_a_segons(lasttrain)
    
    # si el tren acaba al dia seguent, sumar els segons del dia abans (sino, es trenca tot)
    if seg_lasttrain < seg_firsttrain:
        seg_lasttrain += 86400

    # Si la hora no està entre l'inici i el final d'un tren, aquell tren no està circulant
    if (segons < seg_firsttrain and segons < seg_lasttrain) or (segons > seg_firsttrain and segons > seg_lasttrain):
        return -1
    
    # Recorrem les columnes del dataframe fins trobar la primera que té una hora major o igual a la donada
    for i in range(len(train)):
        # If value is Nan, skip cell
        if pd.isna(train[i]):
            continue
        else:
            # For each station, check if the departure time is larger than the specified hour, and stop there.
            if hora_a_segons(train[i]) >= segons:
                break
    
    # Si hem trobat la primera columna amb una hora major o igual a la donada, comprovem si és exactament igual o no
    if train[i] == hora:
        # Si és exactament igual, vol dir que el tren està en aquesta estació
        print(f"El tren {row} està aturat a l'estació de {train.index[i]} ({i}) a les {hora}.")
        return i
    
    # Si no és exactament igual, vol dir que el tren està entre aquesta estació i l'anterior
    # Compute the % of the route between the two stations
    
    # If the train didn't stop at the previous station, we need to get the time of the last actual stop.
    previousstop = train[i-1]
    j = 1
    while pd.isna(previousstop):
        j +=1
        previousstop = train[i-j]

    secondsdifference = hora_a_segons(train[i]) - hora_a_segons(previousstop)
    secondscurrent = segons - hora_a_segons(previousstop)
    routepercent = round(secondscurrent / secondsdifference, 2)
    print(f"El tren {row} està entre les estacions de {train.index[i-j]} i {train.index[i]} ({(i-j)+routepercent*j}) a les {hora}.")
    if inverse == False:
        return (i-j)+routepercent*j
    elif inverse == True: # invert the value ((number of stations-1) - fraction of the route)
        return (len(train)-1)-((i-j)+routepercent*j)



def find_alltrains(df, hora, inverse=False):

    # Drop empty columns (stations where no train stops)
    #df = df.dropna(axis=1, how='all')

    # Insert some random nans, to add more complexity
    for col in df.columns:
        df.loc[df.sample(frac=0.0).index, col] = np.nan

    #display(df)
    positions = []
    for row in range(0,len(df)):
        positions.append(busca_estacions(df, hora, row, inverse))
        
    # Remove non-valid positions (-1)
    positions = list(filter(lambda x: x != -1, positions))
    return positions

