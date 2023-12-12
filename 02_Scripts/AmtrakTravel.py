'''
Contributors: Jia-Shen Tsai

Last Updated: 2023-12-11

Description: When run, script create the elevation plot, show the route and estimated traveling time.
'''

# Import arcpy module
import sys, os, arcpy
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from datetime import datetime
from shapely.geometry import LineString

df_realop = pd.read_csv('../01_data/02_Processed/realopNov12.csv')
s = gpd.GeoSeries.from_wkt(df_realop.SHAPE)
gdf_realop = gpd.GeoDataFrame(
    data = df_realop,
    geometry = s,
    crs = 4326
)
gdf_realop = gdf_realop.drop(columns=['SHAPE'])
gdf_realop = gdf_realop.drop_duplicates(subset=['name', 'latitude', 'longitude'])

gdf_realop['speed'].hist(bins=40);

import contextily as ctx
#Plot them with a base map
realop_plot = gdf_realop.to_crs(3857).plot(column='speed', legend=True)
ctx.add_basemap(realop_plot,
               source=ctx.providers.CartoDB.Voyager)

potential_stop = gdf_realop.query('speed < 1')
potential_stop.shape

#Plot them with a base map
potentialStop_plot = potential_stop.to_crs(3857).plot(column='name', legend=True)
ctx.add_basemap(potentialStop_plot,
               source=ctx.providers.CartoDB.Voyager)






fc = '../01_data/02_Processed/realopNov12.shp'

# Get the user inputs via ArcPy's GetParameter function
Route =  arcpy.GetParameterAsText(0)
start_station = arcpy.GetParameterAsText(1) 
dest_station = arcpy.GetParameterAsText(2)



# Set workspace environment
arcpy.env.workspace = "../01_Data/02_Processed"
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("WGS 1984")
arcpy.env.overwriteOutput = True

# File paths
stations_fp = "NCStation.shp"
amtrak_routes_fp = "Amtrak_Route_NC.shp"
realop_fp = "realop.shp"

# Function to select starting and destination stations
def select_stations():
    stations = arcpy.ListFeatureClasses(stations_fp)[0]
    with arcpy.da.SearchCursor(stations, ["Name"]) as cursor:
        station_names = [row[0] for row in cursor]
    start_station = input(f"Select starting station from: {station_names}: ")
    dest_station = input(f"Select destination station from: {station_names}: ")
    return start_station, dest_station

# Function to create subset polyline between two stations
def subset_amtrak_route(start, dest):
    # Query to select stations
    query = f"Name = '{start}' OR Name = '{dest}'"
    arcpy.SelectLayerByAttribute_management(stations_fp, "NEW_SELECTION", query)
    
    # Subset the route
    subset_route = arcpy.analysis.PairwiseIntersect([amtrak_routes_fp, stations_fp], "in_memory/subset_route")
    
    # Save to new shapefile
    output_fp = "subset_route.shp"
    arcpy.CopyFeatures_management(subset_route, output_fp)
    return output_fp

# Function to create elevation profile
def create_elevation_profile(route_fp):
    # Generate and save the elevation profile
    profile_name = f"profile_{start_station}_{dest_station}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    # Buffer creation and centerline extraction
    arcpy.analysis.Buffer(
        in_features="../01_Data/02_Processed/subset_route.shp",
        out_feature_class="../01_Data/02_Processed/temp/route_buffer",
        buffer_distance_or_field="50 Meters",
        line_side="FULL",
        line_end_type="ROUND",
        dissolve_option="ALL",
        dissolve_field=None,
        method="PLANAR"
    )

    gpd_buffer = gpd.read_file("../01_Data/02_Processed/temp/route_buffer.shp")
    boundary = gpd_buffer.iloc[0].geometry.exterior
    centerline = LineString(boundary)
    gdf_centerline = gpd.GeoDataFrame(geometry=[centerline], crs=4326)
    gdf_centerline.to_file('../01_Data/02_Processed/centerline.shp')

    # Elevation profile generation
    input_fl = "../01_Data/02_Processed/centerline.shp"
    profile_tg = "NC_DEM.tiff"
    output_tbl = "../01_Data/02_Processed/Profile.csv"

    arcpy.ddd.StackProfile(input_fl, profile_tg, output_tbl)

    # Plotting the elevation profile
    Profile_df = pd.read_csv("../01_Data/02_Processed/Profile.csv")
    Profile_re_df = Profile_df[Profile_df['FIRST_Z'] < 1000]
    hz_dist = Profile_re_df['FIRST_DIST']
    elevation = Profile_re_df['FIRST_Z']
    plt.plot(hz_dist, elevation)
    plt.xlabel('Horizontal Distance (degree)')
    plt.ylabel('Elevation (m)')
    plt.title('Elevation Profile Your Trip')
    plt.show()
    plt.savefig(f"{arcpy.env.workspace}/{profile_name}.png")
    return profile_name

# Function to calculate time gap
def calculate_time_gap(start_station, dest_station):
    # Fetch station locations
    # ...

    # Query realop dataset
    # ...

    # Calculate time gap and display popup
    # ...

# Main process
start_station, dest_station = select_stations()
route_fp = subset_amtrak_route(start_station, dest_station)
profile_name = create_elevation_profile(route_fp)
calculate_time_gap(start_station, dest_station)



# rows = arcpy.da.SearchCursor()

# for row in rows:
#     timestamp = row[9]
