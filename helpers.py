 
import tabula
import numpy as np
import pandas as pd

# When importing schedules from PDF files, they might contain invalid characters or other formatting issues, this function does the cleanup.
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

# Converts hh:mm or hh:mm:ss to seconds
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

# Some schedules contain hours that go beyond 23:59 (e.g. 24, 25, 26.. hours into 00, 01, 02...)
def convert_24_to_00(time):
    if time.count(":") == 1:
        h, m = time.split(":")
        s = 0
    else:
        h, m, s = time.split(":")
    seconds = int(h) * 3600 + int(m) * 60 + int(s)
    hours, remainder = divmod(seconds, 3600)
    if hours >= 24:
        hours = hours % 24
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

# Main function that returns the position of a train according to a schedule.
def busca_estacions_multiday(df, time, row, inverse=False):
    #print(f"Finding train {row} at {time}")
    train = df.iloc[row]

    # Get the times of the first and last stops
    firsttrain = train.loc[train.first_valid_index()]
    lasttrain = train.loc[train.last_valid_index()]

    # Convert times to seconds
    seg_firsttrain = hora_a_segons(firsttrain)
    seg_lasttrain = hora_a_segons(lasttrain)

    # First, check if it's a multiday trip (end of the trip is beyond 23:59)
    def is_multiday():
        if seg_lasttrain < seg_firsttrain:
            return True
        return False

    #Checks if, in a multiday trip, the time already corresponds to the next day
    def is_trip_nextday(train, time):
        time_seconds = hora_a_segons(time)
        time_laststop = train.loc[train.last_valid_index()]
        if (time_seconds >= hora_a_segons("00:00")) and (time_seconds < hora_a_segons(time_laststop)):
            return True
        return False

    # Checks if the train is currently circulating
    def is_circulating(time_seconds):
        #print("Time in seconds:", time_seconds)
        #print("First stop, seconds:", seg_firsttrain)
        #print("Last stop, seconds:", seg_lasttrain)
        if (time_seconds >= seg_firsttrain and time_seconds < seg_lasttrain):
            return True
        return False

    multiday = False
    time_seconds = hora_a_segons(time)
    if is_multiday():
        multiday = True
        seg_lasttrain = seg_lasttrain + 86400 # Add one day to the arrival time of the last stop
        if (is_trip_nextday(train, time)):
            #print("And we are beyond the first day!")
            time_seconds = time_seconds + 86400 # Add one day to the current time
    #else:
        #print("Trip starts and ends the same day")
    #print(time_seconds)

    if is_circulating(time_seconds):
        print(f"Train {row} at {time} is circulating from {firsttrain} to {lasttrain}")
        if multiday: print("Trip is multiday")

        # Find the next station the train will stop (i). Basically, for each station, check if the departure time is larger than the specified hour, and stop there.
        for i in range(len(train)):
            # If value is Nan, just skip cell
            if pd.isna(train[i]):
                continue
            else:
                
                #print("train[i]", train[i])
                #print("is multiday", multiday)
                #print("is next day for train[i]", is_trip_nextday(train, train[i]))
                if not (multiday and is_trip_nextday(train, train[i])): time_at_stop = hora_a_segons(train[i])
                else: time_at_stop = hora_a_segons(train[i]) + 86400 # If it's already the next day, add one more day to the times at the schedule 
                print(f"Time at stop {i}, {time_at_stop}")
                print(f"Current time, {time_seconds}")
                if time_at_stop >= time_seconds:
                    print("Ok, this one")
                    break
        
        # Once we found the next stop the train will stop, check if it's exactly at the station
        if time_at_stop == time_seconds:
            # If the time is the same, 
            print(f"El tren {row} està aturat a l'estació de {train.index[i]} ({i}) a les {time}.")
            return i
        
        # Otherwise, it means that the train is circulating between stations
        # Compute the % of the route between the two stations
        # If the train didn't stop at the previous station, we need to get the time of the last actual stop.
        previousstop = train[i-1]
        j = 1
        while pd.isna(previousstop):
            j +=1
            previousstop = train[i-j]
        #print(f"Previous stop was", train.index[i-j], (i-j))
        #print(f"Next stop is", train.index[i], i)
        #print(f"Previous stop was {j} stops ago.")


        if not (multiday and is_trip_nextday(train, previousstop)): time_at_previous_stop = hora_a_segons(previousstop)
        else: time_at_previous_stop = hora_a_segons(previousstop) + 86400

        print("time at stop", time_at_stop)
        print("time at previous stop", time_at_previous_stop)
        print("previousstop", previousstop)
        print("segons:", time_seconds)
        secondsdifference = time_at_stop - time_at_previous_stop
        print("seconds difference:",secondsdifference)
        secondscurrent = time_seconds - time_at_previous_stop
        print("seconds current:", secondscurrent)
        routepercent = round(secondscurrent / secondsdifference, 3)
        print("route %:",routepercent)
        
        print(f"El tren {row} està entre les estacions de {train.index[i-j]} i {train.index[i]} ({(i-j)+routepercent*j}) a les {time}.")
        if inverse == False:
            return (i-j)+routepercent*j
        elif inverse == True: # invert the value ((number of stations-1) - fraction of the route)
            return (len(train)-1)-((i-j)+routepercent*j)


    else:
        return -1 # That trip is not circulating right now


