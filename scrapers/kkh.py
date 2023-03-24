import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from app import get_sim

print("KKH Thread Started...")
kkh_results = []
base_url = "https://www.kkh.com.sg/helms-webinars"
r = requests.get(base_url)
soup = BeautifulSoup(r.text, "html.parser")
section = soup.find("table", {"class": "ms-rteTable-5"}).find("tbody")
rows = section.find_all("tr")[1:]
for row in rows:
  if len(row.find_all("td")) == 5:
    name = row.find_all("td")[1].text
    keywords = get_sim(name)
    start_year = None
    end_year = None
    start_month = None
    end_month = None
    start_date = None
    end_date = None
    start_time = None
    end_time = None
    year_present = False
    month_present = False
    date_present = False
    time_present = False
    description_present = False
    venue = None
    mode = "Virtual"
    fee_type = "Free"
    fees = 0.00
    register_url = None
    description = row.find_all("td")[2].text
    if description != "":
      description_present = True
    date = row.find_all("td")[0].text
    if date != "":
      date_present = True
    start_year = int(re.findall('[1-9][0-9][0-9][0-9]', date)[0])
    end_year = start_year
    date = date.replace(f" {start_year}", "")
    months_list = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    for month in months_list:
      if month in date:
        start_month = month
        break
    end_month = start_month
    date = date.replace(f"{start_month}", "")
    date = date.replace(" ", "")
    date = date.replace("\xa0", "")
    date = date.replace("\u200b", "")
    start_date = int(date)
    end_date = start_date
    if row.find_all("td")[4].find("a"):
      register_url = row.find_all("td")[4].find("a")['href']
    if date_present == True and description_present == True:
      for keyword in keywords:
        kkh_results.append([
            name,
            "KK Women's and Children's Hospital",
            keyword[0],
            keyword[1],
            keyword[2],
            date_present,
            description_present,
            start_year,
            start_month,
            start_date,
            end_year,
            end_month,
            end_date,
            time_present,
            start_time,
            end_time,
            description,
            fee_type,
            fees,
            mode,
            venue,
            register_url
        ])
kkh_df = pd.DataFrame(kkh_results, columns = [
    'event name',
    'organiser',
    'speciality',
    'keyword',
    'similarity',
    'date present',
    'description present',
    'start year',
    'start month',
    'start date',
    'end year',
    'end month',
    'end date',
    'time present',
    'start time',
    'end time',
    'description',
    'fee type',
    'fees',
    'mode',
    'venue',
    'register url'
])
kkh_df.to_csv("resources/kkh.csv")
print("KKH Thread Ended...")