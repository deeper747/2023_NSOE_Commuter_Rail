'''
Contributors: Jia-Shen Tsai, Wendy Wen, Zhengqi Jiao, Miaojun Pang,
Alexander Yoshizumi

Last Updated: 2023-11-14

Description: When run, script scrapes Monthly Performance Report from
the Amtrak website and extracts the Route Level Results.
'''

import requests
import os
import tabula
import fitz
# Approach 1
## Define the URL pattern
#base_url = "https://www.amtrak.com/content/dam/projects/dotcom/english/public/documents/corporate/monthlyperformancereports/{}/Amtrak-Monthly-Performance-Report-{}.pdf"
filepath = "../01_Data/01_Source/Amtrak/Monthly_Performance_Report/{}/Amtrak-Monthly-Performance-Report-{}.pdf"

## Define the column names, coordinates, table area for different periods
column_names = {"Jan2018_Apr2018": ["NEC","Operating Revenue", "Operating Expense", "Adjusted Operating Earnings", "Gross Ticket Revenue", "Ridership (in Thousands)", "Seat Miles (in Millions)", "Passenger Miles (in Millions)", "eCSI", "Average Load Factor", "OTP"],
                "May2018_Sep2019": ["NEC", "Operating Revenue", "Operating Expense", "Adjusted Operating Earnings", "Ridership (in Thousands)", "eCSI", "Average Load Factor", "OTP"],
                "Oct2019_Feb2020": ["NEC", "Operating Revenue", "Operating Expense", "Adjusted Operating Earnings", "Ridership (in Thousands)", "Seat Miles (in Millions)", "Passenger Miles (in Millions)", "CSI", "Average Load Factor", "OTP"],
                "Mar2020_Jun2021": ["NEC", "Operating Revenue", "Operating Expense", "Adjusted Operating Earnings", "Ridership (in Thousands)", "Seat Miles (in Millions)", "Passenger Miles (in Millions)", "Average Load Factor", "OTP"],
                "Jul2021_Apr2022": ["NEC", "Operating Revenue", "Operating Expense", "Adjusted Operating Earnings", "Ridership (in Thousands)", "Seat Miles (in Millions)", "Passenger Miles (in Millions)", "Average Load Factor", "OTP", "Train Miles (in Millions)", "Frequencies"],
                "May2022": ["NEC", "Operating Revenue", "Operating Expense", "Adjusted Operating Earnings", "Ridership (in Thousands)", "Seat Miles (in Millions)", "Passenger Miles (in Millions)", "Train Miles", "Frequencies"],
                "Jun2022": ["NEC", "Operating Revenue", "Operating Expense", "Adjusted Operating Earnings", "Ridership (in Thousands)", "Seat Miles (in Millions)", "Passenger Miles (in Millions)", "Average Load Factor", "OTP", "Train Miles (in Millions)", "Frequencies"],
                "Jul2022_Sep2023":["NEC", "Operating Revenue", "Frequency Variable Costs", "Route Variable Costs", "System/Fixed Cost", "Operating Expense", "Adjusted Operating Earnings", "Gross Ticket Revenue", "Ridership (in Thousands)", "Seat Miles (in Millions)", "Passenger Miles (in Millions)", "Train Miles (in Millions)", "Frequencies"]}

column_coordinates = {"Jan2018_Apr2018": [140, 175, 210, 265, 302, 343, 380, 423, 443, 478],
                      "May2018_Jul2018": [206, 239, 277, 331, 375, 398, 430],
                      "Aug2018_Sep2019": [294, 345, 396, 478, 540, 574, 623],
                      "Oct2018": [251, 313, 370, 449, 515, 575, 636],
                      "May2019": [288, 337, 391, 472, 533, 570, 618],
                      "Oct2019_Feb2020": [239, 288, 339, 420, 480, 535, 598, 630, 679],
                      "Mar2020_Jun2021": [255, 305, 359, 442, 504, 561, 625, 670],
                      "Jul2021_Apr2022": [207, 267, 328, 385, 446, 491, 548, 601, 640, 691],
                      "May2022": [154, 200, 248, 316, 374, 430, 489, 552],
                      "Jun2022": [167, 224, 283, 359, 430, 494, 559, 612, 656, 727],
                      "Jul2022_Sep2023":[118, 150, 192, 233, 274, 309, 355, 396, 436, 474, 515, 558]}

