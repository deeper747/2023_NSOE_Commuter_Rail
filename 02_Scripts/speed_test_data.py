'''
Contributors: Jia-Shen Tsai, Wendy Wen, Zhengqi Jiao, Miaojun Pang,
Alexander Yoshizumi

Last Updated: 2024-4-5

Description: When run, script create the variables with regard to the key nodes
'''
# Setup
## Packages
import pandas as pd
import numpy as np
import geopandas as gpd
import contextily as ctx

## Read the dataset
df_test = pd.read_csv('/Users/jason/Library/CloudStorage/GoogleDrive-deeperduke@gmail.com/.shortcut-targets-by-id/1gsetPzqCMaQ4qQzbQ7GR4eMkBkcvb_5f/2023_NSOE_Commuter_Rail/01_Data/02_Processed/CR_East_Milepost.csv')

## transform to gpd
g1 = gpd.points_from_xy(x=df_test['x_coordinate'], y = df_test['y_coordinate'])
gdf_test = gpd.GeoDataFrame(
    data = df_test,
    geometry = g1,
    crs = 4326
)

## examination
test_plot = gdf_test.to_crs(3857).plot(column='Cumulative_Length_ft', legend=True)
ctx.add_basemap(test_plot,
                source=ctx.providers.CartoDB.Voyager)

# Discrete nodes

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

intersection_dist = dist_to_key_node(gdf_test,'Intersection_if')
station_dist = dist_to_key_node(gdf_test,'Station_if')
switch_dist = dist_to_key_node(gdf_test,'Switch_if')

gdf_test['Distance_to_FOL_Intersection'] = intersection_dist
gdf_test['Distance_to_FOL_Station'] = station_dist
gdf_test['Distance_to_FOL_Switch'] = switch_dist

# Continuous Variables

## Identify the maximum angle in the five preceding and following observations, measured in angular degree
gdf_test = gdf_test.rename(columns={'Curve_Current_degrees': 'Curve_CUR_degree'})
size = 50

gdf_test['Curve_Max_PRE_2500ft_degree'] = gdf_test['Curve_CUR_degree'].rolling(window=size, min_periods=1).max().shift(1)
indexer = pd.api.indexers.FixedForwardWindowIndexer(window_size=size)
gdf_test['Curve_Max_FOL_2500ft_degree'] = gdf_test['Curve_CUR_degree'].rolling(window=indexer, min_periods=1).max().shift(-1)

gdf_test[['Curve_CUR_degree','Curve_Max_PRE_2500ft_degree']].head(20)

gdf_test['Curve_Max_PRE_2k5_5kft_degree'] = gdf_test['Curve_CUR_degree'].rolling(window=size, min_periods=1).max().shift(51)
gdf_test['Curve_Max_FOL_2k5_5kft_degree'] = gdf_test['Curve_CUR_degree'].rolling(window=indexer, min_periods=1).max().shift(-51)

gdf_test['Curve_Max_PRE_5k_7k5ft_degree'] = gdf_test['Curve_CUR_degree'].rolling(window=size, min_periods=1).max().shift(101)
gdf_test['Curve_Max_FOL_5k_7k5ft_degree'] = gdf_test['Curve_CUR_degree'].rolling(window=indexer, min_periods=1).max().shift(-101)

gdf_test['Curve_Max_PRE_7k5_10kft_degree'] = gdf_test['Curve_CUR_degree'].rolling(window=size, min_periods=1).max().shift(151)
gdf_test['Curve_Max_FOL_7k5_10kft_degree'] = gdf_test['Curve_CUR_degree'].rolling(window=indexer, min_periods=1).max().shift(-151)

gdf_test[['Curve_CUR_degree','Curve_Max_FOL_2500ft_degree','Curve_Max_PRE_7k5_10kft_degree']][150:170]

## Identify the change in elevation from the preceding observation to the following observation. 
## Using observations spaced 50 feet apart, this corresponds to the change in elevation over a 100-feet run.
gdf_test['Elev_Delta_CUR_ft'] = -(gdf_test['Elevation_Smoothen_ft'].diff(periods=-2).shift(1))/100
gdf_test[['Elevation_Smoothen_ft','Elev_Delta_CUR_ft']]
gdf_test.at[0, 'Elev_Delta_CUR_ft'] = (gdf_test.at[1,'Elevation_Smoothen_ft'] - gdf_test.at[0,'Elevation_Smoothen_ft'])/50
gdf_test.at[14339, 'Elev_Delta_CUR_ft'] = (gdf_test.at[14339,'Elevation_Smoothen_ft'] - gdf_test.at[14338,'Elevation_Smoothen_ft'])/50

