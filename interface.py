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
######### Query Input #########################################################
##############################################################################

# Street Input:
address = st.text_input('Adress')

#preferences, the User is able to choose from:
preferences = st.selectbox(' Classes', options = ("shop", "office", "highway", "public_transport", "tourism", "amenity", "sport"))

# Radius Selector:


##############################################################################
######### Data to be used ####################################################
##############################################################################

#function that gets the location data:
location=get_location(address)

# DataFrame for our class selection:
df_cleaned=column_selection(location, preferences)
#st.write(df_cleaned)

# Subcat Selector:
subcolumn = st.multiselect('Preferences', options = (df_cleaned[preferences].unique()))

#Final DataFrame, that only shows the selected subcolumns:
#info_input=subcolumn_selection(df_cleaned, preferences, subcolumn)
#st.write(info_input)

#Renaming the Data to be used in the final frame:
#display_data = info_input.rename(columns = {'@lon': 'lon', '@lat':'lat', 'name': 'name'})

##############################################################################
### Data Cleaning Step 1 - Classes ###########################################
##############################################################################

###### this checks the classes available.
#checks_classes = df_cleaned[preferences].unique()

#defining the data to be displayed in the class data frame. We might be able to use subclass_data.
#class_data = info_input[info_input[preferences].isin(checks_classes)].reset_index()
class_data = df_cleaned

##############################################################################
## Data Cleaning Step 2 - Subclasses #########################################
##############################################################################

subclass_check = list(subcolumn)
#for i in range(len(subcolumn)):
  #  subclass_check.append(subcolumn[i])


t = df_cleaned[df_cleaned[preferences].isin(subclass_check)]
display_data = t.rename(columns = {'@lon': 'lon', '@lat':'lat', 'name': 'name'}).reset_index()
#st.write(display_data)
##############################################################################
################### Displaying Data  #########################################
##############################################################################


#giving each amenity a color:
color = {
         'bar' : 'red',
         'restaurant': 'blue'
         }

#initilaizing our map
map = folium.Map(location = location, zoom_start=14, control_scale=True)


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
