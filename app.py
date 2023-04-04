# Import Required Modules
from flask import Flask, render_template, Response, stream_with_context
import pandas as pd
import helpers, gtfsdata , tabuladata
import tabula
from datetime import datetime
import time
import pytz 
import json
import numpy as np

estacions_r5=["Plaça Espanya", "Magòria-La Campana", "Ildefons Cerdà", "Europa | Fira", "Gornal", "Sant Josep", "L’Hospitalet-Av. Carrilet", "Almeda", "Cornellà Riera", "Sant Boi", "Molí Nou-Ciutat Cooperativa", "Colònia Güell", "Santa Coloma de Cervelló", "Sant Vicenç dels Horts", "Can Ros", "Quatre Camins", "Pallejà", "Sant Andreu de la Barca", "El Palau", "Martorell Vila | Castellbisbal", "Martorell Central", "Martorell Enllaç", "Abrera", "Olesa de Montserrat", "Aeri de Montserrat", "Monistrol de Montserrat", "Castellbell i el Vilar", "Sant Vicenç | CastellGalí", "Manresa-Viladordis", "Manresa-Alta", "Manresa-Baixador"]
estacions_s2s6=['Barcelona - Pl. Catalunya', 'Provença', 'Gràcia', 'Sant Gervasi', 'Muntaner', 'La Bonanova', 'Les Tres Torres', 'Sarrià', 'Peu del Funicular', 'Baixador de Vallvidrera', 'Les Planes', 'La Floresta', 'Valldoreix', 'Sant Cugat', 'Volpelleres', 'Sant Joan', 'Bellaterra', 'Universitat Autònoma', 'Sant Quirze', 'Can Feu | Gràcia', 'Sabadell Plaça Major', 'La Creu Alta', 'Sabadell Nord', 'Sabadell Parc del Nord']
estacions_s1s5s7=['Barcelona - Pl. Catalunya', 'Provença', 'Gràcia', 'Sant Gervasi', 'Muntaner', 'La Bonanova', 'Les Tres Torres', 'Sarrià', 'Peu del Funicular', 'Baixador de Vallvidrera', 'Les Planes', 'La Floresta', 'Valldoreix', 'Sant Cugat', 'Mira-sol', 'Hospital General', 'Rubí', 'Les Fonts', 'Terrassa Rambla', 'Vallparadís Universitat', 'Terrassa Estació del Nord', 'Terrassa Nacions Unides']

# Test (getting route from gtfs)
route = "R1"
data_cer = gtfsdata.update_dataset("cercanias")
df = gtfsdata.get_schedule_cercanias(data_cer, route, 20230405)
#for schedule in df:
#    print(schedule)

#r1_anada_feiners = df[0]
#r1_tornada_feiners = df[1]


area_s3s4s8s9_anada_feiners = (380, 30, 1320, 700)
area_s3s4s8s9_tornada_feiners = (1385, 30, 2340, 700)
area_s2s6_anada_feiners = [(410, 40, 600, 700), # 1st
                           (600, 40, 630, 700), # 2nd (just 4 rows). Includes just the minutes. Will need to be repeated from 10 to 12.
                           (630, 35, 700, 700), # 3rd
                           (706, 35, 740, 700), # 4th (5 more rows), same case as 2nd
                           (740, 35, 800, 700), # 5th (10 more rows), same case as 2nd
                           (800, 35, 835, 700), # 6th (10 more rows), same case as 2nd
                           (835, 35, 875, 700), # 7th (a normal one)
                           (877, 30, 885, 700)] # 8th (last train for weekdays (except friday), just one row)
area_s2s6_tornada_feiners = [(440, 40, 610, 700), # 1st (normal part, 5:01 to 9:43)
                             (610, 30, 635, 690), # 2nd (just 4 rows)
                             (640, 35, 795, 690), # 3rd (normal part again)
                             (800, 30, 860, 690), # 4th (weird part one more time)
                             (865, 35, 880, 690), # 5th (normal part, but just two rows...)
                             (885, 30, 915, 690), # 6th (weird part one more time, but not as weird as part 4)
                             (920, 30, 950, 690), # 7th (normal part again, 4 rows)
                             (955, 30, 975, 690)] # 8th (normal part, but only fridays and weekdays before holidays)

# Getting schedules from PDF timetables
print("Getting train schedules...")
r1_anada_feiners = tabuladata.get_tabula_schedule("R1", tornada=False)
r1_tornada_feiners = tabuladata.get_tabula_schedule("R1", tornada=True)

r2_anada_feiners = tabuladata.get_tabula_schedule("R2", tornada=False)
r2_tornada_feiners = tabuladata.get_tabula_schedule("R2", tornada=True)

