 
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



# Filters out trains whose first stop is not between two hours
from datetime import datetime, timedelta
import pandas as pd

def filter_interval(df, beginning, end):
    # Fill NaN values with previous non-NaN value, assuming that the DataFrame is sorted by time
    df.iloc[:, 0].fillna(method='ffill', inplace=True)


    # If the first value is NaN, copy the next non-NaN value and subtract one minute
    if pd.isna(df.iloc[0, 0]):
        next_nonnan = df.iloc[:, 0].dropna().iloc[0]
        next_nonnan = datetime.strptime(next_nonnan, '%H:%M') - timedelta(minutes=1)
        df.iloc[0, 0] = next_nonnan.strftime('%H:%M')

    # Convert the beginning and end times to datetime objects
    beginning_time = datetime.strptime(beginning, '%H:%M')
    end_time = datetime.strptime(end, '%H:%M')

    # If the end time is earlier than the beginning time, add 1 day to the end time
    if end_time <= beginning_time:
        end_time += timedelta(days=1)

    # Define a lambda function to convert a time string to a datetime object
    to_datetime = lambda x: datetime.strptime(x, '%H:%M') + timedelta(days=1) if int(x[:2]) < 4 else datetime.strptime(x, '%H:%M') # If the hour is less than 4(am), assume it's referring to the next day

    # Apply the to_datetime function to the first column of the DataFrame
    times = df.iloc[:, 0].apply(to_datetime)

    # Filter the DataFrame based on the time interval
    mask = (times >= beginning_time) & (times <= end_time)
    filtered_df = df[mask]
    filtered_df = filtered_df.sort_values(by=filtered_df.columns[0], key=lambda x: pd.to_datetime(x, format='%H:%M'))
    filtered_df.iloc[filtered_df.iloc[:, 1].isna(), 0] = np.nan # Remove the placeholders to filter out the times in the first column. This is an ugly workaround...
    return filtered_df


# Controls the cases when, if a time goes from 23:50 to 23:02, correct to 00:02
def fix_time_discontinuity(df):
    for i in range(len(df)):
        prev_hour, prev_minute = None, None
        hour_offset = 0
        for j in range(len(df.columns)):
            current_time = df.iloc[i, j]
            if pd.isna(current_time):
                continue
            current_hour, current_minute = map(int, current_time.split(":"))
            if prev_hour is not None:
                if current_minute < prev_minute:
                    hour_offset += 1 if current_minute - prev_minute < 0 else 0
            current_hour += hour_offset
            current_hour %= 24
            prev_hour, prev_minute = current_hour, current_minute
            df.iloc[i, j] = f"{current_hour:02d}:{current_minute:02d}"
    return df


# For those schedules that only show the minutes, add the hours (h_values) (e.g. S2 and S6 schedules)
def generate_hours(df, h_values): 
    def add_zero(x): # Adds 0 to values, like 12:5 -> 12:50
        return x if x == 'nan' else (x if len(x) == 5 else x + '0')

    dfs = []
    for h in h_values:
        df_temp = df.astype(str)
        df_temp = df_temp.replace('0\.', f'{h}:', regex=True)
        df_temp = cleanup_trainschedule(df_temp)
        #df_temp = df_temp.applymap(add_zero) # cleanup_trainschedule(0) already does that
        #df_temp = df_temp.replace('nan', np.nan)
        dfs.append(df_temp)
        
    return pd.concat(dfs, axis=0, ignore_index=True)