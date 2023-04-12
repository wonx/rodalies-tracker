# Import Required Modules
from flask import Flask, render_template, Response, stream_with_context
from apscheduler.schedulers.background import BackgroundScheduler
import pandas as pd
import helpers, gtfsdata, tabuladata
import tabula
from datetime import datetime
import time
import pytz 
import json
import numpy as np

estacions_r5=["Plaça Espanya", "Magòria-La Campana", "Ildefons Cerdà", "Europa | Fira", "Gornal", "Sant Josep", "L’Hospitalet-Av. Carrilet", "Almeda", "Cornellà Riera", "Sant Boi", "Molí Nou-Ciutat Cooperativa", "Colònia Güell", "Santa Coloma de Cervelló", "Sant Vicenç dels Horts", "Can Ros", "Quatre Camins", "Pallejà", "Sant Andreu de la Barca", "El Palau", "Martorell Vila | Castellbisbal", "Martorell Central", "Martorell Enllaç", "Abrera", "Olesa de Montserrat", "Aeri de Montserrat", "Monistrol de Montserrat", "Castellbell i el Vilar", "Sant Vicenç | CastellGalí", "Manresa-Viladordis", "Manresa-Alta", "Manresa-Baixador"]
estacions_s2s6=['Barcelona - Pl. Catalunya', 'Provença', 'Gràcia', 'Sant Gervasi', 'Muntaner', 'La Bonanova', 'Les Tres Torres', 'Sarrià', 'Peu del Funicular', 'Baixador de Vallvidrera', 'Les Planes', 'La Floresta', 'Valldoreix', 'Sant Cugat', 'Volpelleres', 'Sant Joan', 'Bellaterra', 'Universitat Autònoma', 'Sant Quirze', 'Can Feu | Gràcia', 'Sabadell Plaça Major', 'La Creu Alta', 'Sabadell Nord', 'Sabadell Parc del Nord']
estacions_s1s5s7=['Barcelona - Pl. Catalunya', 'Provença', 'Gràcia', 'Sant Gervasi', 'Muntaner', 'La Bonanova', 'Les Tres Torres', 'Sarrià', 'Peu del Funicular', 'Baixador de Vallvidrera', 'Les Planes', 'La Floresta', 'Valldoreix', 'Sant Cugat', 'Mira-sol', 'Hospital General', 'Rubí', 'Les Fonts', 'Terrassa Rambla', 'Vallparadís Universitat', 'Terrassa Estació del Nord', 'Terrassa Nacions Unides']


today = datetime.today().strftime('%Y%m%d')
today = int(today)

# Test (getting routes from gtfs)
def refresh_datasets():
    global data_cer
    global data_fgc
    print("Getting train schedules from GTFS data...")
    data_cer = gtfsdata.update_dataset("cercanias")
    data_fgc = gtfsdata.update_dataset("fgc")
    return data_cer, data_fgc

refresh_datasets()

routes = ['R1', 'R3', 'R4', 'R5', 'R50', 'R6', 'R60', 'R7', 'R8', 'S1', 'S2', 'S3', 'S4', 'S8', 'S9']
def refresh_schedules():
    today = datetime.today().strftime('%Y%m%d')
    today = int(today)
    print(f"Refreshing schedules for {today}...")
    global schedules_dict
    schedules_dict = {} # Dict to store all schedules
    for route in routes:
        print("Processing route", route)
        if route[:1] == 'S' or route[:2] in ("R5", "R6"):
            df_anada, df_tornada = gtfsdata.get_schedule_fgc(data_fgc, route, today)
        else:
            df_anada, df_tornada = gtfsdata.get_schedule_cercanias(data_cer, route, today)
        # Standardize the amount of station and their names
        df_anada = helpers.fix_stationnames(df_anada, route)
        df_tornada = helpers.fix_stationnames(df_tornada, route)
        # Check if the columns need reversing
        df_anada = helpers.check_df_needsreversing(df_anada)
        df_tornada = helpers.check_df_needsreversing(df_tornada)
        # Make sure the "Anada" matches the same direction on the train line
        if df_tornada.columns[0] == helpers.stations_dict[route][0]:
            print("Exchanging inbound and outbound trains dataframes")
            df_anada, df_tornada = df_tornada, df_anada

        # Convert hours beyond 23h to 00h.
        df_anada = df_anada.applymap(lambda x: gtfsdata.convert_24_to_00(x) if not pd.isna(x) else x)
        df_tornada = df_tornada.applymap(lambda x: gtfsdata.convert_24_to_00(x) if not pd.isna(x) else x)
        
        # Save in the dict
        schedules_dict.setdefault(route, {})["Anada"] = df_anada
        schedules_dict.setdefault(route, {})["Tornada"] = df_tornada

    print("...done.")
    return schedules_dict

