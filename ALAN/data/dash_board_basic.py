import streamlit as st

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
from ALAN.data.data_engineering import data_cleaning, filter_columns, subcolumn_selection, get_location
from bs4 import BeautifulSoup
import requests
import folium
import io
from folium import plugins
import warnings
warnings.filterwarnings("ignore")

##load Dataset
## df_raw=raw_data("Rudi-Dutschke-Straße 26, 10969 Berlin")
#df_cleaned=data_cleaning("Rudi-Dutschke-Straße 26, 10969 Berlin")
#df_filter=filter_columns(df_cleaned,"Shopping")
#df_final=subcolumn_selection(df_filter, "Shopping", ["Supermarket", "Hairdresser", "Clothes"])
#location=get_location("Rudi-Dutschke-Straße 26, 10969 Berlin")



##Function which gives the evolution of number of establishments based on year
# returns a tuple of lists: (years, counts)
#if the function stops in the middle, returns ([2022], [current_value])
def time_based_stats(location, preference, subpreference:str ,radius=2000):
    overpass_url = 'https://z.overpass-api.de/api/interpreter'
    years=[2012,2013,2014,2015,2016,2017,2018,2019,2020,2021,2022]
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
            way(around:{radius},{location[0]},{location[1]});
            relation(around:{radius},{location[0]},{location[1]});
            );
            out center;
            out count;'''
        response = requests.get(overpass_url, params={'data': overpass_query})
        return ([2022], [int(BeautifulSoup(response.text).select("tag")[0]["v"])])

#gives heatmap based on distribution of establishments in the datfarame taking
# longitude an dlatitude values from the dataframe
def heat_map(df,location):
    heatmap_map = folium.Map([location[0],location[1]], zoom_start=14)
    stationArr = df[['Latitude', 'Longitude']]
    # plot heatmap
    heatmap_map.add_children(plugins.HeatMap(stationArr, radius=14))
    return heatmap_map

#if time_bases_stats function worked, it takes its output and plots number of establishments vs the years
def create_yearbased_plot(counts_vs_years, subclass):
    plt.plot(counts_vs_years[0], counts_vs_years[1])
    plt.xlabel("Years")
    plt.ylabel(f"Number of {subclass}s in a 2000m radius")
    return plt

 ##lists few important features in the given radius
 ## searchs again with the api
 ##returns a dataframe with names and values
def important_features(location, radius=2000):
    overpass_url = 'https://z.overpass-api.de/api/interpreter'
    feat_dict={}
    overpass_query = f"""
    [out:csv(
        ::id, amenity, shop, office, highway, public_transport, tourism, sport,name, ::lat, ::lon, 'contact:phone','contact:website', 'addr:city','addr:street','addr:housenumber',
        'addr:postcode', 'addr:suburb', 'addr:country'
      )];
    (node["amenity"~"doctors|pharmacy|fire_station|post_office|bank|police"](around:{radius},{location[0]},{location[1]});
    node["station"="subway"](around:{radius},{location[0]},{location[1]}););
    out;
    """
    response = requests.get(overpass_url,
                            params={'data': overpass_query})
    r=response.content
#     print(r)
    rawData = pd.read_csv(io.StringIO(r.decode('utf-8')), delimiter='\t')


    if "doctors" in rawData.amenity.unique():
        feat_dict["Doctors"]=rawData.amenity.value_counts()["doctors"]
    else:
        feat_dict["Doctors"]=0

    feat_dict["Subway Stations"]=rawData.amenity.isna().sum()

    if "pharmacy" in rawData.amenity.unique():
        feat_dict["Pharmacy"]=rawData.amenity.value_counts()["pharmacy"]
    else:
        feat_dict["Pharmacy"]=0

    if "bank" in rawData.amenity.unique():
        feat_dict["Bank"]=rawData.amenity.value_counts()["bank"]
    else:
        feat_dict["Bank"]=0

    if "fire_station" in rawData.amenity.unique():
        feat_dict["Fire Stations"]=rawData.amenity.value_counts()["fire_station"]
    else:
        feat_dict["Fire Stations"]=0

    if "police" in rawData.amenity.unique():
        feat_dict["Police"]=rawData.amenity.value_counts()["police"]
    else:
        feat_dict["Police"]=0

    if "post_office" in rawData.amenity.unique():
        feat_dict["Post Office"]=rawData.amenity.value_counts()["post_office"]
    else:
        feat_dict["Post Office"]=0
    features_nearby=pd.DataFrame.from_dict(feat_dict, orient='index' ,columns=["Number of Establishments"])
    return features_nearby
