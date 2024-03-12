'''
Contributors: Jia-Shen Tsai, Wendy Wen, Zhengqi Jiao, Miaojun Pang,
Alexander Yoshizumi

Last Updated: 2024-3-11

Description: When run, script plot the real operation data in given formats.
'''
import pandas as pd
import geopandas as gpd
import contextily as ctx

df1_realop = pd.read_csv('../01_data/02_Processed/GIS/realop_total.csv')
df2_realop = pd.read_csv('../01_data/02_Processed/GIS/realop_march.csv')

df1_realop.columns
df2_realop.columns

df_realop = pd.concat([df1_realop, df2_realop])

df_realop.describe()

df_realop['speed'].describe()
grouped_data = df_realop.groupby('name')
grouped_data['speed'].describe()

df_realop.boxplot(column='speed',by='number', figsize=(8,4))
df_realop['speed'].hist(bins=20)
df_realop.hist(column='speed',by='number',figsize=(20,20))

s = gpd.GeoSeries.from_wkt(df_realop.geometry)
gdf_realop = gpd.GeoDataFrame(
    data = df_realop,
    geometry = s,
    crs = 4326
)

#Plot them with a base map
realop_plot = gdf_realop.to_crs(3857).plot(column='speed', legend=True)
ctx.add_basemap(realop_plot,
               source=ctx.providers.CartoDB.Voyager)


#Potential stops
potential_stop = gdf_realop.query('speed < 1')
potential_stop.shape

potentialStop_plot = potential_stop.to_crs(3857).plot(column='name', legend=True)
ctx.add_basemap(potentialStop_plot,
               source=ctx.providers.CartoDB.Voyager)

# Clipping the line
gdf_hline = gpd.read_file('../01_Data/02_Processed/GIS/H_Line.zip')

gdf_hline.crs.axis_info[0].unit_name # Check the unit
gs_hline_buffer = gdf_hline.buffer(15)
# gs_hline_buffer.plot(color = 'black');

gdf_realop = gdf_realop.to_crs(gdf_hline.crs)
gdf_realop_hline = gpd.clip(gdf_realop, gs_hline_buffer)

# Plot it
realop_clip_plot = gdf_realop_hline.to_crs(3857).plot(column='speed', legend=True)
ctx.add_basemap(realop_clip_plot,
               source=ctx.providers.CartoDB.Voyager)

gdf_realop_hline.shape
gdf_realop_hline.columns
gdf_realop_hline['number'].unique()

# Splitting east-bound and west bound


east_bound = [20,72,74,76,78,80]
east_mask = gdf_realop_hline["number"].isin(east_bound)
gdf_realop_h_east = gdf_realop_hline[east_mask]
gdf_realop_h_east.shape

west_bound = [19,71,73,75,77,79]
west_mask = gdf_realop_hline["number"].isin(west_bound)
gdf_realop_h_west = gdf_realop_hline[west_mask]
gdf_realop_h_west.shape

gdf_filtered = pd.concat([gdf_realop_h_east, gdf_realop_h_west]) # checking the number of observation

# removed points from Palmetto
palmetto = gdf_realop_hline[~gdf_realop_hline.apply(tuple,1).isin(gdf_filtered.apply(tuple,1))]
palmetto.plot()

palmetto_plot = palmetto.to_crs(3857).plot(column='speed', legend=True)
ctx.add_basemap(palmetto_plot,
               source=ctx.providers.CartoDB.Voyager)

# Export the gdfs

gdf_realop_h_east= gdf_realop_h_east.rename(columns={'origin_date': 'date','last_updated': 'updated'})
gdf_realop_h_west= gdf_realop_h_west.rename(columns={'origin_date': 'date','last_updated': 'updated'})

gdf_realop_h_east.to_file(
    filename = '../01_data/02_Processed/GIS/speed_east.shp',
    driver = 'ESRI Shapefile',
    index = False
)

gdf_realop_h_west.to_file(
    filename = '../01_data/02_Processed/GIS/speed_west.shp',
    driver = 'ESRI Shapefile',
    index = False
)