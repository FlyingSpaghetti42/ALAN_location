import streamlit as st
import folium
from folium import plugins
import streamlit_folium as st_folium
from data.data_engineering import get_location, column_selection, distance_calculation
from data.colors import colors
from data.distance import manhattan_distance_vectorized
from routing.dataframe_builder import routing_limitation, df_add_dist_dur, df_transform_dist_dur
from routing.geodistances import routing_final
from routing.utils import speed

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
preferences = st.selectbox(' Classes', options = ("shop", "office", "highway", "public_transport", "tourism", "amenity", "sport"))

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
    @st.cache()
    def first():
        return column_selection(location, preferences)

    df_cleaned = first()

else:
    df_cleaned = 0


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


t = df_cleaned[df_cleaned[preferences].isin(subclass_check)]

display_data = t.rename(columns = {'longitude': 'lon', 'latitude':'lat', 'name': 'name'}).reset_index()

if checker == False:
    display_data = distance_calculation(display_data,location,distance=radius)

    distance = manhattan_distance_vectorized(location[0],location[1],display_data.lat, display_data.lon)

    #customize

    display_data['walking time'] = display_data.distance.apply(lambda x: (x*60)/time_min_km)

    display_data['biking time'] = display_data.distance.apply(lambda x: (x*60)/13000)

    display_data['Car Travel time'] = display_data.distance.apply(lambda x: (x*60)/18000)

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
            <td> {display_data['name'][i]} </td>
        </tr>
        <tr>
            <th>Adress</th>
            <td>{display_data['address'][i]}</td>
        </tr>
        <tr>
            <th>Amenity</th>
            <td>{display_data['shop'][i]}</td>
        </tr>
        <tr>
            <th> Distance </th>
            <td>{round(display_data['distance'][i],2)} metres</td>
        </tr>
        <tr>
            <th> Walking Time </th>
            <td>{round(display_data['walking time'][i],2)} minutes </td>
        </tr>
    </table>
    </table>
    </p>'''
    folium.Marker([display_data.lat[i],
                display_data.lon[i]],
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
color="#3186cc",
fill=True,
fill_color="#3186cc",
).add_to(map)

#displaying the map:
fmtr = "function(num) {return L.Util.formatNum(num, 3);};"

#map pointer, checks where the position is on map:


#loc = plugins.MousePosition(position='topright', separator=' , ',numDigits = 6,
#              lat_formatter=fmtr, lng_formatter=fmtr).add_to(map)


st_folium.folium_static(map, width = 1600, height = 1000)

#def color_coding(df):
#    return ['background-color:red'] * len(
#        df) if df.lon == loc
#
#    if loc == (display_data.lon , display_data.lat):
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
