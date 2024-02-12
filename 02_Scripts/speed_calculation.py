'''
Contributors: Jia-Shen Tsai, Wendy Wen, Zhengqi Jiao, Miaojun Pang,
Alexander Yoshizumi

Last Updated: 2024-2-11

Description: When run, script summarize the speed for every segment in the input file
'''
import pandas as pd
import geopandas as gpd
import contextily as ctx

df_realop = pd.read_csv('../01_data/02_Processed/realop.csv')
