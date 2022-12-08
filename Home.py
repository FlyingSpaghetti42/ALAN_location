import streamlit as st
import folium
import os
from folium import plugins
import streamlit_folium as st_folium
from decimal import Decimal

from ALAN.public_t.public_transport import get_data
from ALAN.data.data_engineering import get_location, distance_calculation, raw_data, data_cleaning, filter_columns,format_subclass_transport
from ALAN.data.dash_board_basic import important_features, heat_map
from ALAN.data.colors import colors
from ALAN.data.distance import manhattan_distance_vectorized
from ALAN.routing.dataframe_builder import df_add_dist_dur, df_transform_dist_dur
from ALAN.routing.geodistances import routing_final, get_isochrone
from ALAN.routing.utils import speed, transform_km, transform_min

api_key = '5b3ce3597851110001cf6248f3265acccea64a2cbc94701747f1410f'

##############################################################################
######### Website Layout #####################################################
##############################################################################


# These are the width and height of each map displayed on the website
width = 1400
height = 800
width_df = 2140

st.set_page_config(page_title='ALAN',
                   layout="wide",
                   page_icon = 'ALAN/data/logo_header.png')




st.sidebar.markdown('___')
st.sidebar.header("Settings")
st.sidebar.markdown('___')


# Title of the Website:
st.title('ALAN - Automated Location Analysis')
st.markdown('___')



# Checkboxes on the sidebar:

# Displays informations regarding each step:
checker_help = st.sidebar.checkbox('How to use this app?')



# Helper: Selecting the routing function without a mode defined, leads to crash.
mode = 'walking'
# Helper: Needed, since the isochrones wont work otherwise.
time_min_km = speed('medium')





##############################################################################
######### Query Input ########################################################
##############################################################################

# Street Input:
if checker_help == True:
    st.markdown('1. Enter the adress of the Location you want to analyze')


address = st.text_input('Adress', 'Rudi Dutschke Straße 26', placeholder='Enter Text here')

checker_pt = st.sidebar.checkbox('Nearest Public Transport')

# Function that gets the lat and lon of the Adress used
location=get_location(address)


#This function defines the data to be used:
if address  != 'Please enter Adress':
    @st.cache()
    def get_dataframe(address, radius=2000):
        return data_cleaning(address, radius=radius)
    data = get_dataframe(address)

    data_copy = data.copy()

elif address  == 'Please enter Adress':
    pass

else:
    st.write('The address you entered is invalid. Please enter a valid address')



# Preference Input (displayed, once you entered a valid adress)
if address  != 'Please enter Adress':
    if checker_help == True:
        st.markdown('2. Please choose the types of Amneties, you want to include in your analysis')
    preferences = st.selectbox('**Classes**', options = ('Shopping', 'Office',
                                                    'Transport','Tourism',
                                                    'Amenity', 'Sports'))
    if checker_help == True:
        st.markdown('3. Please choose the subclasses, you want to include in your analysis (You can choose up to 5 different subclasses')


# DataFrame that only displays data from the choosen Class:
if address  != 'Please enter Adress':
    @st.cache()
    def select_class(df,preferences):
        if preferences == 'Transport':
            df_cleaned = filter_columns(df, preferences)
            df_cleaned = format_subclass_transport(df_cleaned)
        else:
            df_cleaned = filter_columns(df, preferences)
        return df_cleaned

    df_cleaned = select_class(data_copy,preferences)

public_transport = get_data(location,address, radius=2000)
display_tansport = public_transport[['Name', 'Distance', 'Modes of Transportation']]
display_tansport['Distance'] = display_tansport['Distance'].apply(lambda x: transform_km(x/1000))



# Subcategory Selection Box:

subcolumn = st.multiselect('**Preferences**', options = df_cleaned[preferences].unique(),
                                                         default= df_cleaned[preferences].unique()[0])


# Help Info:
if checker_help == True:
    st.markdown('4. If you want to use our routing service, please check the according box in the sidebar. Otherwise we will use an approximation method, to calculate the distance and duration ')

# Option to display Isochrones in the Map:
checker_iso = st.sidebar.checkbox('Isochrone',)



# Option to use the built-in routing function:
checker = st.sidebar.checkbox('Routing')
if checker == True:
    api_key = st.text_input('In order to use the Routing Service, please enter a Open Route Service API key')


# Choose the mode for the routing option (only available with routing enabled)
if checker == True or checker_iso == True:
    mode = st.selectbox('**Transportation Mode**n', options = ("bikeing",
                                                       "walking",
                                                       "driving"))


# Select your walking speed (only enabled while Routing disabled)
if checker == False and checker_iso == False:
    walker_speed = st.selectbox('**Walking Speed**', options = ("fast", "medium", "slow"))
    time_min_km = speed(walker_speed) # output of the function ->  walking speed in km/h


