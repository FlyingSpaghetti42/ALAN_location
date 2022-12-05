import pandas as pd
import io
import requests
from geopy.distance import geodesic


def get_location(address):
    '''
    Function takes address as input and returns latitude and longitude
    '''
    from geopy.geocoders import Nominatim
    geolocator = Nominatim(user_agent='default')
    location = geolocator.geocode(address)
    if location is not None:
        return (location.latitude, location.longitude)
    return "Address not found"

def get_complete_data(location, radius=2000):
    '''
    Function takes tuple of longitude and latitude and returns a dataframe with
    data with in 2 KM  radius

    location: tuple (lat,lon)
    '''
    overpass_url = 'https://z.overpass-api.de/api/interpreter'

    overpass_query = f"""
    [out:csv(
        ::id, amenity, shop, office, highway, public_transport, tourism, sport,name, ::lat, ::lon, 'contact:phone','contact:website', 'addr:city','addr:street','addr:housenumber',
        'addr:postcode', 'addr:suburb', 'addr:country'
      )];
    (node(around:{radius},{location[0]},{location[1]});
    );
    out center;
    """
    response = requests.get(overpass_url,
                            params={'data': overpass_query})
    r=response.content

    rawData = pd.read_csv(io.StringIO(r.decode('utf-8')), delimiter='\t')
    return rawData


def column_selection(location,column_name):
    '''
    Function cleans the data based on column selection
    '''
    df=get_complete_data(location)
    list_columns=[ "shop", "office", "highway", "public_transport", "tourism", "amenity", "sport"]
    list_address=['name','addr:street','addr:housenumber','addr:suburb','addr:city','addr:postcode',
                  'addr:country','contact:phone','contact:website']
    df_amenity= df.dropna(subset=[column_name, 'name'])
    df_amenity.rename(columns={"@lon":"longitude", "@lat":"latitude"}, inplace=True)
    list_columns.remove(column_name)
    df_amenity.drop(columns=list_columns, inplace=True)
    df_amenity.fillna(" ",inplace=True)
    df_amenity["address"]=df_amenity[list_address].astype(str).apply(",".join, axis=1)
    df_amenity["address"]=df_amenity["address"].apply(lambda x: x.strip(', '))
    list_address.remove('name')
    df_amenity.drop(columns=list_address, inplace=True)
    df_amenity.reset_index(inplace=True, drop=True)
    return df_amenity


def subcolumn_selection(df, column_name,subcolumn_name):
    '''
    Function to update the dateframe with sub column selection
    '''
    return df[df[column_name]in subcolumn_name]

def distance_calculation(df,location,distance=2000):
    '''
    Function calculates the distance from the center
    '''
    df['distance']= df.apply(lambda df: geodesic(location, (df.lat,df.lon)).m, axis=1)
    return df[df['distance']<distance].sort_values(by=["distance"]).reset_index(drop=True)

if __name__ == '__main__':
    address=input("please enter the address:")
    preference=input ('select yor interests ("shop", "office", "highway", "public_transport", "tourism", "amenity", "sport"):')
    location=get_location(address)
    # df=get_complete_data(location)
    df_cleaned=column_selection(location, preference)
    # subcolumn=input('select your sub interests:')
    # df_final=subcolumn_selection(df_cleaned, preference,subcolumn)
    print(df_cleaned.head(20))