# Basically loops through busca_estacions()
def find_alltrains(df, time, inverse=False):

    # Drop empty columns (stations where no train stops)
    #df = df.dropna(axis=1, how='all')

    # Insert some random nans, to add more complexity
    for col in df.columns:
        df.loc[df.sample(frac=0.0).index, col] = np.nan

    #display(df)
    positions = []
    for row in range(0,len(df)):
        positions.append(busca_estacions_multiday(df, time, row, inverse))
        
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


# For those schedules that only show the minutes, add the hours (h_values) (e.g. S2 and S6 schedules obtained through tabula)
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


# Fixes the station names returned by GTFS and adds any missing intermediate station
from fuzzywuzzy import fuzz
def fix_stationnames(df, route):
    df = df.copy()
    # Define a function to match column names using fuzzy string matching
    def match_columns(column_name, column_names):
        # Find the best match between the column_name and the column_names using fuzzy string matching
        best_match = max(column_names, key=lambda x: fuzz.ratio(column_name, x))
        # If the best match has a high similarity ratio, return it as the new column name, otherwise return None
        if fuzz.ratio(column_name, best_match) >= 70:
            return best_match
        else:
            return column_name

    # Preprocess special cases:
    df = df.rename(columns={"Cabrera De Mar": "Cabrera de Mar-Vilassar de Mar",
                            "La Tour De Carol": "Latour-de-Carol-Enveig",
                            "Els Hostalets De Balenyà":"Balenyà-Els Hostalets",
                            "Balenyà":"Balenyà-Tona-Seva",
                            "Barcelona-Torre Del Baró":"Torre del Baró-Vallbona",
                            "Sant Andreu Arenal":"Barcelona St.Andreu Arenal",
                            "Sant Cugat":"Sant Cugat del Vallès",
                            "Montserrat-Aeri":"Aeri de Montserrat",
                            "Pl. Catalunya": "Barcelona - Pl. Catalunya",
                            "Martorell Vila":"Martorell Vila | Castellbisbal",
                            "El Prat Aeroport":"Aeroport"})

    # Rename the columns in df2 that have misspelled names using fuzzy string matching
    df = df.rename(columns=lambda x: match_columns(x, stations_dict[route]))
    _df = pd.DataFrame(columns=stations_dict[route])
    df = pd.concat([_df, df], join='outer')
    return df
# Usage: 
# df = fix_stationnames(df, route) 


# Check if the columns of a schedule are reversed horizontally, and returns the df in the correct order
def check_df_needsreversing(df):
    for row in df.itertuples(index=False):
        prev_time = None
        for time in row:
            if pd.isna(time):
                continue
            if prev_time is not None and time < prev_time:
                return df[df.columns[::-1]]
            prev_time = time
    return df
# Usage: df = check_df_needsreversing(df)


# Data imported from gtfs might not include all columns (stops/stations). 
# We might need to standarize the column names before passing them to the map
# Using dict, perhaps?

