# rodalies-tracker

![](https://github.com/wonx/rodalies-tracker/blob/master/static/mapsquarescreenshot.png)

***rodalies-tracker*** an experiment to create a visualization of [Barcelona's commuter trains](https://en.wikipedia.org/wiki/Rodalies_de_Catalunya) in real time.

The commuter rail network is managed by two companies: [Renfe](https://en.wikipedia.org/wiki/Renfe) and [Ferrocarrils de la Generalitat (FGC)](https://en.wikipedia.org/wiki/Ferrocarrils_de_la_Generalitat_de_Catalunya), which together operate under the brand Rodalies de Catalunya.

Neither company offers an API where the position of each train can be tracked in real time. Instead, rodalies-tracker uses [*General Transit Feed Specification* (GTFS)](https://gtfs.org/) data that each operator provides to Google to map their routes on Google Maps. Therefore, rodalies-tracker does not reflect any delays in the trains. Actually, the only source information about delays or cancellations is currently twitter.

The application is composed of two parts: the backend, written in Python, reconstructs the train schedules for each line using GTFS data sources, and uses those schedules to interpolate the position of each train in a line/route for the current time. The frontend, written in Javascript and CSS, and published as a Flask app, places the positions of the trains in their route (in line view) or in the map (in map view). 

The schedules are recreated every night (so they account for weekends, holidays, and maintenance work on the lines), and the position of the trains is updated every second.

So, a couple things to keep in mind:

- This is just an experiment on visualizing data. I cannot guarantee its accuracy.

- It was done as a hobby and as a learning experience, and I do not have plans to maintain it indefinitely. So it might break at any time if Renfe or FGC do any substantial changes to their routes.
## Online demo:
- An instance of rodalies-tracker is currently accesible at: http://rodalies.marcpalaus.com
## How it works:

- It obtains publicly available data in GTFS format from the respective Renfe and FGC websites ([Renfe](https://data.renfe.com/dataset/horarios-cercanias), [FGC](https://www.fgc.cat/opendata/)). That data is periodically queried (currently once a week).

- The GTFS data is queried and schedules for each route/line are recreated. Some data cleaning and treatment of edge cases was required.

- The Python backend assigns an index to each station of a line. Then, based on the current day and time, finds out the position of each train that is currently circulating in a line. If a train is located between two stops, it also returns the % of the route between those two stops.

- The Flask app streams that data for each one of the lines. Several HTML templates use that information to display the data:
    - In line view, using Javascript and CSS, each the train line is dynamically created from a list of stations, and the positions are placed as markers on the line (yellow for outbound trains, orange for inbound trains) based on the stream of data from the Python backend.
    - In map view, using a SVG map of the train network as a base, markers are placed alongside each path of the SVG file. The location of each station in the map has been manually placed, and the positions provided by the backend are then translated to fractions of the lengths of the corresponding SVG path.
