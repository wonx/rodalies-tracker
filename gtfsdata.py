# Read from google traffic files and create schedule for a line

# Routes: Train lines (S1, S2, R3, R2 south, etc.)
# Services: each of the possible services in a train route. e.g. from linia S1 towards Terrassa, there are ~15 different services, depending on the day. Each service can have many Trips.
# Trips: each of the trains that tranverses a route in the context of a service. (e.g. the train from 5:20 to 6:40 from Pl. Cat to Terrassa Nacions Unides). Each trip can only belong to one service.


import requests
import zipfile
import io
import pandas as pd
import numpy as np
from datetime import datetime

# Downloads datasets from the respective URL (cercanias and FGC) and returns them into a dict of dataframes
def download_and_load_data(url, network, csv_files):
    today = datetime.today().strftime('%Y%m%d')
    path = 'static/google_transit-schedule/' + network + '/'
    response = requests.get(url)

    with open(path+today + "-" + url.split("/")[-1], 'wb') as f:
        f.write(response.content)
    zip_file = zipfile.ZipFile(io.BytesIO(response.content))
    data = {}
    for csv_file in csv_files:
        data[csv_file] = pd.read_csv(zip_file.open(csv_file), keep_default_na=False)
    return data

def update_dataset(network):
    try:
        if network == 'cercanias':
            url = 'https://ssl.renfe.com/ftransit/Fichero_CER_FOMENTO/fomento_transit.zip'
            csv_files = ['calendar.txt', 'trips.txt', 'routes.txt', 'stop_times.txt', 'stops.txt']
        elif network == 'fgc':
            url = 'https://www.fgc.cat/google/google_transit.zip'
            csv_files = ['calendar_dates.txt', 'trips.txt', 'routes.txt', 'stop_times.txt', 'stops.txt']
        else:
            raise ValueError("Invalid network name. Choose either 'cercanias' or 'fgc'.")

        data = download_and_load_data(url, network, csv_files)

        return data

    except Exception as e:
        print("Error:", e)
        return None, None

# Example usage
#data = update_dataset("cercanias")
#if data is not None:
#    print(data.keys())


# Check if a date (in yyyymmdd format) is available in a schedule dataset
def check_date(date, dataset, network):
    if network == 'cercanias':
        df_calendar_dates = dataset['calendar.txt']
        available_dates = df_calendar_dates['start_date'].sort_values().unique()
    elif network == 'fgc':
        df_calendar_dates = dataset['calendar_dates.txt']
        available_dates = df_calendar_dates['date'].sort_values().unique()

    print("Available dates for dataset:" , available_dates)

    if int(date) in available_dates:
        print("We're good")
        return True
    else:
        print("Today's date is not available in the dataset, update the dataset")
        return False

# Example usage
#data_cer = update_dataset("cercanias")
#check_date(20230405, data_cer, 'cercanias')


# Topological sort algorithm to find the order of the stops based on the order of each individual list. Takes a list of lists as argument.
def deduce_stop_order(lst):
    print("Determining station order...")
    # Create an empty dictionary to hold the adjacency list of the graph
    graph = {}

    # Create a set of all stops
    stops = set(stop for sublst in lst for stop in sublst)

    # Initialize the indegree of each stop to 0
    indegree = {stop: 0 for stop in stops}

    # Populate the adjacency list and the indegree of each stop
    for sublst in lst:
        for i in range(len(sublst)-1):
            u, v = sublst[i], sublst[i+1]
            if u not in graph:
                graph[u] = set()
            if v not in graph:
                graph[v] = set()
            if v not in graph[u]:
                graph[u].add(v)
                indegree[v] += 1

    # Perform topological sort
    queue = [stop for stop in stops if indegree[stop] == 0]
    order = []
    while queue:
        u = queue.pop(0)
        order.append(u)
        if u in graph:
            for v in graph[u]:
                indegree[v] -= 1
                if indegree[v] == 0:
                    queue.append(v)

    return order

# Sorts a schedule in dataframe format
def sort_schedule(schedule):
    # find the columns with the fewer nan values
    first_valid_indices = schedule.isna().sum()

    # find the name of the leftmost column with no null values
    sorting_column = schedule.columns[first_valid_indices.argmin()]
    print("Sorting schedule by column:", sorting_column)

    # Sort by that column
    schedule = schedule.sort_values(by=[sorting_column], ascending=True, ignore_index=True)

    return schedule


