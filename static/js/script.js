function addTrainLine(lineName, lineColor, stations) {
    const trainLinesContainer = document.querySelector('.train-lines-container');
    const newTrainLine = document.createElement('div');
    newTrainLine.classList.add('train-line');
    newTrainLine.style.backgroundColor = lineColor; // Set the background color
    trainLinesContainer.appendChild(newTrainLine);
  
    const trainLineName = document.createElement('h2');
    trainLineName.classList.add('train-line__name');
    trainLineName.textContent = lineName;
    newTrainLine.appendChild(trainLineName);
  
    const circleContainer = document.createElement('div');
    circleContainer.classList.add('circle-container');
    newTrainLine.appendChild(circleContainer);
  
    stations.forEach((stationName) => {
      const circle = document.createElement('div');
      circle.classList.add('circle');
      circle.style.borderColor = lineColor;
      circleContainer.appendChild(circle);
  
      const circleText = document.createElement('div');
      circleText.classList.add('circle-text');
      circleText.textContent = stationName;
      circle.appendChild(circleText);
    });
  }
  

  function setTrainMarkers(lineName, positions1, positions2) {
    const trainLineElements = document.querySelectorAll('.train-line');
    const trainLineElement = Array.from(trainLineElements).find((element) => element.querySelector('.train-line__name').textContent === lineName);
    if (!trainLineElement) {
      console.error(`Train line '${lineName}' not found`);
      return;
    }
  
    const existingTrainMarkers = trainLineElement.querySelectorAll('.train-marker');
    existingTrainMarkers.forEach((marker) => marker.remove());
  
    [positions1, positions2].forEach((positions, index) => {
      const color = index === 0 ? '#ffcc66' : '#ff9966';
      const circleContainer = trainLineElement.querySelector('.circle-container');
      positions.forEach((position) => {
        const stationIndex = Math.floor(position);
        const fraction = position - stationIndex;
        const previousStation = circleContainer.children[stationIndex];
        const nextStation = circleContainer.children[stationIndex + 1];
        const distance = nextStation ? nextStation.offsetLeft - previousStation.offsetLeft : 0;
        const trainPosition = previousStation.offsetLeft + (distance * fraction);
        const newTrain = document.createElement('div');
        newTrain.classList.add('train-marker');
        newTrain.style.left = trainPosition + 'px';
        newTrain.style.backgroundColor = color;
        trainLineElement.appendChild(newTrain);
      });
    });
  }

addTrainLine('Rodalies R2', '#0fab4b', ["Maçanet-Massanes", "Hostalric", "Riells i Viabrea-Breda", "Gualba", "Sant Celoni", "Palautordera", "Llinars del Vallès", "Cardedeu", "Les Franqueses del Vallès-Granollers Nord", "Granollers Centre", "Montmeló", "Mollet-Sant Fost", "La Llagosta", "Montcada i Reixac", "Barcelona - Sant Andreu", "Barcelona-El Clot-Aragó", "Barcelona - Estació de França", "Barcelona-Passeig de Gràcia ", "Barcelona-Sants", "Bellvitge", "El Prat de Llobregat", "Aeroport", "Viladecans", "Gavà", "Castelldefels", "Platja de Castelldefels", "Garraf", "Sitges", "Vilanova i la Geltrú", "Cubelles", "Cunit", "Segur de Calafell", "Calafell", "Sant Vicenç de Calders"])

addTrainLine('Rodalies R3', '#e82d30', ["L'Hospitalet de Llobregat", "Barcelona-Sants", "Barcelona-Plaça Catalunya", "Barcelona-Arc de Triomf", "Barcelona-La Sagrera-Meridiana", "Sant Andreu Arenal", "Torre del Baró-Vallbona", "Montcada Bifurcació", "Montcada Ripollet", "Santa Perpètua de Mogoda-La Florida", "Mollet-Santa Rosa", "Parets del Vallès", "Granollers-Canovelles", "Les Franqueses del Vallès", "La Garriga", "Figaró", "Sant Martí de Centelles", "Centelles", "Balenyà-Els Hostalets", "Balenyà-Tona-Seva", "Vic", "Manlleu", "Torelló", "Borgonyà", "Sant Quirze de Besora", "La Farga de Bebié", "Ripoll", "Campdevànol", "Ribes de Freser", "Planoles", "Toses", "La Molina", "Urtx-Alp", "Puigcerdà","Latour-de-Carol-Enveig"]);
  
addTrainLine('Rodalies R8', '#810d6a', ['Martorell', 'Castellbisbal', 'Rubí', 'Sant Cugat del Vallès', 'Cerdanyola Universitat', 'Santa Perpètua de Mogoda - Riera de caldes', 'Mollet - Sant Fost', 'Montmeló', 'Granollers Centre']);


//setTrainMarkers('Rodalies R3', [1.0, 3.4, 13.8, 34], [2.5, 3.0, 7.2, 11.7, 33.98]);
//setTrainMarkers('Rodalies R8', [0.0, 0.6], [2.5, 2.0]);



const eventSource = new EventSource('/stream-data');
eventSource.onmessage = function(event) {
  console.log(event);
  const data = JSON.parse(event.data);
  console.log(data);
  data.forEach(line => {
    setTrainMarkers(line.trainLine, line.positions1, line.positions2);
  });
};