refresh_schedules()

# Line R2 is a completely different story that must be pre-processed in a different way
def prepare_r2(): 
    print("Processing line R2...")
    global schedules_dict
    today = datetime.today().strftime('%Y%m%d')
    today = int(today)
    routes = ['R2N', 'R2', 'R2S']
    for route in routes:
        df_anada, df_tornada = gtfsdata.get_schedule_cercanias(data_cer, route, today)
        # Standardize the amount of station and their names
        df_anada = helpers.fix_stationnames(df_anada, 'R2')
        df_tornada = helpers.fix_stationnames(df_tornada, 'R2')
        df_anada = df_anada[df_anada.columns.intersection(helpers.stations_dict['R2'])] #Keep only columns from that line (deals with edge case where Montcada Bifurcació appears in a R2 trip)
        df_tornada = df_tornada[df_tornada.columns.intersection(helpers.stations_dict['R2'])]
        df_anada = helpers.check_df_needsreversing(df_anada)
        df_tornada = helpers.check_df_needsreversing(df_tornada)
        if df_tornada.columns[0] == helpers.stations_dict[route][0]:
            print("Exchanging inbound and outbound trains dataframes")
            df_anada, df_tornada = df_tornada, df_anada
        print(f"Primera estació d'anada de la {route}: {df_anada.columns[0]}")
        print(f"Primera estació d tornada de la {route}: {df_tornada.columns[0]}")
        # Save in the dict
        schedules_dict.setdefault(route, {})["Anada"] = df_anada
        schedules_dict.setdefault(route, {})["Tornada"] = df_tornada

    # Merge the three R2 dataframes into one and sort it
    schedules_dict['R2']['Anada'] = pd.concat([schedules_dict['R2N']['Anada'], schedules_dict['R2']['Anada'], schedules_dict['R2S']['Anada']], ignore_index=True)
    schedules_dict['R2']['Anada'] = gtfsdata.sort_schedule(schedules_dict['R2']['Anada'])
    schedules_dict['R2']['Tornada'] = pd.concat([schedules_dict['R2N']['Tornada'], schedules_dict['R2']['Tornada'], schedules_dict['R2S']['Tornada']], ignore_index=True)
    schedules_dict['R2']['Tornada'] = gtfsdata.sort_schedule(schedules_dict['R2']['Tornada'])
    print(f"Primera estació d'anada de la R2: {schedules_dict['R2']['Anada'].columns[0]}")
    print(f"Primera estació de tornada de la R2: {schedules_dict['R2']['Tornada'].columns[0]}")

    # Process the merged dataframe into North, Center and South
    schedules_dict['R2 Centre'] = {}
    schedules_dict['R2N']['Anada'], schedules_dict['R2 Centre']['Anada'], schedules_dict['R2S']['Anada'] = tabuladata.get_r2_nordcentresud(schedules_dict['R2']['Anada'])
    # Same, for "Tornada" (we have to reverse the columns so the function works, and then reverse back)
    schedules_dict['R2N']['Tornada'], schedules_dict['R2 Centre']['Tornada'], schedules_dict['R2S']['Tornada'] = tabuladata.get_r2_nordcentresud(schedules_dict['R2']['Tornada'][schedules_dict['R2']['Tornada'].columns[::-1]])
    schedules_dict['R2N']['Tornada'], schedules_dict['R2 Centre']['Tornada'], schedules_dict['R2S']['Tornada'] = [df[df.columns[::-1]] for df in [schedules_dict['R2N']['Tornada'], schedules_dict['R2 Centre']['Tornada'], schedules_dict['R2S']['Tornada']]] # Reverse back
    # Now, make sure they all have the proper columns
    routes = ['R2N', 'R2 Centre', 'R2S', 'R2']
    for route in routes:
        schedules_dict[route]['Anada'] = helpers.fix_stationnames(schedules_dict[route]['Anada'], route)
        schedules_dict[route]['Tornada'] = helpers.fix_stationnames(schedules_dict[route]['Tornada'], route)
        schedules_dict[route]['Anada'] = helpers.check_df_needsreversing(schedules_dict[route]['Anada'])
        schedules_dict[route]['Tornada'] = helpers.check_df_needsreversing(schedules_dict[route]['Tornada'])
        # Convert hours beyond 23h to 00h.
        schedules_dict[route]['Anada'] = schedules_dict[route]['Anada'].applymap(lambda x: gtfsdata.convert_24_to_00(x) if not pd.isna(x) else x)
        schedules_dict[route]['Tornada'] = schedules_dict[route]['Tornada'].applymap(lambda x: gtfsdata.convert_24_to_00(x) if not pd.isna(x) else x)
        
    print("...done.")

