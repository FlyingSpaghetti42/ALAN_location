import pandas as pd
import numpy as np
from ALAN.routing.utils import transform_km, transform_min


def df_add_dist_dur(df,
                    dist_mode,
                    dur_mode,
                    mode):
    df[f'Distance {mode}'] = dist_mode
    df[f'Duration {mode}'] = dur_mode
    return df

def df_transform_dist_dur(df,mode):
    df[f'Distance {mode}'] = df[f'Distance {mode}'].apply(lambda x: transform_km(x))
    df[f'Duration {mode}'] = df[f'Duration {mode}'].apply(lambda x: transform_min(x))
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
