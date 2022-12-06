#====================================
#===========    Features ============
#====================================

import streamlit as st
from ALAN.data.data_engineering import get_location, distance_calculation, raw_data, data_cleaning, filter_columns,format_subclass_transport
from ALAN.data.dash_board_basic import important_features, heat_map
from ALAN.data.colors import colors
from ALAN.data.distance import manhattan_distance_vectorized
from ALAN.routing.dataframe_builder import df_add_dist_dur, df_transform_dist_dur
from ALAN.routing.geodistances import routing_final, get_isochrone
from ALAN.routing.utils import speed, transform_km, transform_min

st.set_page_config(page_title="Features", layout="wide", page_icon="📈")

st.markdown("# Features")
st.sidebar.header("Features")
st.write(
    """readme""")

address = st.text_input('Adress', 'Please Input the Adress')
location=get_location(address)


##############################################################################
################### Kumar - Historic and Heatmap  ############################
##############################################################################

# important features:
## Add st.cache


# historic data:

# progress_bar.empty()
