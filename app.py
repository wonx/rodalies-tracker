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

#estacions_r5=["Plaça Espanya", "Magòria-La Campana", "Ildefons Cerdà", "Europa | Fira", "Gornal", "Sant Josep", "L’Hospitalet-Av. Carrilet", "Almeda", "Cornellà Riera", "Sant Boi", "Molí Nou-Ciutat Cooperativa", "Colònia Güell", "Santa Coloma de Cervelló", "Sant Vicenç dels Horts", "Can Ros", "Quatre Camins", "Pallejà", "Sant Andreu de la Barca", "El Palau", "Martorell Vila | Castellbisbal", "Martorell Central", "Martorell Enllaç", "Abrera", "Olesa de Montserrat", "Aeri de Montserrat", "Monistrol de Montserrat", "Castellbell i el Vilar", "Sant Vicenç | CastellGalí", "Manresa-Viladordis", "Manresa-Alta", "Manresa-Baixador"]
#estacions_s2s6=['Barcelona - Pl. Catalunya', 'Provença', 'Gràcia', 'Sant Gervasi', 'Muntaner', 'La Bonanova', 'Les Tres Torres', 'Sarrià', 'Peu del Funicular', 'Baixador de Vallvidrera', 'Les Planes', 'La Floresta', 'Valldoreix', 'Sant Cugat', 'Volpelleres', 'Sant Joan', 'Bellaterra', 'Universitat Autònoma', 'Sant Quirze', 'Can Feu | Gràcia', 'Sabadell Plaça Major', 'La Creu Alta', 'Sabadell Nord', 'Sabadell Parc del Nord']
#estacions_s1s5s7=['Barcelona - Pl. Catalunya', 'Provença', 'Gràcia', 'Sant Gervasi', 'Muntaner', 'La Bonanova', 'Les Tres Torres', 'Sarrià', 'Peu del Funicular', 'Baixador de Vallvidrera', 'Les Planes', 'La Floresta', 'Valldoreix', 'Sant Cugat', 'Mira-sol', 'Hospital General', 'Rubí', 'Les Fonts', 'Terrassa Rambla', 'Vallparadís Universitat', 'Terrassa Estació del Nord', 'Terrassa Nacions Unides']


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

    # Merge overlapping routes from FGC, for the simplified line view
    prepare_r5r50r6r60()

    # Process R2 routes into R2 North, R2 Center and R2 South they fit the paths in the map view.
    prepare_r2()

    print("...done.")
    return schedules_dict


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


# For the allroutes.html, combine several lines: (R5, R50, S3, S4, S8, S9) & (R6, R60)
def prepare_r5r50r6r60():
    global schedules_dict
    print("Merging R5, R50, S3, S4, S8 & S9")
    routes = ['R50', 'S3', 'S4', 'S8', 'S9']
    schedules_dict['R5 R50 S3 S4 S8 S9'] = schedules_dict['R5'].copy()
    for route in routes:
        for direction in ['Anada', 'Tornada']:
            schedules_dict['R5 R50 S3 S4 S8 S9'][direction] = pd.concat([schedules_dict['R5 R50 S3 S4 S8 S9'][direction], schedules_dict[route][direction]])

    # Sorting elements after concatenating
    schedules_dict['R5 R50 S3 S4 S8 S9']['Anada'] = gtfsdata.sort_schedule(schedules_dict['R5 R50 S3 S4 S8 S9']['Anada'])
    schedules_dict['R5 R50 S3 S4 S8 S9']['Tornada'] = gtfsdata.sort_schedule(schedules_dict['R5 R50 S3 S4 S8 S9']['Tornada'])

    print("Merging R6, R60")
    routes = ['R60']
    schedules_dict['R6 R60'] = schedules_dict['R6'].copy()
    for route in routes:
        for direction in ['Anada', 'Tornada']:
            schedules_dict['R6 R60'][direction] = pd.concat([schedules_dict['R6 R60'][direction], schedules_dict[route][direction]])

    # Sorting elements after concatenating
    schedules_dict['R6 R60']['Anada'] = gtfsdata.sort_schedule(schedules_dict['R6 R60']['Anada'])
    schedules_dict['R6 R60']['Tornada'] = gtfsdata.sort_schedule(schedules_dict['R6 R60']['Tornada'])

refresh_schedules()


print("...all done.")

#tz = pytz.timezone('US/Eastern') # zona horària de NYC, for testing purposes 
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
#scheduler.add_job(prepare_r2, 'cron', hour=3)

scheduler.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/alllines')
def alllines():
    return render_template('alllines.html')

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
            routes = list(schedules_dict.keys())
            for route in routes:
                data.append({
                    "trainLine": f"Rodalies {route}",
                    "positions1": helpers.find_alltrains(schedules_dict[route]['Anada'], bcn_time),
                    "positions2": helpers.find_alltrains(schedules_dict[route]['Tornada'], bcn_time, inverse=True)
                })

            print(data)
            yield f"data: {json.dumps(data)}\n\n"
            time.sleep(1)

@app.route('/stream-data')
def stream_data():
    return Response(stream_with_context(generate_data()), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9019, debug=False)