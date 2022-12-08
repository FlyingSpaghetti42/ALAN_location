import pandas as pd
import numpy as np
import requests
from ALAN.data.data_engineering import get_location, distance_calculation



def get_data(location, address, radius):
    location = get_location(address)
    latitude = round(location[0],3)
    longitude = round(location[1],3)
    url_nearby = 'https://v5.bvg.transport.rest/stops/nearby?'
    params_ = {'latitude' : latitude,
               'longitude' : longitude,
               'distance' : radius,
               'results' : 10
              }
    data_1 = requests.get(url_nearby,params_)
    query = data_1.json()
    df_name = []
    df_lat = []
    df_lon = []
    df_dist = []
    names ={}
    for i in range(len(query)):
        df_name.append(query[i]['name'])
        df_lat.append(query[i]['location']['latitude'])
        df_lon.append(query[i]['location']['longitude'])
        df_dist.append(query[i]['distance'])
    for i in range(len(df_name)):
        types = list()
        for key in query[i]['products']:
            if query[i]['products'][key] == True:
                types.append(key)
        types=tuple(types)
        names.update({query[i]['name']:list(types)})
    df = pd.DataFrame()
    df['Name'] = df_name
    df['lat'] = df_lat
    df['lon'] = df_lon
    df['Distance'] = df_dist
    df['Modes of Transportation'] = names.values()
    return df
