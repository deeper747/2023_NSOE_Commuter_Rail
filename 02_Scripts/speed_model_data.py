'''
Contributors: Jia-Shen Tsai, Wendy Wen, Zhengqi Jiao, Miaojun Pang,
Alexander Yoshizumi

Last Updated: 2024-3-14

Description: When run, script create the variables with regard to the key nodes
'''
# Setup
## Packages
import pandas as pd
import numpy as np
import geopandas as gpd
import contextily as ctx
from scipy.spatial import cKDTree

## Read the dataset
df_milepost = pd.read_csv('/Users/jason/Library/CloudStorage/GoogleDrive-deeperduke@gmail.com/.shortcut-targets-by-id/1gsetPzqCMaQ4qQzbQ7GR4eMkBkcvb_5f/2023_NSOE_Commuter_Rail/01_Data/02_Processed/milepost.csv')
df_station = pd.read_excel('/Users/jason/Library/CloudStorage/GoogleDrive-deeperduke@gmail.com/.shortcut-targets-by-id/1gsetPzqCMaQ4qQzbQ7GR4eMkBkcvb_5f/2023_NSOE_Commuter_Rail/01_Data/02_Processed/GIS/H_Line_Stations.xlsx')
df_intersection = pd.read_excel('/Users/jason/Library/CloudStorage/GoogleDrive-deeperduke@gmail.com/.shortcut-targets-by-id/1gsetPzqCMaQ4qQzbQ7GR4eMkBkcvb_5f/2023_NSOE_Commuter_Rail/01_Data/02_Processed/GIS/H_Line_Crossing.xlsx')

## filter the columns
### df_intersection.columns
intersection_clms = ['OBJECTID','latdd','longdd']
df_intersection = df_intersection[intersection_clms]

### df_station.columns
mask = (df_station['statype']=='Station Building (with waiting room)')
df_station = df_station[mask]

station_clms = ['OBJECTID','NEAR_X','NEAR_Y']
df_station = df_station[station_clms]

## transform to gpd
g1 = gpd.points_from_xy(x=df_milepost['x_coordinate'], y = df_milepost['y_coordinate'])
gdf_milepost = gpd.GeoDataFrame(
    data = df_milepost,
    geometry = g1,
    crs = 4326
)

df_milepost.head()
df_intersection.head()
g2 = gpd.points_from_xy(x = df_intersection['longdd'], y = df_intersection['latdd'])
gdf_intersection = gpd.GeoDataFrame(
    data = df_intersection,
    geometry = g2,
    crs = 4326
)


g3 = gpd.points_from_xy(x = df_station['NEAR_X'], y = df_station['NEAR_Y'])
gdf_station = gpd.GeoDataFrame(
    data = df_station,
    geometry = g3,
    crs=102100
)

gdf_station = gdf_station.to_crs(gdf_milepost.crs)
mask = (gdf_milepost["Switch_if"] == 1)
gdf_switches = gdf_milepost[mask]

# ## examination
# milepost_plot = gdf_milepost.to_crs(3857).plot(column='Cumulative_Length_ft', legend=True)
# ctx.add_basemap(milepost_plot,
#                source=ctx.providers.CartoDB.Voyager)

# intersection_plot = gdf_intersection.to_crs(3857).plot()
# ctx.add_basemap(intersection_plot,
#                source=ctx.providers.CartoDB.Voyager)

# station_plot = gdf_station.to_crs(3857).plot()
# ctx.add_basemap(station_plot,
#                source=ctx.providers.CartoDB.Voyager)


# switch_plot = gdf_switches.to_crs(3857).plot()
# ctx.add_basemap(switch_plot,
#                 source=ctx.providers.CartoDB.Voyager)

# Discrete nodes
## Snapping points to the corresponding mileposts

def ckdnearest(gdA, gdB):

    nA = np.array(list(gdA.geometry.apply(lambda x: (x.x, x.y))))
    nB = np.array(list(gdB.geometry.apply(lambda x: (x.x, x.y))))
    btree = cKDTree(nB)
    dist, idx = btree.query(nA, k=1)
    gdB_nearest = gdB.iloc[idx].drop(columns="geometry").reset_index(drop=True)
    gdf = pd.concat(
        [
            gdA.reset_index(drop=True),
            gdB_nearest
        ], 
        axis=1)

    return gdf

