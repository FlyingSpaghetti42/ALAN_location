import requests
#from geopy.distance import geodesic
import time
import requests

api_key = '5b3ce3597851110001cf62482818c293528942238de6f690d9ec3b11'

# add to streamlit: option to choose mode of mobility
# allow selection of only ONE type

# add to streamlit: instructions on how to set up own api_key
# as well as ask for api key when making a routing request
# instead of providing an api key (i.e.: input api-key, then request)

def routing(mode:str,
            lat_start:float,lon_start:float,
            lat_end:float,lon_end:float,
            api_key,
            url = 'https://api.openrouteservice.org/v2/directions/'):
    '''
    The function takes mode of transport as well coordinates for
    the start and end point of a routing request as input.

    The intermediate output is a geoJSON file, which subsequently.

    The default uses the publicly availbale, although API key
    restricted API. This contains some restrictions regarding
    requests. For instance for routing services, only 2000 requests
    per day are possible, as are 40 requests per minute. Thus, if
    more locations need to be queried there are two options.

    1) sticking to the public API (create key here:
    https://openrouteservice.org/plans/) activates sleeper functions
    in the code, which causes the code to sleep if the per minute
    request restriction is hit. It will continue after 60 seconds
    are passed

    2) one can install the api locally and use a localhost, which
    circumvents restrictions and gives possibilities for
    individualisation. Instructions can be found here:
    https://giscience.github.io/openrouteservice/. If this option is
    chosen, the url parameter should be specified like:
    'http://localhost:PORT/ors/v2/directions/'
    '''
    # specify mode and base-url
    modes_dict = {
        'biking': 'cycling-regular',
        'walking': 'foot-walking',
        'driving': 'driving-car'
    }
    url = url + modes_dict[mode]

    # specify the start and end coordinates
    ## start
    lat_start = lat_start
    lon_start = lon_start
    ## end
    lat_end = lat_end
    lon_end = lon_end


    # create params list for query
    params = {
        'api_key': api_key,
        'start': f'{lon_start},{lat_start}',
        'end': f'{lon_end},{lat_end}',
    }
    # make request
    result_geojson = requests.get(url,params=params)
    return result_geojson


def routing_mode_transport(lat_start:float,lon_start:float,
                           lat_end:float,lon_end:float,
                           api_key:str, mode:str=None):
    '''
    This function utilises the routing function to make the routing api request
    and outputs the geojsons to be used in the distance_duration_road
    function.
    '''
    # keep for the case one wants to input multiple selections
    # e.g. if want to run using localhost (if restrictions do
    # not apply)
    if type(mode) == list:
        modes_transport = ['foot-walking','cycling-regular','driving-car']
        modes_geojsons = []
        for mode in modes_transport:
            result = routing(mode,lat_start,lon_start,lat_end,lon_end,api_key)
            modes_geojsons.append(result)
        return modes_geojsons

    # if not list
    try:
        modes_geojsons = routing(mode,
                         lat_start,lon_start,
                         lat_end,lon_end,
                         api_key)
    except KeyError:
        print('Error: Mode needs to be specified!')
        return
    return modes_geojsons


def dist_dur_road(result_geojson):
    '''
    The function uses the output of the routing api request
    to extract the distance by road in km and the travel-time in
    minutes between the location of interest and an amenity
    utilising the mobility mode selected (walk, bike, e-bike)
    '''
    # return json and transform distance to km
    # duration to minutes
    distance = round((result_geojson.json()['features'
                          ][0]['properties'
                              ]['summary'
                               ]['distance']) / 1000, 2)

    duration = round((result_geojson.json()['features'
                          ][0]['properties'

                              ]['summary'
                               ]['duration']) / 60, 2)
    return distance, duration


def dist_dur_all_modes(lat_start:float,lon_start:float,
                       lat_end:float,lon_end:float,
                       api_key:str,mode:str = None):
    '''
    Output a tuple (or list of tuples for multiple mode selection)
    containing the distance and travel time for the selected mode
    of transport to one location
    '''
    geojsons = routing_mode_transport(lat_start,lon_start,lat_end,lon_end,api_key,mode)

    # keep for the case one wants to input multiple selections
    # e.g. if want to run using localhost (if restrictions do
    # not apply)
    if type(geojsons) == list:
        dist_dur = []
        for geojson in geojsons:
            dist_dur.append(dist_dur_road(geojson))
        return dist_dur

    dist_dur = dist_dur_road(geojsons)
    return dist_dur


