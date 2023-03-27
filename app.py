# Import Required Modules
from flask import Flask, render_template, Response, stream_with_context
import pandas as pd
import helpers
import tabula
from datetime import datetime
import time
import pytz 
import json
import numpy as np

estacions_r1=("L'Hospitalet de Llobregat", "Barcelona - Sants", "Barcelona - Plaça de Catalunya", "Barcelona - Arc de Triomf", "Barcelona - El Clot Aragó", "St. Adrià de Besòs", "Badalona", "Montgat", "Montgat Nord", "El Masnou", "Ocata", "Premià de Mar", "Vilassar de Mar", "Cabrera de Mar-Vilassar de Mar", "Mataró", "St. Andreu de Llavaneres", "Caldes d'Estrac", "Arenys de Mar", "Canet de Mar", "St. Pol de Mar","Calella","Pineda de Mar","Santa Susanna","Malgrat de Mar","Blanes","Tordera","Maçanet-Massanes")
estacions_r2=("Maçanet-Massanes", "Hostalric", "Riells i Viabrea-Breda", "Gualba", "Sant Celoni", "Palautordera", "Llinars del Vallès", "Cardedeu", "Les Franqueses del Vallès-Granollers Nord", "Granollers Centre", "Montmeló", "Mollet-Sant Fost", "La Llagosta", "Montcada i Reixac", "Barcelona - Sant Andreu", "Barcelona-El Clot-Aragó", "Barcelona - Estació de França", "Barcelona-Passeig de Gràcia", "Barcelona-Sants", "Bellvitge", "El Prat de Llobregat", "Aeroport", "Viladecans", "Gavà", "Castelldefels", "Platja de Castelldefels", "Garraf", "Sitges", "Vilanova i la Geltrú", "Cubelles", "Cunit", "Segur de Calafell", "Calafell", "Sant Vicenç de Calders")
estacions_r3=("L'Hospitalet de Llobregat", "Barcelona-Sants", "Barcelona-Plaça Catalunya", "Barcelona-Arc de Triomf", "Barcelona-La Sagrera-Meridiana", "Sant Andreu Arenal", "Torre del Baró-Vallbona", "Montcada Bifurcació", "Montcada Ripollet", "Santa Perpètua de Mogoda-La Florida", "Mollet-Santa Rosa", "Parets del Vallès", "Granollers-Canovelles", "Les Franqueses del Vallès", "La Garriga", "Figaró", "Sant Martí de Centelles", "Centelles", "Balenyà-Els Hostalets", "Balenyà-Tona-Seva", "Vic", "Manlleu", "Torelló", "Borgonyà", "Sant Quirze de Besora", "La Farga de Bebié", "Ripoll", "Campdevànol", "Ribes de Freser", "Planoles", "Toses", "La Molina", "Urtx-Alp", "Puigcerdà","Latour-de-Carol-Enveig")
estacions_r4=("St. Vicenç de Calders", "El Vendrell", "L'Arboç", "Els Monjos", "Vilafranca del Penedès", "La Granada", "Lavern-Subirats", "St. Sadurní d'Anoia", "Gelida", "Martorell", "Castellbisbal", "El Papiol","Molins de Rei","St. Feliu de Llobregat","St. Joan Despí","Cornellà","L'Hospitalet de Llobregat","Barcelona Sants","Barcelona Plaça de Catalunya","Barcelona Arc de Triomf","Barcelona La Sagrera-Meridiana","Barcelona St.Andreu Arenal","Barcelona Torre del Baró","Montcada Bifurcació","Montcada i Reixac-Manresa","Montcada i Reixac-Sta. Maria","Cerdanyola del Vallès","Barberà del Vallès","Sabadell Sud","Sabadell Centre","Sabadell Nord","Terrassa Est" ,"Terrassa" ,"St. Miquel de Gonteres" ,"Viladecavalls" ,"Vacarisses-Torreblanca" ,"Vacarisses" ,"Castellbell i el Vilar-Monistrol de Montserrat" ,"St. Vicenç de Castellet" ,"Manresa")
estacions_r5 = ["Plaça Espanya", "Magòria-La Campana", "Ildefons Cerdà", "Europa | Fira", "Gornal", "Sant Josep", "L’Hospitalet-Av. Carrilet", "Almeda", "Cornellà Riera", "Sant Boi", "Molí Nou-Ciutat Cooperativa", "Colònia Güell", "Santa Coloma de Cervelló", "Sant Vicenç dels Horts", "Can Ros", "Quatre Camins", "Pallejà", "Sant Andreu de la Barca", "El Palau", "Martorell Vila | Castellbisbal", "Martorell Central", "Martorell Enllaç", "Abrera", "Olesa de Montserrat", "Aeri de Montserrat", "Monistrol de Montserrat", "Castellbell i el Vilar", "Sant Vicenç | CastellGalí", "Manresa-Viladordis", "Manresa-Alta", "Manresa-Baixador"]
estacions_r6=['Plaça Espanya', 'Magòria-La Campana', 'Ildefons Cerdà', 'Europa | Fira', 'Gornal', 'Sant Josep', 'L’Hospitalet-Av. Carrilet', 'Almeda', 'Cornellà Riera', 'Sant Boi', 'Molí Nou-Ciutat Cooperativa', 'Colònia Güell', 'Santa Coloma de Cervelló', 'Sant Vicenç dels Horts', 'Can Ros', 'Quatre Camins', 'Pallejà', 'Sant Andreu de la Barca', 'El Palau', 'Martorell Vila | Castellbisbal', 'Martorell Central', 'Martorell Enllaç', 'Sant Esteve Sesrovires', 'La Beguda', 'Can Parellada', 'Masquefa', 'Piera', 'Vallbona d’Anoia', 'Capellades', 'La Pobla de Claramunt', 'Vilanova del Camí', 'Igualada']
estacions_r7=('Barcelona St. Andreu Arenal','Barcelona Torre del Baró','Montcada Bifurcació','Montcada i Reixac-Manresa','Montcada i Reixac-Sta. Maria', 'Cerdanyola del Vallès','Cerdanyola Universitat')
estacions_r8=('Martorell', 'Castellbisbal', 'Rubí', 'Sant Cugat del Vallès', 'Cerdanyola Universitat', 'Santa Perpètua de Mogoda - Riera de caldes', 'Mollet - Sant Fost', 'Montmeló', 'Granollers Centre')