prepare_r2()

print("...all done.")


""" r1_anada_feiners, r1_tornada_feiners = gtfsdata.get_schedule_cercanias(data_cer, "R1", today)
r1_anada_feiners, r1_tornada_feiners = helpers.fix_stationnames(r1_anada_feiners, "R1"), helpers.fix_stationnames(r1_tornada_feiners, "R1")
# (R2 here)
r3_anada_feiners, r3_tornada_feiners = gtfsdata.get_schedule_cercanias(data_cer, "R3", today)
r4_anada_feiners, r4_tornada_feiners = gtfsdata.get_schedule_cercanias(data_cer, "R4", today)
#r7_anada_feiners, r7_tornada_feiners = gtfsdata.get_schedule_cercanias(data_cer, "R7", today) # Make sure the stations match before enabling
r8_anada_feiners, r8_tornada_feiners = gtfsdata.get_schedule_cercanias(data_cer, "R8", today)

data_fgc = gtfsdata.update_dataset("fgc")
r5_anada_feiners, r5_tornada_feiners = gtfsdata.get_schedule_fgc(data_fgc, "R5", today)
r50_anada_feiners, r50_tornada_feiners = gtfsdata.get_schedule_fgc(data_fgc, "R50", today)
r6_anada_feiners, r6_tornada_feiners = gtfsdata.get_schedule_fgc(data_fgc, "R6", today)
r60_anada_feiners, r60_tornada_feiners = gtfsdata.get_schedule_fgc(data_fgc, "R60", today)
s3_anada_feiners, s3_tornada_feiners = gtfsdata.get_schedule_fgc(data_fgc, "S3", today)
s4_anada_feiners, s4_tornada_feiners = gtfsdata.get_schedule_fgc(data_fgc, "S4", today)
s8_anada_feiners, s8_tornada_feiners = gtfsdata.get_schedule_fgc(data_fgc, "S8", today)
s9_anada_feiners, s9_tornada_feiners = gtfsdata.get_schedule_fgc(data_fgc, "S9", today)

s1_anada_feiners, s1_tornada_feiners = gtfsdata.get_schedule_fgc(data_fgc, "S1", today)
s2_anada_feiners, s2_tornada_feiners = gtfsdata.get_schedule_fgc(data_fgc, "S2", today) """



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
print("Getting train schedules from PDF files...")
#r1_anada_feiners = tabuladata.get_tabula_schedule("R1", tornada=False)
#r1_tornada_feiners = tabuladata.get_tabula_schedule("R1", tornada=True)

# r2_anada_feiners = tabuladata.get_tabula_schedule("R2", tornada=False)
# r2_tornada_feiners = tabuladata.get_tabula_schedule("R2", tornada=True)

