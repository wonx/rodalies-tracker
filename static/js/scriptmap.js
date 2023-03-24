var mySVG = document.getElementById("SVG");
var svgDoc;

mySVG.addEventListener("load", function() {
    svgDoc = mySVG.contentDocument;
    
    var stationPositions = [1.000, 0.9543, 0.9300, 0.9025, 
      0.869, 0.8457, 0.8232, 0.803, 
      0.7875, 0.7573, 0.7195, 0.6988, 
      0.6626, 0.6454, 0.6284, 0.6123,
      0.5905, 0.5273, 0.5001, 0.482,
      0.4291, 0.4142, 0.3993, 0.3895,
      0.3377, 0.321, 0.3039, 0.2733,
      0.2564, 0.2375, 0.2212, 0.1531,
      0.1375, 0.1085, 0.0935, 0.0785,
      0.0638, 0.0487, 0.034 , 0.0000]
    var pathId = "path9534"
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
  var r7stationPositions = [0, 0.1, 0.195, 0.497, 0.607, 0.722, 1];
  var r8stationPositions = [1, 0.915, 0.6837, 0.499, 0.4237, 0.208, 0.055, 0.0295, 0];
  //data.forEach(line => {
  //  setTrainMarkers(svgDoc, line.positions1[0], r3stationPositions, "green");
  //});
  console.log(data[3]) //data[2] es la linia R3
  color1 = "yellow"
  color2 = "orange"
  setTrainMarkers(svgDoc, "path9823_joined", data[2].positions1, data[2].positions2, r3stationPositions, color1, color2);
  setTrainMarkers(svgDoc, "path9534", data[3].positions1, data[3].positions2, r4stationPositions, color1, color2);
  setTrainMarkers(svgDoc, "path9845-4", data[4].positions1, data[4].positions2, r7stationPositions, color1, color2);
  setTrainMarkers(svgDoc, "path9845", data[5].positions1, data[5].positions2, r8stationPositions, color1, color2);

};