r3_anada_feiners = tabuladata.get_tabula_schedule("R3", tornada=False)
r3_tornada_feiners = tabuladata.get_tabula_schedule("R3", tornada=True)
                                            
r4_anada_feiners = tabuladata.get_tabula_schedule("R4", tornada=False)
r4_tornada_feiners = tabuladata.get_tabula_schedule("R4", tornada=True)

r5_anada_feiners = tabuladata.get_tabula_schedule("R5", tornada=False)
r5_tornada_feiners = tabuladata.get_tabula_schedule("R5", tornada=True)

r6_anada_feiners = tabuladata.get_tabula_schedule("R6", tornada=False)
r6_tornada_feiners = tabuladata.get_tabula_schedule("R6", tornada=True)

r7_anada_feiners = tabuladata.get_tabula_schedule("R7", tornada=False)
r7_tornada_feiners = tabuladata.get_tabula_schedule("R7", tornada=True)

r8_anada_feiners = tabuladata.get_tabula_schedule("R8", tornada=False)
r8_tornada_feiners = tabuladata.get_tabula_schedule("R8", tornada=True)


# S3, S4, S8 and S9 (Pl España - Martorell Enllaç)
url = "static/horarispdf/S8_Martorell_LA_octubre_20.pdf"
schedule = tabula.read_pdf(url, pages=1, stream=True, lattice=False, multiple_tables=False, guess=False, area=area_s3s4s8s9_anada_feiners, pandas_options={'header': None})
estacions_s3s4s8s9 = estacions_r5[:22] # First 22 stations of R4
schedule[0].columns = estacions_s3s4s8s9
s3s4s8s9_anada_feiners = helpers.cleanup_trainschedule(schedule[0])

# S3, S4, S8 and S9 (Martorell Enllaç - Pl España)
url = "static/horarispdf/S8_Martorell_LA_octubre_20.pdf"
schedule = tabula.read_pdf(url, pages=1, stream=True, lattice=False, multiple_tables=False, guess=False, area=area_s3s4s8s9_tornada_feiners, pandas_options={'header': None})
estacions_s3s4s8s9 = estacions_r5[:22] # First 22 stations of R4
estacions_s3s4s8s9 = estacions_s3s4s8s9[::-1]
schedule[0].columns = estacions_s3s4s8s9
s3s4s8s9_tornada_feiners = helpers.cleanup_trainschedule(schedule[0])


# S2, and S6 (Pl. Catalunya - Universitat Autònoma/Sabadell)
s2s6_anada_feiners = []
url = "static/horarispdf/Sabadell_s2_s6_gener_19.pdf"

 #part 1
partindex = 0 
schedule = tabula.read_pdf(url, pages=1, stream=True, lattice=False, multiple_tables=False, guess=False, area=area_s2s6_anada_feiners[partindex], pandas_options={'header': None})
schedule[0].columns = estacions_s2s6
s2s6_anada_feiners.append(helpers.cleanup_trainschedule(schedule[0]))
#display(s2s6_anada_feiners_1)

 # part 2 (de 10:07 a 12:07)
partindex = 1
h_values = [10, 11, 12]
schedule = tabula.read_pdf(url, pages=1, stream=True, lattice=True, multiple_tables=False, guess=False, area=area_s2s6_anada_feiners[partindex], pandas_options={'header': None})
schedule[0].columns = estacions_s2s6
df_temp = schedule[0]
#df_temp = cleanup_trainschedule(schedule[0])
df_temp = df_temp.dropna(axis=0, how='all') # Drop empty rows
df_temp = helpers.generate_hours(df_temp, h_values)
df_temp = helpers.fix_time_discontinuity(df_temp)
s2s6_anada_feiners.append(helpers.filter_interval(df_temp, "10:07", "12:07"))

 # Part 3 (de 12:21 a 14:20)
partindex = 2
schedule = tabula.read_pdf(url, pages=1, stream=True, lattice=False, multiple_tables=False, guess=False, area=area_s2s6_anada_feiners[partindex], pandas_options={'header': None, 'dtype': str})
schedule[0].columns = estacions_s2s6
s2s6_anada_feiners.append(helpers.cleanup_trainschedule(schedule[0]))

 # Part 4 (de 14:24 a 16:36)