# Radius of Items to be displayed (no impact on the radius used for the analysis):
if checker_help == True:
    st.markdown('5. Select the radius of your analysis ')

st.markdown('____')
radius = st.slider('**Radius**', 500, 2000, 2000, 50)
st.markdown('____')

##############################################################################
## Data Cleaning Step 1 - Subclasses #########################################
##############################################################################

#Helpers: Routing / Building the final DF.
# Function to apply different colors per subclass-icon, to be displayed on the map:
subclass_check = list(subcolumn)
color = colors(subclass_check)

# Dict used to Display different Names, per Routing mode, in Map.
routing_dict = {"bikeing": 'Bike',
                "walking": 'Foot',
                "driving": 'Car'
                }

#for i in range(len(subcolumn)):
#    subclass_check.append(subcolumn[i])


# Function to define the data to be displayed in the map, aswell as the final DF:
display_data = df_cleaned[df_cleaned[preferences].isin(subclass_check)]



# While Routing is disabled, the following lines will calculate an approx distance as well as an approx duration:
if checker == False:
    display_data = distance_calculation(display_data,location,distance=radius)
    #display_data['Linear Distance'] = display_data['Linear Distance'].apply(lambda x: transform_km(x, True))

    distance = round(manhattan_distance_vectorized(location[0],location[1],display_data.Latitude, display_data.Longitude)/1000,2)

    #customize

    display_data['Distance Approx'] = distance
    #st.write(display_data)

    display_data['Walking time'] = display_data['Distance Approx'].apply(
                            lambda x: (x*60)/time_min_km).apply(
                            lambda x: transform_min(x,if_manhattan=True))

    display_data['Biking time'] = display_data['Distance Approx'].apply(
                            lambda x: (x*60)/13).apply(
                            lambda x: transform_min(x,if_manhattan=True))

    display_data['Car travel time'] = display_data['Distance Approx'].apply(
                            lambda x: (x*60)/18).apply(
                            lambda x: transform_min(x,if_manhattan=True))

    display_data['Distance Approx'] = display_data['Distance Approx'].apply(
                        lambda x: transform_km(x, if_m=False))

# While Routing is enabled, the following lines will calculate the actual distance / duration by mode of transportation:
else:
    try:
        df = distance_calculation(display_data,location,distance=radius)
        dist_mode, dur_mode= routing_final(df,location[0],location[1],api_key, mode = mode)

        df = df_add_dist_dur(df, dist_mode, dur_mode, mode)

        display_data = df_transform_dist_dur(df,mode).rename(
                                columns = {f'Distance {mode}': 'Distances',
                                        f'Duration {mode}': f'Duration ({routing_dict[mode]})'
                                                                })
    except KeyError:
            display_data = distance_calculation(display_data,location,distance=radius)
            #display_data['Linear Distance'] = display_data['Linear Distance'].apply(lambda x: transform_km(x, True))

            distance = round(manhattan_distance_vectorized(location[0],location[1],display_data.Latitude, display_data.Longitude)/1000,2)

            #customize

            display_data['Distance Approx'] = distance
            #st.write(display_data)

            display_data['Walking time'] = display_data['Distance Approx'].apply(
                                    lambda x: (x*60)/time_min_km).apply(
                                    lambda x: transform_min(x,if_manhattan=True))

            display_data['Biking time'] = display_data['Distance Approx'].apply(
                                    lambda x: (x*60)/13).apply(
                                    lambda x: transform_min(x,if_manhattan=True))

            display_data['Car travel time'] = display_data['Distance Approx'].apply(
                                    lambda x: (x*60)/18).apply(
                                    lambda x: transform_min(x,if_manhattan=True))

            display_data['Distance Approx'] = display_data['Distance Approx'].apply(
                                lambda x: transform_km(x, if_m=False))

##############################################################################
################### Displaying Data  #########################################
##############################################################################

# Helpers: Displaying the Data:
# Dict to define the zoom of the  map (while using the isochrones feature)
iso_dict = {'bikeing': 13,
            'walking':15,
            'driving':12
            }

# HTML Style definition for the tables used in the popup of each Icon.
html_style = '''
            <style>
            table, th, td {
            border: 1px solid black;
            border-collapse: collapse;
            }
            </style>
            '''

# Dict to define the Icons, that will be displayed per Class.
icon_dict = {'Shopping': 'shopping-bag',
             'Office': 'archive',
             'Transport': 'bycicle',
             'Tourism': 'hotel',
             'Sports': 'heart',
             'suburban': 'subway' ,
             'tram' : 'subway' ,
             'ferry': 'ship',
             'public': 'bus',
             'express': 'train' ,
             'regional': 'train',
            }