table_area = {"Jan2018_Apr2018": [118, 40, 573, 500],
              "May2018_Jul2018": [118, 101, 564, 454],
              "Aug2018_Sep2019": [110, 140, 767, 656],
              "Oct2018":[112, 112, 760, 685],
              "May2019":[106, 143, 756, 649],
              "Oct2019_Feb2020": [108, 118, 755, 707],
              "Mar2020_Jun2021": [115, 100, 751, 708],
              "Jul2021_Apr2022": [89, 83, 763, 746],
              "May2022": [57, 7 ,572, 602],
              "Jun2022": [88, 1, 760, 791],
              "Jul2022_Sep2023":[47, 14, 559, 598]}

## Define the functions
def get_colnames_for_month(monyr):
    if monyr in ["January-2018", "February-2018", "March-2018", "April-2018"]:
        return column_names["Jan2018_Apr2018"]
    elif monyr in ["May-2018", "June-2018", "July-2018", "August-2018", "September-2018", "October-2018", "November-2018", "December-2018", "January-2019", "February-2019", "March-2019", "April-2019"]:
        return column_names["May2018_Sep2019"]
    elif monyr in ["May-2019", "June-2019", "July-2019", "August-2019", "September-2019", "October-2019", "November-2019", "December-2019", "January-2020", "February-2020"]:
        return column_names["Oct2019_Feb2020"]
    elif monyr in ["March-2020", "April-2020", "May-2020", "June-2020", "July-2020", "August-2020", "September-2020", "October-2020", "November-2020", "December-2020", "January-2021", "February-2021", "March-2021", "April-2021", "May-2021", "June-2021"]:
        return column_names["Mar2020_Jun2021"]
    elif monyr in ["July-2021", "August-2021", "September-2021", "October-2021", "November-2021", "December-2021", "January-2022", "February-2022", "March-2022", "April-2022"]:
        return column_names["Jul2021_Apr2022"]
    elif monyr in ["May-2022"]:
        return column_names["May2022"]
    elif monyr in ["June-2022"]:
        return column_names["Jun2022"]
    elif monyr in ["July-2022", "August-2022", "September-2022", "October-2022", "November-2022", "December-2022", "January-2023", "February-2023", "March-2023", "April-2023", "May-2023", "June-2023", "July-2023", "August-2023", "September-2023"]:
        return column_names["Jul2022_Sep2023"]

def get_coordinates_for_month(monyr):
    if monyr in ["January-2018", "February-2018", "March-2018", "April-2018"]:
        return column_coordinates["Jan2018_Apr2018"]
    elif monyr in ["May-2018", "June-2018", "July-2018"]:
        return column_coordinates["May2018_Jul2018"]
    elif monyr in ["August-2018", "September-2018", "November-2018", "December-2018", "January-2019", "February-2019", "March-2019", "April-2019", "June-2019", "July-2019", "August-2019", "September-2019"]:
        return column_coordinates["Aug2018_Sep2019"]
    elif monyr in ["October-2018"]:
        return column_coordinates["Oct2018"]
    elif monyr in ["May-2019"]:
        return column_coordinates["May2019"]
    elif monyr in ["October-2019", "November-2019", "December-2019", "January-2020", "February-2020"]:
        return column_coordinates["Oct2019_Feb2020"]
    elif monyr in ["March-2020", "April-2020", "May-2020", "June-2020", "July-2020", "August-2020", "September-2020", "October-2020", "November-2020", "December-2020", "January-2021", "February-2021", "March-2021", "April-2021", "May-2021", "June-2021"]:
        return column_coordinates["Mar2020_Jun2021"]
    elif monyr in ["July-2021", "August-2021", "September-2021", "October-2021", "November-2021", "December-2021", "January-2022", "February-2022", "March-2022", "April-2022"]:
        return column_coordinates["Jul2021_Apr2022"]
    elif monyr in ["May-2022"]:
        return column_coordinates["May2022"]
    elif monyr in ["June-2022"]:
        return column_coordinates["Jun2022"]
    elif monyr in ["July-2022", "August-2022", "September-2022", "October-2022", "November-2022", "December-2022", "January-2023", "February-2023", "March-2023", "April-2023", "May-2023", "June-2023", "July-2023", "August-2023", "September-2023"]:
        return column_coordinates["Jul2022_Sep2023"]

