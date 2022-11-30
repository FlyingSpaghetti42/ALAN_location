import pandas as pd
import numpy as np
import pydeck as pdk
import streamlit as st
import folium
import streamlit_folium as st_folium
from data.data_engineering import get_location, get_complete_data, column_selection, subcolumn_selection
import io
import requests
import geopy

##############################################################################
######### Map Layout #########################################################
##############################################################################

#defining the map layout:
st.set_page_config(page_title='ALAN',layout="wide", page_icon = ':cry:')


##############################################################################
######### Data to be used ####################################################
##############################################################################

#Street, the user wants to search for:
address = st.text_input('Adress')
preferences = st.selectbox(' Preferences', options = ("shop", "office", "highway", "public_transport", "tourism", "amenity", "sport"))
location=get_location(address)

# DataFrame for our class selection
df_cleaned=column_selection(location, preferences)
#st.write(df_cleaned)


# DataFrame for our class selection
subcolumn = st.selectbox('Preferences', options = (df_cleaned[preferences]))


info_input=subcolumn_selection(df_cleaned, preferences, subcolumn)
#st.write(info_input)



##############################################################################
######### Query Input ########################################################
##############################################################################

#Input params:
#radius = st.slider('Radius',100,5000,1000,50)
#Selector on the webiste:

##############################################################################
### Data Cleaning Step 2 - Classes ###########################################
##############################################################################

###### this checks the classes.
checks_classes = df_cleaned[preferences].unique()

#giving each amenity a color:
color = {
         'bar' : 'red',
         'restaurant': 'blue'
         }


#defining the data to be displayed in the class data frame. We might be able to use subclass_data.
#class_data = info_input[info_input[preferences].isin(checks_classes)].reset_index()
class_data = df_cleaned

##############################################################################
## Data Cleaning Step 2 - Subclasses #########################################
##############################################################################

#subclass = list(subcolumn[preferences].unique())
#st.write(subclass)

#checks_subclass = info_input[preferences].unique()

#display_data = class_data[class_data['id'].isin(checks_subclass)].reset_index()
display_data = info_input.rename(columns = {'@lon': 'lon', '@lat':'lat', 'name': 'name'})
#st.write(display_data)
##############################################################################
################### Displaying Data  #########################################
##############################################################################


#initilaizing our map
map = folium.Map(location=[display_data.lat.mean(), display_data.lon.mean()], zoom_start=14, control_scale=True)


#getting all the selected datapoints into the map (we only display up to 100 datapoints)
for i in range(len(display_data)):
    folium.Marker([display_data.lat[i],
                display_data.lon[i]],
                popup=display_data['name'][i],
                icon = folium.Icon(color = 'red',
                                    icon = 'info-sign')).add_to(map)

#creating a radius:
folium.Circle(
    location=[display_data.lat.mean(),display_data.lon.mean()],
    radius=2000, #hardcoded for now
    popup=f"2000m Radius", #hardcoded for now
    color="#3186cc",
    fill=True,
    fill_color="#3186cc",
).add_to(map)


#displaying the map:
st_folium.folium_static(map, width = 1600, height = 1000)

st.dataframe(display_data, width = 1600)