#r3_anada_feiners = tabuladata.get_tabula_schedule("R3", tornada=False)
#r3_tornada_feiners = tabuladata.get_tabula_schedule("R3", tornada=True)
                                            
#r4_anada_feiners = tabuladata.get_tabula_schedule("R4", tornada=False)
#r4_tornada_feiners = tabuladata.get_tabula_schedule("R4", tornada=True)

#r5_anada_feiners = tabuladata.get_tabula_schedule("R5", tornada=False)
#r5_tornada_feiners = tabuladata.get_tabula_schedule("R5", tornada=True)

#r6_anada_feiners = tabuladata.get_tabula_schedule("R6", tornada=False)
#r6_tornada_feiners = tabuladata.get_tabula_schedule("R6", tornada=True)

#r7_anada_feiners = tabuladata.get_tabula_schedule("R7", tornada=False)
#r7_tornada_feiners = tabuladata.get_tabula_schedule("R7", tornada=True)

#r8_anada_feiners = tabuladata.get_tabula_schedule("R8", tornada=False)
#r8_tornada_feiners = tabuladata.get_tabula_schedule("R8", tornada=True)


# # S3, S4, S8 and S9 (Pl España - Martorell Enllaç)
# url = "static/horarispdf/S8_Martorell_LA_octubre_20.pdf"
# schedule = tabula.read_pdf(url, pages=1, stream=True, lattice=False, multiple_tables=False, guess=False, area=area_s3s4s8s9_anada_feiners, pandas_options={'header': None})
# estacions_s3s4s8s9 = estacions_r5[:22] # First 22 stations of R4
# schedule[0].columns = estacions_s3s4s8s9
# s3s4s8s9_anada_feiners = helpers.cleanup_trainschedule(schedule[0])

# # S3, S4, S8 and S9 (Martorell Enllaç - Pl España)
# url = "static/horarispdf/S8_Martorell_LA_octubre_20.pdf"
# schedule = tabula.read_pdf(url, pages=1, stream=True, lattice=False, multiple_tables=False, guess=False, area=area_s3s4s8s9_tornada_feiners, pandas_options={'header': None})
# estacions_s3s4s8s9 = estacions_r5[:22] # First 22 stations of R4
# estacions_s3s4s8s9 = estacions_s3s4s8s9[::-1]
# schedule[0].columns = estacions_s3s4s8s9
# s3s4s8s9_tornada_feiners = helpers.cleanup_trainschedule(schedule[0])


# # S2, and S6 (Pl. Catalunya - Universitat Autònoma/Sabadell)
# s2s6_anada_feiners = []
# url = "static/horarispdf/Sabadell_s2_s6_gener_19.pdf"

#  #part 1
# partindex = 0 
# schedule = tabula.read_pdf(url, pages=1, stream=True, lattice=False, multiple_tables=False, guess=False, area=area_s2s6_anada_feiners[partindex], pandas_options={'header': None})
# schedule[0].columns = estacions_s2s6
# s2s6_anada_feiners.append(helpers.cleanup_trainschedule(schedule[0]))
# #display(s2s6_anada_feiners_1)

#  # part 2 (de 10:07 a 12:07)
# partindex = 1
# h_values = [10, 11, 12]
# schedule = tabula.read_pdf(url, pages=1, stream=True, lattice=True, multiple_tables=False, guess=False, area=area_s2s6_anada_feiners[partindex], pandas_options={'header': None})
# schedule[0].columns = estacions_s2s6
# df_temp = schedule[0]
# #df_temp = cleanup_trainschedule(schedule[0])
# df_temp = df_temp.dropna(axis=0, how='all') # Drop empty rows
# df_temp = helpers.generate_hours(df_temp, h_values)
# df_temp = helpers.fix_time_discontinuity(df_temp)
# s2s6_anada_feiners.append(helpers.filter_interval(df_temp, "10:07", "12:07"))

#  # Part 3 (de 12:21 a 14:20)
# partindex = 2
# schedule = tabula.read_pdf(url, pages=1, stream=True, lattice=False, multiple_tables=False, guess=False, area=area_s2s6_anada_feiners[partindex], pandas_options={'header': None, 'dtype': str})
# schedule[0].columns = estacions_s2s6
# s2s6_anada_feiners.append(helpers.cleanup_trainschedule(schedule[0]))