partindex = 3
h_values = [14, 15, 16]
schedule = tabula.read_pdf(url, pages=1, stream=True, lattice=True, multiple_tables=False, guess=False, area=area_s2s6_anada_feiners[partindex], pandas_options={'header': None})
schedule[0].columns = estacions_s2s6
df_temp = schedule[0]
df_temp = df_temp.dropna(axis=0, how='all') # Drop empty rows
df_temp = helpers.generate_hours(df_temp, h_values)
df_temp = helpers.fix_time_discontinuity(df_temp)
s2s6_anada_feiners.append(helpers.filter_interval(df_temp, "14:24", "16:36"))

 # Part 5 (de 16:44 a 18:48)
partindex = 4
h_values = [16, 17, 18]
schedule = tabula.read_pdf(url, pages=1, stream=True, lattice=True, multiple_tables=False, guess=False, area=area_s2s6_anada_feiners[partindex], pandas_options={'header': None})
schedule[0].columns = estacions_s2s6
df_temp = schedule[0]
df_temp = df_temp.dropna(axis=0, how='all') # Drop empty rows
df_temp = helpers.generate_hours(df_temp, h_values)
df_temp = helpers.fix_time_discontinuity(df_temp)
s2s6_anada_feiners.append(helpers.filter_interval(df_temp, "16:44", "18:48"))

 # Part 6 (de 19:00 a 21:00)
partindex = 5
h_values = [19, 20, 21]
schedule = tabula.read_pdf(url, pages=1, stream=True, lattice=True, multiple_tables=False, guess=False, area=area_s2s6_anada_feiners[partindex], pandas_options={'header': None})
schedule[0].columns = estacions_s2s6
df_temp = schedule[0]
df_temp = df_temp.dropna(axis=0, how='all') # Drop empty rows
df_temp = helpers.generate_hours(df_temp, h_values)
df_temp = helpers.fix_time_discontinuity(df_temp)
s2s6_anada_feiners.append(helpers.filter_interval(df_temp, "19:00", "21:00"))

 # Part 7 (de 21:15 a 23:17)
partindex = 6
schedule = tabula.read_pdf(url, pages=1, stream=True, lattice=True, multiple_tables=False, guess=False, area=area_s2s6_anada_feiners[partindex], pandas_options={'header': None})
schedule[0].columns = estacions_s2s6
df_temp = helpers.cleanup_trainschedule(schedule[0])
s2s6_anada_feiners.append(df_temp.dropna(axis=0, how='all')) # Drop empty rows

 # Part 8 (Last trains weekdays before weekdays)
partindex = 7
schedule = tabula.read_pdf(url, pages=1, stream=True, lattice=True, multiple_tables=False, guess=False, area=area_s2s6_anada_feiners[partindex], pandas_options={'header': None})
schedule[0].columns = estacions_s2s6
df_temp = helpers.cleanup_trainschedule(schedule[0])
s2s6_anada_feiners.append(df_temp.dropna(axis=0, how='all')) # Drop empty rows

# Concat all the parts together
s2s6_anada_feiners = pd.concat(s2s6_anada_feiners, axis=0)
s2s6_anada_feiners.reset_index(drop=True, inplace=True)
del schedule, url, h_values

s2s6_tornada_feiners = []

url = "static/horarispdf/Sabadell_s2_s6_gener_19.pdf"

 #part 1
partindex = 0
schedule = tabula.read_pdf(url, pages=2, stream=True, lattice=False, multiple_tables=False, guess=False, area=area_s2s6_tornada_feiners[partindex], pandas_options={'header': None})
schedule[0].columns = estacions_s2s6[::-1]
s2s6_tornada_feiners.append(helpers.cleanup_trainschedule(schedule[0]))

 #part 2
partindex = 1
h_values = [9, 10, 11, 12]
schedule = tabula.read_pdf(url, pages=2, stream=True, lattice=True, multiple_tables=False, guess=False, area=area_s2s6_tornada_feiners[partindex], pandas_options={'header': None})
df_temp = schedule[0]
df_temp.iloc[3, :] = df_temp.iloc[3, :].shift(1) # The 4th row appears shifted to the left... correct that manually
df_temp.drop(columns=0, inplace=True) # And now drop the first column, which is all Nan
df_temp.columns = estacions_s2s6[::-1]
df_temp = helpers.generate_hours(df_temp, h_values)
df_temp = helpers.fix_time_discontinuity(df_temp)
s2s6_tornada_feiners.append(helpers.filter_interval(df_temp, "9:55", "12:10"))

 #part 3
partindex = 2
schedule = tabula.read_pdf(url, pages=2, stream=True, lattice=False, multiple_tables=False, guess=False, area=area_s2s6_tornada_feiners[partindex], pandas_options={'header': None})
schedule[0].columns = estacions_s2s6[::-1]
s2s6_tornada_feiners.append(helpers.cleanup_trainschedule(schedule[0]))

 #part 4