area_r1_anada_feiners = (605, 10, 2360, 950)
area_r1_tornada_feiners = (605, 10, 2370, 950)
area_r2_anada_feiners = (630, 10, 2450, 955)
area_r2_tornada_feiners = (630, 10, 2450, 955)
area_r3_anada_feiners = (555, 10, 1500, 960)
area_r3_tornada_feiners = (557, 10, 1450, 960)
area_r4_anada_feiners = (576, 10, 2320, 965)
area_r4_tornada_feiners = (576, 10, 2320, 965)
area_r5_anada_feiners = (500, 10, 850, 965)
area_r5_tornada_feiners = (900, 10, 2320, 965)
area_r6_anada_feiners = (500, 35, 750, 595)
area_r6_tornada_feiners = (825, 35, 2000, 595)
area_r7_anada = (620, 140, 1650, 800)
area_r7_tornada = (620, 140, 1600, 800)
area_r8_anada = (468, 10, 1300, 950)
area_r8_tornada = (1625, 10, 2300, 950)

print("Getting train schedules...")

# R1 (L'Hospitalet - Maçanet)
url = "https://rodalies.gencat.cat/web/.content/02_Horaris/horaris/R1.pdf"
url = "static/horarispdf/R1.pdf"
schedule = tabula.read_pdf(url, pages=1, stream=True, lattice=False, multiple_tables=True, area=area_r1_anada_feiners)
schedule[0].columns = estacions_r1
r1_anada_feiners = helpers.cleanup_trainschedule(schedule[0])

# R1 (Maçanet - L'Hospitalet)
url = "https://rodalies.gencat.cat/web/.content/02_Horaris/horaris/R1.pdf"
url = "static/horarispdf/R1.pdf"
schedule = tabula.read_pdf(url, pages=2, stream=True, lattice=False, multiple_tables=True, area=area_r1_tornada_feiners)
schedule[0].columns = estacions_r1[::-1]
r1_tornada_feiners = helpers.cleanup_trainschedule(schedule[0])

# R5 (Pl España - Manresa)
url = "static/horarispdf/R5_Manresa_220x450_LA_octubre_20.pdf"
schedule = tabula.read_pdf(url, pages=1, stream=True, lattice=True, multiple_tables=False, guess=False, area=area_r5_anada_feiners, pandas_options={'header': None})
schedule[0].columns = estacions_r5
r5_anada_feiners = helpers.cleanup_trainschedule(schedule[0])

