import pandas as pd
import io
import requests
from geopy.distance import geodesic


def get_location(address):
    '''
    Function takes address as input and returns latitude and longitude

    address: string in the form: 'street, house number, city, (country)'
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
     way(around:{radius},{location[0]},{location[1]});
     relation(around:{radius},{location[0]},{location[1]});
        );
    out center;
    """
    response = requests.get(overpass_url,
                            params={'data': overpass_query})
    r=response.content

    rawData = pd.read_csv(io.StringIO(r.decode('utf-8')), delimiter='\t')
    return rawData

def raw_data(address:str, radius=2000):
    location_lat,location_lon = get_location(address)
    return get_complete_data((location_lat,location_lon),radius)

def data_cleaning(address:str, radius=2000):
    '''
    This function uses the above raw_data() function to make the
    overpass api call to get the data for all nodes within the
    specified radius.

    It then proceeds to apply various data cleaning operations to get
    a nice looking dataframe, which can be used for further analyses.

    Parameters:
    address: string of the address of concern for optimale results best
            passed in the form: 'street,house no.,city, country'
    radius: integer specifying in metres the radius around the location
            that is to be searched
    '''
    # get the data:
    df = raw_data(address,radius=2000)

    # Remove rows with no entries for none of categories:
    df.dropna(subset=["shop", "office", "highway",
                         "public_transport", "tourism",
                         "amenity", "sport"], how='all', inplace=True)
    df.dropna(subset=["name"], how='any', inplace=True)

    # Operations on the addresses to get one column containing the address:
    ## list of address related columns
    list_address = ['name','addr:street',
                    'addr:housenumber','addr:suburb',
                    'addr:city','addr:postcode',
                    'addr:country']
    ## Merge the address columns
    df.fillna(" ",inplace=True)
    df['addr:postcode'] = df['addr:postcode'].astype(str).apply(lambda x: x.replace('.0',''))
    df["Address"] = df[list_address].astype(str).apply(",".join, axis=1)
    df["Address"] = df["Address"].apply(lambda x: x.strip(', '))
    list_address.remove('name')
    df.drop(columns = list_address, inplace = True)

    # Create new column merging highway and Transport category
    df['Transport'] = df[['highway',
                            'public_transport']].astype(str).apply(",".join, axis=1)
    ## remove redundant columns
    df.drop(columns = ['highway', 'public_transport', '@id'], inplace = True)

    # Rename columns:
    ## dict of columns to be renamed
    column_rename = {
        "shop": 'Shopping',
        "office": 'Office',
        "tourism": 'Tourism',
        "amenity": 'Amenity',
        "sport": 'Sports',
        "@lat": 'Latitude',
        "@lon": 'Longitude',
        "name": 'Location Name',
        "contact:website": 'Website',
        "contact:phone": 'Phone Number'
    }
    ## rename the columns using the above dict
    df.rename(columns = column_rename, inplace = True)

    # Data cleaning subclasses:

    ## Get rid of Location Name in Address line and format Address
    df['Address'] = df.apply(lambda df: df['Address'].replace(df['Location Name'],''),axis=1)
    ### Remove leading or trailing commas
    df['Address'] = df['Address'].apply(lambda x: x.strip(','))
    ### Add whitespace after comma
    df['Address'] = df['Address'].apply(lambda x: x.replace(',',' '))

    ## String formatting of Subclass Names:
    cols = ['Amenity', 'Transport', 'Shopping',
            'Office', 'Tourism', 'Sports']
    ### clear commas
    df[cols] = df[cols].apply(lambda x: x.str.replace(',',' '))
    ### clear leading and trailing whitespace
    df[cols] = df[cols].apply(lambda x: x.str.strip())
    ### replace snake format with whitespace sep
    df[cols] = df[cols].apply(lambda x: x.str.replace('_',' '))
    ### capitalize
    df[cols] = df[cols].apply(lambda x: x.str.capitalize())

    # rearrange columns
    df = df.reindex(columns=['Location Name','Address','Website','Phone Number',
                             'Latitude', 'Longitude',
                             'Amenity', 'Transport',
                             'Shopping', 'Office',
                             'Tourism', 'Sports'])

    # reset index
    df.reset_index(inplace=True, drop = True)
    return df

def filter_columns(df, column_name):
    '''
    Replaces the column_selection function

    Filters the preprocessed DataFrame to only include the category chosen
    (Shopping Facility, Office, Transport, Public Transport, Tourism, Amenity,
    Sport Facility)
    '''
    list_columns = ['Shopping',
                    'Office', 'Transport','Tourism',
                    'Amenity', 'Sports']
    list_columns.remove(column_name)
    df.drop(columns = list_columns, inplace = True)
    df = df[df[column_name] != '']
    df.reset_index(inplace=True, drop = True)
    return df

def format_subclass_transport(df):
    '''
    Structure Traffic column to make results more tractable

    Function renames entries and deletes duplicates (e.g. if bus station on both sides of road)

    Should not be applied to the whole dataframe

    Input: Dataframe already filtered
    '''
    # rename stations
    df.loc[:,'Transport'] = df.Transport.apply(lambda x: x.replace('Stop position','Bus stop'))
    df.loc[:,'Transport'] = df.Transport.apply(lambda x: x.replace('Bus stop platform','Bus stop'))
    df.loc[:,'Transport'] = df.Transport.apply(lambda x: x.replace('Station','Train station'))

    # next, get rid of duplicate stations
    df = df.drop_duplicates(subset=['Location Name','Transport']).reset_index(drop=True)

    # only retain specified columns:
    categories = ['Bus stop','Train station']
    df = df[df.Transport.isin(categories)]
    return df


def subcolumn_selection(df, column_name,subcolumn_name):
    '''
    Function to update the dateframe with sub column selection
    '''
    return df[df[column_name] in subcolumn_name]

def distance_calculation(df,location,distance=2000):
    '''
    Function calculates the distance from the center
    '''
    df['Linear Distance']= df.apply(lambda df: geodesic(location, (df.Latitude,df.Longitude)).m, axis=1)
    return df[df['Linear Distance']<distance].sort_values(by=["Linear Distance"]).reset_index(drop=True)

if __name__ == '__main__':
    address=input("please enter the address:")
    preference=input ('select yor interests ("shop", "office", "highway", "public_transport", "tourism", "amenity", "sport"):')
    location=get_location(address)
    # df=get_complete_data(location)
    #df_cleaned=column_selection(location, preference)
    # subcolumn=input('select your sub interests:')
    # df_final=subcolumn_selection(df_cleaned, preference,subcolumn)
    #print(df_cleaned.head(20))