stations_dict = {
       "R1": ["L'Hospitalet de Llobregat", "Barcelona - Sants", "Barcelona - Plaça de Catalunya", 
              "Barcelona - Arc de Triomf", "Barcelona - El Clot Aragó", "St. Adrià de Besòs", 
              "Badalona", "Montgat", "Montgat Nord", "El Masnou", "Ocata", "Premià de Mar", "Vilassar de Mar", 
              "Cabrera de Mar-Vilassar de Mar", "Mataró", "St. Andreu de Llavaneres", "Caldes d'Estrac", 
              "Arenys de Mar", "Canet de Mar", "St. Pol de Mar","Calella","Pineda de Mar","Santa Susanna",
              "Malgrat de Mar","Blanes","Tordera","Maçanet-Massanes"],
       "R2": ["Maçanet-Massanes", "Hostalric", "Riells i Viabrea-Breda", "Gualba", "Sant Celoni", 
              "Palautordera", "Llinars del Vallès", "Cardedeu", "Les Franqueses del Vallès-Granollers Nord", 
              "Granollers Centre", "Montmeló", "Mollet-Sant Fost", "La Llagosta", "Montcada i Reixac", 
              "Barcelona - Sant Andreu", "Barcelona-El Clot-Aragó", "Barcelona - Estació de França", 
              "Barcelona-Passeig de Gràcia", "Barcelona-Sants", "Bellvitge", "El Prat de Llobregat", 
              "Aeroport", "Viladecans", "Gavà", "Castelldefels", "Platja de Castelldefels", "Garraf", 
              "Sitges", "Vilanova i la Geltrú", "Cubelles", "Cunit", "Segur de Calafell", "Calafell", "Sant Vicenç de Calders"],
       "R2N": ["Maçanet-Massanes", "Hostalric", "Riells i Viabrea-Breda", "Gualba", "Sant Celoni", 
              "Palautordera", "Llinars del Vallès", "Cardedeu", "Les Franqueses del Vallès-Granollers Nord", 
              "Granollers Centre", "Montmeló", "Mollet-Sant Fost", "La Llagosta", "Montcada i Reixac", 
              "Barcelona - Sant Andreu", "Barcelona-El Clot-Aragó", "Barcelona-Passeig de Gràcia", 
              "Barcelona-Sants", "Bellvitge", "El Prat de Llobregat", "Aeroport"],
       "R2 Centre": ["Granollers Centre", "Montmeló", "Mollet-Sant Fost", "La Llagosta", "Montcada i Reixac", 
              "Barcelona - Sant Andreu", "Barcelona-El Clot-Aragó", "Barcelona-Passeig de Gràcia", 
              "Barcelona-Sants", "Bellvitge", "El Prat de Llobregat", "Viladecans", "Gavà", "Castelldefels"],
       "R2S": ["Barcelona - Estació de França", "Barcelona-Passeig de Gràcia", "Barcelona-Sants", 
              "Bellvitge", "El Prat de Llobregat", "Viladecans", "Gavà", "Castelldefels", "Platja de Castelldefels", 
              "Garraf", "Sitges", "Vilanova i la Geltrú", "Cubelles", "Cunit", "Segur de Calafell", "Calafell", 
              "Sant Vicenç de Calders"],
       "R3": ["L'Hospitalet de Llobregat", "Barcelona-Sants", "Barcelona-Plaça Catalunya", "Barcelona-Arc de Triomf", 
              "Barcelona-La Sagrera-Meridiana", "Sant Andreu Arenal", "Torre del Baró-Vallbona", "Montcada Bifurcació", 
              "Montcada Ripollet", "Santa Perpètua de Mogoda-La Florida", "Mollet-Santa Rosa", "Parets del Vallès", 
              "Granollers-Canovelles", "Les Franqueses del Vallès", "La Garriga", "Figaró", "Sant Martí de Centelles", 
              "Centelles", "Balenyà-Els Hostalets", "Balenyà-Tona-Seva", "Vic", "Manlleu", "Torelló", "Borgonyà", 
              "Sant Quirze de Besora", "La Farga de Bebié", "Ripoll", "Campdevànol", "Ribes de Freser", "Planoles", 
              "Toses", "La Molina", "Urtx-Alp", "Puigcerdà","Latour-de-Carol-Enveig"],
       "R4": ["St. Vicenç de Calders", "El Vendrell", "L'Arboç", "Els Monjos", "Vilafranca del Penedès", 
              "La Granada", "Lavern-Subirats", "St. Sadurní d'Anoia", "Gelida", "Martorell", "Castellbisbal", 
              "El Papiol","Molins de Rei","St. Feliu de Llobregat","St. Joan Despí","Cornellà","L'Hospitalet de Llobregat",
              "Barcelona Sants","Barcelona Plaça de Catalunya","Barcelona Arc de Triomf","Barcelona La Sagrera-Meridiana",
              "Barcelona St.Andreu Arenal","Torre del Baró-Vallbona","Montcada Bifurcació","Montcada i Reixac-Manresa",
              "Montcada i Reixac-Sta. Maria","Cerdanyola del Vallès","Barberà del Vallès","Sabadell Sud","Sabadell Centre",
              "Sabadell Nord","Terrassa Est" ,"Terrassa" ,"St. Miquel de Gonteres" ,"Viladecavalls" ,"Vacarisses-Torreblanca",
              "Vacarisses" ,"Castellbell i el Vilar-Monistrol de Montserrat" ,"St. Vicenç de Castellet" ,"Manresa"],
       "R5": ['Plaça Espanya', 'Magòria-La Campana', 'Ildefons Cerdà', 'Europa | Fira', 'Gornal', 
              'Sant Josep', 'L’Hospitalet-Av. Carrilet', 'Almeda', 'Cornellà Riera', 'Sant Boi', 
              'Molí Nou-Ciutat Cooperativa', 'Colònia Güell', 'Santa Coloma de Cervelló', 'Sant Vicenç dels Horts', 
              'Can Ros', 'Quatre Camins', 'Pallejà', 'Sant Andreu de la Barca', 'El Palau', 
              'Martorell Vila | Castellbisbal', 'Martorell Central', 'Martorell Enllaç', 'Abrera', 
              'Olesa de Montserrat', 'Aeri de Montserrat', 'Monistrol de Montserrat', 'Castellbell i el Vilar', 
              'Sant Vicenç | CastellGalí', 'Manresa-Viladordis', 'Manresa-Alta', 'Manresa-Baixador'],
       "R6": ['Plaça Espanya', 'Magòria-La Campana', 'Ildefons Cerdà', 'Europa | Fira', 'Gornal', 'Sant Josep', 
              'L’Hospitalet-Av. Carrilet', 'Almeda', 'Cornellà Riera', 'Sant Boi', 'Molí Nou-Ciutat Cooperativa', 
              'Colònia Güell', 'Santa Coloma de Cervelló', 'Sant Vicenç dels Horts', 'Can Ros', 'Quatre Camins', 
              'Pallejà', 'Sant Andreu de la Barca', 'El Palau', 'Martorell Vila | Castellbisbal', 'Martorell Central', 
              'Martorell Enllaç', 'Sant Esteve Sesrovires', 'La Beguda', 'Can Parellada', 'Masquefa', 'Piera', 
              'Vallbona d’Anoia', 'Capellades', 'La Pobla de Claramunt', 'Vilanova del Camí', 'Igualada'],
       "R7": ["Molins de Rei","St. Feliu de Llobregat","St. Joan Despí","Cornellà","L'Hospitalet de Llobregat",
              "Barcelona Sants","Barcelona Plaça de Catalunya","Barcelona Arc de Triomf","Barcelona La Sagrera-Meridiana",
              "Barcelona St.Andreu Arenal",'Torre del Baró-Vallbona','Montcada Bifurcació','Montcada i Reixac-Manresa',
              'Montcada i Reixac-Sta. Maria', 'Cerdanyola del Vallès','Cerdanyola Universitat'],
       "R8": ['Martorell', 'Castellbisbal', 'Rubí', 'Sant Cugat del Vallès', 'Cerdanyola Universitat', 
              'Santa Perpètua de Mogoda - Riera de caldes', 'Mollet - Sant Fost', 'Montmeló', 'Granollers Centre'],
       "S1": ['Barcelona - Pl. Catalunya', 'Provença', 'Gràcia', 'Sant Gervasi', 'Muntaner', 'La Bonanova', 
              'Les Tres Torres', 'Sarrià', 'Peu del Funicular', 'Baixador de Vallvidrera', 'Les Planes', 'La Floresta', 
              'Valldoreix', 'Sant Cugat del Vallès', 'Mira-sol', 'Hospital General', 'Rubí', 'Les Fonts', 'Terrassa Rambla', 
              'Vallparadís Universitat', 'Terrassa Estació del Nord', 'Terrassa Nacions Unides'],
       "S2": ['Barcelona - Pl. Catalunya', 'Provença', 'Gràcia', 'Sant Gervasi', 'Muntaner', 'La Bonanova', 
              'Les Tres Torres', 'Sarrià', 'Peu del Funicular', 'Baixador de Vallvidrera', 'Les Planes', 'La Floresta', 
              'Valldoreix', 'Sant Cugat del Vallès', 'Volpelleres', 'Sant Joan', 'Bellaterra', 'Universitat Autònoma', 'Sant Quirze', 
              'Can Feu | Gràcia', 'Sabadell Plaça Major', 'La Creu Alta', 'Sabadell Nord', 'Sabadell Parc del Nord']
}
# Some keys are redundant, we can generate them dynamically:
stations_dict.update({'R50': stations_dict['R5'], 
                      'R60': stations_dict['R6'], 
                      'S3': stations_dict['R5'][:15], 
                      'S4': stations_dict['R5'][:24],
                      'S8': stations_dict['R5'][:22],
                      'S9': stations_dict['R5'][:16]})