# R5 (Manresa - Pl Espanya)
url = "static/horarispdf/R5_Manresa_220x450_LA_octubre_20.pdf"
schedule = tabula.read_pdf(url, pages=1, stream=True, lattice=True, multiple_tables=False, guess=False, area=area_r5_tornada_feiners, pandas_options={'header': None})
schedule[0].columns = estacions_r5[::-1]
r5_tornada_feiners = helpers.cleanup_trainschedule(schedule[0])

# R6 (Pl España - Igualada)
url = "static/horarispdf/R6_Igualada_LA_octubre_20.pdf"
schedule = tabula.read_pdf(url, pages=1, stream=True, lattice=False, multiple_tables=False, guess=False, area=area_r6_anada_feiners)
schedule[0] = schedule[0].drop(['Unnamed: 11', 'Unnamed: 12', 'Unnamed: 14', 'Unnamed: 23', 'Unnamed: 24'], axis=1) # empty columns that were read incorrectly
schedule[0].columns = estacions_r6
r6_anada_feiners = helpers.cleanup_trainschedule(schedule[0])

# R6 (Igualada - Pl Espanya)
url = "static/horarispdf/R6_Igualada_LA_octubre_20.pdf"
schedule = tabula.read_pdf(url, pages=1, stream=True, lattice=False, multiple_tables=False, guess=False, area=area_r6_tornada_feiners)
schedule[0] = schedule[0].drop(['Unnamed: 13', 'Unnamed: 22'], axis=1) # empty columns that were read incorrectly
schedule[0].columns = estacions_r6[::-1]
r6_tornada_feiners = helpers.cleanup_trainschedule(schedule[0])

# R7 (Bcn St Andreu-Cerdanyola Universitat)
url = "https://rodalies.gencat.cat/web/.content/02_Horaris/horaris/R7.pdf"
url = "static/horarispdf/R7.pdf"
schedule = tabula.read_pdf(url, pages=1, stream=True, lattice=False, multiple_tables=True, area=area_r7_anada)
schedule[0].columns = estacions_r7
r7_anada = helpers.cleanup_trainschedule(schedule[0])

# R7 (Cerdanyola Universitat - Bcn St Andreu)
url = "https://rodalies.gencat.cat/web/.content/02_Horaris/horaris/R7.pdf"
url = "static/horarispdf/R7.pdf"
schedule = tabula.read_pdf(url, pages=2, stream=True, lattice=False, multiple_tables=True, area=area_r7_tornada)
schedule[0].columns = estacions_r7[::-1]
r7_tornada = helpers.cleanup_trainschedule(schedule[0])

# R8 (Martorell-Granollers)
url = "https://rodalies.gencat.cat/web/.content/02_Horaris/horaris/R8.pdf"
url = "static/horarispdf/R8.pdf"
schedule = tabula.read_pdf(url, pages=1, stream=True, lattice=False, multiple_tables=True, area=area_r8_anada)
schedule[0].columns = estacions_r8
r8_anada = helpers.cleanup_trainschedule(schedule[0])

# R8 (Granollers-Martorell)
url = "https://rodalies.gencat.cat/web/.content/02_Horaris/horaris/R8.pdf"
url = "static/horarispdf/R8.pdf"
schedule = tabula.read_pdf(url, pages=1, stream=True, lattice=False, multiple_tables=True, area=area_r8_tornada)
schedule[0].columns = estacions_r8[::-1]
r8_tornada = helpers.cleanup_trainschedule(schedule[0])

# R2 (Maçanet - St. Vicenç de Calders)
url = "https://rodalies.gencat.cat/web/.content/02_Horaris/horaris/R2.pdf"
url = "static/horarispdf/R2.pdf"
schedule = tabula.read_pdf(url, pages=1, stream=True, lattice=False, multiple_tables=True, area=area_r2_anada_feiners)
schedule[0].columns = estacions_r2
r2_anada_feiners = helpers.cleanup_trainschedule(schedule[0])