gdf_test['Elev_Delta_PRE_2500ft_ft'] = gdf_test['Elev_Delta_CUR_ft'].rolling(window=size, min_periods=1).max().shift(1)
gdf_test['Elev_Delta_FOL_2500ft_ft'] = gdf_test['Elev_Delta_CUR_ft'].rolling(window=indexer, min_periods=1).max().shift(-1)

gdf_test['Elev_Delta_PRE_2k5_5kft_ft'] = gdf_test['Elev_Delta_CUR_ft'].rolling(window=size, min_periods=1).max().shift(51)
gdf_test['Elev_Delta_FOL_2k5_5kft_ft'] = gdf_test['Elev_Delta_CUR_ft'].rolling(window=indexer, min_periods=1).max().shift(-51)

gdf_test['Elev_Delta_PRE_5k_7k5ft_ft'] = gdf_test['Elev_Delta_CUR_ft'].rolling(window=size, min_periods=1).max().shift(101)
gdf_test['Elev_Delta_FOL_5k_7k5ft_ft'] = gdf_test['Elev_Delta_CUR_ft'].rolling(window=indexer, min_periods=1).max().shift(-101)

gdf_test['Elev_Delta_PRE_7k5_10kft_ft'] = gdf_test['Elev_Delta_CUR_ft'].rolling(window=size, min_periods=1).max().shift(151)
gdf_test['Elev_Delta_FOL_7k5_10kft_ft'] = gdf_test['Elev_Delta_CUR_ft'].rolling(window=indexer, min_periods=1).max().shift(-151)

# West-bound

## Create a dataset flipping the line
gdf_test_wb = gdf_test.loc[::-1].reset_index(drop=True)
gdf_test_wb['Intersection_if'].head()
gdf_test_wb.shape

gdf_test_wb['Cumulative_Length_ft'] = gdf_test_wb.index * 50

gdf_test_wb.head()

## recalculate the distance

intersection_dist = dist_to_key_node(gdf_test_wb,'Intersection_if')
station_dist = dist_to_key_node(gdf_test_wb,'Station_if')
switch_dist = dist_to_key_node(gdf_test_wb,'Switch_if')

gdf_test_wb['Distance_to_FOL_Intersection'] = intersection_dist
gdf_test_wb['Distance_to_FOL_Station'] = station_dist
gdf_test_wb['Distance_to_FOL_Switch'] = switch_dist

## extract the distance value to the next key node in the west-bound dataset
## as the distance to the preceding key node in the east-bound dataset
gdf_test['Distance_to_PRE_Intersection'] = gdf_test['Node_ID'].map(gdf_test_wb.set_index('Node_ID')['Distance_to_FOL_Intersection'])
gdf_test['Distance_to_PRE_Station'] = gdf_test['Node_ID'].map(gdf_test_wb.set_index('Node_ID')['Distance_to_FOL_Station'])
gdf_test['Distance_to_PRE_Switch'] = gdf_test['Node_ID'].map(gdf_test_wb.set_index('Node_ID')['Distance_to_FOL_Switch'])

# Rerun the process for the West-Bound dataset
## Identify the maximum angle in the five preceding and following observations, measured in angular degree
gdf_test_wb['Curve_Max_PRE_2500ft_degree'] = gdf_test_wb['Curve_CUR_degree'].rolling(window=size, min_periods=1).max().shift(1)
gdf_test_wb['Curve_Max_FOL_2500ft_degree'] = gdf_test_wb['Curve_CUR_degree'].rolling(window=indexer, min_periods=1).max().shift(-1)

gdf_test_wb['Curve_Max_PRE_2k5_5kft_degree'] = gdf_test_wb['Curve_CUR_degree'].rolling(window=size, min_periods=1).max().shift(51)
gdf_test_wb['Curve_Max_FOL_2k5_5kft_degree'] = gdf_test_wb['Curve_CUR_degree'].rolling(window=indexer, min_periods=1).max().shift(-51)

gdf_test_wb['Curve_Max_PRE_5k_7k5ft_degree'] = gdf_test_wb['Curve_CUR_degree'].rolling(window=size, min_periods=1).max().shift(101)
gdf_test_wb['Curve_Max_FOL_5k_7k5ft_degree'] = gdf_test_wb['Curve_CUR_degree'].rolling(window=indexer, min_periods=1).max().shift(-101)

