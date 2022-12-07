
import requests

def how_far_do_i_get(location, address, max_dur):
    latitude = location[0]
    longitude = location[1]
    base = 'https://v5.bvg.transport.rest/stops/reachable-from?'
    params_1 = {'latitude' : latitude,
                'longitude' : longitude,
                'address' : address,
                'maxDuration' : max_dur
            }

    query_1 = requests.get(base,params_1).json()

    mins ={}
    stations = []

    for i in range(len(query_1)):
        stations=list()
        for x in range(len(query_1[i])):
            stations.append(query_1[i]['stations'][x]['name'])
        mins.update({query_1[i]['duration']:stations})

    return mins