# R2 (St. Vicenç de Calders - Maçanet)
url = "https://rodalies.gencat.cat/web/.content/02_Horaris/horaris/R2.pdf"
url = "static/horarispdf/R2.pdf"
schedule = tabula.read_pdf(url, pages=2, stream=True, lattice=False, multiple_tables=True, area=area_r2_tornada_feiners)
schedule[0].columns = estacions_r2[::-1]
r2_tornada_feiners = helpers.cleanup_trainschedule(schedule[0])

# R3 (Hospitalet-Vic)
url = "https://rodalies.gencat.cat/web/.content/02_Horaris/horaris/R3.pdf"
url = "static/horarispdf/R3.pdf"
schedule = tabula.read_pdf(url, pages=1, stream=True, lattice=False, multiple_tables=True, area=area_r3_anada_feiners)
schedule[0].columns = estacions_r3
r3_anada = helpers.cleanup_trainschedule(schedule[0])

# R3 (Vic-Hospitalet)
url = "https://rodalies.gencat.cat/web/.content/02_Horaris/horaris/R3.pdf"
url = "static/horarispdf/R3.pdf"
schedule = tabula.read_pdf(url, pages=2, stream=True, lattice=False, multiple_tables=True, area=area_r3_tornada_feiners)
schedule[0].columns = estacions_r3[::-1]
r3_tornada = helpers.cleanup_trainschedule(schedule[0])

# R4 (St. Vicenç de Calders - Manresa)
url = "https://rodalies.gencat.cat/web/.content/02_Horaris/horaris/R4.pdf"
url = "static/horarispdf/R4.pdf"
schedule = tabula.read_pdf(url, pages=1, stream=True, lattice=True, multiple_tables=False, guess=False, area=area_r4_anada_feiners)
schedule[0] = schedule[0].iloc[:, : len(estacions_r4)]
schedule[0] = schedule[0].replace(">>> Cerdanyola Universitat", np.NaN) # Esborrar les celes amb aquest string
schedule[0].columns = estacions_r4
## Els valors de Molins de Rei (columna 12) a la fila 1 s'han fusionat. Moure totes les files un pas a la dreta, i després separar aquella cela en particular.
schedule[0].iloc[1, 12:] = schedule[0].iloc[1, 12:].shift(periods=1)
#el valor de (1,"Molins de Rei") s'ha de dividir entre (1,"Molins de Rei" i 1,"St. Feliu de Llobregat")
cell_value = schedule[0].at[1, "St. Feliu de Llobregat"]
sliced_value1 = cell_value[:4]
sliced_value2 = cell_value[4:]
schedule[0].at[1, "Molins de Rei"] = sliced_value1
schedule[0].at[1, "St. Feliu de Llobregat"] = sliced_value2
r4_anada_feiners = helpers.cleanup_trainschedule(schedule[0])

# R4 (Manresa - St Vicenç de Calders)
url = "https://rodalies.gencat.cat/web/.content/02_Horaris/horaris/R4.pdf"
url = "static/horarispdf/R4.pdf"
schedule = tabula.read_pdf(url, pages=2, stream=True, lattice=True, multiple_tables=False, guess=False, area=area_r4_tornada_feiners)
schedule[0] = schedule[0].iloc[:, : len(estacions_r4)]
schedule[0].columns = estacions_r4
r4_tornada_feiners = helpers.cleanup_trainschedule(schedule[0])

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

r2_nord_anada_feiners, r2_centre_anada_feiners, r2_sud_anada_feiners = get_r2_nordcentresud(r2_anada_feiners)
r2_nord_tornada_feiners, r2_centre_tornada_feiners, r2_sud_tornada_feiners = get_r2_nordcentresud(r2_tornada_feiners[r2_tornada_feiners.columns[::-1]]) # Reverse columns, so the function works
r2_nord_tornada_feiners, r2_centre_tornada_feiners, r2_sud_tornada_feiners = [df[df.columns[::-1]] for df in [r2_nord_tornada_feiners, r2_centre_tornada_feiners, r2_sud_tornada_feiners]] # Reverse back

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

r5_r5_anada_feiners, r5_s4_anada_feiners, r5_r50_anada_feiners = get_r5_services(r5_anada_feiners)
r5_r5_tornada_feiners, r5_s4_tornada_feiners, r5_r50_tornada_feiners = get_r5_services(r5_tornada_feiners)

print("...done")

#tz = pytz.timezone('US/Eastern') # zona horària de NYC,f or testing purposes 
tz = pytz.timezone('Europe/Madrid') # zona horària de Madrid 
#bcn_time = datetime.now(tz).strftime("%H:%M:%S") # hora de Barcelona en format hh:mm
#print(bcn_time)
#print(helpers.find_alltrains(r3_anada, bcn_time))

