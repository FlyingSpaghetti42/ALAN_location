#====================================
#===========    Home     ============
#====================================

import requests
import streamlit as st
#from streamlit_lottie import st_lottie
from streamlit_option_menu import option_menu
from geopy.geocoders import Nominatim
from prettymapp.geo import get_aoi
from prettymapp.osm import get_osm_geometries
from prettymapp.plotting import Plot
from prettymapp.settings import STYLES
from PIL import Image
import pandas as pd
import numpy as np
import cv2

from pages import Featues
from pages import About
#from pages import About_exp

#tapet-------------------





#explanation about the app----------------

#st.set_page_config(layout="wide")

st.set_page_config(page_title = "ALAN", page_icon = ":earth_africa:", layout = "wide"
                   ,initial_sidebar_state="expanded")

#change color---------------

original_title1 = '<p style="font-family:Courier; color: #ff007f; font-size: 40px;">ALAN, Help you to find vendors</p>'
st.markdown(original_title1 ,unsafe_allow_html=True)


original_title2 = '<p style="font-family:Courier; color: #ff007f; font-size: 20px;">Write street, Choose type of vendor and define Distance</p>'
st.markdown(original_title2, unsafe_allow_html=True)

#with st.container():
    #st.subheader("ALA, Help you to find vendors", textColor)
    #st.title("Write street, Choose type of vendor and define Distance")




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

maxval = 20.0
minval = 0.0

val = st.slider("km", minval, maxval)
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

st.map(df, zoom = val)


#menu----------------
# with st.set_page_config:
#     selected = option_menu(
#         menu_title = None,
#         options = sorted(["Home","Features","About"],reverse=True))


#     if selected == "Home":
#         st.title(f"you have selected {selected}")
#     if selected == "Features":
#         st.title(f"you have selected {selected}")
#     if selected == "About":
#         st.title(f"you have selected {selected}")



#connected pages ----------------------------------




# st.set_page_config(page_title="About", page_icon="📈")

# st.markdown("# About")
# st.sidebar.header("About")
# st.write(
#     """readme"""
# )

# progress_bar.empty()

# Streamlit widgets automatically run the script from top to bottom. Since
# this button is not connected to any other logic, it just causes a plain
# rerun.
#st.button("Re-run")