# Initilaizing our map (with isochrones disabled)
if checker_iso == False and checker_pt == False:
    map = folium.Map(location = location,
                zoom_start=14,
                control_scale=True,
                width=width,
                height = height)


# Initilaizing our map (with isochrones enabled)
elif checker_iso == True and checker_pt == False:
    map = folium.Map(location = location,
                zoom_start=iso_dict[mode],
                control_scale=True,
                width=width,
                height = height)


elif checker_iso == False and checker_pt == True:
    map = folium.Map(location = location,
                zoom_start=15,
                control_scale=True,
                width=width,
                height = height)




checker_heatmap = st.sidebar.checkbox('Display Heatmap')

if checker_heatmap == False and checker_pt == False:
    # Loop to get all the datapoints of the final dataframe into the Popups (using Approx Distance / Duration):

    for i in range(len(display_data)):
        try:
            html = f'''
            {html_style}
            <p style="font-family: Arial">
            <table>
                <tr>
                    <th>Amenity</th>
                    <td> {display_data[preferences][i]} </td>
                </tr>
                <tr>
                    <th>Name</th>
                    <td> {display_data['Location Name'][i]} </td>
                </tr>
                <tr>
                    <th>Adress</th>
                    <td>{display_data['Address'][i]}</td>
                </tr>
                    <tr>
                    <th>Phone Number</th>
                    <td>{display_data['Phone Number'][i]}</td>
                </tr>
                <tr>
                    <th> Distance </th>
                    <td>{display_data['Distance Approx'][i]}</td>
                </tr>
                <tr>
                    <th> Walking Time </th>
                    <td>{display_data['Walking time'][i]} </td>
                </tr>
            </table>
            </table>
            </p>'''

    # Loop to get all the datapoints of the final dataframe into the Popups (using Real Distance / Duration):
        except:
            html = f'''
            {html_style}
            <p style="font-family: Arial">
            <table>
                <tr>
                    <th>Name</th>
                    <td> {display_data['Location Name'][i]} </td>
                </tr>
                <tr>
                    <th>Adress</th>
                    <td>{display_data['Address'][i]}</td>
                </tr>
                </tr>
                <tr>
                    <th>Phone Number</th>
                    <td>{display_data['Phone Number'][i]}</td>
                </tr>
                <tr>
                    <th>Amenity</th>
                    <td>{display_data[preferences][i]}</td>
                </tr>
                <tr>
                    <th> Distance </th>
                    <td>{display_data['Distances'][i]}</td>
                </tr>
                <tr>
                    <th> Duration ({routing_dict[mode]}) </th>
                    <td> {display_data[f'Duration ({routing_dict[mode]})'][i]} </td>
                </tr>
            </table>
            </table>
            </p>'''



    # Block of the for loop, to get all the datapoints displayed as markers in the map:

        folium.Marker([display_data.Latitude[i],
                    display_data.Longitude[i]],
                    popup = folium.Popup(folium.IFrame(html=html, width=500, height=200), max_width=2000, max_height=500),
                    icon = folium.Icon(color = color[display_data[preferences][i]],
                                        icon = icon_dict[preferences],
                                        prefix='fa')).add_to(map)


    # Marker, to display your current location (/entered adress):
    folium.Marker([location[0],location[1]],
                    popup = folium.Popup(html=f'''{html_style}
                    <p style="font-family: Arial">
                    <table>
                        <tr>
                            <th>You</th>
                        </tr>
                        <tr>
                            <th>Current Location:</th>
                            <td>{address}</td>
                        </tr>
                    </table>
                    </p>
                    ''',width=200, height=100),
                    icon = folium.Icon(color='blue', icon='user', prefix = 'fa')).add_to(map)



    if checker_iso == False:
        folium.Circle(
        location=location,
        radius=radius, #hardcoded for now
        popup=f"{radius}m Radius", #hardcoded for now
        color="#696969",
        fill=True,
        fill_color="#696969",
        ).add_to(map)
    else:
        pass



elif checker_heatmap == True and checker_pt == False:

    map = heat_map(display_data, location)
    folium.Marker([location[0],location[1]],
                    popup = folium.Popup(html=f'''{html_style}
                    <p style="font-family: Arial">
                    <table>
                        <tr>
                            <th>You</th>
                        </tr>
                        <tr>
                            <th>Current Location:</th>
                            <td>{address}</td>
                        </tr>
                    </table>
                    </p>
                    ''',width=200, height=100),
                    icon = folium.Icon(color='blue', icon='user', prefix = 'fa')).add_to(map)


    folium.Circle(
    location=location,
    radius=radius, #hardcoded for now
    popup=f"{radius}m Radius", #hardcoded for now
    color="#696969",
    fill=True,
    fill_color="#696969",
    ).add_to(map)



    #st.map(display_map)