def routing_final(df,
                  lat_start:float,lon_start:float,
                  api_key:str,
                  mode:str = None,
                  modes:bool = False):
    '''
    Takes a pandas dataframe as input, which contains the locations
    for which we want to compute the routing information (distance
    and duration for the mode selected).

    Outputs arrays containing for the selected mode the distance
    and the location, which in a next step can be added into to
    the dataframe (in case multiple mode selection is allowed, it
    also provides the code for multi-selection)

    In case one wants to use the function for multi-selection, the
    modes parameter needs to set to true. This will output

    mode: parameter to set the mode of transport selected
    modes: parameter bool that acts as a switch for multi-
    selection code
    '''
    # keep for the case one wants to input multiple selections
    # e.g. if want to run using localhost (if restrictions do
    # not apply)
    # create empty lists to hold the results of the calls
    if modes == True:
        dist_walk = []
        dur_walk = []
        dist_cycl_reg = []
        dur_cycl_reg = []
        dist_cycl_e = []
        dur_cycl_e =[]

        for i in range((df.shape[0])):
            lat_end, lon_end = float(df.loc[i,'Latitude']), float(df.loc[i,'Longitude'])
            request = dist_dur_all_modes(lat_start,lon_start,lat_end,lon_end,api_key)
            dist_walk.append(request[0][0])
            dur_walk.append(request[0][1])
            dist_cycl_reg.append(request[1][0])
            dur_cycl_reg.append(request[1][1])
            dist_cycl_e.append(request[2][0])
            dur_cycl_e.append(request[2][1])
        return dist_walk, dur_walk, dist_cycl_reg, dur_cycl_reg, dist_cycl_e, dur_cycl_e

    # regular case, for single selection:
    dist_mode = []
    dur_mode = []
    count = 0
    for i in range((df.shape[0])):
        count += 1
        if count % 10 == 0:
            print("Another 10 requests have been processed")
        if count % 40 == 0:
            print("Everything's fine, I just need to recharge my batteries")
            time.sleep(61)
        lat_end, lon_end = float(df.loc[i,'Latitude']), float(df.loc[i,'Longitude'])
        request = dist_dur_all_modes(lat_start,lon_start,lat_end,lon_end,api_key,mode)
        dist_mode.append(request[0])
        dur_mode.append(request[1])
    return dist_mode, dur_mode


def get_isochrone(mode:str,
                  locations, # at centre of isochrone (e.g.[[13.38895,52.515115]])
                  api_key:str,
                  url = 'https://api.openrouteservice.org/v2/isochrones/',
                  range_iso = [900,600,300],
                  range_type = 'time',
                  attributes = ["total_pop"]):
    '''
    This function does an api request to the ors api to get isochrones
    around the location of interest, showcasing for the mode selected
    how far one could get in 5, 10, and 15 minutes (areas of reachability)

    Parameters:
    url: the base url for the api request; the 'isochrones' endpoint specifies
        that we want to get the isochrones
    mode: options to choose - in the interface the user will select between:
        car, walk, bike, which in the function will transform to the parameter
        values 'driving-car','cycling-regular', and 'foot-walking'
    locations: here the location to searched will be inputted based on
        the coordinates generated when inputting the location.
        Input format: [[13.38895,52.515115]]; one could also pass multiple
        locations, however there is a limit of 5 set by ors
    range_iso: defines the isochrone distances, default is set to 5,10, and
        15 minutes.
    range_type: defines the unit of measurement used for defining the range_iso,
        alternative specification is: distance in meters
    attributes: also passes some population information for the isochrones
    '''
    modes_dict = {
        'biking': 'cycling-regular',
        'walking': 'foot-walking',
        'driving': 'driving-car'
    }
    mode = modes_dict[mode]
    base_url = url + mode
    headers = {
        'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
        'Authorization': api_key,
        'Content-Type': 'application/json; charset=utf-8'
    }

    body = {
        "locations": locations,
        "range":range_iso, #time in seconds
        "range_type":range_type,
        "attributes": attributes
    }

    result = requests.post(base_url,json=body,headers=headers).json()
    return result
