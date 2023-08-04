# This is an alternative to reading the train schedules from google traffic data (gtfsdata.py module)
# It uses tabulat o read the schedules from PDF tables.
# Each train line is in a separate PDF file, and the area of the table with the times must be manually specified
# Moreover, some specialized functions are required to cleanse the data

import pandas as pd
import numpy as np
import tabula


# Station list for each line:
stations = {
    "R1": ["L'Hospitalet de Llobregat", "Barcelona - Sants", "Barcelona - Plaça de Catalunya", "Barcelona - Arc de Triomf", 
            "Barcelona - El Clot Aragó", "St. Adrià de Besòs", "Badalona", "Montgat", "Montgat Nord", "El Masnou", "Ocata", 
            "Premià de Mar", "Vilassar de Mar", "Cabrera de Mar-Vilassar de Mar", "Mataró", "St. Andreu de Llavaneres", 
            "Caldes d'Estrac", "Arenys de Mar", "Canet de Mar", "St. Pol de Mar","Calella","Pineda de Mar","Santa Susanna",
            "Malgrat de Mar","Blanes","Tordera","Maçanet-Massanes"],

    "R2": ["Maçanet-Massanes", "Hostalric", "Riells i Viabrea-Breda", "Gualba", "Sant Celoni", "Palautordera", "Llinars del Vallès", 
            "Cardedeu", "Les Franqueses del Vallès-Granollers Nord", "Granollers Centre", "Montmeló", "Mollet-Sant Fost", "La Llagosta", 
            "Montcada i Reixac", "Barcelona - Sant Andreu", "Barcelona-El Clot-Aragó", "Barcelona - Estació de França", 
            "Barcelona-Passeig de Gràcia", "Barcelona-Sants", "Bellvitge | Gornal", "El Prat de Llobregat", "Aeroport", "Viladecans", 
            "Gavà", "Castelldefels", "Platja de Castelldefels", "Garraf", "Sitges", "Vilanova i la Geltrú", "Cubelles", "Cunit", 
            "Segur de Calafell", "Calafell", "Sant Vicenç de Calders"],

    "R3": ["L'Hospitalet de Llobregat", "Barcelona-Sants", "Barcelona-Plaça Catalunya", "Barcelona-Arc de Triomf", "Barcelona-La Sagrera-Meridiana", 
            "Sant Andreu Arenal", "Torre del Baró-Vallbona", "Montcada Bifurcació", "Montcada Ripollet", "Santa Perpètua de Mogoda-La Florida", 
            "Mollet-Santa Rosa", "Parets del Vallès", "Granollers-Canovelles", "Les Franqueses del Vallès", "La Garriga", "Figaró", 
            "Sant Martí de Centelles", "Centelles", "Balenyà-Els Hostalets", "Balenyà-Tona-Seva", "Vic", "Manlleu", "Torelló", "Borgonyà", 
            "Sant Quirze de Besora", "La Farga de Bebié", "Ripoll", "Campdevànol", "Ribes de Freser", "Planoles", "Toses", "La Molina", 
            "Urtx-Alp", "Puigcerdà","Latour-de-Carol-Enveig"],

    "R4": ["St. Vicenç de Calders", "El Vendrell", "L'Arboç", "Els Monjos", "Vilafranca del Penedès", "La Granada", "Lavern-Subirats", 
           "St. Sadurní d'Anoia", "Gelida", "Martorell", "Castellbisbal", "El Papiol","Molins de Rei","St. Feliu de Llobregat",
           "St. Joan Despí","Cornellà","L'Hospitalet de Llobregat","Barcelona Sants","Barcelona Plaça de Catalunya","Barcelona Arc de Triomf",
           "Barcelona La Sagrera-Meridiana","Barcelona St.Andreu Arenal","Barcelona Torre del Baró","Montcada Bifurcació",
           "Montcada i Reixac-Manresa", "Montcada i Reixac-Sta. Maria","Cerdanyola del Vallès","Barberà del Vallès","Sabadell Sud",
           "Sabadell Centre","Sabadell Nord","Terrassa Est", "Terrassa Estació del Nord" ,"St. Miquel de Gonteres", "Viladecavalls", "Vacarisses-Torreblanca",
           "Vacarisses" ,"Castellbell i el Vilar-Monistrol de Montserrat","St. Vicenç de Castellet" ,"Manresa"],

    "R5": ["Plaça Espanya", "Magòria-La Campana", "Ildefons Cerdà", "Europa | Fira", "Gornal", "Sant Josep", "L’Hospitalet-Av. Carrilet", 
           "Almeda", "Cornellà Riera", "Sant Boi", "Molí Nou-Ciutat Cooperativa", "Colònia Güell", "Santa Coloma de Cervelló", 
           "Sant Vicenç dels Horts", "Can Ros", "Quatre Camins", "Pallejà", "Sant Andreu de la Barca", "El Palau", 
           "Martorell Vila | Castellbisbal", "Martorell Central", "Martorell Enllaç", "Abrera", "Olesa de Montserrat", "Aeri de Montserrat", 
           "Monistrol de Montserrat", "Castellbell i el Vilar", "Sant Vicenç | CastellGalí", "Manresa-Viladordis", "Manresa-Alta", "Manresa-Baixador"],

    "R6": ['Plaça Espanya', 'Magòria-La Campana', 'Ildefons Cerdà', 'Europa | Fira', 'Gornal', 'Sant Josep', 'L’Hospitalet-Av. Carrilet', 
           'Almeda', 'Cornellà Riera', 'Sant Boi', 'Molí Nou-Ciutat Cooperativa', 'Colònia Güell', 'Santa Coloma de Cervelló', 
           'Sant Vicenç dels Horts', 'Can Ros', 'Quatre Camins', 'Pallejà', 'Sant Andreu de la Barca', 'El Palau', 
           'Martorell Vila | Castellbisbal', 'Martorell Central', 'Martorell Enllaç', 'Sant Esteve Sesrovires', 'La Beguda', 
           'Can Parellada', 'Masquefa', 'Piera', 'Vallbona d’Anoia', 'Capellades', 'La Pobla de Claramunt', 'Vilanova del Camí', 'Igualada'],

    "R7": ['Barcelona St. Andreu Arenal','Barcelona Torre del Baró','Montcada Bifurcació','Montcada i Reixac-Manresa',
           'Montcada i Reixac-Sta. Maria', 'Cerdanyola del Vallès','Cerdanyola Universitat'],

    "R8": ['Martorell Central', 'Castellbisbal', 'Rubi Can Vallhonrat', 'Sant Cugat Coll Favà', 'Cerdanyola Universitat', 'Santa Perpètua de Mogoda - Riera de caldes', 
          'Mollet - Sant Fost', 'Montmeló', 'Granollers Centre'],

    "S1": ['Barcelona - Pl. Catalunya', 'Provença', 'Gràcia', 'Sant Gervasi', 'Muntaner', 'La Bonanova', 'Les Tres Torres', 'Sarrià', 'Peu del Funicular', 
           'Baixador de Vallvidrera', 'Les Planes', 'La Floresta', 'Valldoreix', 'Sant Cugat', 'Volpelleres', 'Sant Joan', 'Bellaterra', 
           'Universitat Autònoma', 'Sant Quirze', 'Can Feu | Gràcia', 'Sabadell Plaça Major', 'La Creu Alta', 'Sabadell Nord', 'Sabadell Parc del Nord'],

    "S2": ['Barcelona - Pl. Catalunya', 'Provença', 'Gràcia', 'Sant Gervasi', 'Muntaner', 'La Bonanova', 'Les Tres Torres', 'Sarrià', 'Peu del Funicular', 
           'Baixador de Vallvidrera', 'Les Planes', 'La Floresta', 'Valldoreix', 'Sant Cugat', 'Mira-sol', 'Hospital General', 'Rubí', 
           'Les Fonts', 'Terrassa Rambla', 'Vallparadís Universitat', 'Terrassa Estació del Nord', 'Terrassa Nacions Unides']
}


