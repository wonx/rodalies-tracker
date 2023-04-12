var mySVG = document.getElementById("SVG");
var svgDoc;

mySVG.addEventListener("load", function() {
    svgDoc = mySVG.contentDocument;
    
    var stationPositions = [1.0, 0.9625, 0.9240, 0.8905, 0.8430, 0.7900, 0.7340, 0.6690, 0.6045, 0.5600, 0.5290, 0.4965, 0.4630, 0.4305, 0.3970, 0.3650, 0.3315, 0.2985, 0.2660, 0.2330, 0.1445, 0.0925, 0.0260, 0.00]
    var pathId = "path9516"
    //addStations(svgDoc, pathId, stationPositions);

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

  //console.log(data[18]) //data[2] es la linia R3
  color1 = "yellow"
  color2 = "orange"

  const pathDict = {
    "Rodalies R1": {
        "path": "path9386",
        "stationPositions": [1.000, 0.8650, 0.8070, 0.7700, 
          0.6710, 0.4870, 0.4610, 0.4360, 
          0.4110, 0.3850, 0.3610, 0.3370, 
          0.3120, 0.2880, 0.2630, 0.2390, 
          0.2140, 0.1910, 0.1660, 0.1410, 
          0.1210, 0.1040, 0.0850, 0.0680, 
          0.0480, 0.0280, 0.000]
    },
    "Rodalies R2N": {
        "path": "path9390",
        "stationPositions": [0.000, 0.0355, 0.0645, 0.0930, 
          0.1230, 0.1520, 0.1825, 0.2120, 
          0.2405, 0.2720, 0.3000, 0.3240, 
          0.3475, 0.3715, 0.4495, 0.5215, 
          0.6085, 0.7120, 0.8295, 0.8705, 1.000]
    },
    "Rodalies R2 Centre": {
        "path": "path9552",
        "stationPositions": [1.0, 0.9625, 0.931, 0.902, 
          0.8705, 0.7595, 0.6745, 0.5605, 
          0.424, 0.263, 0.2105, 0.0945, 0.05, 0]
    },
    "Rodalies R2S": {
        "path": "path9388",
        "stationPositions": [0.0000, 0.172, 0.284, 0.403, 
          0.456, 0.5510, 0.5870, 0.6280, 
          0.6600, 0.6960, 0.7485, 0.7832, 
          0.8250, 0.8670, 0.9070, 0.9490, 
          1.0000]
    },
    "Rodalies R3": {
        "path": "path9823_joined",
        "stationPositions": [0, 0.0935, 0.1335, 0.16, 
          0.2345, 0.256, 0.278, 0.2985, 
          0.3445, 0.3593, 0.3845, 0.4000, 
          0.4475, 0.4782, 0.539, 0.5621, 
          0.585, 0.608, 0.630, 0.653, 
          0.6985, 0.7165, 0.731, 0.7543, 
          0.7727, 0.791, 0.809, 0.8355, 
          0.872, 0.8903, 0.9085, 0.9268, 
          0.9451, 0.9815, 1]
    },
    "Rodalies R4": {
        "path": "path9534",
        "stationPositions": [1.000, 0.9543, 0.9300, 0.9025, 
          0.869, 0.8457, 0.8232, 0.803, 
          0.7875, 0.7573, 0.7195, 0.6988, 
          0.6626, 0.6454, 0.6284, 0.6123,
          0.5905, 0.5273, 0.5001, 0.482,
          0.4291, 0.4142, 0.3993, 0.3895,
          0.3377, 0.321, 0.3039, 0.2733,
          0.2564, 0.2375, 0.2212, 0.1531,
          0.1375, 0.1085, 0.0935, 0.0785,
          0.0638, 0.0487, 0.034 , 0.0000]
    },
    "Rodalies R5": {
        "path": "path9518",
        "stationPositions": [1.0, 0.9670, 0.9390, 0.9130, 
          0.8750, 0.8320, 0.7825, 0.7285, 
          0.6750, 0.6485, 0.6220, 0.5950, 
          0.5680, 0.5410, 0.5140, 0.4880, 
          0.4605, 0.4330, 0.4070, 0.3790, 
          0.3075, 0.2640, 0.2080, 0.1865, 
          0.1565, 0.1300, 0.1065, 0.0780, 
          0.0470, 0.0205, 0.00]
    },
    "Rodalies R50": {
        "path": "path9518-1",
        "stationPositions": [1.0, 0.9680, 0.9380, 0.9165, 
          0.8790, 0.8345, 0.7795, 0.7250, 
          0.6720, 0.6570, 0.6295, 0.6025, 
          0.5755, 0.5480, 0.5205, 0.4930, 
          0.4655, 0.4395, 0.4105, 0.3855, 
          0.3100, 0.2675, 0.2110, 0.1885, 
          0.1580, 0.1310, 0.1070, 0.0790, 
          0.0485, 0.0220, 0.00]   
    },
    "Rodalies R6": {
        "path": "path9514",
        "stationPositions": [0.00, 0.026, 0.0495, 0.0755, 
          0.108, 0.142, 0.177, 0.22, 
          0.2635, 0.3005, 0.322, 0.3445, 
          0.3655, 0.3875, 0.4085, 0.431, 
          0.452, 0.4745, 0.496, 0.5185, 
          0.5785, 0.613, 0.713, 0.7445, 
          0.7755, 0.808, 0.8405, 0.8725, 
          0.9035, 0.936, 0.9665, 1.0] 
    },
    "Rodalies R60": {
        "path": "path9514-9_joined",
        "stationPositions": [1.000, 0.974, 0.951, 0.92, 
          0.889, 0.855, 0.824, 0.779, 
          0.738, 0.691, 0.669, 0.646, 
          0.626, 0.603, 0.582, 0.56, 
          0.537, 0.516, 0.494, 0.472, 
          0.413, 0.379, 0.285, 0.254, 
          0.222, 0.191, 0.159, 0.127, 
          0.096, 0.064, 0.032, 0.00]
    },
    "Rodalies S1": {
      "path": "path14991_joined",
      "stationPositions": [1.000, 0.8620, 0.8300, 0.8020, 
        0.7720, 0.7430, 0.7120, 0.6830, 
        0.6520, 0.6230, 0.5940, 0.5620, 
        0.5340, 0.4830, 0.4410, 0.4040, 
        0.3020, 0.2210, 0.1740, 0.1270, 
        0.0840, 0.0000]
    },
    "Rodalies S2": {
      "path": "path15293_joined",
      "stationPositions": [1.0000, 0.8720, 0.8440, 0.8160, 
        0.7880, 0.7610, 0.7340, 0.7060, 
        0.6790, 0.6510, 0.6230, 0.5950, 
        0.5680, 0.5210, 0.4460, 0.3710, 
        0.3190, 0.2590, 0.2200, 0.1800, 
        0.1470, 0.1080, 0.0670, 0.000]
    },
    "Rodalies S3": {
      "path": "path9522-1",
      "stationPositions": [1.0, 0.949, 0.894, 0.805, 
        0.729, 0.6530, 0.602, 0.508, 
        0.409, 0.25, 0.199, 0.152, 
        0.1, 0.054, 0.00]
    },
    "Rodalies S4": {
      "path": "path9516",
      "stationPositions": [1.0, 0.9625, 0.9240, 0.8905, 
        0.8430, 0.7900, 0.7340, 0.6690, 
        0.6045, 0.5600, 0.5290, 0.4965, 
        0.4630, 0.4305, 0.3970, 0.3650, 
        0.3315, 0.2985, 0.2660, 0.2330, 
        0.1445, 0.0925, 0.0260, 0.00]
    },
    "Rodalies S5": {
      "path": "path9807-0",
      "stationPositions": [1.0000, 0.7320, 0.6740, 0.6160, 
        0.5590, 0.5000, 0.4420, 0.3890, 
        0.3290, 0.2720, 0.2130, 0.1560, 
        0.1010, 0.0000]
    },
    "Rodalies S6": {
      "path": "path15271_joined",
      "stationPositions": [1.0000, 0.8230, 0.7870, 0.7500, 
        0.7120, 0.6730, 0.6370, 0.5980, 
        0.5620, 0.5220, 0.4850, 0.4460, 
        0.4100, 0.3460, 0.2490, 0.1560, 
        0.0860, 0.0000]
    },
    "Rodalies S7": {
      "path": "path9807",
      "stationPositions": [1.0000, 0.8000, 0.7590, 0.7170, 
        0.6730, 0.6300, 0.5880, 0.5470, 
        0.5050, 0.4610, 0.4180, 0.3760, 
        0.3330, 0.2620, 0.2020, 0.1480, 
        0.0000]
    },
    "Rodalies S8": {
      "path": "path9512-2",
      "stationPositions": [1.000, 0.9590, 0.9230, 0.8680, 
        0.8210, 0.7640, 0.7210, 0.6520, 
        0.5830, 0.4980, 0.4630, 0.4290, 
        0.3940, 0.3590, 0.3250, 0.2900, 
        0.2560, 0.2210, 0.1860, 0.1510, 
        0.0570, 0.000]
    },
    "Rodalies S9": {
      "path": "path9522",
      "stationPositions": [1.0, 0.948, 0.895, 0.814, 
        0.747, 0.67, 0.617, 0.521, 
        0.427, 0.288, 0.243, 0.196, 
        0.146, 0.098, 0.052, 0.0]
    },
    "Rodalies R7": {
      "path": "path9845-4",
      "stationPositions": [0.000, 0.0450, 0.0900, 0.1310, 
        0.1730, 0.3360, 0.4050, 0.4520, 
        0.5750, 0.6130, 0.6500, 0.6860, 
        0.8050, 0.8490, 0.8920, 1.000]


    },
    "Rodalies R8": {
      "path": "path9845",
      "stationPositions": [1, 0.915, 0.6837, 0.499, 
        0.4237, 0.208, 0.055, 0.0295, 0]
    }
  };

  for (let i = 0; i < data.length; i++) {
    if (data[i].trainLine in pathDict) {
        setTrainMarkers(svgDoc, pathDict[data[i].trainLine].path, data[i].positions1, data[i].positions2, pathDict[data[i].trainLine].stationPositions, color1, color2);
    }
  }
};
