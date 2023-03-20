# Import Required Modules
from flask import Flask, render_template, jsonify, Response, stream_with_context
import pandas as pd
import helpers
import tabula
from datetime import datetime
import time
import pytz 
import json


estacions_r2=("Maçanet-Massanes", "Hostalric", "Riells i Viabrea-Breda", "Gualba", "Sant Celoni", "Palautordera", "Llinars del Vallès", "Cardedeu", "Les Franqueses del Vallès-Granollers Nord", "Granollers Centre", "Montmeló", "Mollet-Sant Fost", "La Llagosta", "Montcada i Reixac", "Barcelona - Sant Andreu", "Barcelona-El Clot-Aragó", "Barcelona - Estació de França", "Barcelona-Passeig de Gràcia ", "Barcelona-Sants", "Bellvitge", "El Prat de Llobregat", "Aeroport", "Viladecans", "Gavà", "Castelldefels", "Platja de Castelldefels", "Garraf", "Sitges", "Vilanova i la Geltrú", "Cubelles", "Cunit", "Segur de Calafell", "Calafell", "Sant Vicenç de Calders")
estacions_r3=("L'Hospitalet de Llobregat", "Barcelona-Sants", "Barcelona-Plaça Catalunya", "Barcelona-Arc de Triomf", "Barcelona-La Sagrera-Meridiana", "Sant Andreu Arenal", "Torre del Baró-Vallbona", "Montcada Bifurcació", "Montcada Ripollet", "Santa Perpètua de Mogoda-La Florida", "Mollet-Santa Rosa", "Parets del Vallès", "Granollers-Canovelles", "Les Franqueses del Vallès", "La Garriga", "Figaró", "Sant Martí de Centelles", "Centelles", "Balenyà-Els Hostalets", "Balenyà-Tona-Seva", "Vic", "Manlleu", "Torelló", "Borgonyà", "Sant Quirze de Besora", "La Farga de Bebié", "Ripoll", "Campdevànol", "Ribes de Freser", "Planoles", "Toses", "La Molina", "Urtx-Alp", "Puigcerdà","Latour-de-Carol-Enveig")
estacions_r8=('Martorell', 'Castellbisbal', 'Rubí', 'Sant Cugat del Vallès', 'Cerdanyola Universitat', 'Santa Perpètua de Mogoda - Riera de caldes', 'Mollet - Sant Fost', 'Montmeló', 'Granollers Centre')

area_r3_anada_feiners = (555, 10, 1500, 960)
area_r3_tornada_feiners = (557, 10, 1450, 960)
area_r2_anada_feiners = (630, 10, 2450, 955)
area_r2_tornada_feiners = (630, 10, 2450, 955)
area_r8_anada = (468, 10, 1300, 950)
area_r8_tornada = (1625, 10, 2300, 950)

# R8 (Martorell-Granollers)
url = "https://rodalies.gencat.cat/web/.content/02_Horaris/horaris/R8.pdf"
schedule = tabula.read_pdf(url, pages=1, stream=True, lattice=False, multiple_tables=True, area=area_r8_anada)
schedule[0].columns = estacions_r8
r8_anada = helpers.cleanup_trainschedule(schedule[0])

# R8 (Granollers-Martorell)
url = "https://rodalies.gencat.cat/web/.content/02_Horaris/horaris/R8.pdf"
schedule = tabula.read_pdf(url, pages=1, stream=True, lattice=False, multiple_tables=True, area=area_r8_tornada)
schedule[0].columns = estacions_r8[::-1]
r8_tornada = helpers.cleanup_trainschedule(schedule[0])
print(r8_tornada)

# R2 (Maçanet - St. Vicenç de Calders)
url = "https://rodalies.gencat.cat/web/.content/02_Horaris/horaris/R2.pdf"
schedule = tabula.read_pdf(url, pages=1, stream=True, lattice=False, multiple_tables=True, area=area_r2_anada_feiners)
schedule[0].columns = estacions_r2
r2_anada = helpers.cleanup_trainschedule(schedule[0])

# R2 (St. Vicenç de Calders - Maçanet)
url = "https://rodalies.gencat.cat/web/.content/02_Horaris/horaris/R2.pdf"
schedule = tabula.read_pdf(url, pages=2, stream=True, lattice=False, multiple_tables=True, area=area_r2_tornada_feiners)
schedule[0].columns = estacions_r2[::-1]
r2_tornada = helpers.cleanup_trainschedule(schedule[0])

# R3 (Hospitalet-Vic)
url = "https://rodalies.gencat.cat/web/.content/02_Horaris/horaris/R3.pdf"
schedule = tabula.read_pdf(url, pages=1, stream=True, lattice=False, multiple_tables=True, area=area_r3_anada_feiners)
schedule[0].columns = estacions_r3
r3_anada = helpers.cleanup_trainschedule(schedule[0])

# R3 (Vic-Hospitalet)
url = "https://rodalies.gencat.cat/web/.content/02_Horaris/horaris/R3.pdf"
schedule = tabula.read_pdf(url, pages=2, stream=True, lattice=False, multiple_tables=True, area=area_r3_tornada_feiners)
schedule[0].columns = estacions_r3[::-1]
r3_tornada = helpers.cleanup_trainschedule(schedule[0])


tz = pytz.timezone('Europe/Madrid') # zona horària de Madrid 
#bcn_time = datetime.now(tz).strftime("%H:%M:%S") # hora de Barcelona en format hh:mm
#print(bcn_time)
#print(helpers.find_alltrains(r3_anada, bcn_time))

# Create Home Page Route
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def generate_data():
    while True:
        bcn_time = datetime.now(tz).strftime("%H:%M:%S") # hora de Barcelona en format hh:mm
        print(bcn_time)
        with app.app_context():
            data = [
                {
                    "trainLine": "Rodalies R3",
                    "positions1": helpers.find_alltrains(r3_anada, bcn_time),
                    "positions2": helpers.find_alltrains(r3_tornada, bcn_time, inverse=True)
                },
                {
                    "trainLine": "Rodalies R2",
                    "positions1": helpers.find_alltrains(r2_anada, bcn_time),
                    "positions2": helpers.find_alltrains(r2_tornada, bcn_time, inverse=True)
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
    app.run(host='0.0.0.0', port=9018, debug=True)