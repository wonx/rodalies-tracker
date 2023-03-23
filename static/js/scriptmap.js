var mySVG = document.getElementById("SVG");
var svgDoc;

mySVG.addEventListener("load", function() {
    svgDoc = mySVG.contentDocument;
    
    var stationPositions = [0, 0.0935, 0.1335, 0.16, 0.2345, 0.256, 0.278, 0.2985, 0.3445, 0.3593, 0.3845, 0.4000, 0.4475, 0.4782, 0.541, 0.5685, 0.597, 0.623, 0.6505, 0.6985, 0.7165, 0.731, 0.7543, 0.7727, 0.791, 0.809, 0.8355, 0.872, 0.8903, 0.9085, 0.9268, 0.9451, 0.9815, 1];
    //addStations(svgDoc, stationPositions);

    // Example usage: add a marker at station 2.5 (between station 2 and 3)
    //setTrainMarkers(svgDoc, 3.15, stationPositions, "green");
});

function setTrainMarkers(svgDoc, trainPositions1, trainPositions2, stationPositions, color1, color2) {
  var path = svgDoc.getElementById("path9823_joined");
  var pathLength = path.getTotalLength();

  // Remove existing markers with class name "train-marker"
  var markers = path.parentNode.querySelectorAll('.train-marker');
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
      marker.classList.add("train-marker");

      path.parentNode.appendChild(marker);
    }
  }

  // Set markers for train positions 1
  setMarkers(trainPositions1, color1);

  // Set markers for train positions 2
  setMarkers(trainPositions2, color2);
}

// Draws the position of the stations on the map. Not strictly necessary, but useful to determine their position
function addStations(svgDoc, stationPositions) {
  var path = svgDoc.getElementById("path9823_joined");
  var pathLength = path.getTotalLength();

  for (var i = 0; i < stationPositions.length; i++) {
    var stationPos = path.getPointAtLength(pathLength * stationPositions[i]);
    
    var station = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    station.setAttribute("cx", stationPos.x);
    station.setAttribute("cy", stationPos.y);
    station.setAttribute("r", 3);
    station.setAttribute("fill", "purple");

    path.parentNode.appendChild(station);
  }
}

const eventSource = new EventSource('/stream-data');
eventSource.onmessage = function(event) {
  //console.log(event);
  const data = JSON.parse(event.data);
  console.log(data);
  console.log(svgDoc)
  var r3stationPositions = [0, 0.0935, 0.1335, 0.16, 0.2345, 0.256, 0.278, 0.2985, 0.3445, 0.3593, 0.3845, 0.4000, 0.4475, 0.4782, 0.541, 0.5685, 0.597, 0.623, 0.6505, 0.6985, 0.7165, 0.731, 0.7543, 0.7727, 0.791, 0.809, 0.8355, 0.872, 0.8903, 0.9085, 0.9268, 0.9451, 0.9815, 1];
  //data.forEach(line => {
  //  setTrainMarkers(svgDoc, line.positions1[0], r3stationPositions, "green");
  //});
  console.log(data[2]) //data[2] es la linia R3
  setTrainMarkers(svgDoc, data[2].positions1, data[2].positions2, r3stationPositions, "yellow", "orange");
  //setTrainMarkers(svgDoc, data[2].positions2[0], r3stationPositions, "orange");
  
};