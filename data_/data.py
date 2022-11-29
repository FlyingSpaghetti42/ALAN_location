import pandas as pd

def cleaning():
    cities = pd.read_csv('data_/draft_data.csv',header = 0)
    info_input = pd.DataFrame(cities[['amenity', 'name','@lat','@lon', '@id']])
    info_input = info_input.rename(columns={'@lat':'lat','@lon':'lon','@id':'id'})
    return info_input
