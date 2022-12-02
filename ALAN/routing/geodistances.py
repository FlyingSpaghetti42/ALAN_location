
import requests
from geopy.distance import geodesic

def routing(mode,lat_start,lon_start,lat_end,lon_end,api_key):
    '''
    The function takes mode of transport as well coordinates for
    the start and end point of a routing request as input.

    The intermediate output is a geoJSON file, which subsequently
    '''
    # specify mode and base-url
    url = f'https://api.openrouteservice.org/v2/directions/{mode}'

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

def routing_mode_transport(lat_start,lon_start,lat_end,lon_end,api_key):
    '''
    This function utilises the routing function to make the routing api request
    and outputs the geojsons to be used in the distance_duration_road
    function.
    '''
    modes_transport = ['foot-walking','cycling-regular','cycling-electric']
    modes_geojsons = []
    for mode in modes_transport:
        result = routing(mode,lat_start,lon_start,lat_end,lon_end,api_key)
        modes_geojsons.append(result)
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

def dist_dur_all_modes(lat_start,lon_start,lat_end,lon_end,api_key):
    '''
    Puts all the other information together to output a list containing
    the distance and duration for 3 modes of transport (walk, cycle,
    e-cycle)
    '''
    geojsons = routing_mode_transport(lat_start,lon_start,lat_end,lon_end,api_key)
    dist_dur = []
    for geojson in geojsons:
        dist_dur.append(dist_dur_road(geojson))
    return dist_dur

def routing_final(df,lat_start,lon_start,api_key):
    # create empty lists to hold the results of the calls
    dist_walk = []
    dur_walk = []
    dist_cycl_reg = []
    dur_cycl_reg = []
    dist_cycl_e = []
    dur_cycl_e =[]

    for i in range((df.shape[0])):
        lat_end, lon_end = float(df.loc[i,'lat']), float(df.loc[i,'lon'])
        request = dist_dur_all_modes(lat_start,lon_start,lat_end,lon_end,api_key)
        dist_walk.append(request[0][0])
        dur_walk.append(request[0][1])
        dist_cycl_reg.append(request[1][0])
        dur_cycl_reg.append(request[1][1])
        dist_cycl_e.append(request[2][0])
        dur_cycl_e.append(request[2][1])
    return dist_walk, dur_walk, dist_cycl_reg, dur_cycl_reg, dist_cycl_e, dur_cycl_e

def distance_beeline(lat_start,lon_start,lat_end,lon_end):
    start = (lat_start, lon_start)
    end = (lat_end,lon_end)
    distance = geodesic(start,end).km
    return distance
