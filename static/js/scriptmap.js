var mySVG = document.getElementById("SVG");
var svgDoc;

mySVG.addEventListener("load", function() {
    svgDoc = mySVG.contentDocument;
    
    var stationPositions = [1.0, 0.9625, 0.9240, 0.8905, 0.8430, 0.7900, 0.7340, 0.6690, 0.6045, 0.5600, 0.5290, 0.4965, 0.4630, 0.4305, 0.3970, 0.3650, 0.3315, 0.2985, 0.2660, 0.2330, 0.1445, 0.0925, 0.0260, 0.00]
    var pathId = "path9516"
    //addStations(svgDoc, pathId, stationPositions);

    // Paths - lines correspondence in svg file:
    // R1: path9386
    // R2 nord: path9390
    // R2 centre: path9552
    // R2 sud: path9388
    // R3: path9823_joined
    // R4: path9534
    // R5: path9518
    // R50: path9518-1
    // S4: path9516
    // R6: path9514
    // R60: path9512 + path9514-9
    // R7: path9845-4
    // R8: path9845

    // Example usage: add a marker at station 2.5 (between station 2 and 3)
    //setTrainMarkers(svgDoc, 3.15, stationPositions, "green");
});

// Places two sets of positions on the train map. The positions of the stations need to be passed too, as well as the colors of the markers.
function setTrainMarkers(svgDoc, pathId, trainPositions1, trainPositions2, stationPositions, color1, color2) {
  var path = svgDoc.getElementById(pathId);
  var pathLength = path.getTotalLength();

  // Remove existing markers with class name "train-marker"
  var markers = path.parentNode.querySelectorAll(".train-marker_"+pathId);
  for (var i = markers.length - 1; i >= 0; i--) {
      markers[i].parentNode.removeChild(markers[i]);
  }

  // Set markers for a single set of train positions
  function setMarkers(trainPositions, color) {
    for (var i = 0; i < trainPositions.length; i++) {
      var [stationIndex, positionFraction = "0"] = trainPositions[i].toString().split(".");
      positionFraction = "0." + positionFraction;

      var markerPos = path.getPointAtLength(pathLength * (stationPositions[stationIndex]+(stationPositions[(parseInt(stationIndex)+1)]-stationPositions[stationIndex]) * positionFraction))

      var marker = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      marker.setAttribute("cx", markerPos.x);
      marker.setAttribute("cy", markerPos.y);
      marker.setAttribute("r", 3);
      marker.setAttribute("fill", color);
      marker.setAttribute("stroke", "black");
      marker.setAttribute("stroke-width", "1");
      marker.classList.add("train-marker_"+pathId);

      path.parentNode.appendChild(marker);
    }
  }

  // Set markers for train positions 1
  setMarkers(trainPositions1, color1);

  // Set markers for train positions 2
  setMarkers(trainPositions2, color2);
}

// Draws the position of the stations on the map. Not strictly necessary, but useful to determine their position
function addStations(svgDoc, pathId, stationPositions) {
  var path = svgDoc.getElementById(pathId);
  var pathLength = path.getTotalLength();

  for (var i = 0; i < stationPositions.length; i++) {
    var stationPos = path.getPointAtLength(pathLength * stationPositions[i]);
    
    var station = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    station.setAttribute("cx", stationPos.x);
    station.setAttribute("cy", stationPos.y);
    station.setAttribute("r", 3);
    station.setAttribute("fill", "red");

    path.parentNode.appendChild(station);
  }
}

