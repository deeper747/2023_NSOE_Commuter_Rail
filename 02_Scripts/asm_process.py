'''
Contributors: Jia-Shen Tsai, Wendy Wen, Zhengqi Jiao, Miaojun Pang,
Alexander Yoshizumi

Last Updated: 2024-2-1

Description: When run, script process the raw json into one csv.
'''

#pip install geopandas
#pip install contextily

import pandas as pd
import arcpy
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import LineString
import contextily as ctx
import os
from arcgis import GeoAccessor
import warnings

gdf_county = gpd.read_file('../01_Data/01_Source/North_Carolina_State_and_County_Boundary_Polygons.zip')

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

    # Initialize an empty GeoDataFrame to store the combined data
    gdf_realop = gpd.GeoDataFrame()

    # Read and process each JSON file in the folder
    for filename in os.listdir(json_folder):
        if filename.endswith('.json'):
            json_filepath = os.path.join(json_folder, filename)

            # Read JSON file into a df
            df = pd.read_json(json_filepath)

            # Filter routes that pass nc and make lng, lat, speed to independent columns
            df_nc = df.query('name in ("Silver Meteor","Carolinian","Piedmont","Palmetto","Crescent")')
            df_nc[['latitude', 'longitude','speed']] = df_nc['location'].apply(extract_coordinates).apply(pd.Series)

            # Create a sdf
            sdf = GeoAccessor.from_xy(df_nc, x_column='longitude', y_column='latitude')

            # Create a gdf
            gdf = gpd.GeoDataFrame(data=sdf, geometry='SHAPE', crs=4326)

            # Clip the GeoDataFrame to the county boundary
            gdf_snap_nc = gpd.clip(gdf, gdf_county)

            # Append the clipped gdf to the combined gdf
            gdf_realop = pd.concat([gdf_realop, gdf_snap_nc], ignore_index=True)

# Remove duplicates based on name and location
gdf_realop = gdf_realop.drop_duplicates(subset=['name', 'latitude', 'longitude'])

gdf_realop.head()

# Remove duplicates based on name and location
gdf_realop = gdf_realop.drop_duplicates(subset=['name', 'latitude', 'longitude'])

gdf_realop.head()

# Export the geodataframe to a CSV file
pd.DataFrame(gdf_realop).to_csv(
    '../01_data/02_Processed/realop.csv',
    index=False
)