partindex = 3
h_values = [16, 17, 18, 19]
schedule = tabula.read_pdf(url, pages=2, stream=True, lattice=True, multiple_tables=False, guess=False, area=area_s2s6_tornada_feiners[partindex], pandas_options={'header': None})
df_temp = schedule[0]
df_temp.iloc[-1, :] = df_temp.iloc[-1, :].shift(1) # The last row appears shifted to the left... correct that manually
df_temp.drop(columns=0, inplace=True) # And now drop the first column, which is all Nan
df_temp.columns = estacions_s2s6[::-1]
df_temp = helpers.generate_hours(df_temp, h_values)
df_temp = helpers.filter_interval(df_temp, "16:52", "19:15")
s2s6_tornada_feiners.append(helpers.fix_time_discontinuity(df_temp))
s2s6_tornada_feiners[partindex].drop(2, inplace=True) # Ugly workaround, delete row 2, which has a train previous to the starting period (the fix_time_discontinuity() should take care of these cases, but there's just one, so...)

 #part5
partindex = 4
schedule = tabula.read_pdf(url, pages=2, stream=True, lattice=False, multiple_tables=False, guess=False, area=area_s2s6_tornada_feiners[partindex], pandas_options={'header': None})
schedule[0].columns = estacions_s2s6[::-1]
s2s6_tornada_feiners.append(helpers.cleanup_trainschedule(schedule[0]))

 #part6
partindex = 5
h_values = [19, 20, 21]
schedule = tabula.read_pdf(url, pages=2, stream=True, lattice=True, multiple_tables=False, guess=False, area=area_s2s6_tornada_feiners[partindex], pandas_options={'header': None})
df_temp = schedule[0]
df_temp.iloc[-1, :] = df_temp.iloc[-1, :].shift(1) # The last row appears shifted to the left... correct that manually
df_temp.drop(columns=0, inplace=True) # And now drop the first column, which is all Nan
df_temp.columns = estacions_s2s6[::-1]
df_temp = helpers.generate_hours(df_temp, h_values)
df_temp = helpers.fix_time_discontinuity(df_temp)
s2s6_tornada_feiners.append(helpers.filter_interval(df_temp, "19:28", "21:16"))

#part 7
partindex = 6
schedule = tabula.read_pdf(url, pages=2, stream=True, lattice=True, multiple_tables=False, guess=False, area=area_s2s6_tornada_feiners[partindex], pandas_options={'header': None})
schedule[0].drop(columns=0, inplace=True)
schedule[0].columns = estacions_s2s6[::-1]
s2s6_tornada_feiners.append(helpers.cleanup_trainschedule(schedule[0]))

#part 8 (Last trains, only Fridays and weekdays before public holidays)
partindex = 7
schedule = tabula.read_pdf(url, pages=2, stream=True, lattice=True, multiple_tables=False, guess=False, area=area_s2s6_tornada_feiners[partindex], pandas_options={'header': None})
schedule[0].drop(columns=0, inplace=True)
schedule[0].columns = estacions_s2s6[::-1]
#s2s6_tornada_feiners.append(cleanup_trainschedule(schedule[0]))

# Merge all the parts
s2s6_tornada_feiners = pd.concat(s2s6_tornada_feiners, axis=0)
s2s6_tornada_feiners.reset_index(drop=True, inplace=True)
del schedule, url, h_values


## End of extraction from pdf with tabula

## Getting specific services within a line (e.g. R2 Nord, S2, etc.)

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


def get_r6_services(df):
    #R6 (Stops at all stations, like Martorell Enllaç)
    df_r6  = df.copy()
    df_r6 = df_r6.dropna(subset=['Martorell Enllaç'], how='all') # Only R5 stops there.

    #R50 (Ends at Manresa Baixador, does not stop at all stations, like Aeri de Montserrat)
    df_r60  = df.copy()
    df_r60 = df_r60.drop(df_r60[df_r60['Martorell Enllaç'].notna()].index) # Does not stop there

    return df_r6, df_r60

r6_r6_anada_feiners, r6_r60_anada_feiners, = get_r6_services(r6_anada_feiners)
r6_r6_tornada_feiners, r6_r60_tornada_feiners = get_r6_services(r6_tornada_feiners)


# Get lines S3, S4, S8 and S9. S4 and S8 are identical in the S8_Martorell_LA_octubre_20.pdf file, but S4 goes further. We need to pass the df for S4 that we got from R5_Manresa_220x450_LA_octubre_20.pdf, where the whole S4 line is shown.
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

