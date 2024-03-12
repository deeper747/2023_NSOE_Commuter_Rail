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
from shapely.ops import split, unary_union
from shapely.geometry import LineString

# read the dataset in
gdf_hline = gpd.read_file('../01_Data/02_Processed/GIS/H_Line.zip')
# gdf_realop_n = gpd.read_file('../01_Data/02_Processed/GIS/realop_n.zip', engine="pyogrio")
df_realop = pd.read_csv('../01_Data/02_Processed/GIS/realop_total.csv')
df_milepost = pd.read_csv('../01_Data/02_Processed/H_Line_50ft_elevation.csv')
gdf_segments = gpd.read_file('../01_Data/02_Processed/GIS/Segments_50ft.zip')

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

gdf_hline = gdf_hline.to_crs(gdf_milepost.crs)
gdf_segments = gdf_segments.to_crs(gdf_realop.crs)

## data examination

gdf_milepost.head()
gdf_milepost.shape

### speed distribution
df_milepost['RASTERVALU'].plot();
gdf_realop.head()
gdf_realop.shape

### Plot the speed data with a base map
realop_plot = gdf_realop_n.to_crs(3857).plot(column='speed', legend=True)
ctx.add_basemap(realop_plot,
               source=ctx.providers.CartoDB.Voyager)

### plot the hline
hline_plot = gdf_hline.plot(color = 'g', figsize=(24,6))
ctx.add_basemap(hline_plot,
                crs = gdf_hline.crs.to_string(),
                source=ctx.providers.CartoDB.Voyager)
# plt.savefig('../05_Deliverables/plots/hline')


# from shapely.ops import nearest_points
# from shapely.geometry import Point, LineString

# # Create a list to store the moved points
# moved_points = []

# # Iterate over each row in gdf_realop
# for _, row in gdf_realop.iterrows():
#     point = row['geometry']

#     # Find the shortest line between the point and gdf_hline
#     line_collection = gdf_hline.geometry.shortest_line(point)

#     # Handle the GeometryCollection and extract the endpoint coordinate
#     for geom in line_collection:
#         if isinstance(geom, LineString):
#             nearest = geom.coords[-1]
#             break

#     # Add the nearest point to the moved_points list
#     moved_points.append(Point(nearest))

# # Create a new GeoDataFrame gdf_realop_nearest with the moved points
# gdf_realop_nearest = gpd.GeoDataFrame(geometry=moved_points, crs=gdf_realop.crs)
# gdf_realop_nearest.head()

# realop_n_plot = gdf_realop_nearest.to_crs(3857).plot()
# ctx.add_basemap(realop_n_plot,
#                source=ctx.providers.CartoDB.Voyager)

# gdf_realop['geometry'] = moved_points

# # Create another list of moved points
# moved_points_mp = []

# # Iterate over each row in gdf_milepost
# for _, row in gdf_milepost.iterrows():
#     point = row['geometry']
#     # Find the shortest line between the point and gdf_hline
#     line_collection = gdf_hline.geometry.shortest_line(point)
#     # Handle the GeometryCollection and extract the endpoint coordinate
#     for geom in line_collection:
#         if isinstance(geom, LineString):
#             nearest = geom.coords[-1]
#             break
#     # Add the nearest point to the moved_points list
#     moved_points_mp.append(Point(nearest))

# gdf_milepost['geometry'] = moved_points_mp

# Split the railway pline at the milepost point
# # Initialize list to store LineString segments
# segments = []
# hline = gdf_hline.geometry.unary_union

# # Iterate over milepost points
# for idx, milepost_point in gdf_milepost.iterrows():
#     # Split the railway line at the milepost point
#     split_line = split(hline, milepost_point.geometry)

#     # Check if split_line is a GeometryCollection
#     if split_line.geom_type == 'GeometryCollection':
#         # Iterate over each geometry in the GeometryCollection
#         for geom in split_line:
#             # Append only LineString geometries to the segments list
#             if isinstance(geom, LineString):
#                 segments.append(geom)

#     elif isinstance(split_line, LineString):
#         # Append the resulting LineString segment to the list
#         segments.append(split_line)
# # Create GeoDataFrame with LineString segments
# gdf_segments = gpd.GeoDataFrame(geometry=segments, crs=gdf_hline.crs)

# segment_plot = gdf_segments.plot(color = 'g', figsize=(24,6))
# ctx.add_basemap(segment_plot,
#                 crs = gdf_segments.crs.to_string(),
#                 source=ctx.providers.CartoDB.Voyager)
# gdf_segments.head()

# gdf_segments.insert(loc = 0,
#                     column= "breaking_points",
#                     value=[1,2]*(len(gdf_segments)//2))
# segment_plot = gdf_segments.plot(column="breaking_points", figsize=(24,6))
# ctx.add_basemap(segment_plot,
#                 crs = gdf_segments.crs.to_string(),
#                 source=ctx.providers.CartoDB.Voyager)

segment = gdf_segments.geometry[0]
intersecting_points = gdf_realop_n[gdf_realop_n.intersects(segment)]
type(intersecting_points)
intersecting_points.head()
type(segment)
segment.plot()

# Calculate average speed for each line segment
average_speeds = []
## Iterate over each line segment
for segment in gdf_segments.geometry:
    s_buffer = segment.buffer(0.001)
    ## Select the real operation points that intersect with the current line segment
    intersecting_points = gdf_realop_n[gdf_realop_n.intersects(s_buffer)]    
    ## Calculate the average speed of the intersecting points
    average_speed = intersecting_points['speed'].mean()    
    ## Append the average speed to the list
    average_speeds.append(average_speed)

## Add the average speeds as a new column in the gdf_segments GeoDataFrame
gdf_segments['average_speed'] = average_speeds
gdf_segments['average_speed'].hist()

gdf_segments.head()

# Plot the line segments with average speed
px = 1/plt.rcParams['figure.dpi']  # pixel in inches
fig, ax = plt.subplots(figsize=(800*px, 450*px))
# Plot the line segments
gdf_segments.to_crs(3857).plot(ax=ax, column="average_speed", linewidth=7.0, legend=True)
# Add a basemap
ctx.add_basemap(ax)
# Show the plot
plt.savefig('../05_Deliverables/plots/AvgSpeed', dpi=300)
plt.show()



# Plot the line segments with average speed
fig, ax = plt.subplots(figsize=(10, 10))
# Plot the line segments
gdf_segments.plot(ax=ax, color='g')
# Add the average speed as labels on the line segments
for idx, row in gdf_segments.iterrows():
    centroid = row.geometry.centroid
    average_speed = row['average_speed']
    ax.annotate(f'{average_speed:.2f}', (centroid.x, centroid.y), color='red')
xmin = -8.81
xmax = -8.825
ymin = 4.315
ymax = 4.305
# Set the x and y axis limits to zoom in to a specific area
ax.set_xlim(xmin, xmax)  
ax.set_ylim(ymin, ymax)
# Add a basemap
ctx.add_basemap(ax)
# Show the plot
plt.show()
