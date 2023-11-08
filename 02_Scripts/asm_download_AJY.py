'''
Contributors: Jia-Shen Tsai, Wendy Wen, Zhengqi Jiao, Miaojun Pang,
Alexander Yoshizumi

Last Updated: 2023-11-02

Description: When run, script pulls time-location data for passenger trains
in the US from https://asm.transitdocs.com/ at a specified interval.
'''


import requests, json, time, os
from datetime import datetime

#os.chdir('../01_Data/01_Source') #don't know why I couldn't change the directory. Might because I use google drvie syncing, but VScode don't have the access to the folder

def download_json_data(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Failed to download data. Status Code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {e}")
    return None

def save_to_json(data, filename):
    with open(filename, 'w') as outfile:
        json.dump(data, outfile, indent=2)
        print(f"Data saved to {filename}")

def main():
    backend_url = "https://asm-backend.transitdocs.com/map"  # the backend URL
    total_loops = 7 * 24 * 60 * 3  # 7 days * 24 hours * 60 minutes/hour * 3 (for 20 seconds intervals)
    current_loop = 0
    data_list = []

    while current_loop < total_loops:
        json_data = download_json_data(backend_url)
        if json_data:
            # Process the downloaded JSON data here
            print("Downloaded JSON data:", json.dumps(json_data, indent=2))
            data_list.append(json_data)

        # Retrieve current date and time. 
        date_time = datetime.now()

        # Save outfile name.
        date_time_clean = str(date_time).replace('-','_',)
        date_time_clean = date_time_clean.replace(' ','_',)
        date_time_clean = date_time_clean.replace(':','_',)
        date_time_clean = date_time_clean.replace('.','_',)
        outfile = '../01_Data/01_Source/' + date_time_clean + '.json'

        # Save the data to a JSON file
        save_to_json(data_list, outfile)
        
        # Wait for 20 seconds before making the next request
        time.sleep(20)
        current_loop += 1

if __name__ == "__main__":
    main()