const eventSource = new EventSource('/stream-data');
eventSource.onmessage = function(event) {
  //console.log(event);
  const data = JSON.parse(event.data);
  console.log(data);
  console.log(svgDoc)
  var r1stationPositions = [0.856, 0.7415, 0.6915, 0.658, 
    0.574, 0.416, 0.395, 0.373, 
    0.351, 0.33, 0.309, 0.2875, 
    0.267, 0.246, 0.225, 0.204, 
    0.183, 0.1625, 0.1415, 0.121, 
    0.103, 0.089, 0.072, 0.0565, 
    0.0395, 0.025, 0] // Per a continuar fins a Molins de Rei, afegir: 0.9085, 0.9385, 0.969, 1.0]
  var r2nordstationPositions = [0.000, 0.0355, 0.0645, 0.0930, 
    0.1230, 0.1520, 0.1825, 0.2120, 
    0.2405, 0.2720, 0.3000, 0.3240, 
    0.3475, 0.3715, 0.4495, 0.5215, 
    0.6085, 0.7120, 0.8295, 0.8705, 1.000]
  var r2centrestationPositions = [1.0, 0.9625, 0.931, 0.902, 
    0.8705, 0.7595, 0.6745, 0.5605, 
    0.424, 0.263, 0.2105, 0.0945, 0.05, 0]
  var r2sudstationPositions = [0.0000, 0.172, 0.284, 0.403, 
    0.456, 0.5510, 0.5870, 0.6280, 
    0.6600, 0.6960, 0.7485, 0.7832, 
    0.8250, 0.8670, 0.9070, 0.9490, 
    1.0000]
  var r3stationPositions = [0, 0.0935, 0.1335, 0.16, 0.2345, 
    0.256, 0.278, 0.2985, 0.3445, 
    0.3593, 0.3845, 0.4000, 0.4475, 
    0.4782, 0.539, 0.5621, 0.585, 
    0.608, 0.630, 0.653, 0.6985, 
    0.7165, 0.731, 0.7543, 0.7727, 
    0.791, 0.809, 0.8355, 0.872, 
    0.8903, 0.9085, 0.9268, 0.9451, 0.9815, 1];
  var r4stationPositions = [1.000, 0.9543, 0.9300, 0.9025, 
    0.869, 0.8457, 0.8232, 0.803, 
    0.7875, 0.7573, 0.7195, 0.6988, 
    0.6626, 0.6454, 0.6284, 0.6123,
    0.5905, 0.5273, 0.5001, 0.482,
    0.4291, 0.4142, 0.3993, 0.3895,
    0.3377, 0.321, 0.3039, 0.2733,
    0.2564, 0.2375, 0.2212, 0.1531,
    0.1375, 0.1085, 0.0935, 0.0785,
    0.0638, 0.0487, 0.034 , 0.0000]
  var r5stationPositions = [1.0, 0.9670, 0.9390, 0.9130, 
    0.8750, 0.8320, 0.7825, 0.7285, 
    0.6750, 0.6485, 0.6220, 0.5950, 
    0.5680, 0.5410, 0.5140, 0.4880, 
    0.4605, 0.4330, 0.4070, 0.3790, 
    0.3075, 0.2640, 0.2080, 0.1865, 
    0.1565, 0.1300, 0.1065, 0.0780, 
    0.0470, 0.0205, 0.00]
  var s4stationPositions = [1.0, 0.9625, 0.9240, 0.8905, 
    0.8430, 0.7900, 0.7340, 0.6690, 
    0.6045, 0.5600, 0.5290, 0.4965, 
    0.4630, 0.4305, 0.3970, 0.3650, 
    0.3315, 0.2985, 0.2660, 0.2330, 
    0.1445, 0.0925, 0.0260, 0.00]
  var r50stationPositions = [1.0, 0.9680, 0.9380, 0.9165, 
    0.8790, 0.8345, 0.7795, 0.7250, 
    0.6720, 0.6570, 0.6295, 0.6025, 
    0.5755, 0.5480, 0.5205, 0.4930, 
    0.4655, 0.4395, 0.4105, 0.3855, 
    0.3100, 0.2675, 0.2110, 0.1885, 
    0.1580, 0.1310, 0.1070, 0.0790, 
    0.0485, 0.0220, 0.00]    

  var r7stationPositions = [0, 0.1, 0.195, 0.497, 0.607, 0.722, 1];
  var r8stationPositions = [1, 0.915, 0.6837, 0.499, 0.4237, 0.208, 0.055, 0.0295, 0];
  //data.forEach(line => {
  //  setTrainMarkers(svgDoc, line.positions1[0], r3stationPositions, "green");
  //});
  //console.log(data[4]) //data[2] es la linia R3
  color1 = "yellow"
  color2 = "orange"

  setTrainMarkers(svgDoc, "path9386", data[0].positions1, data[0].positions2, r1stationPositions, color1, color2); // R1
  setTrainMarkers(svgDoc, "path9390", data[2].positions1, data[2].positions2, r2nordstationPositions, color1, color2); // R2 north
  setTrainMarkers(svgDoc, "path9552", data[3].positions1, data[3].positions2, r2centrestationPositions, color1, color2); // R2 centre
  setTrainMarkers(svgDoc, "path9388", data[4].positions1, data[4].positions2, r2sudstationPositions, color1, color2); // R2 south
  setTrainMarkers(svgDoc, "path9823_joined", data[5].positions1, data[5].positions2, r3stationPositions, color1, color2); //R3
  setTrainMarkers(svgDoc, "path9534", data[6].positions1, data[6].positions2, r4stationPositions, color1, color2); //R4
  setTrainMarkers(svgDoc, "path9518", data[8].positions1, data[8].positions2, r5stationPositions, color1, color2); //R5
  setTrainMarkers(svgDoc, "path9516", data[9].positions1, data[9].positions2, s4stationPositions, color1, color2); //R5
  setTrainMarkers(svgDoc, "path9518-1", data[10].positions1, data[10].positions2, r50stationPositions, color1, color2); //R50
  setTrainMarkers(svgDoc, "path9845-4", data[12].positions1, data[12].positions2, r7stationPositions, color1, color2); //R7
  setTrainMarkers(svgDoc, "path9845", data[13].positions1, data[13].positions2, r8stationPositions, color1, color2); //R8
};