# Cleans imported tables from PDF
def cleanup_trainschedule(df):
    df = df.astype(str)
    df = df.replace('\.', ':', regex=True)
    df = df.replace('–', np.NaN)

    # remove unwanted characters
    for col in df.columns: 
        df[col] = df[col].str.replace('[^0-9:]', '', regex=True) # Removes non numeric characters or :
        df[col] = df[col].str.replace(r'(:\d)$', r'\g<1>0', regex=True) # Adds missing 0 at the end of a time
    df = df.replace('', np.NaN)
    df=df.dropna(how='all')
    #df = df.replace('nan', np.NaN)
    return df


# General function to import schedules from PDF tables (Works for R1-R8. Not S1 and S2)
def get_tabula_schedule(route, tornada=False):

    if tornada == False:
        direction = "anada"
    else:
        direction = "tornada"

    routes = {
        "R1" : {
            "file": "static/horarispdf/R1.pdf",
            "anada": {
                "page": 1,
                "area": (605, 10, 2360, 950),
                "lattice": False
            },
            "tornada":{
                "page": 2,
                "area": (605, 10, 2370, 950),
                "lattice": False
            }
        },
        "R2" : {
            "file": "static/horarispdf/R2.pdf",
            "anada": {
                "page": 1,
                "area": (630, 10, 2450, 955),
                "lattice": False
            },
            "tornada":{
                "page": 2,
                "area": (630, 10, 2450, 955),
                "lattice": False
            }
        },
        "R3" : {
            "file": "static/horarispdf/R3.pdf",
            "anada": {
                "page": 1,
                "area": (555, 10, 1500, 960),
                "lattice": False
            },
            "tornada": {
                "page": 2,
                "area": (557, 10, 1450, 960),
                "lattice": False
            }
        },
        "R4" : {
            "file": "static/horarispdf/R4.pdf",
            "anada": {
                "page": 1,
                "area": (576, 10, 2320, 965),
                "lattice": True
            },
            "tornada": {
                "page": 2,
                "area": (576, 10, 2320, 965),
                "lattice": True
            }
        },
        "R5" : {
            "file": "static/horarispdf/R5_Manresa_220x450_LA_octubre_20.pdf",
            "anada": {
                "page": 1,
                "area": (500, 10, 850, 965),
                "lattice": True
            },
            "tornada": {
                "page": 1,
                "area": (900, 10, 2320, 965),
                "lattice": True
            }
        },
        "R6" : {
            "file": "static/horarispdf/R6_Igualada_LA_octubre_20.pdf",
            "anada": {
                "page": 1,
                "area": (500, 35, 750, 595),
                "lattice": False
            },
            "tornada": {
                "page": 1,
                "area": (825, 35, 2000, 595),
                "lattice": False
            }
        },
        "R7" : {
            "file": "static/horarispdf/R7.pdf",
            "anada": {
                "page": 1,
                "area": (620, 140, 1650, 800),
                "lattice": False
            },
            "tornada": {
                "page": 2,
                "area": (620, 140, 1600, 800),
                "lattice": False
            }
        },
        "R8" : {
            "file": "static/horarispdf/R8.pdf",
            "anada": {
                "page": 1,
                "area": (468, 10, 1300, 950),
                "lattice": False
            },
            "tornada": {
                "page": 1,
                "area": (1625, 10, 2300, 950),
                "lattice": False
            }
        },

    }

    schedule = tabula.read_pdf(routes[route]['file'], pages=routes[route][direction]['page'], stream=True, lattice=routes[route][direction]['lattice'], multiple_tables=True, area=routes[route][direction]['area'], pandas_options={'header': None, 'dtype': str})

    # Data cleaning for some special cases:
    if route == "R4" and tornada==False:
        schedule[0] = schedule[0].iloc[:, : len(stations['R4'])]
        schedule[0] = schedule[0].replace(">>> Cerdanyola Universitat", np.NaN) # Esborrar les celes amb aquest string
    if route == "R4" and tornada==True:
        schedule[0] = schedule[0].iloc[:, : len(stations['R4'])]
    if route == "R6" and tornada == False:
        schedule[0] = schedule[0].drop([11, 12, 14, 23, 24], axis=1) # empty columns that were read incorrectly
    if route == "R6" and tornada == True:
        schedule[0] = schedule[0].drop([13, 22], axis=1) # empty columns that were read incorrectly


    schedule[0] = cleanup_trainschedule(schedule[0])
    
    if direction == "anada": schedule[0].columns = stations[route]
    else: schedule[0].columns = stations[route][::-1]

    # More data cleaning for some special cases:
    if route == "R4" and tornada==False:
        schedule[0].iloc[1, 12:] = schedule[0].iloc[1, 12:].shift(periods=1)
        cell_value = schedule[0].at[1, "St. Feliu de Llobregat"]
        sliced_value1 = cell_value[:4]
        sliced_value2 = cell_value[4:]
        schedule[0].at[1, "Molins de Rei"] = sliced_value1
        schedule[0].at[1, "St. Feliu de Llobregat"] = sliced_value2


    return schedule[0]