#  # Part 4 (de 14:24 a 16:36)
# partindex = 3
# h_values = [14, 15, 16]
# schedule = tabula.read_pdf(url, pages=1, stream=True, lattice=True, multiple_tables=False, guess=False, area=area_s2s6_anada_feiners[partindex], pandas_options={'header': None})
# schedule[0].columns = estacions_s2s6
# df_temp = schedule[0]
# df_temp = df_temp.dropna(axis=0, how='all') # Drop empty rows
# df_temp = helpers.generate_hours(df_temp, h_values)
# df_temp = helpers.fix_time_discontinuity(df_temp)
# s2s6_anada_feiners.append(helpers.filter_interval(df_temp, "14:24", "16:36"))

#  # Part 5 (de 16:44 a 18:48)
# partindex = 4
# h_values = [16, 17, 18]
# schedule = tabula.read_pdf(url, pages=1, stream=True, lattice=True, multiple_tables=False, guess=False, area=area_s2s6_anada_feiners[partindex], pandas_options={'header': None})
# schedule[0].columns = estacions_s2s6
# df_temp = schedule[0]
# df_temp = df_temp.dropna(axis=0, how='all') # Drop empty rows
# df_temp = helpers.generate_hours(df_temp, h_values)
# df_temp = helpers.fix_time_discontinuity(df_temp)
# s2s6_anada_feiners.append(helpers.filter_interval(df_temp, "16:44", "18:48"))

#  # Part 6 (de 19:00 a 21:00)
# partindex = 5
# h_values = [19, 20, 21]
# schedule = tabula.read_pdf(url, pages=1, stream=True, lattice=True, multiple_tables=False, guess=False, area=area_s2s6_anada_feiners[partindex], pandas_options={'header': None})
# schedule[0].columns = estacions_s2s6
# df_temp = schedule[0]
# df_temp = df_temp.dropna(axis=0, how='all') # Drop empty rows
# df_temp = helpers.generate_hours(df_temp, h_values)
# df_temp = helpers.fix_time_discontinuity(df_temp)
# s2s6_anada_feiners.append(helpers.filter_interval(df_temp, "19:00", "21:00"))

#  # Part 7 (de 21:15 a 23:17)
# partindex = 6
# schedule = tabula.read_pdf(url, pages=1, stream=True, lattice=True, multiple_tables=False, guess=False, area=area_s2s6_anada_feiners[partindex], pandas_options={'header': None})
# schedule[0].columns = estacions_s2s6
# df_temp = helpers.cleanup_trainschedule(schedule[0])
# s2s6_anada_feiners.append(df_temp.dropna(axis=0, how='all')) # Drop empty rows

#  # Part 8 (Last trains weekdays before weekdays)
# partindex = 7
# schedule = tabula.read_pdf(url, pages=1, stream=True, lattice=True, multiple_tables=False, guess=False, area=area_s2s6_anada_feiners[partindex], pandas_options={'header': None})
# schedule[0].columns = estacions_s2s6
# df_temp = helpers.cleanup_trainschedule(schedule[0])
# s2s6_anada_feiners.append(df_temp.dropna(axis=0, how='all')) # Drop empty rows

# # Concat all the parts together
# s2s6_anada_feiners = pd.concat(s2s6_anada_feiners, axis=0)
# s2s6_anada_feiners.reset_index(drop=True, inplace=True)
# del schedule, url, h_values

# s2s6_tornada_feiners = []

# url = "static/horarispdf/Sabadell_s2_s6_gener_19.pdf"

#  #part 1
# partindex = 0
# schedule = tabula.read_pdf(url, pages=2, stream=True, lattice=False, multiple_tables=False, guess=False, area=area_s2s6_tornada_feiners[partindex], pandas_options={'header': None})
# schedule[0].columns = estacions_s2s6[::-1]
# s2s6_tornada_feiners.append(helpers.cleanup_trainschedule(schedule[0]))

