import streamlit as st
import folium
import os
from folium import plugins
import streamlit_folium as st_folium
from streamlit_option_menu import option_menu

from ALAN.data.data_engineering import get_location, distance_calculation, raw_data, data_cleaning, filter_columns,format_subclass_transport
from ALAN.data.dash_board_basic import important_features, heat_map
from ALAN.data.colors import colors
from ALAN.data.distance import manhattan_distance_vectorized
from ALAN.routing.dataframe_builder import df_add_dist_dur, df_transform_dist_dur
from ALAN.routing.geodistances import routing_final, get_isochrone
from ALAN.routing.utils import speed, transform_km, transform_min


api_key = os.environ.get('API_KEY')

#try:
##############################################################################
######### Map Layout #########################################################
##############################################################################

#defining the map layout:
st.set_page_config(page_title='ALAN',layout="wide", page_icon = ':cry:')

st.markdown("# ALAN-Automated-Location-Analysis")
st.sidebar.header("Home")

##############################################################################
######### Query Input #########################################################
##############################################################################

# Street Input:
address = st.text_input('Adress', 'Please Input the Adress')
#preferences, the User is able to choose from:
preferences = st.selectbox(' Classes', options = ('Shopping', 'Office',
                                                  'Transport','Tourism',
                                                  'Amenity', 'Sports'))
mode = st.selectbox(' Choose the mode', options = ("bikeing", "walking", "driving"))
# Radius Selector:
radius = st.slider('Select the Radius', 500, 2000, 2000, 50)

walker_speed = st.selectbox(' How fast do you walk', options = ("fast", "medium", "slow"))

checker = st.checkbox('Routing',)

time_min_km = speed(walker_speed)

##############################################################################
######### Data to be used ####################################################
##############################################################################

#function that gets the location data:
location=get_location(address)

# DataFrame for our class selection:
if address  != 'Please Input the Adress':
    # WHY IS THIS WRITTEN THIS WAY?
    @st.cache()
    def get_dataframe(address, radius=2000):
        return data_cleaning(address, radius=radius)
    data = get_dataframe(address)

    data_copy = data.copy()
    #st.write(data)

    @st.cache()
    def select_class(df,preferences):
        if preferences == 'Transport':
            df_cleaned = filter_columns(df, preferences)
            df_cleaned = format_subclass_transport(df_cleaned)
        else:
            df_cleaned = filter_columns(df, preferences)
        return df_cleaned

    df_cleaned = select_class(data_copy,preferences)
    #st.write(df_cleaned)

else:
    data = 0

# Cat Selector:



# Subcat Selector:
subcolumn = st.multiselect('Preferences', options = (df_cleaned[preferences].unique()))

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


display_data = df_cleaned[df_cleaned[preferences].isin(subclass_check)]

#display_data = t.rename(columns = {'longitude': 'lon', 'latitude':'lat', 'name': 'name'}).reset_index()

if checker == False:
    display_data = distance_calculation(display_data,location,distance=radius)
    #display_data['Linear Distance'] = display_data['Linear Distance'].apply(lambda x: transform_km(x, True))

    distance = manhattan_distance_vectorized(location[0],location[1],display_data.Latitude, display_data.Longitude)

    #customize

    display_data['Walking time'] = display_data['Linear Distance'].apply(lambda x: (x*60)/time_min_km).apply(lambda x: transform_min(x,if_manhattan=True))

    display_data['Biking time'] = display_data['Linear Distance'].apply(lambda x: (x*60)/13000).apply(lambda x: transform_min(x,if_manhattan=True))

    display_data['Car travel time'] = display_data['Linear Distance'].apply(lambda x: (x*60)/18000).apply(lambda x: transform_min(x,if_manhattan=True))

##############################################################################
################### Getting Routes  ##########################################
##############################################################################