## Usage: 
#display(get_tabula_schedule("R5", tornada=True))




# Line R2 is divided between R2 North, R2 and R2 South. However, this is not consistent and some trains overlap these lines.
# Separates the R2 line into north, central and south portions
def get_r2_nordcentresud(df):
    # North
    df_nord = df.copy()
    df_nord = df_nord.drop(df_nord[df_nord['Castelldefels'].notna()].index) # Si surt Castelldefels, tampoc es Centre
    df_nord = df_nord.drop(df_nord[df_nord['Barcelona - Estació de França'].notna()].index) # Si surt l'estació de França, tampoc es Nord
    df_nord = df_nord.dropna(axis=0, how='all') # Esborrem les files buides
    df_nord = df_nord.dropna(axis=1, how='all') # Esborrem les columnes buides

    # Center
    df_centre = df.copy()
    df_centre = df_centre[(df_centre['Aeroport'].isnull()) & (df_centre['Barcelona - Estació de França'].isnull())] # Si paren a Aeroport o Estació de França, no poden ser R2 centre.
    df_centre = df_centre.drop(df_centre[df_centre['Vilanova i la Geltrú'].notna()].index) # Si surt Vilanova, tampoc es Centre
    df_centre = df_centre.drop(df_centre[df_centre['Sant Celoni'].notna()].index) # Si surt Sant Celoni, tampoc es Centre
    df_centre = df_centre.dropna(axis=0, how='all') # Delete empty rows (not really necessary here)
    df_centre = df_centre.dropna(axis=1, how='all') # Esborrem les columnes buides

    # South
    df_sud = df.copy()
    df_sud = df_sud.dropna(subset=['Barcelona - Estació de França'], how='all') # Ens quedem només aquells que comencen a Estació de França
    df_sud = df_sud.drop(df_sud[df_sud['Aeroport'].notna()].index) # Si surt l'aeroport, tampoc es Nord
    df_sud = df_sud.dropna(axis=1, how='all') # Esborrem les columnes buides

    # Remove duplicated rows in df_center, since not all conditions are mutually exclusive
    indices_list = df_nord.index.tolist()
    indices_list = indices_list+df_sud.index.tolist()
    df_centre = df_centre.drop(indices_list, errors='ignore')

    # Other
    #  Get the rows that did not fit any of the three dataframes, and create another one (df_other) 
    index_subsets = pd.concat([df_nord, df_centre, df_sud]).index
    index_original = ~df.index.isin(index_subsets)
    df_other = df.loc[index_original]

    #  Now split the others into two (until Passeig de Gràcia, and from Sants)
    df_other_1 = df_other.loc[:, 'Maçanet-Massanes':'Barcelona-Passeig de Gràcia'] 
    df_other_2 = df_other.loc[:, 'Barcelona-Sants':'Sant Vicenç de Calders']

    #  If any lines contain Airport, it's North. If any lines contain Estació de França, it's south
    #  then concat the remainder to their corresponding dataframe (north or south)
    df_nord = pd.concat([df_nord, df_other_1[df_other_1['Barcelona - Estació de França'].isnull()]]).drop(columns='Barcelona - Estació de França')
    df_sud = pd.concat([df_sud, df_other_2[df_other_2['Aeroport'].isnull()]]).drop(columns='Aeroport')

    # Now deal with the train that starts at Estació de França but ends at Aeroport
    df_sud = pd.concat([df_sud, df_other[df_other['Aeroport'].notnull() & df_other['Barcelona - Estació de França'].notnull()].loc[:, 'Barcelona - Estació de França':'Barcelona-Sants']])
    df_nord = pd.concat([df_nord, df_other[df_other['Aeroport'].notnull() & df_other['Barcelona - Estació de França'].notnull()].loc[:, 'Barcelona-Sants':'Aeroport']])

    df_nord.sort_index(inplace=True)
    df_sud.sort_index(inplace=True)

    return df_nord, df_centre, df_sud


