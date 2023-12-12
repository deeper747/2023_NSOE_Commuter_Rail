import pandas as pd

df_realop = pd.read_csv('../01_Data/02_Processed/realtimeNOV12.csv')
df_realop.head()

df_realop.info()
df_realop.number = df_realop.number.astype('str') 
grouped_data = df_realop.groupby('number')
grouped_data.describe()
df_realop.number = df_realop.number.astype('int64') 

route_number = [74,75,77,79,89,90]

stop = df_realop.query('speed<1')

estt = []

for n in route_number:
    stop_byLine = stop.query(f'number=={n}')
    for i in range(len(stop_byLine['last_updated'])-1):
        if ((stop_byLine['last_updated'].iloc[i+1] - stop_byLine['last_updated'].iloc[i]) / 60) > 60:
            hr = round((stop_byLine['last_updated'].iloc[i+1] - stop_byLine['last_updated'].iloc[i]) / 3600)
            print('Estimated travel time to the next stop:', hr, 'hour')
            estt.append(hr)
        else:
            mn = round((stop_byLine['last_updated'].iloc[i+1] - stop_byLine['last_updated'].iloc[i]) / 60)
            print('Estimated travel time to the next stop:', mn, 'minutes')
            estt.append(mn)
    estt.append(0)

len(estt)

stop = stop.sort_values(by = ['number','last_updated'])
stop['estt'] = estt

pd.DataFrame(stop).to_csv(
    '../01_data/02_Processed/stop.csv',
    index=False
)

stop_t = pd.read_csv('../01_data/02_Processed/stop.csv')