s3_anada_feiners, s8_anada_feiners, s9_anada_feiners= get_s3_s8_s9_services(s3s4s8s9_anada_feiners, r5_s4_anada_feiners)
s3_tornada_feiners, s8_tornada_feiners, s9_tornada_feiners= get_s3_s8_s9_services(s3s4s8s9_tornada_feiners, r5_s4_tornada_feiners)

# Merge the 3 lines into one, as we we'll display them as one line in the line view
s3s8s9_anada_feiners = pd.concat([s3_anada_feiners, s8_anada_feiners, s9_anada_feiners])
s3s8s9_tornada_feiners = pd.concat([s3_tornada_feiners, s8_tornada_feiners, s9_tornada_feiners])

# Gets lines S2 and S6 (Universitat Autonoma & Sabadell)
def get_s2_s6_services(df):
    #S6 (Ends at Universitat Autonoma, Stops at Sant Gervasi)
    df_s6  = df.copy()
    df_s6 = df_s6.dropna(subset=['Sant Gervasi'], how='all') # Only R5 stops there.
    
    #S2 (Goes until Sabadell Parc del Nord, the last stop)
    df_s2  = df.copy()
    df_s2 = df_s2.dropna(subset=['Sabadell Parc del Nord'], how='all') # Only R5 stops there.

    return df_s2, df_s6

s2_anada_feiners, s6_anada_feiners = get_s2_s6_services(s2s6_anada_feiners)
s2_tornada_feiners, s6_tornada_feiners = get_s2_s6_services(s2s6_tornada_feiners)


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
                    "positions1": helpers.find_alltrains(r3_anada_feiners, bcn_time),
                    "positions2": helpers.find_alltrains(r3_tornada_feiners, bcn_time, inverse=True)
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
                    "trainLine": "Rodalies R6",
                    "positions1": helpers.find_alltrains(r6_r6_anada_feiners, bcn_time),
                    "positions2": helpers.find_alltrains(r6_r6_tornada_feiners, bcn_time, inverse=True)
                },
                {
                    "trainLine": "Rodalies R60",
                    "positions1": helpers.find_alltrains(r6_r60_anada_feiners, bcn_time),
                    "positions2": helpers.find_alltrains(r6_r60_tornada_feiners, bcn_time, inverse=True)
                },
                {
                    "trainLine": "Rodalies S3 S8 S9",
                    "positions1": helpers.find_alltrains(s3s8s9_anada_feiners, bcn_time),
                    "positions2": helpers.find_alltrains(s3s8s9_tornada_feiners, bcn_time, inverse=True)
                },
                {
                    "trainLine": "Rodalies S3",
                    "positions1": helpers.find_alltrains(s3_anada_feiners, bcn_time),
                    "positions2": helpers.find_alltrains(s3_tornada_feiners, bcn_time, inverse=True)
                },
                {
                    "trainLine": "Rodalies S8",
                    "positions1": helpers.find_alltrains(s8_anada_feiners, bcn_time),
                    "positions2": helpers.find_alltrains(s8_tornada_feiners, bcn_time, inverse=True)
                },
                {
                    "trainLine": "Rodalies S9",
                    "positions1": helpers.find_alltrains(s9_anada_feiners, bcn_time),
                    "positions2": helpers.find_alltrains(s9_tornada_feiners, bcn_time, inverse=True)
                },
                {
                    "trainLine": "Rodalies R7",
                    "positions1": helpers.find_alltrains(r7_anada_feiners, bcn_time),
                    "positions2": helpers.find_alltrains(r7_tornada_feiners, bcn_time, inverse=True),
                },
                {
                    "trainLine": "Rodalies R8",
                    "positions1": helpers.find_alltrains(r8_anada_feiners, bcn_time),
                    "positions2": helpers.find_alltrains(r8_tornada_feiners, bcn_time, inverse=True),
                },
                {
                    "trainLine": "Rodalies S2 S6",
                    "positions1": helpers.find_alltrains(s2s6_anada_feiners, bcn_time),
                    "positions2": helpers.find_alltrains(s2s6_tornada_feiners, bcn_time, inverse=True),
                },
                {
                    "trainLine": "Rodalies S2",
                    "positions1": helpers.find_alltrains(s2_anada_feiners, bcn_time),
                    "positions2": helpers.find_alltrains(s2_tornada_feiners, bcn_time, inverse=True),
                },
                {
                    "trainLine": "Rodalies S6",
                    "positions1": helpers.find_alltrains(s6_anada_feiners, bcn_time),
                    "positions2": helpers.find_alltrains(s6_tornada_feiners, bcn_time, inverse=True),
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