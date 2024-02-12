'''
Contributors: Jia-Shen Tsai,  Wendy Wen, Zhengqi Jiao, Miaojun Pang, Alexander Yoshizumi

Last Updated: 2024-01-18

Description: When run, the script explore the aggregated ASM data
'''

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import LineString
import contextily as ctx

# read the exported csv file
df_realop = pd.read_csv('../01_data/02_Processed/realopNov12.csv')
s = gpd.GeoSeries.from_wkt(df_realop.SHAPE) # assign the geometric column
gdf_realop = gpd.GeoDataFrame(
    data = df_realop,
    geometry = s,
    crs = 4326
)
gdf_realop = gdf_realop.drop(columns=['SHAPE'])  # remove duplicate gemoetric column
gdf_realop = gdf_realop.drop_duplicates(subset=['name', 'latitude', 'longitude']) # drop duplicate observations

# plot the distribution
gdf_realop['speed'].hist(bins=40);

#Create a bar plot of the total # of observations for each route
gdf_line = gdf_realop.groupby('name')
gdf_line['speed'].hist(bins=40);


# plot them with a base map
realop_plot = gdf_realop.to_crs(3857).plot(column='speed', legend=True)
ctx.add_basemap(realop_plot,
               source=ctx.providers.CartoDB.Voyager)

# Look for potential stops at which the speed is 0
potential_stop = gdf_realop.query('speed < 1')
potential_stop.shape

#Plot the stops with a base map
potentialStop_plot = potential_stop.to_crs(3857).plot(column='name', legend=True)
ctx.add_basemap(potentialStop_plot,
               source=ctx.providers.CartoDB.Voyager)