gdf_test_wb['Curve_Max_PRE_7k5_10kft_degree'] = gdf_test_wb['Curve_CUR_degree'].rolling(window=size, min_periods=1).max().shift(151)
gdf_test_wb['Curve_Max_FOL_7k5_10kft_degree'] = gdf_test_wb['Curve_CUR_degree'].rolling(window=indexer, min_periods=1).max().shift(-151)

## Identify the change in elevation from the preceding observation to the following observation. 
## Using observations spaced 50 feet apart, this corresponds to the change in elevation over a 100-feet run.
gdf_test_wb['Elev_Delta_CUR_ft'] = -(gdf_test_wb['Elevation_Smoothen_ft'].diff(periods=-2).shift(1))/100
gdf_test_wb[['Elevation_Smoothen_ft','Elev_Delta_CUR_ft']]

gdf_test_wb.at[0, 'Elev_Delta_CUR_ft'] = (gdf_test_wb.at[1,'Elevation_Smoothen_ft'] - gdf_test_wb.at[0,'Elevation_Smoothen_ft'])/50
gdf_test_wb.at[14339, 'Elev_Delta_CUR_ft'] = (gdf_test_wb.at[14339,'Elevation_Smoothen_ft'] - gdf_test_wb.at[14338,'Elevation_Smoothen_ft'])/50

gdf_test_wb['Elev_Delta_PRE_2500ft_ft'] = gdf_test_wb['Elev_Delta_CUR_ft'].rolling(window=size, min_periods=1).max().shift(1)
gdf_test_wb['Elev_Delta_FOL_2500ft_ft'] = gdf_test_wb['Elev_Delta_CUR_ft'].rolling(window=indexer, min_periods=1).max().shift(-1)

gdf_test_wb['Elev_Delta_PRE_2k5_5kft_ft'] = gdf_test_wb['Elev_Delta_CUR_ft'].rolling(window=size, min_periods=1).max().shift(51)
gdf_test_wb['Elev_Delta_FOL_2k5_5kft_ft'] = gdf_test_wb['Elev_Delta_CUR_ft'].rolling(window=indexer, min_periods=1).max().shift(-51)

gdf_test_wb['Elev_Delta_PRE_5k_7k5ft_ft'] = gdf_test_wb['Elev_Delta_CUR_ft'].rolling(window=size, min_periods=1).max().shift(101)
gdf_test_wb['Elev_Delta_FOL_5k_7k5ft_ft'] = gdf_test_wb['Elev_Delta_CUR_ft'].rolling(window=indexer, min_periods=1).max().shift(-101)

gdf_test_wb['Elev_Delta_PRE_7k5_10kft_ft'] = gdf_test_wb['Elev_Delta_CUR_ft'].rolling(window=size, min_periods=1).max().shift(151)
gdf_test_wb['Elev_Delta_FOL_7k5_10kft_ft'] = gdf_test_wb['Elev_Delta_CUR_ft'].rolling(window=indexer, min_periods=1).max().shift(-151)

## distance to previous key node
gdf_test_wb['Distance_to_PRE_Intersection'] = gdf_test_wb['Node_ID'].map(gdf_test.set_index('Node_ID')['Distance_to_FOL_Intersection'])
gdf_test_wb['Distance_to_PRE_Station'] = gdf_test_wb['Node_ID'].map(gdf_test.set_index('Node_ID')['Distance_to_FOL_Station'])
gdf_test_wb['Distance_to_PRE_Switch'] = gdf_test_wb['Node_ID'].map(gdf_test.set_index('Node_ID')['Distance_to_FOL_Switch'])

gdf_test.shape
gdf_test_wb.shape

## creating the trainset difference variables
gdf_test['Loco'] = 1
gdf_test['Coach'] = 4
gdf_test['CCU'] = 0

gdf_test_wb['Loco'] = 1
gdf_test_wb['Coach'] = 4
gdf_test_wb['CCU'] = 0


gdf_test_exact = gdf_test[6876:11802]

gdf_test_exact.shape

gdf_test_wb_exact = gdf_test_wb[(gdf_test_wb['Node_ID'] >= 6877) & (gdf_test_wb['Node_ID'] <= 11802)]

gdf_test_wb_exact.shape

## reordering the columns