elif checker_heatmap == False and checker_pt == True:
    for i in range(len(public_transport)):
        html = f'''
        {html_style}
        <p style="font-family: Arial">
        <table>
            <tr>
                <th>Name</th>
                <td> {public_transport['Name'][i]} </td>
            </tr>
            <tr>
                <th>Distance</th>
                <td> {public_transport['Distance'][i]/1000} </td>
            </tr>
            <tr>
                <th>Adress</th>
                <td>{public_transport['Modes of Transportation'][i]}</td>
            </tr>
        </table>
        </table>
        </p>'''

    # Block of the for loop, to get all the datapoints displayed as markers in the map:

        folium.Marker([public_transport.lat[i],
                    public_transport.lon[i]],
                    popup = folium.Popup(folium.IFrame(html=html, width=500, height=200), max_width=2000, max_height=500),
                    icon = folium.Icon(color = 'green',
                                        icon = icon_dict['public'],
                                        prefix='fa')).add_to(map)


    # Marker, to display your current location (/entered adress):
    folium.Marker([location[0],location[1]],
                    popup = folium.Popup(html=f'''{html_style}
                    <p style="font-family: Arial">
                    <table>
                        <tr>
                            <th>You</th>
                        </tr>
                        <tr>
                            <th>Current Location:</th>
                            <td>{address}</td>
                        </tr>
                    </table>
                    </p>
                    ''',width=200, height=100),
                    icon = folium.Icon(color='blue', icon='user', prefix = 'fa')).add_to(map)


# Format of the Long and Lat (see function below)
fmtr = "function(num) {return L.Util.formatNum(num, 3);};"

# Displays the mouse positions lon / lat (see top right corner of the map)


# Displays Isochrones (how far do i get in 15/10/5 mins)
if checker_iso == True:
    results = get_isochrone(mode, [[location[1], location[0]]], api_key)
    for isochrone in results['features']:
        folium.Polygon(locations=[list(reversed(coord)) for coord in isochrone['geometry']['coordinates'][0]],
                    fill='00ff00',
                    popup=folium.Popup("Population: {} people".format(isochrone['properties']['total_pop'])),
                    opacity=0.5).add_to(map)

else:
    pass

st_folium.folium_static(map, width = width, height = height)

##############################################################################
################### Displaying Dataframes and Download Option  ###############
##############################################################################

# Before displaying dataframes, transform the distance column
display_data['Linear Distance'] = display_data['Linear Distance'].apply(
                            lambda x: transform_km(x, if_m=True))


if checker_pt == True:
    st.dataframe(display_tansport)


else:
    # Display dataframe with the distance and duration calculations
    st.subheader('Table 1: Subclass selection including distance and travel time estimates')
    st.markdown('The table shows the data as queried. If routing is not ticked, estimates are provided based on average speeds for the three modes of transport')
    st.dataframe(display_data, width = width_df)


    # Download Button for the first DF
    @st.experimental_memo

    def convert_df(df):
        return df.to_csv(index=False).encode('utf-8')

    csv_routing = convert_df(display_data)

    st.download_button(
    "Press to Download",
    csv_routing,
    "travel_time_query.csv",
    "text/csv",
    key='download-csv-routing'
    )

checker_semi = st.sidebar.checkbox('Semi Processed Location Data')
if checker_semi == True:
    # Display another dataframe, which contains the semi-processed data including the linear distance
    st.subheader('Table 2: Semi-processed Location Data')
    st.markdown('The table includes all classes, however, without routing information, as well as with only limited preprocessing.')

    ## Add the linear distance column (create copy of df just to be sure)
    #data_cp = data.copy()
    data_copy = distance_calculation(data_copy,location,distance=radius)
    data_copy['Linear Distance'] = data_copy['Linear Distance'].apply(lambda x: transform_km(x, if_m=True))

    st.dataframe(data_copy, width = width_df)
    csv_all_data = convert_df(data_copy)

    st.download_button(
    "Press to Download",
    csv_all_data,
    "all_data.csv",
    "text/csv",
    key='download-csv-all'
    )


##############################################################################
################### Kumar - Historic and Heatmap  ############################
##############################################################################
# get important features
checker_im_ft = st.sidebar.checkbox('Important Features')
if checker_im_ft == True:
    @st.cache()
    def get_important_features(location, radius=2000):
        if location is not ():
            impo_df = important_features(location, radius = radius)
            return impo_df
        else:
            return 'The table will show once a location is inputted'
    data = get_important_features(location, radius=2000)

    if type(data) != str:
        st.subheader('The following table displays the number of selected features available in the queried area')
        st.dataframe(data,width=1000)
    else:
        st.write(data)

    csv_data = convert_df(data)

    st.download_button(
    "Press to Download",
    csv_data,
    "data.csv",
    "text/csv",
    key='download-csv-data'
    )
