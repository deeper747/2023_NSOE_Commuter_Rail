'''
Contributors: Jia-Shen Tsai, Wendy Wen, Zhengqi Jiao, Miaojun Pang,
Alexander Yoshizumi

Last Updated: 2023-11-05

Description: When run, script scrapes Monthly Performance Report from
the Amtrak website and extracts the Route Level Results.
'''

import requests
import os
import tabula

# Define the URL pattern
base_url = "https://www.amtrak.com/content/dam/projects/dotcom/english/public/documents/corporate/monthlyperformancereports/{}/Amtrak-Monthly-Performance-Report-{}.pdf"

# Define the column names for different periods
column_names = {"Jan2018_Apr2018": ["Operating Revenue", "Operating Expense", "Adjusted Operating Earnings", "Gross Ticket Revenue", "Ridership (in Thousands)", "Seat Miles (in Millions)", "Passenger Miles (in Millions)", "eCSI", "Average Load Factor", "OTP"],
                "May2018_Sep2019": ["Operating Revenue", "Operating Expense", "Adjusted Operating Earnings", "Ridership (in Thousands)", "eCSI", "Average Load Factor", "OTP"],
                "Oct2019_Feb2020": ["Operating Revenue", "Operating Expense", "Adjusted Operating Earnings", "Ridership (in Thousands)", "Seat Miles (in Millions)", "Passenger Miles (in Millions)", "CSI", "Average Load Factor", "OTP"],
                "Mar2020_Jun2023": ["Operating Revenue", "Operating Expense", "Adjusted Operating Earnings", "Ridership (in Thousands)", "Seat Miles (in Millions)", "Passenger Miles (in Millions)", "Average Load Factor", "OTP"],
                "Jul2021_Apr2022": ["Operating Revenue", "Operating Expense", "Adjusted Operating Earnings", "Ridership (in Thousands)", "Seat Miles (in Millions)", "Passenger Miles (in Millions)", "Average Load Factor", "OTP", "Train Miles (in Millions)", "Frequencies"],
                "May2022": ["Operating Revenue", "Operating Expense", "Adjusted Operating Earnings", "Ridership (in Thousands)", "Seat Miles (in Millions)", "Passenger Miles (in Millions)", "Train Miles", "Frequencies"],
                "Jun2022": ["Operating Revenue", "Operating Expense", "Adjusted Operating Earnings", "Ridership (in Thousands)", "Seat Miles (in Millions)", "Passenger Miles (in Millions)", "Average Load Factor", "OTP", "Train Miles (in Millions)", "Frequencies"],
                "Jul2022-Sep2023":["Operating Revenue", "Frequency Variable Costs", "Route Variable Costs", "System/Fixed Cost", "Operating Expense", "Adjusted Operating Earnings", "Gross Ticket Revenue", "Ridership (in Thousands)", "Seat Miles (in Millions)", "Passenger Miles (in Millions)", "Train Miles (in Millions)", "Frequencies"]
}

# Function to extract data from PDF
def extract_data(pdf_url, columns):
    dfs = tabula.read_pdf(pdf_url, pages=7, header=None)
    # Process the DataFrame to match columns and extract the data
    # You need to handle the variations in columns and data structure here
    # ...
    return processed_data

# Function to download and extract data for a specific month
def process_monthly_report(year, month):
    pdf_url = base_url.format(year, month)
    columns = column_names[0]  # Determine columns based on year and month
    data = extract_data(pdf_url, columns)
    # Process and store the extracted data as needed
    # ...

data = extract_data(base_url.format(2018, "January"),column_names[0])

dfs = tabula.read_pdf(base_url.format(2018, "January"), pages=7, table_area = [85, 40, 570, 500])

table_area = [85, 40, 570, 500]  # [top, left, bottom, right] in points

# Loop through the months and years you want to process
for year in range(2018, 2024):
    for month in ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]:
        report_month = f"{month}-{year}"
        process_monthly_report(year, report_month)