#  #part 2
# partindex = 1
# h_values = [9, 10, 11, 12]
# schedule = tabula.read_pdf(url, pages=2, stream=True, lattice=True, multiple_tables=False, guess=False, area=area_s2s6_tornada_feiners[partindex], pandas_options={'header': None})
# df_temp = schedule[0]
# df_temp.iloc[3, :] = df_temp.iloc[3, :].shift(1) # The 4th row appears shifted to the left... correct that manually
# df_temp.drop(columns=0, inplace=True) # And now drop the first column, which is all Nan
# df_temp.columns = estacions_s2s6[::-1]
# df_temp = helpers.generate_hours(df_temp, h_values)
# df_temp = helpers.fix_time_discontinuity(df_temp)
# s2s6_tornada_feiners.append(helpers.filter_interval(df_temp, "9:55", "12:10"))

#  #part 3
# partindex = 2
# schedule = tabula.read_pdf(url, pages=2, stream=True, lattice=False, multiple_tables=False, guess=False, area=area_s2s6_tornada_feiners[partindex], pandas_options={'header': None})
# schedule[0].columns = estacions_s2s6[::-1]
# s2s6_tornada_feiners.append(helpers.cleanup_trainschedule(schedule[0]))

#  #part 4
# partindex = 3
# h_values = [16, 17, 18, 19]
# schedule = tabula.read_pdf(url, pages=2, stream=True, lattice=True, multiple_tables=False, guess=False, area=area_s2s6_tornada_feiners[partindex], pandas_options={'header': None})
# df_temp = schedule[0]
# df_temp.iloc[-1, :] = df_temp.iloc[-1, :].shift(1) # The last row appears shifted to the left... correct that manually
# df_temp.drop(columns=0, inplace=True) # And now drop the first column, which is all Nan
# df_temp.columns = estacions_s2s6[::-1]
# df_temp = helpers.generate_hours(df_temp, h_values)
# df_temp = helpers.filter_interval(df_temp, "16:52", "19:15")
# s2s6_tornada_feiners.append(helpers.fix_time_discontinuity(df_temp))
# s2s6_tornada_feiners[partindex].drop(2, inplace=True) # Ugly workaround, delete row 2, which has a train previous to the starting period (the fix_time_discontinuity() should take care of these cases, but there's just one, so...)

#  #part5
# partindex = 4
# schedule = tabula.read_pdf(url, pages=2, stream=True, lattice=False, multiple_tables=False, guess=False, area=area_s2s6_tornada_feiners[partindex], pandas_options={'header': None})
# schedule[0].columns = estacions_s2s6[::-1]
# s2s6_tornada_feiners.append(helpers.cleanup_trainschedule(schedule[0]))

#  #part6
# partindex = 5
# h_values = [19, 20, 21]
# schedule = tabula.read_pdf(url, pages=2, stream=True, lattice=True, multiple_tables=False, guess=False, area=area_s2s6_tornada_feiners[partindex], pandas_options={'header': None})
# df_temp = schedule[0]
# df_temp.iloc[-1, :] = df_temp.iloc[-1, :].shift(1) # The last row appears shifted to the left... correct that manually
# df_temp.drop(columns=0, inplace=True) # And now drop the first column, which is all Nan
# df_temp.columns = estacions_s2s6[::-1]
# df_temp = helpers.generate_hours(df_temp, h_values)
# df_temp = helpers.fix_time_discontinuity(df_temp)
# s2s6_tornada_feiners.append(helpers.filter_interval(df_temp, "19:28", "21:16"))

# #part 7
# partindex = 6
# schedule = tabula.read_pdf(url, pages=2, stream=True, lattice=True, multiple_tables=False, guess=False, area=area_s2s6_tornada_feiners[partindex], pandas_options={'header': None})
# schedule[0].drop(columns=0, inplace=True)
# schedule[0].columns = estacions_s2s6[::-1]
# s2s6_tornada_feiners.append(helpers.cleanup_trainschedule(schedule[0]))