def group_schedules(df): # Groups train schedules from the same route that go in the same direction. Returns list of df
    print("Grouping train services by route direction...")
    #print("elements in schedule: ", len(df))

    # If the list contains a single element, just return it and do nothing
    if len(df) ==1: return df

    # Check if a sequence if a subsequence of another list (in the same order)
    def is_subsequence(list1, list2):
        for i in range(len(list2)):
            if list2[i:i+len(list1)] == list1:
                return True
        return False

    # Generates all subsequences of length 2 of a list
    def generate_subsequences(lst):
        subsequences = []
        for i in range(len(lst) - 1):
            subsequence = [lst[i], lst[i+1]]
            subsequences.append(subsequence)
        return subsequences

    # Generates pair combinations, based on existing dataframes on the list
    import itertools
    def get_pairs(df):
        lst = range(0,len(df))
        pairs = list(itertools.combinations(lst, 2))
        return pairs
    
        
    # Group the tuples in a dict of tuples based on matching elements (e.g: turns {1: (0, 3), 2: (1, 2), 3: (1, 4), 4: (2, 4)} into  {1: (0, 3), 2: (1, 2, 4)})
    def group_tuple_values(tuple_dict):
        # Initialize an empty list to hold the groups of tuples
        groups = []
        
        # Iterate over each tuple in the input dictionary
        for current_tuple in tuple_dict.values():
            # Find all the groups that contain at least one element of the current tuple
            matching_groups = [g for g in groups if any(x in g for x in current_tuple)]
            
            # If no matching groups were found, create a new group with the current tuple
            if not matching_groups:
                groups.append(set(current_tuple))
            # If one or more matching groups were found, merge them into a new group
            else:
                new_group = set(current_tuple)
                for matching_group in matching_groups:
                    groups.remove(matching_group)
                    new_group |= matching_group
                groups.append(new_group)
        
        # Convert the list of groups to a dictionary with numbered keys
        output_dict = {}
        for i, group in enumerate(groups):
            output_dict[i+1] = tuple(sorted(group))
        
        # Return the resulting dictionary of groups
        return output_dict


    df_schedules = []
    groups = {}
    group_num = 0
    pairs = get_pairs(df)
    for pair in pairs:
        list1 = list(df[pair[0]].columns)
        list2 = list(df[pair[1]].columns)
        samegroup = False
        for subsequence in generate_subsequences(list1):
            if is_subsequence(subsequence, list2):
                samegroup = True

        if samegroup == True:
            group_num +=1
            groups.update({group_num: pair})

    groups = group_tuple_values(groups) # Merges groups with common elements

    #print(groups)

    for key, group in groups.items():
        #print("group", group)
        column_lst = [list(df[i].columns) for i in group]
        column_order = deduce_stop_order(column_lst) # Figure out correct stop order
        df_schedules.append(pd.concat([df[i] for i in group], axis=0, join='outer')) # Merge df in the group
        df_schedules[-1] = df_schedules[-1][column_order] # Apply the correct column order to the df we just appended

    return df_schedules


# Gets schedule for FGC trains. Takes a dict of datasets (generated with update_dataset()), the route name and the date as arguments.
def get_schedule_fgc(dataset, route, date):

    df_calendar_dates = dataset['calendar_dates.txt']
    df_trips = dataset['trips.txt']
    df_stop_times = dataset['stop_times.txt']
    df_stop_names = dataset['stops.txt']
    
    stop_dict = dict(zip(df_stop_names['stop_id'], df_stop_names['stop_name'])) # Dict with the stop code and stop name correspondence

    df_route = df_trips[df_trips['route_id'] == route]

    # Find out which services are available on that date:
    services = df_calendar_dates['service_id'][df_calendar_dates['date'] == date].unique()
    print(f"Services: for {date}: {services}")
    
    # For each service in that day, get the trips for the route we want
    df_service = df_route[df_route['service_id'].isin(services)]

    # For each destination/direction of the train (shape_id) in a service 
    destinations = df_service['shape_id'].unique()

    df_schedule = [pd.DataFrame() for i in range(len(destinations))]  # initialize as a list of dataframes
    for index, destination in enumerate(destinations):
        print("Destination", destination)
        df_service_destination = df_service[df_service['shape_id'] == destination]
        # For each unique trip in the service, print the stops
        trips = df_service_destination['trip_id'].unique()
        for trip in trips:
            df_trip = df_stop_times[df_stop_times['trip_id'] == trip]
            stops = df_trip['stop_id'].values
            arrivals = df_trip['arrival_time'].values
            trip = pd.DataFrame(arrivals).T  # convert the arrival times of the trip to a dataframe
            trip.columns = pd.Series(stops).map(stop_dict).tolist() # ADd the stop names as headers
            #trip.columns = stops  # set the column names to the stops
            df_schedule[index] = pd.concat([df_schedule[index], trip], axis=0, ignore_index=True)

    df_schedule = [sort_schedule(schedule) if not schedule.empty else schedule for schedule in df_schedule]
    
    return df_schedule