# Create Home Page Route
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/map')
def map():
    return render_template('map.html')

@app.route('/data')
def generate_data():
    while True:
        bcn_time = datetime.now(tz).strftime("%H:%M:%S") # hora de Barcelona en format hh:mm
        print(bcn_time)
        with app.app_context():
            data = [
                {
                    "trainLine": "Rodalies R1",
                    "positions1": helpers.find_alltrains(r1_anada_feiners, bcn_time),
                    "positions2": helpers.find_alltrains(r1_tornada_feiners, bcn_time, inverse=True)
                },
                {
                    "trainLine": "Rodalies R2",
                    "positions1": helpers.find_alltrains(r2_anada_feiners, bcn_time),
                    "positions2": helpers.find_alltrains(r2_tornada_feiners, bcn_time, inverse=True)
                },
                {
                    "trainLine": "Rodalies R2 Nord",
                    "positions1": helpers.find_alltrains(r2_nord_anada_feiners, bcn_time),
                    "positions2": helpers.find_alltrains(r2_nord_tornada_feiners, bcn_time, inverse=True)
                },
                {
                    "trainLine": "Rodalies R2 Centre",
                    "positions1": helpers.find_alltrains(r2_centre_anada_feiners, bcn_time),
                    "positions2": helpers.find_alltrains(r2_centre_tornada_feiners, bcn_time, inverse=True)
                },
                {
                    "trainLine": "Rodalies R2 Sud",
                    "positions1": helpers.find_alltrains(r2_sud_anada_feiners, bcn_time),
                    "positions2": helpers.find_alltrains(r2_sud_tornada_feiners, bcn_time, inverse=True)
                },
                {
                    "trainLine": "Rodalies R3",
                    "positions1": helpers.find_alltrains(r3_anada, bcn_time),
                    "positions2": helpers.find_alltrains(r3_tornada, bcn_time, inverse=True)
                },
                {
                    "trainLine": "Rodalies R4",
                    "positions1": helpers.find_alltrains(r4_anada_feiners, bcn_time),
                    "positions2": helpers.find_alltrains(r4_tornada_feiners, bcn_time, inverse=True)
                },
                {
                    "trainLine": "Rodalies R5 R50 S4",
                    "positions1": helpers.find_alltrains(r5_anada_feiners, bcn_time),
                    "positions2": helpers.find_alltrains(r5_tornada_feiners, bcn_time, inverse=True)
                },
                {
                    "trainLine": "Rodalies R5",
                    "positions1": helpers.find_alltrains(r5_r5_anada_feiners, bcn_time),
                    "positions2": helpers.find_alltrains(r5_r5_tornada_feiners, bcn_time, inverse=True)
                },
                {
                    "trainLine": "Rodalies S4",
                    "positions1": helpers.find_alltrains(r5_s4_anada_feiners, bcn_time),
                    "positions2": helpers.find_alltrains(r5_s4_tornada_feiners, bcn_time, inverse=True)
                },
                {
                    "trainLine": "Rodalies R50",
                    "positions1": helpers.find_alltrains(r5_r50_anada_feiners, bcn_time),
                    "positions2": helpers.find_alltrains(r5_r50_tornada_feiners, bcn_time, inverse=True)
                },
                {
                    "trainLine": "Rodalies R6 R60",
                    "positions1": helpers.find_alltrains(r6_anada_feiners, bcn_time),
                    "positions2": helpers.find_alltrains(r6_tornada_feiners, bcn_time, inverse=True)
                },
                {
                    "trainLine": "Rodalies R7",
                    "positions1": helpers.find_alltrains(r7_anada, bcn_time),
                    "positions2": helpers.find_alltrains(r7_tornada, bcn_time, inverse=True),
                },
                {
                    "trainLine": "Rodalies R8",
                    "positions1": helpers.find_alltrains(r8_anada, bcn_time),
                    "positions2": helpers.find_alltrains(r8_tornada, bcn_time, inverse=True),
                }
            ]
            print(data)
            yield f"data: {json.dumps(data)}\n\n"
            time.sleep(1)

@app.route('/stream-data')
def stream_data():
    return Response(stream_with_context(generate_data()), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9019, debug=False)