gdf_station_node = ckdnearest(gdf_station, gdf_milepost)
gdf_intersection_node = ckdnearest(gdf_intersection, gdf_milepost)

# print(gdf_intersection_node.sort_values(by='Node_ID'))

## add the key node information to the sheet
clms_kn = ['Station_if','Intersection_if']
for i in clms_kn:
    gdf_milepost[i]="0"

### Update the 'Intersection_if' column in gdf_milepost where Node_ID matches any value in the list
### Convert the list of Node_ID values to a set for faster lookup
node_id_set = set(gdf_intersection_node['Node_ID'])
gdf_milepost.loc[gdf_milepost['Node_ID'].isin(node_id_set), 'Intersection_if'] = 1

### Update the 'station_if' column in gdf_milepost where Node_ID matches any value in the list
node_id_set = set(gdf_station_node['Node_ID'])
gdf_milepost.loc[gdf_milepost['Node_ID'].isin(node_id_set), 'Station_if'] = 1

## Distance to the Key Nodes
def dist_to_key_node(df, key_node_var):

    distances = []
    next_index = df[df[key_node_var]==1].index.min()
    # Iterate over the rows of the GeoDataFrame
    for index, row in df.iterrows():
    # If the current row is an key node, update the current key node index
        if row[key_node_var] == 1:
            distances.append(0)
            # Find the next key node index
            next_index = df[(df.index > index) & (df[key_node_var] == 1)].index.min()
            if np.isnan(next_index):
                # If there's no next station, set the last index the last node
                next_index = len(df) - 1
        else:
            distance_to_next_node = df.loc[next_index, 'Cumulative_Length_ft'] - row['Cumulative_Length_ft']
            distances.append(distance_to_next_node)
    return distances

intersection_dist = dist_to_key_node(gdf_milepost,'Intersection_if')
station_dist = dist_to_key_node(gdf_milepost,'Station_if')
switch_dist = dist_to_key_node(gdf_milepost,'Switch_if')

gdf_milepost['Distance_to_FOL_Intersection'] = intersection_dist
gdf_milepost['Distance_to_FOL_Station'] = station_dist
gdf_milepost['Distance_to_FOL_Switch'] = switch_dist

gdf_milepost[['Distance_to_FOL_Intersection']]

# Continuous Variables

## Identify the maximum angle in the five preceding and following observations, measured in angular degree
gdf_milepost = gdf_milepost.rename(columns={'Curve_degree': 'Curve_CUR_degree'})
size = 50

gdf_milepost['Curve_Max_PRE_2500ft_degree'] = gdf_milepost['Curve_CUR_degree'].rolling(window=size, min_periods=1).max().shift(1)
indexer = pd.api.indexers.FixedForwardWindowIndexer(window_size=size)
gdf_milepost['Curve_Max_FOL_2500ft_degree'] = gdf_milepost['Curve_CUR_degree'].rolling(window=indexer, min_periods=1).max().shift(-1)

gdf_milepost[['Curve_CUR_degree','Curve_Max_PRE_2500ft_degree']].head(20)

gdf_milepost['Curve_Max_PRE_2k5_5kft_degree'] = gdf_milepost['Curve_CUR_degree'].rolling(window=size, min_periods=1).max().shift(51)
gdf_milepost['Curve_Max_FOL_2k5_5kft_degree'] = gdf_milepost['Curve_CUR_degree'].rolling(window=indexer, min_periods=1).max().shift(-51)

gdf_milepost['Curve_Max_PRE_5k_7k5ft_degree'] = gdf_milepost['Curve_CUR_degree'].rolling(window=size, min_periods=1).max().shift(101)
gdf_milepost['Curve_Max_FOL_5k_7k5ft_degree'] = gdf_milepost['Curve_CUR_degree'].rolling(window=indexer, min_periods=1).max().shift(-101)

gdf_milepost['Curve_Max_PRE_7k5_10kft_degree'] = gdf_milepost['Curve_CUR_degree'].rolling(window=size, min_periods=1).max().shift(151)
gdf_milepost['Curve_Max_FOL_7k5_10kft_degree'] = gdf_milepost['Curve_CUR_degree'].rolling(window=indexer, min_periods=1).max().shift(-151)

gdf_milepost[['Curve_CUR_degree','Curve_Max_FOL_2500ft_degree','Curve_Max_PRE_7k5_10kft_degree']][150:170]