# #part 8 (Last trains, only Fridays and weekdays before public holidays)
# partindex = 7
# schedule = tabula.read_pdf(url, pages=2, stream=True, lattice=True, multiple_tables=False, guess=False, area=area_s2s6_tornada_feiners[partindex], pandas_options={'header': None})
# schedule[0].drop(columns=0, inplace=True)
# schedule[0].columns = estacions_s2s6[::-1]
# #s2s6_tornada_feiners.append(cleanup_trainschedule(schedule[0]))

# # Merge all the parts
# s2s6_tornada_feiners = pd.concat(s2s6_tornada_feiners, axis=0)
# s2s6_tornada_feiners.reset_index(drop=True, inplace=True)
# del schedule, url, h_values


## End of extraction from pdf with tabula

## Getting specific services within a line (e.g. R2 Nord, S2, etc.)

#r2_nord_anada_feiners, r2_centre_anada_feiners, r2_sud_anada_feiners = tabuladata.get_r2_nordcentresud(r2_anada_feiners)
#r2_nord_tornada_feiners, r2_centre_tornada_feiners, r2_sud_tornada_feiners = tabuladata.get_r2_nordcentresud(r2_tornada_feiners[r2_tornada_feiners.columns[::-1]]) # Reverse columns, so the function works
#r2_nord_tornada_feiners, r2_centre_tornada_feiners, r2_sud_tornada_feiners = [df[df.columns[::-1]] for df in [r2_nord_tornada_feiners, r2_centre_tornada_feiners, r2_sud_tornada_feiners]] # Reverse back

# Separating R5 pdf into R5, R50 and S4
#r5_r5_anada_feiners, r5_s4_anada_feiners, r5_r50_anada_feiners = tabuladata.get_r5_services(r5_anada_feiners)
#r5_r5_tornada_feiners, r5_s4_tornada_feiners, r5_r50_tornada_feiners = tabuladata.get_r5_services(r5_tornada_feiners)


# Separating R6 pdf into R6 & R60
#r6_r6_anada_feiners, r6_r60_anada_feiners, = tabuladata.get_r6_services(r6_anada_feiners)
#r6_r6_tornada_feiners, r6_r60_tornada_feiners = tabuladata.get_r6_services(r6_tornada_feiners)


# Get lines S3, S4, S8 and S9. S4 and S8 are identical in the S8_Martorell_LA_octubre_20.pdf file, but S4 goes further. We need to pass the df for S4 that we got from R5_Manresa_220x450_LA_octubre_20.pdf, where the whole S4 line is shown.
#s3_anada_feiners, s8_anada_feiners, s9_anada_feiners= tabuladata.get_s3_s8_s9_services(s3s4s8s9_anada_feiners, r5_s4_anada_feiners)
#s3_tornada_feiners, s8_tornada_feiners, s9_tornada_feiners= tabuladata.get_s3_s8_s9_services(s3s4s8s9_tornada_feiners, r5_s4_tornada_feiners)

# Merge the 3 lines into one, as we we'll display them as one line in the line view
#s3s8s9_anada_feiners = pd.concat([s3_anada_feiners, s8_anada_feiners, s9_anada_feiners])
#s3s8s9_tornada_feiners = pd.concat([s3_tornada_feiners, s8_tornada_feiners, s9_tornada_feiners])


# Gets lines S2 and S6 (Universitat Autonoma & Sabadell)
#s2_anada_feiners, s6_anada_feiners = tabuladata.get_s2_s6_services(s2s6_anada_feiners)
#s2_tornada_feiners, s6_tornada_feiners = tabuladata.get_s2_s6_services(s2s6_tornada_feiners)


print("...done")

#tz = pytz.timezone('US/Eastern') # zona horària de NYC,f or testing purposes 
tz = pytz.timezone('Europe/Madrid') # zona horària de Madrid 
#bcn_time = datetime.now(tz).strftime("%H:%M:%S") # hora de Barcelona en format hh:mm
#print(bcn_time)
#print(helpers.find_alltrains(r3_anada, bcn_time))

# Create Home Page Route
app = Flask(__name__)


# Start scheduled task 
scheduler = BackgroundScheduler()
scheduler.add_job(refresh_datasets, 'interval', days=7)
scheduler.add_job(refresh_schedules, 'cron', hour=3)
scheduler.add_job(prepare_r2, 'cron', hour=3)

