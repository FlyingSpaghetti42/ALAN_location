import streamlit as st
import folium
from folium import plugins
import streamlit_folium as st_folium
from ALAN.data.data_engineering import get_location, distance_calculation, raw_data, data_cleaning, filter_columns
from ALAN.data.colors import colors
from ALAN.data.distance import manhattan_distance_vectorized
from ALAN.routing.dataframe_builder import df_add_dist_dur, df_transform_dist_dur
from ALAN.routing.geodistances import routing_final, get_isochrone
from ALAN.routing.utils import speed

api_key = '5b3ce3597851110001cf62482818c293528942238de6f690d9ec3b11'

#try:
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
preferences = st.selectbox(' Classes', options = ('Shopping', 'Office',
                                                  'Traffic','Tourism',
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
    #@st.cache()
    def first():
        return data_cleaning(address, radius=2000)

    data = first()

    st.write(data)
    df_cleaned = filter_columns(data, preferences)

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

    distance = manhattan_distance_vectorized(location[0],location[1],display_data.Latitude, display_data.Longitude)

    #customize

    display_data['Walking time'] = display_data['Linear Distance'].apply(lambda x: (x*60)/time_min_km)

    display_data['Biking time'] = display_data['Linear Distance'].apply(lambda x: (x*60)/13000)

    display_data['Car travel time'] = display_data['Linear Distance'].apply(lambda x: (x*60)/18000)

##############################################################################
################### Getting Routes  ##########################################
##############################################################################

else:
    df = distance_calculation(display_data,location,distance=radius)
    dist_mode, dur_mode= routing_final(df,location[0],location[1],api_key, mode = mode)

    df = df_add_dist_dur(df, dist_mode, dur_mode)

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
        <tr>
            <th> Distance </th>
            <td>{round(display_data['Linear Distance'][i],2)} metres</td>
        </tr>
        <tr>
            <th> Walking Time </th>
            <td>{round(display_data['Walking time'][i],2)} minutes </td>
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

st_folium.folium_static(map, width = 1600, height = 1000)

#def color_coding(df):
#    return ['background-color:red'] * len(
#        df) if df.Longitude == loc
#
#    if loc == (display_data.Longitude , display_data.Latitude):
#        return ['background-color:green']
#    else: pass



st.dataframe(display_data, width = 1600)

@st.experimental_memo
def convert_df(df):
   return df.to_csv(index=False).encode('utf-8')


csv = convert_df(display_data)

st.download_button(
   "Press to Download",
   csv,
   "file.csv",
   "text/csv",
   key='download-csv'
)




#except:
#pass