## Identify the change in elevation from the preceding observation to the following observation. 
## Using observations spaced 50 feet apart, this corresponds to the change in elevation over a 100-feet run.
gdf_milepost['Elev_Delta_CUR_ft'] = -(gdf_milepost['Elevation_Smoothen_ft'].diff(periods=-2).shift(1))/100
gdf_milepost[['Elevation_Smoothen_ft','Elev_Delta_CUR_ft']]
gdf_milepost.at[0, 'Elev_Delta_CUR_ft'] = (gdf_milepost.at[1,'Elevation_Smoothen_ft'] - gdf_milepost.at[0,'Elevation_Smoothen_ft'])/50
gdf_milepost.at[14339, 'Elev_Delta_CUR_ft'] = (gdf_milepost.at[14339,'Elevation_Smoothen_ft'] - gdf_milepost.at[14338,'Elevation_Smoothen_ft'])/50

gdf_milepost['Elev_Delta_PRE_2500ft_ft'] = gdf_milepost['Elev_Delta_CUR_ft'].rolling(window=size, min_periods=1).max().shift(1)
gdf_milepost['Elev_Delta_FOL_2500ft_ft'] = gdf_milepost['Elev_Delta_CUR_ft'].rolling(window=indexer, min_periods=1).max().shift(-1)

gdf_milepost['Elev_Delta_PRE_2k5_5kft_ft'] = gdf_milepost['Elev_Delta_CUR_ft'].rolling(window=size, min_periods=1).max().shift(51)
gdf_milepost['Elev_Delta_FOL_2k5_5kft_ft'] = gdf_milepost['Elev_Delta_CUR_ft'].rolling(window=indexer, min_periods=1).max().shift(-51)

gdf_milepost['Elev_Delta_PRE_5k_7k5ft_ft'] = gdf_milepost['Elev_Delta_CUR_ft'].rolling(window=size, min_periods=1).max().shift(101)
gdf_milepost['Elev_Delta_FOL_5k_7k5ft_ft'] = gdf_milepost['Elev_Delta_CUR_ft'].rolling(window=indexer, min_periods=1).max().shift(-101)

gdf_milepost['Elev_Delta_PRE_7k5_10kft_ft'] = gdf_milepost['Elev_Delta_CUR_ft'].rolling(window=size, min_periods=1).max().shift(151)
gdf_milepost['Elev_Delta_FOL_7k5_10kft_ft'] = gdf_milepost['Elev_Delta_CUR_ft'].rolling(window=indexer, min_periods=1).max().shift(-151)


# West-bound

## Create a dataset flipping the line
gdf_westbound = gdf_milepost.loc[::-1].reset_index(drop=True)
gdf_westbound['Intersection_if'].head()
gdf_westbound.shape

gdf_westbound['Cumulative_Length_ft'] = gdf_westbound.index * 50

## recalculate the distance

intersection_dist = dist_to_key_node(gdf_westbound,'Intersection_if')
station_dist = dist_to_key_node(gdf_westbound,'Station_if')
switch_dist = dist_to_key_node(gdf_westbound,'Switch_if')

gdf_westbound['Distance_to_FOL_Intersection'] = intersection_dist
gdf_westbound['Distance_to_FOL_Station'] = station_dist
gdf_westbound['Distance_to_FOL_Switch'] = switch_dist

gdf_westbound['Distance_to_FOL_Station']

## extract the distance value to the next key node in the west-bound dataset
## as the distance to the preceding key node in the east-bound dataset
gdf_milepost['Distance_to_PRE_Intersection'] = gdf_milepost['Node_ID'].map(gdf_westbound.set_index('Node_ID')['Distance_to_FOL_Intersection'])
gdf_milepost['Distance_to_PRE_Station'] = gdf_milepost['Node_ID'].map(gdf_westbound.set_index('Node_ID')['Distance_to_FOL_Station'])
gdf_milepost['Distance_to_PRE_Switch'] = gdf_milepost['Node_ID'].map(gdf_westbound.set_index('Node_ID')['Distance_to_FOL_Switch'])

