'''
Contributors: Jia-Shen Tsai, Wendy Wen, Zhengqi Jiao, Miaojun Pang,
Alexander Yoshizumi

Last Updated: 2024-2-1

Description: When run, script process the raw json into one csv.
'''

# !pip install geopandas
# !pip install shapely
# !pip install contextily

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import os
import warnings

# Use the warnings context manager to capture and suppress warnings
with warnings.catch_warnings():
    warnings.filterwarnings("ignore")  # Ignore all warnings
    # Define the folder path where JSON files are located
    json_folder = '//ns-gis.win.duke.edu/StudentData/2023-2024/ct325/2023_NSOE_Commuter_Rail/01_Data/01_Source/ASM'

    # Define the function to extract the lng, la, and speed only from valid dictionaries
    def extract_coordinates(location):
        if isinstance(location, dict):
            return location.get('latitude'), location.get('longitude'), location.get('speed')
        else:
            return None, None, None

    # Initialize empty lists to store the combined data
    origin_dates = []
    names = []
    numbers = []
    last_updated = []
    longitudes = []
    latitudes = []
    speeds = []

    # Read and process each JSON file in the folder
    for filename in os.listdir(json_folder):
        if filename.endswith('.json'):
            json_filepath = os.path.join(json_folder, filename)

            # Read JSON file into a df
            df = pd.read_json(json_filepath)

            # Filter routes that pass nc and make lng, lat, speed into a list of lists
            NC_data = df.query('name in ("Silver Meteor","Carolinian","Piedmont","Palmetto","Crescent")')
            NC_data['location'] = NC_data['location'].apply(extract_coordinates)

            # Extract and store origin_date, name, and number
            origin_dates.extend(NC_data['origin_date'].tolist())
            names.extend(NC_data['name'].tolist())
            numbers.extend(NC_data['number'].tolist())
            last_updated.extend(NC_data['last_updated'].tolist())

            # Extract and store lng, lat, and speed
            latitudes.extend([location[0] for location in NC_data['location']])
            longitudes.extend([location[1] for location in NC_data['location']])
            speeds.extend([location[2] for location in NC_data['location']])

# Create a DataFrame with columns of origin_date, name, number, longitude, latitude, speed
df_realop = pd.DataFrame({
    'origin_date': origin_dates,
    'last_updated': last_updated,
    'name': names,
    'number': numbers,
    'longitude': longitudes,
    'latitude': latitudes,
    'speed': speeds
})

df_realop = df_realop.drop_duplicates(subset=['name', 'latitude', 'longitude'])

# Transform pd to gpd
# s = [Point(xy) for xy in zip(NC_data.longitude, NC_data.latitude)]
s = [Point(xy) for xy in zip(df_realop.longitude, df_realop.latitude)]
gdf_realop = gpd.GeoDataFrame(data = df_realop, geometry= s, crs=4326)

# Clip the GeoDataFrame to the county boundary
gdf_county = gpd.read_file('z://2023_NSOE_Commuter_Rail/01_Data/01_Source/North_Carolina_State_and_County_Boundary_Polygons.zip')
gdf_county = gdf_county.to_crs(4326)
gdf_real = gpd.clip(gdf_realop, gdf_county)

# gdf_real.head()

# Export the geodataframe to a CSV file
pd.DataFrame(gdf_real).to_csv(
    '../01_Data/02_Processed/realop_total.csv',
    index=False
)