# R5 has 3 different services (R5, R50 and S4), depending on which stations the trains stop.
def get_r5_services(df):
    #R5 (Ends at Manresa Baixador (end of the line), doesn't stop at all stations)
    df_r5  = df.copy()
    df_r5 = df_r5.dropna(subset=['Aeri de Montserrat'], how='all') # Only R5 stops there.

    #S4 (Ends at Olesa de Montserrat, stops at all stations)
    df_s4  = df.copy()
    # Stops at Martorell Enllaç but not at Aeri de Montserrat
    df_s4 = df_s4.dropna(subset=['Martorell Enllaç'], how='all') 
    df_s4 = df_s4.drop(df_s4[df_s4['Aeri de Montserrat'].notna()].index)

    #R50 (Ends at Manresa Baixador, does not stop at all stations (even fewer than R5), like Aeri de Montserrat)
    df_r50  = df.copy()
    df_r50 = df_r50.dropna(subset=['Manresa-Baixador'], how='all')
    df_r50 = df_r50.drop(df_r50[df_r50['Aeri de Montserrat'].notna()].index)

    #  Alternative: Get the rows that did not fit any of the three dataframes, and create another one (df_other) 
    #index_subsets = pd.concat([df_r5, df_s4]).index
    #index_original = ~df.index.isin(index_subsets)
    #df_r50 = df.loc[index_original]

    return df_r5, df_s4, df_r50