# Rerun the process for the West-Bound dataset
## Identify the maximum angle in the five preceding and following observations, measured in angular degree
gdf_westbound['Curve_Max_PRE_2500ft_degree'] = gdf_westbound['Curve_CUR_degree'].rolling(window=size, min_periods=1).max().shift(1)
gdf_westbound['Curve_Max_FOL_2500ft_degree'] = gdf_westbound['Curve_CUR_degree'].rolling(window=indexer, min_periods=1).max().shift(-1)

gdf_westbound['Curve_Max_PRE_2k5_5kft_degree'] = gdf_westbound['Curve_CUR_degree'].rolling(window=size, min_periods=1).max().shift(51)
gdf_westbound['Curve_Max_FOL_2k5_5kft_degree'] = gdf_westbound['Curve_CUR_degree'].rolling(window=indexer, min_periods=1).max().shift(-51)

gdf_westbound['Curve_Max_PRE_5k_7k5ft_degree'] = gdf_westbound['Curve_CUR_degree'].rolling(window=size, min_periods=1).max().shift(101)
gdf_westbound['Curve_Max_FOL_5k_7k5ft_degree'] = gdf_westbound['Curve_CUR_degree'].rolling(window=indexer, min_periods=1).max().shift(-101)

gdf_westbound['Curve_Max_PRE_7k5_10kft_degree'] = gdf_westbound['Curve_CUR_degree'].rolling(window=size, min_periods=1).max().shift(151)
gdf_westbound['Curve_Max_FOL_7k5_10kft_degree'] = gdf_westbound['Curve_CUR_degree'].rolling(window=indexer, min_periods=1).max().shift(-151)

## Identify the change in elevation from the preceding observation to the following observation. 
## Using observations spaced 50 feet apart, this corresponds to the change in elevation over a 100-feet run.
gdf_westbound['Elev_Delta_CUR_ft'] = -(gdf_westbound['Elevation_Smoothen_ft'].diff(periods=-2).shift(1))/100
gdf_westbound[['Elevation_Smoothen_ft','Elev_Delta_CUR_ft']]

gdf_westbound.at[0, 'Elev_Delta_CUR_ft'] = (gdf_westbound.at[1,'Elevation_Smoothen_ft'] - gdf_westbound.at[0,'Elevation_Smoothen_ft'])/50
gdf_westbound.at[14339, 'Elev_Delta_CUR_ft'] = (gdf_westbound.at[14339,'Elevation_Smoothen_ft'] - gdf_westbound.at[14338,'Elevation_Smoothen_ft'])/50

gdf_westbound['Elev_Delta_PRE_2500ft_ft'] = gdf_westbound['Elev_Delta_CUR_ft'].rolling(window=size, min_periods=1).max().shift(1)
gdf_westbound['Elev_Delta_FOL_2500ft_ft'] = gdf_westbound['Elev_Delta_CUR_ft'].rolling(window=indexer, min_periods=1).max().shift(-1)

gdf_westbound['Elev_Delta_PRE_2k5_5kft_ft'] = gdf_westbound['Elev_Delta_CUR_ft'].rolling(window=size, min_periods=1).max().shift(51)
gdf_westbound['Elev_Delta_FOL_2k5_5kft_ft'] = gdf_westbound['Elev_Delta_CUR_ft'].rolling(window=indexer, min_periods=1).max().shift(-51)

gdf_westbound['Elev_Delta_PRE_5k_7k5ft_ft'] = gdf_westbound['Elev_Delta_CUR_ft'].rolling(window=size, min_periods=1).max().shift(101)
gdf_westbound['Elev_Delta_FOL_5k_7k5ft_ft'] = gdf_westbound['Elev_Delta_CUR_ft'].rolling(window=indexer, min_periods=1).max().shift(-101)

gdf_westbound['Elev_Delta_PRE_7k5_10kft_ft'] = gdf_westbound['Elev_Delta_CUR_ft'].rolling(window=size, min_periods=1).max().shift(151)
gdf_westbound['Elev_Delta_FOL_7k5_10kft_ft'] = gdf_westbound['Elev_Delta_CUR_ft'].rolling(window=indexer, min_periods=1).max().shift(-151)

## distance to previous key node
gdf_westbound['Distance_to_PRE_Intersection'] = gdf_westbound['Node_ID'].map(gdf_milepost.set_index('Node_ID')['Distance_to_FOL_Intersection'])
gdf_westbound['Distance_to_PRE_Station'] = gdf_westbound['Node_ID'].map(gdf_milepost.set_index('Node_ID')['Distance_to_FOL_Station'])
gdf_westbound['Distance_to_PRE_Switch'] = gdf_westbound['Node_ID'].map(gdf_milepost.set_index('Node_ID')['Distance_to_FOL_Switch'])

