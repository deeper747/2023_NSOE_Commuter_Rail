'''
Contributors: Jia-Shen Tsai, Wendy Wen, Zhengqi Jiao, Miaojun Pang,
Alexander Yoshizumi

Last Updated: 2024-3-13

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

## examination
milepost_plot = gdf_milepost.to_crs(3857).plot(column='Cumulative_Length_ft', legend=True)
ctx.add_basemap(milepost_plot,
               source=ctx.providers.CartoDB.Voyager)

intersection_plot = gdf_intersection.to_crs(3857).plot()
ctx.add_basemap(intersection_plot,
               source=ctx.providers.CartoDB.Voyager)

station_plot = gdf_station.to_crs(3857).plot()
ctx.add_basemap(station_plot,
               source=ctx.providers.CartoDB.Voyager)


switch_plot = gdf_switches.to_crs(3857).plot()
ctx.add_basemap(switch_plot,
                source=ctx.providers.CartoDB.Voyager)

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

gdf_milepost.head()

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
                # If there's no next station, set the next index the last node
                next_index = len(df) - 1
        else:
            distance_to_next_node = df.loc[next_index, 'Cumulative_Length_ft'] - row['Cumulative_Length_ft']
            distances.append(distance_to_next_node)
    return distances

intersection_dist = dist_to_key_node(gdf_milepost,'Intersection_if')
station_dist = dist_to_key_node(gdf_milepost,'Station_if')
switch_dist = dist_to_key_node(gdf_milepost,'Switch_if')

gdf_milepost["Intersection_dist"] = intersection_dist
gdf_milepost["Station_dist"] = station_dist
gdf_milepost["Switch_dist"] = switch_dist

gdf_milepost[['Intersection_dist', 'Station_dist', 'Switch_dist']]


### Next Key Node column
# Initialize lists to store the next key node types
intersection_next = []
station_next = []
switch_next = []

# Initialize variables to store the next key node types
next_intersection = 0
next_station = 0
next_switch = 0

# Iterate over the rows of the GeoDataFrame
for index, row in gdf_milepost.iterrows():
   
    # Find the next key node in the forward direction
    forward_next_index = gdf_milepost[(gdf_milepost.index > index) & ((gdf_milepost['Intersection_if'] == 1) | (gdf_milepost['Station_if'] == 1) | gdf_milepost['Switch_if'] == 1)].index.min()
    if forward_next_index is not np.nan:
        if gdf_milepost.loc[forward_next_index, 'Intersection_if'] == 1:
            next_intersection = 1
            next_station = 0
            next_switch = 0
        elif gdf_milepost.loc[forward_next_index, 'Station_if'] == 1:
            next_intersection = 0
            next_station = 1
            next_switch = 0
        else:
            next_intersection = 0
            next_station = 0
            next_switch = 1
    else:
        next_intersection = 0
        next_station = 0
        next_switch = 0
    
    # Append the next key node types to the lists
    intersection_next.append(next_intersection)
    station_next.append(next_station)
    switch_next.append(next_switch)

# Add the new columns to the GeoDataFrame
gdf_milepost['Intersection'] = intersection_next
gdf_milepost['Station'] = station_next
gdf_milepost['Switch'] = switch_next
gdf_milepost.tail()

gdf_milepost['Distance_to_FOL_Intersection'] = gdf_milepost['Intersection']*gdf_milepost['Intersection_dist']
gdf_milepost['Distance_to_FOL_Station'] = gdf_milepost['Station']*gdf_milepost['Station_dist']
gdf_milepost['Distance_to_FOL_Switch'] = gdf_milepost['Switch']*gdf_milepost['Switch_dist']

gdf_milepost['Distance_to_Key_Nodes_FOL'] = gdf_milepost['Distance_to_FOL_Intersection'] + gdf_milepost['Distance_to_FOL_Station'] + gdf_milepost['Distance_to_FOL_Switch']

# Continuous Variables

## Identify the maximum angle in the five preceding and following observations, measured in angular degree
gdf_milepost = gdf_milepost.rename(columns={'Curve_CUR_degree': 'Curve_CUR_degree'})
size = 10

gdf_milepost['Curve_Max_PRE_500ft_degree'] = gdf_milepost['Curve_CUR_degree'].rolling(window=size, min_periods=1).max().shift(1)
indexer = pd.api.indexers.FixedForwardWindowIndexer(window_size=size)
gdf_milepost['Curve_Max_FOL_500ft_degree'] = gdf_milepost['Curve_CUR_degree'].rolling(window=indexer, min_periods=1).max().shift(-1)

gdf_milepost[['Curve_CUR_degree','Curve_Max_PRE_500ft_degree']].head(20)

gdf_milepost['Curve_Max_PRE_500_1kft_degree'] = gdf_milepost['Curve_CUR_degree'].rolling(window=size, min_periods=1).max().shift(11)
gdf_milepost['Curve_Max_FOL_500_1kft_degree'] = gdf_milepost['Curve_CUR_degree'].rolling(window=indexer, min_periods=1).max().shift(-11)

gdf_milepost['Curve_Max_PRE_1k_1k5ft_degree'] = gdf_milepost['Curve_CUR_degree'].rolling(window=size, min_periods=1).max().shift(21)
gdf_milepost['Curve_Max_FOL_1k_1k5ft_degree'] = gdf_milepost['Curve_CUR_degree'].rolling(window=indexer, min_periods=1).max().shift(-21)

gdf_milepost['Curve_Max_PRE_1k5_2kft_degree'] = gdf_milepost['Curve_CUR_degree'].rolling(window=size, min_periods=1).max().shift(31)
gdf_milepost['Curve_Max_FOL_1k5_2kft_degree'] = gdf_milepost['Curve_CUR_degree'].rolling(window=indexer, min_periods=1).max().shift(-31)

gdf_milepost['Curve_Max_PRE_2k_2k5ft_degree'] = gdf_milepost['Curve_CUR_degree'].rolling(window=size, min_periods=1).max().shift(41)
gdf_milepost['Curve_Max_FOL_2k_2k5ft_degree'] = gdf_milepost['Curve_CUR_degree'].rolling(window=indexer, min_periods=1).max().shift(-41)

gdf_milepost[['Curve_CUR_degree','Curve_Max_PRE_500ft_degree','Curve_Max_PRE_2k_2k5ft_degree']].head(50)
gdf_milepost[['Curve_CUR_degree','Curve_Max_FOL_500ft_degree','Curve_Max_FOL_2k_2k5ft_degree']].tail(50)

## Identify the change in elevation from the preceding observation to the following observation. 
## Using observations spaced 50 feet apart, this corresponds to the change in elevation over a 100-feet run.
gdf_milepost['Elev_Delta_CUR_ft'] = -(gdf_milepost['Elevation_Smoothen_ft'].diff(periods=-2).shift(1))
gdf_milepost[['Elevation_Smoothen_ft','Elev_Delta_CUR_ft']]
gdf_milepost.at[0, 'Elev_Delta_CUR_ft'] = gdf_milepost.at[1,'Elevation_Smoothen_ft'] - gdf_milepost.at[0,'Elevation_Smoothen_ft']
gdf_milepost.at[14339, 'Elev_Delta_CUR_ft'] = gdf_milepost.at[14339,'Elevation_Smoothen_ft'] - gdf_milepost.at[14338,'Elevation_Smoothen_ft']

gdf_milepost['Elev_Delta_PRE_500ft_ft'] = gdf_milepost['Elev_Delta_CUR_ft'].rolling(window=size, min_periods=1).max().shift(1)
gdf_milepost['Elev_Delta_FOL_500ft_ft'] = gdf_milepost['Elev_Delta_CUR_ft'].rolling(window=indexer, min_periods=1).max().shift(-1)

gdf_milepost[['Elev_Delta_CUR_ft','Elev_Delta_PRE_500ft_ft']].head(10)

gdf_milepost['Elev_Delta_PRE_500_1kft_ft'] = gdf_milepost['Elev_Delta_CUR_ft'].rolling(window=size, min_periods=1).max().shift(11)
gdf_milepost['Elev_Delta_FOL_500_1kft_ft'] = gdf_milepost['Elev_Delta_CUR_ft'].rolling(window=indexer, min_periods=1).max().shift(-11)

gdf_milepost['Elev_Delta_PRE_1k_1k5ft_ft'] = gdf_milepost['Elev_Delta_CUR_ft'].rolling(window=size, min_periods=1).max().shift(21)
gdf_milepost['Elev_Delta_FOL_1k_1k5ft_ft'] = gdf_milepost['Elev_Delta_CUR_ft'].rolling(window=indexer, min_periods=1).max().shift(-21)

gdf_milepost['Elev_Delta_PRE_1k5_2kft_ft'] = gdf_milepost['Elev_Delta_CUR_ft'].rolling(window=size, min_periods=1).max().shift(31)
gdf_milepost['Elev_Delta_FOL_1k5_2kft_ft'] = gdf_milepost['Elev_Delta_CUR_ft'].rolling(window=indexer, min_periods=1).max().shift(-31)

gdf_milepost['Elev_Delta_PRE_2k_2k5ft_ft'] = gdf_milepost['Elev_Delta_CUR_ft'].rolling(window=size, min_periods=1).max().shift(41)
gdf_milepost['Elev_Delta_FOL_2k_2k5ft_ft'] = gdf_milepost['Elev_Delta_CUR_ft'].rolling(window=indexer, min_periods=1).max().shift(-41)

gdf_milepost[['Elev_Delta_CUR_ft','Elev_Delta_PRE_500ft_ft','Elev_Delta_PRE_2k_2k5ft_ft']].head(50)

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

gdf_westbound["Intersection_dist"] = intersection_dist
gdf_westbound["Station_dist"] = station_dist
gdf_westbound["Switch_dist"] = switch_dist

### Next Key Node column
# Initialize lists to store the next key node types
intersection_next = []
station_next = []
switch_next = []

# Initialize variables to store the next key node types
next_intersection = 1
next_station = 0
next_switch = 0

# Iterate over the rows of the GeoDataFrame
for index, row in gdf_westbound.iterrows():
   
    # Find the next key node in the forward direction
    forward_next_index = gdf_westbound[(gdf_westbound.index > index) & ((gdf_westbound['Intersection_if'] == 1) | (gdf_westbound['Station_if'] == 1) | gdf_westbound['Switch_if'] == 1)].index.min()
    if forward_next_index is not np.nan:
        if gdf_westbound.loc[forward_next_index, 'Intersection_if'] == 1:
            next_intersection = 1
            next_station = 0
            next_switch = 0
        elif gdf_westbound.loc[forward_next_index, 'Station_if'] == 1:
            next_intersection = 0
            next_station = 1
            next_switch = 0
        else:
            next_intersection = 0
            next_station = 0
            next_switch = 1
    else:
        next_intersection = 0
        next_station = 0
        next_switch = 0
    
    # Append the next key node types to the lists
    intersection_next.append(next_intersection)
    station_next.append(next_station)
    switch_next.append(next_switch)

# Add the new columns to the GeoDataFrame
gdf_westbound['Intersection'] = intersection_next
gdf_westbound['Station'] = station_next
gdf_westbound['Switch'] = switch_next

gdf_westbound['Distance_to_FOL_Intersection'] = gdf_westbound['Intersection']*gdf_westbound['Intersection_dist']
gdf_westbound['Distance_to_FOL_Station'] = gdf_westbound['Station']*gdf_westbound['Station_dist']
gdf_westbound['Distance_to_FOL_Switch'] = gdf_westbound['Switch']*gdf_westbound['Switch_dist']

gdf_westbound['Distance_to_Key_Nodes_FOL'] = gdf_westbound['Distance_to_FOL_Intersection'] + gdf_westbound['Distance_to_FOL_Station'] + gdf_westbound['Distance_to_FOL_Switch']

## extract the distance value to the next key node in the west-bound dataset
## as the distance to the preceding key node in the east-bound dataset
gdf_milepost['Distance_to_PRE_Intersection'] = gdf_milepost['Node_ID'].map(gdf_westbound.set_index('Node_ID')['Distance_to_FOL_Intersection'])
gdf_milepost['Distance_to_PRE_Station'] = gdf_milepost['Node_ID'].map(gdf_westbound.set_index('Node_ID')['Distance_to_FOL_Station'])
gdf_milepost['Distance_to_PRE_Switch'] = gdf_milepost['Node_ID'].map(gdf_westbound.set_index('Node_ID')['Distance_to_FOL_Switch'])

gdf_milepost['Distance_to_Key_Nodes_PRE'] = gdf_milepost['Node_ID'].map(gdf_westbound.set_index('Node_ID')['Distance_to_Key_Nodes_FOL'])

# Rerun the process for the West-Bound dataset
## Identify the maximum angle in the five preceding and following observations, measured in angular degree
gdf_westbound['Curve_Max_PRE_500ft_degree'] = gdf_westbound['Curve_CUR_degree'].rolling(window=size, min_periods=1).max().shift(1)
gdf_westbound['Curve_Max_FOL_500ft_degree'] = gdf_westbound['Curve_CUR_degree'].rolling(window=indexer, min_periods=1).max().shift(-1)

gdf_westbound['Curve_Max_PRE_500_1kft_degree'] = gdf_westbound['Curve_CUR_degree'].rolling(window=size, min_periods=1).max().shift(11)
gdf_westbound['Curve_Max_FOL_500_1kft_degree'] = gdf_westbound['Curve_CUR_degree'].rolling(window=indexer, min_periods=1).max().shift(-11)

gdf_westbound['Curve_Max_PRE_1k_1k5ft_degree'] = gdf_westbound['Curve_CUR_degree'].rolling(window=size, min_periods=1).max().shift(21)
gdf_westbound['Curve_Max_FOL_1k_1k5ft_degree'] = gdf_westbound['Curve_CUR_degree'].rolling(window=indexer, min_periods=1).max().shift(-21)

gdf_westbound['Curve_Max_PRE_1k5_2kft_degree'] = gdf_westbound['Curve_CUR_degree'].rolling(window=size, min_periods=1).max().shift(31)
gdf_westbound['Curve_Max_FOL_1k5_2kft_degree'] = gdf_westbound['Curve_CUR_degree'].rolling(window=indexer, min_periods=1).max().shift(-31)

gdf_westbound['Curve_Max_PRE_2k_2k5ft_degree'] = gdf_westbound['Curve_CUR_degree'].rolling(window=size, min_periods=1).max().shift(41)
gdf_westbound['Curve_Max_FOL_2k_2k5ft_degree'] = gdf_westbound['Curve_CUR_degree'].rolling(window=indexer, min_periods=1).max().shift(-41)

gdf_westbound[['Curve_CUR_degree','Curve_Max_PRE_500ft_degree','Curve_Max_PRE_2k_2k5ft_degree']].head(50)
gdf_westbound[['Curve_CUR_degree','Curve_Max_FOL_500ft_degree','Curve_Max_FOL_2k_2k5ft_degree']].tail(50)


## Identify the change in elevation from the preceding observation to the following observation. 
## Using observations spaced 50 feet apart, this corresponds to the change in elevation over a 100-feet run.
gdf_westbound['Elev_Delta_CUR_ft'] = -(gdf_westbound['Elevation_Smoothen_ft'].diff(periods=-2).shift(1))
gdf_westbound[['Elevation_Smoothen_ft','Elev_Delta_CUR_ft']]

gdf_westbound.at[0, 'Elev_Delta_CUR_ft'] = gdf_westbound.at[1,'Elevation_Smoothen_ft'] - gdf_westbound.at[0,'Elevation_Smoothen_ft']
gdf_westbound.at[14339, 'Elev_Delta_CUR_ft'] = gdf_westbound.at[14339,'Elevation_Smoothen_ft'] - gdf_westbound.at[14338,'Elevation_Smoothen_ft']

gdf_westbound['Elev_Delta_PRE_500ft_ft'] = gdf_westbound['Elev_Delta_CUR_ft'].rolling(window=size, min_periods=1).max().shift(1)
gdf_westbound['Elev_Delta_FOL_500ft_ft'] = gdf_westbound['Elev_Delta_CUR_ft'].rolling(window=indexer, min_periods=1).max().shift(-1)

# gdf_westbound[['Elev_Delta_CUR_ft','Elev_Delta_PRE_500ft_ft']].head(10)

gdf_westbound['Elev_Delta_PRE_500_1kft_ft'] = gdf_westbound['Elev_Delta_CUR_ft'].rolling(window=size, min_periods=1).max().shift(11)
gdf_westbound['Elev_Delta_FOL_500_1kft_ft'] = gdf_westbound['Elev_Delta_CUR_ft'].rolling(window=indexer, min_periods=1).max().shift(-11)

gdf_westbound['Elev_Delta_PRE_1k_1k5ft_ft'] = gdf_westbound['Elev_Delta_CUR_ft'].rolling(window=size, min_periods=1).max().shift(21)
gdf_westbound['Elev_Delta_FOL_1k_1k5ft_ft'] = gdf_westbound['Elev_Delta_CUR_ft'].rolling(window=indexer, min_periods=1).max().shift(-21)

gdf_westbound['Elev_Delta_PRE_1k5_2kft_ft'] = gdf_westbound['Elev_Delta_CUR_ft'].rolling(window=size, min_periods=1).max().shift(31)
gdf_westbound['Elev_Delta_FOL_1k5_2kft_ft'] = gdf_westbound['Elev_Delta_CUR_ft'].rolling(window=indexer, min_periods=1).max().shift(-31)

gdf_westbound['Elev_Delta_PRE_2k_2k5ft_ft'] = gdf_westbound['Elev_Delta_CUR_ft'].rolling(window=size, min_periods=1).max().shift(41)
gdf_westbound['Elev_Delta_FOL_2k_2k5ft_ft'] = gdf_westbound['Elev_Delta_CUR_ft'].rolling(window=indexer, min_periods=1).max().shift(-41)

gdf_westbound[['Elev_Delta_CUR_ft','Elev_Delta_PRE_500ft_ft','Elev_Delta_PRE_2k_2k5ft_ft']].head(50)

gdf_westbound['Distance_to_PRE_Intersection'] = gdf_westbound['Node_ID'].map(gdf_milepost.set_index('Node_ID')['Distance_to_FOL_Intersection'])
gdf_westbound['Distance_to_PRE_Station'] = gdf_westbound['Node_ID'].map(gdf_milepost.set_index('Node_ID')['Distance_to_FOL_Station'])
gdf_westbound['Distance_to_PRE_Switch'] = gdf_westbound['Node_ID'].map(gdf_milepost.set_index('Node_ID')['Distance_to_FOL_Switch'])

gdf_westbound['Distance_to_Key_Nodes_PRE'] = gdf_westbound['Node_ID'].map(gdf_milepost.set_index('Node_ID')['Distance_to_Key_Nodes_FOL'])

gdf_milepost.shape
gdf_westbound.shape


# Snapping observations
gdf_speed_east = gpd.read_file('../01_data/02_Processed/GIS/speed_east.shp', engine="pyogrio")
gdf_speed_west = gpd.read_file('../01_data/02_Processed/GIS/speed_west.shp', engine="pyogrio")

gdf_speed_west.head()

west_speed_plot = gdf_speed_west.to_crs(3857).plot(column='speed', legend=True)
ctx.add_basemap(west_speed_plot,
               source=ctx.providers.CartoDB.Voyager)

west_speed_outlier_plot = gdf_speed_west[0:35].to_crs(3857).plot(column='speed', figsize=(10,6), legend=True)
ctx.add_basemap(west_speed_outlier_plot,
               source=ctx.providers.CartoDB.Voyager)

east_speed_outlier_plot = gdf_speed_east[0:35].to_crs(3857).plot(column='speed', figsize=(10,10))
ctx.add_basemap(east_speed_outlier_plot,
               source=ctx.providers.CartoDB.Voyager)

gdf_speed_east = gdf_speed_east.to_crs(gdf_milepost.crs)
gdf_speed_west = gdf_speed_west.to_crs(gdf_westbound.crs)

model_east = ckdnearest(gdf_speed_east, gdf_milepost)
model_west = ckdnearest(gdf_speed_west, gdf_westbound)

model_east = model_east.rename(columns={'speed': 'Speed_mph'})
model_west = model_west.rename(columns={'speed': 'Speed_mph'})

# The points beyond the Greensboro station will give mixed signal to the model because the H-Line is not long enoguh for distinguishing the points
# so I am removing points beyond the station
model_east.columns

outlier_mask = (model_east['Node_ID']>=32)
model_east_rmol = model_east[outlier_mask]
model_east_rmol.shape

outlier_mask = (model_west['Node_ID']>=32)
model_west_rmol = model_west[outlier_mask]

# Export the east-bound dataset
## reordering the columns

model_clms = ['Speed_mph', 'Elevation_Smoothen_ft', 'Elev_Delta_CUR_ft','Elev_Delta_FOL_500ft_ft','Elev_Delta_FOL_500_1kft_ft', 'Elev_Delta_FOL_1k_1k5ft_ft', 'Elev_Delta_FOL_1k5_2kft_ft', 'Elev_Delta_FOL_2k_2k5ft_ft', 'Elev_Delta_PRE_500ft_ft', 'Elev_Delta_PRE_500_1kft_ft', 'Elev_Delta_PRE_1k_1k5ft_ft', 'Elev_Delta_PRE_1k5_2kft_ft', 'Elev_Delta_PRE_2k_2k5ft_ft', 'Curve_CUR_degree','Curve_Max_FOL_500ft_degree','Curve_Max_FOL_500_1kft_degree','Curve_Max_FOL_1k_1k5ft_degree','Curve_Max_FOL_1k5_2kft_degree','Curve_Max_FOL_2k_2k5ft_degree','Curve_Max_PRE_500ft_degree','Curve_Max_PRE_500_1kft_degree','Curve_Max_PRE_1k_1k5ft_degree','Curve_Max_PRE_1k5_2kft_degree','Curve_Max_PRE_2k_2k5ft_degree','Elev_Delta_FOL_500ft_ft','Curve_Max_FOL_500_1kft_degree','Curve_Max_FOL_1k_1k5ft_degree','Curve_Max_FOL_1k5_2kft_degree','Curve_Max_FOL_2k_2k5ft_degree','Curve_Max_PRE_500ft_degree','Curve_Max_PRE_500_1kft_degree','Curve_Max_PRE_1k_1k5ft_degree','Curve_Max_PRE_1k5_2kft_degree','Curve_Max_PRE_2k_2k5ft_degree','Distance_to_Key_Nodes_FOL', 'Distance_to_Key_Nodes_PRE', 'Station','Intersection', 'Switch', 'geometry','x_coordinate', 'y_coordinate', 'Station_if', 'Intersection_if', 'Switch_if', 'Intersection_dist', 'Station_dist','Node_ID','Cumulative_Length_ft','Distance_to_FOL_Intersection','Distance_to_FOL_Station','Distance_to_FOL_Switch','Distance_to_PRE_Intersection','Distance_to_PRE_Station','Distance_to_PRE_Switch']
r_clms = ['Speed_mph','Curve_CUR_degree','Curve_Max_FOL_500ft_degree','Curve_Max_FOL_500_1kft_degree','Curve_Max_FOL_1k_1k5ft_degree','Curve_Max_FOL_1k5_2kft_degree','Curve_Max_FOL_2k_2k5ft_degree','Curve_Max_PRE_500ft_degree','Curve_Max_PRE_500_1kft_degree','Curve_Max_PRE_1k_1k5ft_degree','Curve_Max_PRE_1k5_2kft_degree','Curve_Max_PRE_2k_2k5ft_degree','Elev_Delta_CUR_ft' ,'Elev_Delta_FOL_500ft_ft','Elev_Delta_FOL_500_1kft_ft','Elev_Delta_FOL_1k_1k5ft_ft','Elev_Delta_FOL_1k5_2kft_ft','Elev_Delta_FOL_2k_2k5ft_ft','Elev_Delta_PRE_500ft_ft','Elev_Delta_PRE_500_1kft_ft','Elev_Delta_PRE_1k_1k5ft_ft','Elev_Delta_PRE_1k5_2kft_ft','Elev_Delta_PRE_2k_2k5ft_ft','Distance_to_FOL_Intersection','Distance_to_FOL_Station','Distance_to_FOL_Switch','Distance_to_PRE_Intersection','Distance_to_PRE_Station','Distance_to_PRE_Switch',]

model_east_spreadsheet = model_east_rmol[model_clms]
model_west_spreadsheet = model_west_rmol[model_clms]

model_east_r = model_east_rmol[r_clms]
model_west_r = model_west_rmol[r_clms]
model_r = pd.concat([model_east_r,model_west_r])

## if not removing outliers
model_east_spreadsheet = model_east[model_clms]
model_west_spreadsheet = model_west[model_clms]

model_east_r = model_east_rmol[r_clms]
model_west_r = model_west_rmol[r_clms]
model_r = pd.concat([model_east_r,model_west_r])

na_counts = model_r.isna().sum()
na_counts

model_r.dropna(how='any', inplace=True)

na_counts = model_r.isna().sum()
na_counts

model_east_spreadsheet.to_csv('../01_Data/02_Processed/Speed_Model_East.csv', index=False)
model_west_spreadsheet.to_csv('../01_Data/02_Processed/Speed_Model_West.csv', index=False)
model_r.to_csv('../01_Data/02_Processed/Speed_Model_R.csv', index=False)