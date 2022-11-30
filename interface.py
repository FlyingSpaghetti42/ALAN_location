import pandas as pd
import numpy as np
import pydeck as pdk
import streamlit as st
import folium
import streamlit_folium as st_folium
from data_.data import cleaning

##############################################################################
######### Map Layout #########################################################
##############################################################################

#defining the map layout:
st.set_page_config(page_title='ALAN',layout="wide", page_icon = ':sheep:')


##############################################################################
######### Data to be used ####################################################
##############################################################################

#Street, the user wants to search for:
'info_input = Here, the function for the query has to stand'

#getting the data: (PLACEHOLDER)
info_input = cleaning()

#Amenities, he can  search for:
classes = list(info_input.amenity.unique())

##############################################################################
######### Query Input ########################################################
##############################################################################

#Input params:
radius = st.slider('Radius',100,5000,1000,50)
#Selector on the webiste:
option = st.multiselect('Select amenit:', classes)

##############################################################################
### Data Cleaning Step 2 - Classes ###########################################
##############################################################################

#creating a checklist for our dataframe (only the amenities in this list will be kept in our DF):
checks = []
for i in range(len(option)):
    checks.append(option[i])


#giving each amenity a color:
color = {
         'bar' : 'red',
         'restaurant': 'blue'
         }


#defining the data to be displayed:
class_data = info_input[info_input['amenity'].isin(checks)].reset_index()

##############################################################################
## Data Cleaning Step 2 - Subclasses #########################################
##############################################################################


subclass = list(class_data.id.unique())
options = st.multiselect('Select amenit:', subclass)

checks_subclass = []
for i in range(len(options)):
    checks_subclass.append(options[i])

display_data = class_data[class_data['id'].isin(checks_subclass)].reset_index()


##############################################################################
################### Displaying Data  #########################################
##############################################################################


#initilaizing our map
map = folium.Map(location=[info_input.lat.mean(), info_input.lon.mean()], zoom_start=14, control_scale=True)


#getting all the selected datapoints into the map (we only display up to 100 datapoints)
for i in range(len(display_data)):
    folium.Marker([display_data["lat"][i],
                display_data["lon"][i]],
                popup=display_data["name"][i],
                icon = folium.Icon(color = color[display_data["amenity"][i]],
                                    icon = 'info-sign')).add_to(map)

#creating a radius:
folium.Circle(
    location=[info_input.lat.mean(),info_input.lon.mean()],
    radius=radius,
    popup=f"{radius }m Radius",
    color="#3186cc",
    fill=True,
    fill_color="#3186cc",
).add_to(map)


#displaying the map:
st_folium.folium_static(map, width = 1600, height = 1000)


st.dataframe(display_data, width = 1600)
