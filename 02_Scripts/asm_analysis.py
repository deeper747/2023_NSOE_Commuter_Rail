'''
Contributors: Jia-Shen Tsai, Wendy Wen, Zhengqi Jiao, Miaojun Pang,
Alexander Yoshizumi

Last Updated: 2024-2-1

Description: When run, script plot the real operation data in given formats.
'''
import pandas as pd
import geopandas as gpd
import contextily as ctx

df_realop = pd.read_csv('../01_data/02_Processed/realop.csv')
s = gpd.GeoSeries.from_wkt(df_realop.SHAPE)
gdf_realop = gpd.GeoDataFrame(
    data = df_realop,
    geometry = s,
    crs = 4326
)
gdf_realop = gdf_realop.drop(columns=['SHAPE'])

gdf_realop['speed'].hist(bins=40);


#Plot them with a base map
realop_plot = gdf_realop.to_crs(3857).plot(column='speed', legend=True)
ctx.add_basemap(realop_plot,
               source=ctx.providers.CartoDB.Voyager)



#Potentila stops
potential_stop = gdf_realop.query('speed < 1')
potential_stop.shape

potentialStop_plot = potential_stop.to_crs(3857).plot(column='name', legend=True)
ctx.add_basemap(potentialStop_plot,
               source=ctx.providers.CartoDB.Voyager)