def get_area_for_month(monyr):
    if monyr in ["January-2018", "February-2018", "March-2018", "April-2018"]:
        return table_area["Jan2018_Apr2018"]
    elif monyr in ["May-2018", "June-2018", "July-2018"]:
        return table_area["May2018_Jul2018"]
    elif monyr in ["August-2018", "September-2018", "November-2018", "December-2018", "January-2019", "February-2019", "March-2019", "April-2019", "June-2019", "July-2019", "August-2019", "September-2019"]:
        return table_area["Aug2018_Sep2019"]
    elif monyr in ["October-2018"]:
        return table_area["Oct2018"]
    elif monyr in ["May-2019"]:
        return table_area["May2019"]
    elif monyr in ["October-2019", "November-2019", "December-2019", "January-2020", "February-2020"]:
        return table_area["Oct2019_Feb2020"]
    elif monyr in ["March-2020", "April-2020", "May-2020", "June-2020", "July-2020", "August-2020", "September-2020", "October-2020", "November-2020", "December-2020", "January-2021", "February-2021", "March-2021", "April-2021", "May-2021", "June-2021"]:
        return table_area["Mar2020_Jun2021"]
    elif monyr in ["July-2021", "August-2021", "September-2021", "October-2021", "November-2021", "December-2021", "January-2022", "February-2022", "March-2022", "April-2022"]:
        return table_area["Jul2021_Apr2022"]
    elif monyr in ["May-2022"]:
        return table_area["May2022"]
    elif monyr in ["June-2022"]:
        return table_area["Jun2022"]
    elif monyr in ["July-2022", "August-2022", "September-2022", "October-2022", "November-2022", "December-2022", "January-2023", "February-2023", "March-2023", "April-2023", "May-2023", "June-2023", "July-2023", "August-2023", "September-2023"]:
        return table_area["Jul2022_Sep2023"]

def get_total_pages(year, monyr):
    pdf_all = fitz.open(filepath.format(year, monyr))
    total_pages = len(pdf_all)
    return total_pages

# Function to extract data from PDF
# def extract_data(pdf,coordinates,tabarea):
#     total_pages = len(tabula.read_pdf(pdf, pages='all')) - 1 
#     dfs = tabula.read_pdf(pdf, columns = coordinates, guess = False, pages = total_pages, area = tabarea)
#     return dfs

def extract_data(pdf, coordinates, total_pages, tabarea):
    dfs = tabula.read_pdf(pdf, columns = coordinates, guess = False, pages = total_pages, area = tabarea)
    return dfs

# Function to download and extract data for a specific month
def process_monthly_report(year, monyr):
    pdf = filepath.format(year, monyr)
    coordinates = get_coordinates_for_month(monyr)
    tabarea = get_area_for_month(monyr)
    colnames = get_colnames_for_month(monyr)
    total_pages = get_total_pages(year, monyr)
    dfs = extract_data(pdf, coordinates, total_pages, tabarea)
    dfs[0].columns = colnames
    dfs[0].to_csv('../01_Data/02_Processed/RLR/{}_RLR.csv'.format(monyr))

# Loop through the months and years you want to process
for year in range(2018, 2023):
    for month in ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]:
        monyr = f"{month}-{year}"
        process_monthly_report(year, monyr)

# #dfs = tabula.read_pdf(base_url.format(2018, "January"), pages=-1, area = [85, 40, 570, 500])
# dfs = tabula.read_pdf(pdf, pages = 'last', area = [118, 40, 573, 500])
# dfs[0]

# dfs2 = tabula.read_pdf(pdf, pages = 7, columns = [140, 175, 210, 265, 302, 343, 380, 423, 443, 478], guess = False, area = [118, 40, 573, 500])
# dfs2[0]

# dfs2[0].columns = column_names["Jan2018_Apr2018"]
# dfs2[0]

# table_area = [94, 40, 573, 500]  # [top, left, bottom, right] in points

# tabula.convert_into(dfs2[0], "output.csv", output_format = "csv")
# dfs2[0].to_csv('pdf.csv')


# Single File Inspection
monyr = 'June-2018'
year = "2018"
pdf = filepath.format(year,monyr)

pdf_all = fitz.open(filepath.format(year, monyr))
total_pages = len(pdf_all)

## Execute Function to download and extract data for a specific month
coordinates = get_coordinates_for_month(monyr)
tabarea = get_area_for_month(monyr)
colnames = get_colnames_for_month(monyr)

dfs = tabula.read_pdf(pdf, columns = coordinates, guess = False, pages = 8, area = tabarea)
# dfs = tabula.read_pdf(pre_pdf, pages = 8, area = tabarea)
dfs[0].columns = colnames
dfs[0]
dfs[0].to_csv('{}_RLR.csv'.format(monyr))

# Loop through the months and years you want to process
process_monthly_report(year, monyr)


# Approach two: remove dollar sign (under construction)
## Function to remove dollar sign
def preprocess_pdf(pdf):
    df = tabula.read_pdf(pdf, pages = total_pages)
    for i, page_df in enumerate(df):
        # Remove dollar signs from the 'Amount' column (change 'Amount' to your actual column name)
        if 'Amount' in page_df.columns:
            df[i]['Amount'] = df[i]['Amount'].str.replace('$', '').astype(float)
    return df

## Call the preprocess_pdf function to get the processed DataFrame
pre_pdf = preprocess_pdf(pdf)
