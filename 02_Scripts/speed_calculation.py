'''
Contributors: Jia-Shen Tsai, Wendy Wen, Zhengqi Jiao, Miaojun Pang,
Alexander Yoshizumi

Last Updated: 2024-2-11

Description: When run, script summarize the speed for every segment in the input file
'''
# import packages
import pandas as pd
import geopandas as gpd
import contextily as ctx
import matplotlib.pyplot as plt

# read the dataset in
df_realop = pd.read_csv('../01_Data/02_Processed/realop.csv')
gdf_hline = gpd.read_file('../01_Data/02_Processed/GIS/H_Line.shp')
df_milepost = pd.read_csv('../01_Data/02_Processed/HLine_milepost.csv')

## transfrom csv to gdf
g1 = gpd.points_from_xy(x=df_realop['longitude'], y = df_realop['latitude'])
gdf_realop = gpd.GeoDataFrame(
    data = df_realop,
    geometry = g1,
    crs = 4326
)

g2 = gpd.points_from_xy(x = df_milepost['x_coordinate'], y = df_milepost['y_coordinate'])
gdf_milepost = gpd.GeoDataFrame(
    data = df_milepost,
    geometry = g2,
    crs = 4326
)

## data examination

gdf_milepost.head()
gdf_milepost.shape

### speed distribution
df_milepost['RASTERVALU'].plot();
gdf_realop.head()
gdf_realop.shape

### Plot the speed data with a base map
realop_plot = gdf_realop.to_crs(3857).plot(column='speed', legend=True)
ctx.add_basemap(realop_plot,
               source=ctx.providers.CartoDB.Voyager)

### plot the hline
hline_plot = gdf_hline.plot(color = 'g', figsize=(24,6))
ctx.add_basemap(hline_plot,
                crs = gdf_hline.crs.to_string(),
                source=ctx.providers.CartoDB.Voyager)
plt.savefig('../05_Deliverables/plots/hline')

