import requests
import streamlit as st
#from streamlit_lottie import st_lottie
from streamlit_option_menu import option_menu
from geopy.geocoders import Nominatim
from prettymapp.geo import get_aoi
from prettymapp.osm import get_osm_geometries
from prettymapp.plotting import Plot
from prettymapp.settings import STYLES

import pandas as pd
import numpy as np

#explanation about the app----------------

st.set_page_config(page_title = "ALA", page_icon = ":tada:", layout = "wide"
                   ,initial_sidebar_state="expanded")

#change color---------------

original_title1 = '<p style="font-family:Courier; color: #ff007f; font-size: 40px;">ALA, Help you to find vendors</p>'
st.markdown(original_title1, unsafe_allow_html=True)



original_title2 = '<p style="font-family:Courier; color: #ff007f; font-size: 20px;">Write street, Choose type of vendor and define Distance</p>'
st.markdown(original_title2, unsafe_allow_html=True)

#with st.container():
    #st.subheader("ALA, Help you to find vendors", textColor)
    #st.title("Write street, Choose type of vendor and define Distance")


#menu----------------
with st.sidebar:
    selected = option_menu(
        menu_title = None,
        options = ["Home","About"]
    )

    if selected == "Home":
        st.title(f"you have selected {selected}")
    if selected == "About":
        st.title(f"you have selected {selected}")

#writing box for streets --------------------



#type(location1)


sentence = st.text_input("Write street name:", 'Berlin, goltzstr 13')


geolocator = Nominatim(user_agent='automated_location_analysis')
location1 = geolocator.geocode(sentence)

f"""{location1}"""

location1.longitude
location1.latitude

#if sentence:
 #   st.write(my_model.predict(location1))

#choosing vendors------------

status = st.radio("Select vendor: ", ('shop', 'sport'))

if (status == 'shop'):
    st.success("shop")
    st.radio("Select vendor", ('Bar', 'resturant', 'coffie'))
else:
    st.success("sport")
    st.radio("Select vendor", ('boldering', 'football', 'gym'))


#slidebar---------

maxval = 2.0
minval = 0.0

val = st.slider("km", maxval, minval)
if val!=50:
    st.write("The Distance Km", val)


#map----------------

# aoi = get_aoi(address=location1, distance=500, rectangular=True)
# df = get_osm_geometries(aoi=aoi)


# fig = Plot(
#     df=df,
#     aoi_bounds=aoi.bounds,
#     draw_settings=STYLES["Peach"]
#     ).plot_all()

df = pd.DataFrame([[location1.longitude, location1.latitude]], columns = ['lon', 'lat'])

st.map(df, zoom = 10)
