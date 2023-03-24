import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from app import get_sim

print("NUHS Thread Started...")
nuhs_results = []
base_url = "https://www.nuhs.edu.sg/Events/Pages/Events.aspx"
r = requests.get(base_url)
soup = BeautifulSoup(r.text, "html.parser")
section = soup.find("div", {"class": "mediacollection"})
rows = section.find_all("div", {"class": "media"})
for row in rows:
  try:
    name = row.find("h4").find("a").text
    print(name)
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
    date_present = True
    time_present = False
    description_present = False
    venue = None
    mode = None
    fee_type = None
    fees = 0.00
    register_url = None
    date1 = row.find("div", {"class": "datebox"}).find_all("div", {"class": "date"})[0]
    date2 = row.find("div", {"class": "datebox"}).find_all("div", {"class": "date"})[1]
    start_year = int(date1.find("div", {"class": "year"}).text)
    start_month = date1.find("div", {"class": "month"}).text
    start_date = int(date1.find("div", {"class": "day"}).text)
    end_year = int(date2.find("div", {"class": "year"}).text)
    end_month = date2.find("div", {"class": "month"}).text
    end_date = int(date2.find("div", {"class": "day"}).text)
    months_list = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Oct", "Nov", "Dec"]
    try:
      if len(row.find("p", {"class": "desc"}).find_all("div")) == 0:
        description = row.find("p", {"class": "desc"}).text
        description_present = True
    except:
      None
    try:
      time = row.find("div", {"class": "media time"}).find("div", {"class": "media-body"}).text
      if time != "":
        time_present = True
        time = time.replace(".", ":")
        start_time = time.split(" to ")[0]
        end_time = time.split(" to ")[0]
    except:
      None
    try:
      mode_venue = row.find("div", {"class": "media venue"}).find("div", {"class": "media-body"}).text
      if mode_venue != "":
        if "zoom" in mode_venue.lower() or "webinar" in mode_venue.lower():
          mode = "Virtual"
        else:
          mode = "Face-to-Face"
          venue = mode_venue
    except:
      None
    try:
      fees_fee_type = row.find("div", {"class": "media fees"}).find("div", {"class": "media-body"}).text
      if fees_fee_type != "":
        if "free" in fees_fee_type.lower():
          fee_type = "Free"
        elif "$" in fees_fee_type:
          fee_type = "Paid"
          fees = int(fees_fee_type.split(" ")[0].replace("$", ""))
    except:
      None
    try:
      register_url = row.find("button", {"class": "btn btn-default register"})['eventdetaillink']
    except:
      None
    if description_present == True and fee_type != None:
      for keyword in keywords:
        nuhs_results.append([
          name,
          "National University Health System",
          keyword[0],
          keyword[1],
          keyword[2],
          date_present,
          description_present,
          start_year,
          int(months_list.index(start_month) + 1),
          start_date,
          end_year,
          int(months_list.index(end_month) + 1),
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
  except:
    None
nuhs_df = pd.DataFrame(nuhs_results, columns = [
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
nuhs_df.to_csv("resources/nuhs.csv")
print("NUHS Thread Ended...")