'''
Contributors: Jia-Shen Tsai, Wendy Wen, Zhengqi Jiao, Miaojun Pang,
Alexander Yoshizumi

Last Updated: 2023-11-27

Description: When run, script segment the amtrak route by elevation
'''

import arcpy
import pandas as pd
import geopandas as gpd

# Input polyline feature class
input_fc = 

# Field containing elevation change values
elevation_change_field = "ElevationChange"

# Field to hold the classification (e.g., "Uphill" or "Downhill")
classification_field = "Classification"

# Create a new field for classification if it doesn't exist
if not arcpy.ListFields(input_fc, classification_field):
    arcpy.AddField_management(input_fc, classification_field, "TEXT")

# Update the classification field based on elevation change and keep the change as an attribute
with arcpy.da.UpdateCursor(input_fc, [elevation_change_field, classification_field]) as cursor:
    for row in cursor:
        elevation_change = row[0]
        if elevation_change > 0:
            row[1] = f"Uphill ({elevation_change} meters)"
        else:
            row[1] = f"Downhill ({abs(elevation_change)} meters)"
        cursor.updateRow(row)

print("Classification complete.")