gdf_milepost.shape
gdf_westbound.shape

gdf_westbound[['Distance_to_PRE_Station','Distance_to_FOL_Station','Station_if']][30:40]
gdf_westbound[30:40]

gdf_export = pd.concat([gdf_milepost,gdf_westbound])
milepost_clms = ['Node_ID','Elevation_Smoothen_ft','Elev_Delta_CUR_ft','Elev_Delta_FOL_2500ft_ft','Elev_Delta_FOL_2k5_5kft_ft','Elev_Delta_FOL_5k_7k5ft_ft','Elev_Delta_FOL_7k5_10kft_ft','Elev_Delta_PRE_2500ft_ft','Elev_Delta_PRE_2k5_5kft_ft','Elev_Delta_PRE_5k_7k5ft_ft','Elev_Delta_PRE_7k5_10kft_ft','Curve_CUR_degree','Curve_Max_FOL_2500ft_degree','Curve_Max_FOL_2k5_5kft_degree','Curve_Max_FOL_5k_7k5ft_degree','Curve_Max_FOL_7k5_10kft_degree','Curve_Max_PRE_2500ft_degree','Curve_Max_PRE_2k5_5kft_degree','Curve_Max_PRE_5k_7k5ft_degree','Curve_Max_PRE_7k5_10kft_degree','Elev_Delta_FOL_2500ft_ft','Curve_Max_FOL_2k5_5kft_degree','Curve_Max_FOL_5k_7k5ft_degree','Curve_Max_FOL_7k5_10kft_degree','Curve_Max_PRE_2500ft_degree','Curve_Max_PRE_2k5_5kft_degree','Curve_Max_PRE_5k_7k5ft_degree','Curve_Max_PRE_7k5_10kft_degree','geometry','x_coordinate','y_coordinate','Station_if','Intersection_if','Switch_if','Cumulative_Length_ft','Distance_to_FOL_Intersection','Distance_to_FOL_Station','Distance_to_FOL_Switch','Distance_to_PRE_Intersection','Distance_to_PRE_Station','Distance_to_PRE_Switch']
gdf_export = gdf_export[milepost_clms]
export_spreadsheet = gdf_export.to_csv('../01_Data/02_Processed/milepost_processed.csv', index=False)


# Snapping observations
gdf_speed_east = gpd.read_file('../01_data/02_Processed/GIS/speed_east.shp', engine="pyogrio")
gdf_speed_west = gpd.read_file('../01_data/02_Processed/GIS/speed_west.shp', engine="pyogrio")

gdf_speed_east['speed'].hist(bins=80)
gdf_speed_west['speed'].hist(bins=80)

gdf_speed_east.shape
len(gdf_speed_east[gdf_speed_east['speed'] == 0])
gdf_speed_east['speed'].value_counts()

# west_speed_plot = gdf_speed_west.to_crs(3857).plot(column='speed', legend=True)
# ctx.add_basemap(west_speed_plot,
#                 source=ctx.providers.CartoDB.Voyager)

gdf_speed_east = gdf_speed_east.to_crs(gdf_milepost.crs)
gdf_speed_west = gdf_speed_west.to_crs(gdf_westbound.crs)

model_east = ckdnearest(gdf_speed_east, gdf_milepost)
model_west = ckdnearest(gdf_speed_west, gdf_westbound)

model_east = model_east.rename(columns={'speed': 'Speed_mph'})
model_west = model_west.rename(columns={'speed': 'Speed_mph'})

## remove 0s that are not at the stations
mask = (model_east['Speed_mph']==0) & (model_east['Station_if']!=1)
model_east_zero = model_east[mask]

model_east_zt = model_east.merge(model_east_zero, 
                                 how='outer', 
                                 indicator=True).query("_merge == 'left_only'").drop('_merge', axis=1)

model_east_zt.shape

# east_zt_speed_plot = model_east_zt.to_crs(3857).plot(column='Speed_mph', legend=True)
# ctx.add_basemap(east_zt_speed_plot,
#                 source=ctx.providers.CartoDB.Voyager)

