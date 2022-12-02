import pandas as pd
import numpy as np
from routing.utils import transform_km, transform_min


def df_add_dist_dur(df,
                    dist_mode,
                    dur_mode):
    df['dist_mode'] = dist_mode
    df['dur_mode'] = dur_mode
    return df

def df_transform_dist_dur(df):
    df['dist_mode'] = df['dist_mode'].apply(lambda x: transform_km(x))
    df['dur_mode'] = df['dur_mode'].apply(lambda x: transform_min(x))
#    df['dist_cycl_reg'] = df['dist_cycl_reg'].apply(lambda x: transform_km(x))
#    df['dur_cycl_reg'] = df['dur_cycl_reg'].apply(lambda x: transform_min(x))
#    df['dist_cycl_e'] = df['dist_cycl_e'].apply(lambda x: transform_km(x))
#    df['dur_cycl_e'] = df['dur_cycl_e'].apply(lambda x: transform_min(x))
    return df

#def df_add_beeline(df, lat_start, lon_start):
#    df['beeline'] = df.apply(lambda row:
#                                    distance_beeline(lat_start,
#                                                        lon_start,
#                                                        row.lat,
#                                                        row.lon), axis=1)
#    return df

def df_transform_beeline(df):
    df['beeline'] = df['beeline'].apply(lambda x: transform_km(x))
    return df