else:
    df = distance_calculation(display_data,location,distance=radius)
    dist_mode, dur_mode= routing_final(df,location[0],location[1],api_key, mode = mode)

    df = df_add_dist_dur(df, dist_mode, dur_mode, mode)

    display_data = df_transform_dist_dur(df,mode)



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
#defining the html style of the boxes on the map
html_style = '''
<style>
table, th, td {
border: 1px solid black;
border-collapse: collapse;
}
</style>
'''

for i in range(len(display_data)):

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
        <tr>
            <th>Amenity</th>
            <td>{display_data[preferences][i]}</td>
        </tr>
    </table>
    </table>
    </p>'''
    folium.Marker([display_data.Latitude[i],
                display_data.Longitude[i]],
                popup = folium.Popup(folium.IFrame(html=html, width=500, height=200), max_width=2000, max_height=500),
                icon = folium.Icon(color = color[display_data[preferences][i]],
                                    icon = 'info-sign')).add_to(map)

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
                icon = folium.Icon(color='blue', icon='alien', prefix = 'fa')).add_to(map)



#creating a radius:
folium.Circle(
location=location,
radius=radius, #hardcoded for now
popup=f"{radius}m Radius", #hardcoded for now
color="#696969",
fill=True,
fill_color="#696969",
).add_to(map)

#displaying the map:
fmtr = "function(num) {return L.Util.formatNum(num, 3);};"

#map pointer, checks where the position is on map:


#loc = plugins.MousePosition(position='topright', separator=' , ',numDigits = 6,
#              lat_formatter=fmtr, lng_formatter=fmtr).add_to(map)


results = get_isochrone(mode, [[location[1], location[0]]], api_key)

checker_iso = st.checkbox('Isochrome',)
if checker_iso == True:
    for isochrone in results['features']:
        folium.Polygon(locations=[list(reversed(coord)) for coord in isochrone['geometry']['coordinates'][0]],
                    fill='00ff00',
                    popup=folium.Popup("Population: {} people".format(isochrone['properties']['total_pop'])),
                    opacity=0.5).add_to(map)

else:
    pass

st_folium.folium_static(map, width = 2140, height = 1000)

#def color_coding(df):
#    return ['background-color:red'] * len(
#        df) if df.Longitude == loc
#
#    if loc == (display_data.Longitude , display_data.Latitude):
#        return ['background-color:green']
#    else: pass

##############################################################################
################### Displaying Dataframes and Download Option  ################
##############################################################################

# before displaying dataframes, transform the distance column
display_data['Linear Distance'] = display_data['Linear Distance'].apply(lambda x: transform_km(x, if_m=True))

# display dataframe with the distance and duration calculations
st.subheader('Table 1: Subclass selection including distance and travel time estimates')
st.markdown('The table shows the data as queried. If routing is not ticked, estimates are provided based on average speeds for the three modes of transport')
st.dataframe(display_data, width = 2140)

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

# Display another dataframe, which contains the semi-processed data including the linear distance
st.subheader('Table 2: Semi-processed Location Data')
st.markdown('The table includes all classes, however, without routing information, as well as with only limited preprocessing.')

## Add the linear distance column (create copy of df just to be sure)
#data_cp = data.copy()
data_copy = distance_calculation(data_copy,location,distance=radius)
data_copy['Linear Distance'] = data_copy['Linear Distance'].apply(lambda x: transform_km(x, if_m=True))

st.dataframe(data_copy, width = 2140)
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

# important features:
## Add st.cache
st.subheader('The following table displays the number of selected features available in the queried area')
impo_df = important_features(location, radius = 2000)
st.dataframe(impo_df, width = 1000)

# display display_data as heatmap:
# LORENZ: Manage to Display Data
display_map = heat_map(display_data, location)
#st.map(display_map)
st_folium.folium_static(display_map, width = 2140, height = 1000)

# historic data:


#with st.set_page_config:
#    selected = option_menu(
#        menu_title = None,
#        options = sorted(["Features","About"],reverse=True))
#
#
#    # if selected == "Home":
#    #     st.title(f"you have selected {selected}")
#    if selected == "Features":
#        st.title(f"you have selected {selected}")
#    if selected == "About":
#        st.title(f"you have selected {selected}")
