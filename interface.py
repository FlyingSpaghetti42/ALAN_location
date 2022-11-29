import pandas as pd
import numpy as np
import pydeck as pdk
import streamlit as st
import folium
import streamlit_folium as st_folium
from data_.data import cleaning




st.set_page_config(layout="wide")
#creating a dictionary to get different colors per amenity:


# calling the cleaning function to get our data in the interface frame:
info_input = cleaning()

#defining the options, the user is able to choose amenities from:
amenities = list(info_input.amenity.unique())

#Selector on the webiste:
option = st.multiselect('Select amenit:', amenities)
st.write(option)

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
display_data = info_input[info_input['amenity'].isin(checks)].reset_index()


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
    radius=2000,
    popup="Laurelhurst Park",
    color="#3186cc",
    fill=True,
    fill_color="#3186cc",
).add_to(map)


#displaying the map:
st_folium.folium_static(map, width = 1600, height = 1000)
