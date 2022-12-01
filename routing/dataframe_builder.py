import pandas as pd
import numpy as np
from geodistances import distance_beeline
from utils import transform_km, transform_min

def df_preprocess(df):
#function to only select the first 13 items from the dataframe.
#Adjust to 40 items later on.
    df = df.drop(columns=['Unnamed: 0','@id'])
    df = df.replace(np.nan, 'Not Available')
    df = df.rename(columns={'@lat':'lat', '@lon':'lon'})
    df = df[0:12]
    return df

def df_add_dist_dur(df,
                    dist_walk,
                    dur_walk,
                    dist_cycl_reg,
                    dur_cycl_reg,
                    dist_cycl_e,
                    dur_cycl_e):
    df['dist_walk'] = dist_walk
    df['dur_walk'] = dur_walk
    df['dist_cycl_reg'] = dist_cycl_reg
    df['dur_cycl_reg'] = dur_cycl_reg
    df['dist_cycl_e'] = dist_cycl_e
    df['dur_cycl_e'] = dur_cycl_e
    return df

def df_transform_dist_dur(df):
    df['dist_walk'] = df['dist_walk'].apply(lambda x: transform_km(x))
    df['dur_walk'] = df['dur_walk'].apply(lambda x: transform_min(x))
    df['dist_cycl_reg'] = df['dist_cycl_reg'].apply(lambda x: transform_km(x))
    df['dur_cycl_reg'] = df['dur_cycl_reg'].apply(lambda x: transform_min(x))
    df['dist_cycl_e'] = df['dist_cycl_e'].apply(lambda x: transform_km(x))
    df['dur_cycl_e'] = df['dur_cycl_e'].apply(lambda x: transform_min(x))
    return df

def df_add_beeline(df, lat_start, lon_start):
    df['beeline'] = df.apply(lambda row:
                                    distance_beeline(lat_start,
                                                        lon_start,
                                                        row.lat,
                                                        row.lon), axis=1)
    return df

def df_transform_beeline(df):
    df['beeline'] = df['beeline'].apply(lambda x: transform_km(x))
    return df