mask = (model_west['Speed_mph']==0) & (model_west['Station_if']!=1)
model_west_zero = model_west[mask]

model_west_zt = model_west.merge(model_west_zero, 
                                 how='outer', 
                                 indicator=True).query("_merge == 'left_only'").drop('_merge', axis=1)

## reordering the columns

model_clms = ['Node_ID','Speed_mph', 'Elevation_Smoothen_ft', 'Elev_Delta_CUR_ft','Elev_Delta_FOL_2500ft_ft','Elev_Delta_FOL_2k5_5kft_ft', 'Elev_Delta_FOL_5k_7k5ft_ft', 'Elev_Delta_FOL_7k5_10kft_ft', 'Elev_Delta_PRE_2500ft_ft', 'Elev_Delta_PRE_2k5_5kft_ft', 'Elev_Delta_PRE_5k_7k5ft_ft', 'Elev_Delta_PRE_7k5_10kft_ft', 'Curve_CUR_degree','Curve_Max_FOL_2500ft_degree','Curve_Max_FOL_2k5_5kft_degree','Curve_Max_FOL_5k_7k5ft_degree','Curve_Max_FOL_7k5_10kft_degree','Curve_Max_PRE_2500ft_degree','Curve_Max_PRE_2k5_5kft_degree','Curve_Max_PRE_5k_7k5ft_degree','Curve_Max_PRE_7k5_10kft_degree','Elev_Delta_FOL_2500ft_ft','Curve_Max_FOL_2k5_5kft_degree','Curve_Max_FOL_5k_7k5ft_degree','Curve_Max_FOL_7k5_10kft_degree','Curve_Max_PRE_2500ft_degree','Curve_Max_PRE_2k5_5kft_degree','Curve_Max_PRE_5k_7k5ft_degree','Curve_Max_PRE_7k5_10kft_degree','Station','Intersection', 'Switch', 'geometry','x_coordinate', 'y_coordinate', 'Station_if', 'Intersection_if', 'Switch_if','Node_ID','Cumulative_Length_ft','Distance_to_FOL_Intersection','Distance_to_FOL_Station','Distance_to_FOL_Switch','Distance_to_PRE_Intersection','Distance_to_PRE_Station','Distance_to_PRE_Switch','Loco','Coach','CCU']
r_clms = ['Speed_mph','Curve_CUR_degree','Curve_Max_FOL_2500ft_degree','Curve_Max_FOL_2k5_5kft_degree','Curve_Max_FOL_5k_7k5ft_degree','Curve_Max_FOL_7k5_10kft_degree','Curve_Max_PRE_2500ft_degree','Curve_Max_PRE_2k5_5kft_degree','Curve_Max_PRE_5k_7k5ft_degree','Curve_Max_PRE_7k5_10kft_degree','Elev_Delta_CUR_ft' ,'Elev_Delta_FOL_2500ft_ft','Elev_Delta_FOL_2k5_5kft_ft','Elev_Delta_FOL_5k_7k5ft_ft','Elev_Delta_FOL_7k5_10kft_ft','Elev_Delta_PRE_2500ft_ft','Elev_Delta_PRE_2k5_5kft_ft','Elev_Delta_PRE_5k_7k5ft_ft','Elev_Delta_PRE_7k5_10kft_ft','Distance_to_FOL_Intersection','Distance_to_FOL_Station','Distance_to_FOL_Switch','Distance_to_PRE_Intersection','Distance_to_PRE_Station','Distance_to_PRE_Switch','Loco','Coach','CCU']


model_east_spreadsheet = model_east_zt[model_clms]
model_west_spreadsheet = model_west_zt[model_clms]

model_east_r = model_east_zt[r_clms]
model_west_r = model_west_zt[r_clms]
model_r = pd.concat([model_east_r,model_west_r])

na_counts = model_r.isna().sum()
na_counts

model_r.dropna(how='any', inplace=True)

na_counts = model_r.isna().sum()
na_counts
model_r.shape

model_east_spreadsheet.to_csv('../01_Data/02_Processed/randomForest/Speed_Model_East_v5.csv', index=False)
model_west_spreadsheet.to_csv('../01_Data/02_Processed/randomForest/Speed_Model_West_v5.csv', index=False)
model_r.to_csv('../01_Data/02_Processed/randomForest/Speed_Model_R_v5.csv', index=False)