model_clms = ['Node_ID','Elevation_Smoothen_ft', 'Elev_Delta_CUR_ft','Elev_Delta_FOL_2500ft_ft','Elev_Delta_FOL_2k5_5kft_ft', 'Elev_Delta_FOL_5k_7k5ft_ft', 'Elev_Delta_FOL_7k5_10kft_ft', 'Elev_Delta_PRE_2500ft_ft', 'Elev_Delta_PRE_2k5_5kft_ft', 'Elev_Delta_PRE_5k_7k5ft_ft', 'Elev_Delta_PRE_7k5_10kft_ft', 'Curve_CUR_degree','Curve_Max_FOL_2500ft_degree','Curve_Max_FOL_2k5_5kft_degree','Curve_Max_FOL_5k_7k5ft_degree','Curve_Max_FOL_7k5_10kft_degree','Curve_Max_PRE_2500ft_degree','Curve_Max_PRE_2k5_5kft_degree','Curve_Max_PRE_5k_7k5ft_degree','Curve_Max_PRE_7k5_10kft_degree','Elev_Delta_FOL_2500ft_ft','Curve_Max_FOL_2k5_5kft_degree','Curve_Max_FOL_5k_7k5ft_degree','Curve_Max_FOL_7k5_10kft_degree','Curve_Max_PRE_2500ft_degree','Curve_Max_PRE_2k5_5kft_degree','Curve_Max_PRE_5k_7k5ft_degree','Curve_Max_PRE_7k5_10kft_degree','geometry','x_coordinate', 'y_coordinate', 'Station_if', 'Intersection_if', 'Switch_if','Node_ID','Cumulative_Length_ft','Distance_to_FOL_Intersection','Distance_to_FOL_Station','Distance_to_FOL_Switch','Distance_to_PRE_Intersection','Distance_to_PRE_Station','Distance_to_PRE_Switch','Loco','Coach','CCU']
r_clms = ['Curve_CUR_degree','Curve_Max_FOL_2500ft_degree','Curve_Max_FOL_2k5_5kft_degree','Curve_Max_FOL_5k_7k5ft_degree','Curve_Max_FOL_7k5_10kft_degree','Curve_Max_PRE_2500ft_degree','Curve_Max_PRE_2k5_5kft_degree','Curve_Max_PRE_5k_7k5ft_degree','Curve_Max_PRE_7k5_10kft_degree','Elev_Delta_CUR_ft' ,'Elev_Delta_FOL_2500ft_ft','Elev_Delta_FOL_2k5_5kft_ft','Elev_Delta_FOL_5k_7k5ft_ft','Elev_Delta_FOL_7k5_10kft_ft','Elev_Delta_PRE_2500ft_ft','Elev_Delta_PRE_2k5_5kft_ft','Elev_Delta_PRE_5k_7k5ft_ft','Elev_Delta_PRE_7k5_10kft_ft','Distance_to_FOL_Intersection','Distance_to_FOL_Station','Distance_to_FOL_Switch','Distance_to_PRE_Intersection','Distance_to_PRE_Station','Distance_to_PRE_Switch','Loco','Coach','CCU','x_coordinate','y_coordinate']

## all the columns
test_east_spreadsheet = gdf_test_exact[model_clms]
test_west_spreadsheet = gdf_test_wb[model_clms]

test_east_spreadsheet.to_csv('../01_Data/02_Processed/randomForest/Speed_Model_East_TestData.csv', index=False)
test_west_spreadsheet.to_csv('../01_Data/02_Processed/randomForest/Speed_Model_West_TestData.csv', index=False)

## only the columns in random forest
# gdf_test_east_150_r = gdf_test_150[r_clms]
# gdf_test_west_150_r = gdf_test_wb_150[r_clms]
# test_150_r = pd.concat([gdf_test_east_150_r, gdf_test_west_150_r])

# na_counts = test_150_r.isna().sum()
# na_counts

# test_150_r.to_csv('../01_Data/02_Processed/randomForest/TestData_150.csv', index=False)

## create the csv to feed in R
gdf_test_east_exact_r = gdf_test_exact[r_clms]
gdf_test_west_exact_r = gdf_test_wb_exact[r_clms]
test_exact_r = pd.concat([gdf_test_east_exact_r, gdf_test_west_exact_r])

na_counts = test_exact_r.isna().sum()
na_counts

test_exact_r.to_csv('../01_Data/02_Processed/randomForest/TestData_exact.csv', index=False)
