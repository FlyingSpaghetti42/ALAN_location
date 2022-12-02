import streamlit as st
import folium
import pandas as pd
import streamlit_folium as st_folium
from data.data_engineering import get_location, column_selection, distance_calculation, subcolumn_selection
from data.colors import colors
from data.distance import manhattan_distance_vectorized
from routing.dataframe_builder import routing_limitation, df_add_dist_dur, df_transform_dist_dur, df_add_beeline, df_transform_beeline
from routing.geodistances import routing_final
api_key = '5b3ce3597851110001cf62482818c293528942238de6f690d9ec3b11'

try:
    ##############################################################################
    ######### Map Layout #########################################################
    ##############################################################################

    #defining the map layout:
    st.set_page_config(page_title='ALAN',layout="wide", page_icon = ':cry:')

    ##############################################################################
    ######### Query Input #########################################################
    ##############################################################################


    # Street Input:
    address = st.text_input('Adress', 'Please Input the Adress')

    #preferences, the User is able to choose from:
    preferences = st.selectbox(' Classes', options = ("shop", "office", "highway", "public_transport", "tourism", "amenity", "sport"))

    # Radius Selector:
    radius = st.slider('Select the Radius', 500, 2000, 2000, 50)

    walker_speed = st.selectbox(' How fast do you walk', options = ("fast", "medium", "slow"))

    checker = st.checkbox('Routing',)
    def speed():
        if walker_speed == 'fast':
            return (7000)
        elif walker_speed == 'medium':
            return (4000)
        elif walker_speed == 'slow':
            return (3000)

    time_min_km = speed()

    ##############################################################################
    ######### Data to be used ####################################################
    ##############################################################################

    #function that gets the location data:
    location=get_location(address)

    # DataFrame for our class selection:

    if address  != 'Please Input the Adress':
        @st.cache()
        def first():
            return column_selection(location, preferences)

        df_cleaned = first()

    else:
        df_cleaned = 0

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

    ##############################################################################
    ## Data Cleaning Step 2 - Subclasses #########################################
    ##############################################################################

    subclass_check = list(subcolumn)

    for i in range(len(subcolumn)):
        subclass_check.append(subcolumn[i])


    t = df_cleaned[df_cleaned[preferences].isin(subclass_check)]

    display_data = t.rename(columns = {'longitude': 'lon', 'latitude':'lat', 'name': 'name'}).reset_index()

    if checker == False:
        display_data = distance_calculation(display_data,location,distance=radius)

        distance = manhattan_distance_vectorized(location[0],location[1],display_data.lat, display_data.lon)

        #customize

        display_data['walking time'] = display_data.distance.apply(lambda x: (x*60)/time_min_km)

        display_data['biking time'] = display_data.distance.apply(lambda x: (x*60)/13000)

        display_data['E-Biking time'] = display_data.distance.apply(lambda x: (x*60)/18000)

        #display_data = subcolumn_selection(df_cleaned,preferences, subclass_check)

    ##############################################################################
    ################### Getting Routes  ##########################################
    ##############################################################################

    else:
        df = distance_calculation(display_data,location,distance=radius)
        df = routing_limitation(display_data)

        dist_walk, dur_walk, dist_cycl_reg, dur_cycl_reg, dist_cycl_e, dur_cycl_e= routing_final(df,location[0],location[1],api_key)

        df = df_add_dist_dur(df,
                        dist_walk,
                        dur_walk,
                        dist_cycl_reg,
                        dur_cycl_reg,
                        dist_cycl_e,
                        dur_cycl_e)

        display_data = df_transform_dist_dur(df)



    ##############################################################################
    ################### Displaying Data  #########################################
    ##############################################################################



    #giving each amenity a color:
    color = colors(subclass_check)
    #initilaizing our map
    map = folium.Map(location = location,
                zoom_start=14,
                control_scale=True)


    #getting all the selected datapoints into the map (we only display up to 100 datapoints)


    for i in range(len(display_data)):
        folium.Marker([display_data.lat[i],
                    display_data.lon[i]],
                    popup=display_data.name[i],
                    icon = folium.Icon(color = color[display_data[preferences][i]],
                                        icon = 'info-sign')).add_to(map)

        folium.Marker([location[0],location[1]],
                    popup = '<b>You</b>',
                    icon = folium.Icon(color='blue', icon='alien', prefix = 'fa')).add_to(map)

    #creating a radius:
    folium.Circle(
    location=location,
    radius=radius, #hardcoded for now
    popup=f"{radius}m Radius", #hardcoded for now
    color="#3186cc",
    fill=True,
    fill_color="#3186cc",
).add_to(map)


    #displaying the map:
    st_folium.folium_static(map, width = 1600, height = 1000)
    st.dataframe(display_data, width = 1600)

except:
    pass