# Usage example:
#route = "S1"
#df = get_schedule_fgc(data_fgc, route, 20230405)
#for schedule in df:
#    display(schedule)


# Gets schedule for Cercanias trains. Takes a dict of datasets (generated with update_dataset()), the route name and the date as arguments.
def get_schedule_cercanias(dataset, route, date):
    
    df_calendar_dates = dataset['calendar.txt']
    df_trips = dataset['trips.txt']
    df_routes = dataset['routes.txt']
    df_stop_times = dataset['stop_times.txt']
    df_stop_names = dataset['stops.txt']
    
    routes_dict = dict(zip(df_routes['route_id'].astype(str).str.strip(), df_routes['route_short_name'].astype(str).str.strip()))
    stop_dict = dict(zip(df_stop_names['stop_id'], df_stop_names['stop_name'])) # Dict with the stop code and stop name correspondence

    # Remove unnecessary elements from the station name
    for key, value in stop_dict.items():
            stop_dict[key] = value.replace(' (apd)', '').replace(' (apt)', '').replace('Estación de tren ', '')

    route_ids = {i for i in routes_dict if routes_dict[i]==route} # Will return a set of the route codes. Usually two (go and back)

    print(f"The route {route} has the following route ids: {route_ids}")

    df_route = df_trips[df_trips['route_id'].isin(route_ids)]

    # Find out which services are available on that date:
    services = df_calendar_dates['service_id'][df_calendar_dates['start_date'] == date].unique()
    print(f"Services for date {date}: {services} (that includes all routes)")
    
    # For each service in that day, get the trips for the route we want
    df_service = df_route[df_route['service_id'].isin(services)]
    print(f"Services relevant to route {route} on {date}: {df_service['service_id'].unique()}")

    # If there are no services for that day and route, return empty list
    if len(df_service['service_id'].unique()) == 0: return []

    schedule_list = [] # List to store all the schedules. This is what will be returned at the end

    for index, route_id in enumerate(route_ids): # For each route (direction of the train)
        print("Processing route_id:", route_id)
        df_service_destination = df_service[df_service['route_id'] == route_id]

        # For each unique trip in the service, print the stops
        trips = df_service_destination['trip_id'].unique()
        print(f"Trips for route id {route_id}: {len(trips)}")
        if len(trips) == 0:
            print("Route is empty, skiping.")
            continue

        trip_list_df = []# Empty list that will contain a list of trips ini df form. (so, one-row dataframes)
        for trip in trips:
            df_trip = df_stop_times[df_stop_times['trip_id'] == trip]
            
            arrivals = df_trip['arrival_time'].values
            trip = pd.DataFrame(arrivals).T  # convert the arrival times of the trip to a dataframe
            stops = df_trip['stop_id'].values
            trip.columns = stops  # set the column names to the stops
            trip_list_df.append(trip)
            #display(trip)

        # Groups the trips in trip_list_df into dataframes # Breaks R7.
        for element in group_schedules(trip_list_df):
            schedule_list.append(element) # add a list of dataframes to that position of df_schedule (some lines, like R7 contain more than one schedule in a single service....)
        
        # Set the columns in order
        # (this is already being done inside the group_schedules())

    #print("Elements in schedule_list:", len(schedule_list))

    # If that resulted in more than 2 schedules (we want one for each direction of the route), group them again:
    if len(schedule_list) > 2: schedule_list = group_schedules(schedule_list)

    # Place the names of the stations in the columns
    schedule_list = [schedule.rename(columns=stop_dict) for schedule in schedule_list]

    # Finally, sort the schedules
    schedule_list = [sort_schedule(schedule) if not schedule.empty else schedule for schedule in schedule_list]

    return schedule_list

# Usage example:
#route = "R7"
#df = get_schedule_fgc(data_cer, route, 20230405)
#for schedule in df:
#    display(schedule)