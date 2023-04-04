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
            "Barcelona-Passeig de Gràcia", "Barcelona-Sants", "Bellvitge", "El Prat de Llobregat", "Aeroport", "Viladecans", 
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
           "Sabadell Centre","Sabadell Nord","Terrassa Est", "Terrassa" ,"St. Miquel de Gonteres", "Viladecavalls", "Vacarisses-Torreblanca",
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

    "R8": ['Martorell', 'Castellbisbal', 'Rubí', 'Sant Cugat del Vallès', 'Cerdanyola Universitat', 'Santa Perpètua de Mogoda - Riera de caldes', 
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