# R6 schedule includes R6 and R60
def get_r6_services(df):
    #R6 (Stops at all stations, like Martorell Enllaç)
    df_r6  = df.copy()
    df_r6 = df_r6.dropna(subset=['Martorell Enllaç'], how='all') # Only R5 stops there.

    #R60 
    df_r60  = df.copy()
    df_r60 = df_r60.drop(df_r60[df_r60['Martorell Enllaç'].notna()].index) # Does not stop there

    return df_r6, df_r60


def get_s3_s8_s9_services(df, df_s4):
    df_s3  = df.copy() # Ends at Can Ros. Stops at every station
    # Keep station that stop at Colonia Güell, but not Quatre camins
    df_s3 = df_s3.dropna(subset=['Colònia Güell'], how='all') # Only trains that stop there
    df_s3 = df_s3.drop(df_s3[df_s3['Quatre Camins'].notna()].index) # But remove trains stopping there

    df_s8 = df.copy() # Trains that end at Martorell Enllaç and Stop at every station, and are not part of S4
    df_s8 = df_s8.dropna(subset=['Martorell Enllaç', 'Martorell Vila | Castellbisbal'], how='any')
    df_s8.drop(df_s8[df_s8['Plaça Espanya'].isin(df_s4['Plaça Espanya'])].index, inplace=True) # Remove rows not in S4
    
    df_s9  = df.copy() # End at Quatre Camins. Stops at every station
    df_s9 = df_s9.dropna(subset=['Quatre Camins', 'Colònia Güell'], how='any') # Only trains that stop there
    df_s9 = df_s9.drop(df_s9[df_s9['Sant Andreu de la Barca'].notna()].index)

    return df_s3, df_s8, df_s9


# Gets lines S2 and S6 (Universitat Autonoma & Sabadell)
def get_s2_s6_services(df):
    #S6 (Ends at Universitat Autonoma, Stops at Sant Gervasi)
    df_s6  = df.copy()
    df_s6 = df_s6.dropna(subset=['Sant Gervasi'], how='all') # Only R5 stops there.
    
    #S2 (Goes until Sabadell Parc del Nord, the last stop)
    df_s2  = df.copy()
    df_s2 = df_s2.dropna(subset=['Sabadell Parc del Nord'], how='all') # Only R5 stops there.

    return df_s2, df_s6