scheduler.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/map')
def map():
    return render_template('map.html')

@app.route('/schedules')
def schedules():
    from collections import OrderedDict
    dfs = []
    for route, df_dict in schedules_dict.items():
        for direction, df in df_dict.items():
            # Replace NaN values with an empty string
            df = df.fillna('')
            column_order = df.columns.tolist()
            data = [OrderedDict(zip(column_order, [row[col] for col in column_order])) for row in df.to_dict('records')]
            dfs.append({'name': route+" "+direction, 'columns': column_order, 'data': data})
    return render_template('schedules.html', dfs=dfs)


@app.route('/data')
def generate_data():
    while True:
        bcn_time = datetime.now(tz).strftime("%H:%M:%S") # hora de Barcelona en format hh:mm
        print(bcn_time)
        with app.app_context():

            data = []
            routes = ['R1', 'R2', 'R2N', 'R2 Centre', 'R2S', 'R3', 'R4', 'R5', 'R50', 'R6', 'R60', 'R7', 'R8', 'S1', 'S2', 'S3', 'S4', 'S8', 'S9']
            for route in routes:
                data.append({
                    "trainLine": f"Rodalies {route}",
                    "positions1": helpers.find_alltrains(schedules_dict[route]['Anada'], bcn_time),
                    "positions2": helpers.find_alltrains(schedules_dict[route]['Tornada'], bcn_time, inverse=True)
                })

            """ data = [
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
                # {
                #     "trainLine": "Rodalies R5 R50 S4",
                #     "positions1": helpers.find_alltrains(r5_anada_feiners, bcn_time),
                #     "positions2": helpers.find_alltrains(r5_tornada_feiners, bcn_time, inverse=True)
                # },
                {
                    "trainLine": "Rodalies R5",
                    "positions1": helpers.find_alltrains(r5_anada_feiners, bcn_time),
                    "positions2": helpers.find_alltrains(r5_tornada_feiners, bcn_time, inverse=True)
                },
                {
                    "trainLine": "Rodalies S4",
                    "positions1": helpers.find_alltrains(s4_anada_feiners, bcn_time),
                    "positions2": helpers.find_alltrains(s4_tornada_feiners, bcn_time, inverse=True)
                },
                {
                    "trainLine": "Rodalies R50",
                    "positions1": helpers.find_alltrains(r50_anada_feiners, bcn_time),
                    "positions2": helpers.find_alltrains(r50_tornada_feiners, bcn_time, inverse=True)
                },
                # {
                #     "trainLine": "Rodalies R6 R60",
                #     "positions1": helpers.find_alltrains(r6_anada_feiners, bcn_time),
                #     "positions2": helpers.find_alltrains(r6_tornada_feiners, bcn_time, inverse=True)
                # },
                {
                    "trainLine": "Rodalies R6",
                    "positions1": helpers.find_alltrains(r6_anada_feiners, bcn_time),
                    "positions2": helpers.find_alltrains(r6_tornada_feiners, bcn_time, inverse=True)
                },
                {
                    "trainLine": "Rodalies R60",
                    "positions1": helpers.find_alltrains(r60_anada_feiners, bcn_time),
                    "positions2": helpers.find_alltrains(r60_tornada_feiners, bcn_time, inverse=True)
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
                    "trainLine": "Rodalies S1",
                    "positions1": helpers.find_alltrains(s1_anada_feiners, bcn_time),
                    "positions2": helpers.find_alltrains(s1_tornada_feiners, bcn_time, inverse=True),
                },
                {
                    "trainLine": "Rodalies S2",
                    "positions1": helpers.find_alltrains(s2_anada_feiners, bcn_time),
                    "positions2": helpers.find_alltrains(s2_tornada_feiners, bcn_time, inverse=True),
                }
            ] """
            print(data)
            yield f"data: {json.dumps(data)}\n\n"
            time.sleep(1)

@app.route('/stream-data')
def stream_data():
    return Response(stream_with_context(generate_data()), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9019, debug=False)