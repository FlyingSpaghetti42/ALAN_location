import streamlit as st

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
from data_engineering import data_cleaning, filter_columns, subcolumn_selection, get_location
from bs4 import BeautifulSoup
import requests
import folium
import io
from folium import plugins
import warnings
warnings.filterwarnings("ignore")

#load Dataset
# df_raw=raw_data("Rudi-Dutschke-Straße 26, 10969 Berlin")
df_cleaned=data_cleaning("Rudi-Dutschke-Straße 26, 10969 Berlin")
df_filter=filter_columns(df_cleaned,"Shopping")
df_final=subcolumn_selection(df_filter, "Shopping", ["Supermarket", "Hairdresser", "Clothes"])
location=get_location("Rudi-Dutschke-Straße 26, 10969 Berlin")
overpass_url = 'https://z.overpass-api.de/api/interpreter'
years=[2012,2013,2014,2015,2016,2017,2018,2019,2020,2021,2022]

##Function which gives the evolution of number of establishments based on year
# returns a tuple of lists: (years, counts)
#if the function stops in the middle, returns ([2022], [current_value])
def time_based_stats(location=(52.506883, 13.3913836),radius=2000, preference="amenity", subpreference="restaurant"):
    counts=[]
    try:
        for year in years:
            overpass_query=f'''[date:"{year}-01-01T00:00:00Z"]
            [out:xml][timeout:2400];
            (
            node[{preference}={subpreference}](around:{radius},{location[0]}, {location[1]});
            );
            out count;'''
            response = requests.get(overpass_url, params={'data': overpass_query})
            # print(year, BeautifulSoup(response.text).select("tag")[0]["v"])
            counts.append(int(BeautifulSoup(response.text).select("tag")[0]["v"],features="xml"))
        if len(counts)== len(years):
            return (years, counts)
    except:
        overpass_query=f'''
            [out:xml][timeout:2400];
            (
            node[{preference}={subpreference}](around:{radius},{location[0]}, {location[1]});
            );
            out count;'''
        response = requests.get(overpass_url, params={'data': overpass_query})
        return ([2022], [int(BeautifulSoup(response.text).select("tag")[0]["v"])])

#gives heatmap based on distribution of establishments in the datfarame taking
# longitude an dlatitude values from the dataframe
def heat_map(df,location=(52.506883, 13.3913836),radius=2000):
    heatmap_map = folium.Map([52.506883, 13.3913836], zoom_start=14)
    stationArr = df[['latitude', 'longitude']]
    # plot heatmap
    heatmap_map.add_children(plugins.HeatMap(stationArr, radius=14))
    return heatmap_map

#if time_bases_stats function worked, it takes its output and plots number of establishments vs the years
def create_yearbased_plot(counts_vs_years):
    plt.plot(counts_vs_years[0], counts_vs_years[1])
    # plt.ylim(100,500)
    # plt.xlim(2011, 2023,1)
    plt.xlabel("years")
    plt.ylabel("number of restaurants in 2000m radius")
    return plt

 ##lists few important features in the given radius
 ## searchs again with the api
 ##returns a dataframe with names and values
def important_features(location, radius=2000):
    overpass_url = 'https://z.overpass-api.de/api/interpreter'

    overpass_query = f"""
    [out:csv(
        ::id, amenity, shop, office, highway, public_transport, tourism, sport,name, ::lat, ::lon, 'contact:phone','contact:website', 'addr:city','addr:street','addr:housenumber',
        'addr:postcode', 'addr:suburb', 'addr:country'
      )];
    (node["amenity"~"doctors|subway|supermarket|pharmacy|fire_station| post_office|bank"](around:{radius},{location[0]},{location[1]});
     (node["station"="subway"](around:{radius},{location[0]},{location[1]});
    );
    out center;
    """
    response = requests.get(overpass_url,
                            params={'data': overpass_query})
    r=response.content

    rawData = pd.read_csv(io.StringIO(r.decode('utf-8')), delimiter='\t')
    k={"Doctors":rawData.amenity.value_counts()["doctors"],
      "Subway Stations":rawData.amenity.isna().sum(),
       "Pharmacy":rawData.amenity.value_counts()["pharmacy"],
       "Bank":rawData.amenity.value_counts()["bank"],
       "Police":rawData.amenity.value_counts()["police"],
       "Fire Stations":rawData.amenity.value_counts()["fire_station"],
       "Post Office":rawData.amenity.value_counts()["post_office"]
      }
    features_nearby=pd.DataFrame.from_dict(k, orient='index' ,columns=["Number of Establishments"])
    return features_nearby
