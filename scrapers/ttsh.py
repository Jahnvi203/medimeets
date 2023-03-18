import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from main import get_sim

print("TTSH Thread Started...")
ttsh_results = []
base_url = "https://www.ttsh.com.sg/about-ttsh/ttsh-events/Pages/default.aspx"
r = requests.get(base_url)
soup = BeautifulSoup(r.text, "html.parser")
paging = soup.find("div", {"class": "pagingOf"}).text
n_pages = int(paging.split(" of ")[-1])
for i in range(1, n_pages + 1):
    url = f"https://www.ttsh.com.sg/about-ttsh/ttsh-events/Pages/default.aspx?sr_category=&sr_datey=&sr_datem=&pgNo={i}"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    section = soup.find("section", {"class": "listing"})
    articles = section.find_all("article")
    for article in articles:
        name = article.find("h2").text
        keywords = get_sim(name)
        details_url = "https://www.ttsh.com.sg" + article.find("h2").find("a")['href']
        r_details = requests.get(details_url)
        soup_details = BeautifulSoup(r_details.text, "html.parser")
        main_article = soup_details.find("article")
        main_divs = main_article.find_all("div", {"class": "item-wrapper"})
        details = []
        for main_div in main_divs:
            label = main_div.find("div", {"class": "item-label"}, recursive = False).text
            if label == "Synopsis" or label == "Description":
                value = main_div.find("div", {"class": "item-value"}, recursive = False).decode_contents()
            else:
                value = main_div.find("div", {"class": "item-value"}, recursive = False).text
            details.append([label, value])
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
        temp_time = None
        description = None
        add_info = None
        venue = None
        mode = None
        fee_type = None
        fees = 0.00
        saot_fees = None
        non_saot_fees = None
        contact_person = None
        contact_email = None
        register_url = None
        for detail in details:
            if "Date" in detail[0] and "Time" in detail[0]:
                date = detail[1].replace("\r", "").replace("\n", " ").split(" / ")[0]
                if len(date) > 0:
                    years = re.findall("[1-3][0-9][0-9][0-9]", date)
                    if len(years) > 0:
                        year_present = True
                        if len(years) == 1:
                            start_year = int(years[0])
                            end_year = start_year
                        elif len(years) == 2:
                            if int(years[0]) <= int(years[1]):
                                start_year = int(years[0])
                                end_year = int(years[1])
                            else:
                                start_year = int(years[0])
                                end_year = int(years[0])
                if year_present == True:
                    date = re.sub(" [1-3][0-9][0-9][0-9]", "", date)
                    months_list = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
                    months = []
                    for month in months_list:
                        if month in date:
                            months.append(month)
                    if len(months) > 0:
                        month_present = True
                        if len(months) == 1:
                            start_month = months[0]
                            end_month = months[0]
                        else:
                            start_month = months[0]
                            end_month = months[1]
                if month_present == True:
                    date = date.replace(f" {start_month}", "")
                    date = date.replace(f" {end_month}", "")
                    date = date.replace(f"{start_month}", "")
                    date = date.replace(f"{end_month}", "")
                    if "to be confirmed" not in date.lower():
                        if " - " in date:
                            if len(date.split(" ")) == 3:
                                date_present = True
                                start_date = int(date.split(" - ")[0])
                                end_date = int(date.split(" - ")[1])
                        elif " to " in date:
                            if len(date.split(" ")) == 3:
                                date_present = True
                                start_date = int(date.split(" to ")[0])
                                end_date = int(date.split(" to ")[1])
                        elif " and " in date:
                            if len(date.split(" ")) == 3:
                                date_present = True
                                start_date = int(date.split(" and ")[0])
                                end_date = int(date.split(" and ")[1])
                        elif date != "":
                            date_present = True
                            start_date = int(date)
                            end_date = int(date)
                if len(detail[1].replace("\r", "").replace("\n", " ").split(" / ")) > 1:
                    temp_time = " / ".join(detail[1].replace("\r", "").replace("\n", " ").split(" / ")[1:])
                    if "to be confirmed" not in temp_time.lower():
                        time_present = True
                        if len(temp_time.split(" / ")) == 1:
                            temp_time = temp_time.lower()
                            temp_time_new = []
                            if " - " in temp_time:
                                temp_time = temp_time.split(" - ")
                                for item in temp_time:
                                    temp_time_new.append(item.replace(" ", "").replace(".", ":"))
                                start_time = temp_time_new[0]
                                end_time = temp_time_new[1]
                            elif " to " in temp_time:
                                temp_time = temp_time.split(" to ")
                                for item in temp_time:
                                    temp_time_new.append(item.replace(" ", "").replace(".", ":"))
                                start_time = temp_time_new[0]
                                end_time = temp_time_new[1]
                        else:
                            temp_time_1 = temp_time.split(" / ")[0]
                            temp_time_2 = temp_time.split(" / ")[1]
                            temp_time_1 = temp_time_1.split(": ")
                            temp_time_2 = temp_time_2.split(": ")
                            temp_time_1_2 = temp_time_1[1].lower()
                            temp_time_2_2 = temp_time_2[1].lower()
                            temp_time_new_1 = []
                            temp_time_new_2 = []
                            if " – " in temp_time_1_2:
                                temp_time_1_2 = temp_time_1_2.split(" – ")
                                for item in temp_time_1_2:
                                    temp_time_new_1.append(item.replace(" ", "").replace(".", ":"))
                            elif " to " in temp_time_1_2:
                                temp_time_1_2 = temp_time_1_2.split(" to ")
                                for item in temp_time_1_2:
                                    temp_time_new_1.append(item.replace(" ", "").replace(".", ":"))
                            if " – " in temp_time_2_2:
                                temp_time_2_2 = temp_time_2_2.split(" – ")
                                for item in temp_time_2_2:
                                    temp_time_new_2.append(item.replace(" ", "").replace(".", ":"))
                            elif " to " in temp_time_2_2:
                                temp_time_2_2 = temp_time_2_2.split(" to ")
                                for item in temp_time_2_2:
                                    temp_time_new_2.append(item.replace(" ", "").replace(".", ":"))
                            time_label_1 = temp_time_1[0]
                            time_label_2 = temp_time_2[0]
                            while time_label_1[0] == " ":
                                time_label_1 = time_label_1[1:]
                            while time_label_2[0] == " ":
                                time_label_2 = time_label_2[1:]
                            time_label_1 = time_label_1.title()
                            time_label_2 = time_label_2.title()
                            if temp_time_new_1[0][-1] == ":":
                                start_time = f'{temp_time_new_1[0][:-1]} ({time_label_1}); {temp_time_new_2[0]} ({time_label_2})'
                            elif temp_time_new_2[0][-1] == ":":
                                start_time = f'{temp_time_new_1[0]} ({time_label_1}); {temp_time_new_2[0][:-1]} ({time_label_2})'
                            else:
                                start_time = f'{temp_time_new_1[0]} ({time_label_1}); {temp_time_new_2[0]} ({time_label_2})'
                            if temp_time_new_1[1][-1] == ":":
                                end_time = f'{temp_time_new_1[1][:-1]} ({time_label_1}); {temp_time_new_2[1]} ({time_label_2})'
                            elif temp_time_new_2[1][-1] == ":":
                                end_time = f'{temp_time_new_1[1]} ({time_label_1}); {temp_time_new_2[1][:-1]} ({time_label_2})'
                            else:
                                end_time = f'{temp_time_new_1[1]} ({time_label_1}); {temp_time_new_2[1]} ({time_label_2})'
                    else:
                        temp_time = None
            elif detail[0] == "Synopsis":
                if "NIL" not in detail[1]:
                    description = detail[1]
            elif detail[0] == "Description":
                if "NIL" not in detail[1]:
                    add_info = detail[1]
                    if description == None and add_info != None:
                        description = add_info
                        add_info = None
                    if description != None:
                        description_present = True
            elif detail[0] == "Event Fees":
                if "$" in detail[1]:
                    fee_type = "Paid"
                    fees = float(detail[1].split("$")[1])
                elif add_info != None and "$" in add_info:
                    fee_type = "Paid"
                    saot_fees = float(re.findall('[1-9][0-9][0-9]', add_info)[0])
                    non_saot_fees = float(re.findall('[1-9][0-9][0-9]', add_info)[1])
                    fees = f'{str(saot_fees)} (SAOT Member); {str(non_saot_fees)} (Non-SAOT Member)'
                else:
                    fee_type = "Free"
            elif detail[0] == "Venue":
                if "via zoom" in detail[1].lower() or "virtual" in detail[1].lower() or "over zoom" in detail[1].lower():
                    mode = "Virtual"
                else:
                    mode = "Face-to-Face"
                    if "to be confirmed" not in detail[1].lower():
                        if "TTSH " in detail[1]:
                            venue = detail[1].replace("TTSH ", "Tan Tock Seng Hospital, ")
                        elif detail[1] == "TTSH":
                            venue = "Tan Tock Seng Hospital"
                        else:
                            venue = detail[1]
            elif detail[0] == "Contact Person":
                if "TTSH" in detail[1]:
                    contact_person = detail[1].replace("TTSH", "Tan Tock Seng Hospital")
                else:
                    contact_person = detail[1]
            elif detail[0] == "Email":
                contact_email = detail[1]
        if month_present == True and year_present == True and description_present == True:
            description = BeautifulSoup(description, "html.parser")
            description_final = ""
            paras = description.find_all("p", recursive = False)
            register_url = ""
            paras_final = []
            for para in paras:
                if not para.find("a"):
                    paras_final.append(para.text)
                else:
                    register_url = para.find("a")['href']
            description_final += "<br><br>".join(paras_final)
            ul = description.find("ul")
            ol = description.find("ol")
            if ul:
                lis = ul.find_all("li")
                for i in range(len(lis)):
                    description_final += "<br>" + f"{str(i + 1)}) {lis[i].text}"
            if ol:
                lis = ol.find_all("li")
                for i in range(len(lis)):
                    description_final += "<br>" + f"{str(i + 1)}) {lis[i].text}"
            for row in keywords:
                ttsh_results.append([
                    name,
                    "Tan Tock Seng Hospital",
                    row[0],
                    row[1],
                    row[2],
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
                    description_final,
                    fee_type,
                    fees,
                    mode,
                    venue,
                    register_url
                ])
ttsh_df = pd.DataFrame(ttsh_results, columns = [
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
ttsh_df.to_csv("resources/ttsh.csv")
print("TTSH Thread Ended...")