from flask import Flask, render_template, request
import os
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from datetime import date as current_date
import requests
from specialities import sp_str
import re
import json
from threading import Thread
import spacy
nlp = spacy.load("en_core_sci_lg")

app = Flask(__name__)

def get_sim(name):
    sp_list = sp_str.lower().split("\n")
    nlp_name = name.lower()
    for chr in nlp_name:
        if chr not in " abcdefghijklmnopqrstuvwxyz ":
            nlp_name = nlp_name.replace(chr, " ")
    entities = list(nlp(nlp_name).ents)
    df_list = []
    for sp in sp_list:
        nlp_sp = nlp(sp)
        for ent in entities:
            nlp_ent = nlp(ent.text)
            df_list.append([sp, ent.text, nlp_sp.similarity(nlp_ent)])
    df_list_new = []
    df = pd.DataFrame(df_list, columns = ['Speciality', 'Word', 'Similarity']).sort_values(['Similarity'], ascending = False)
    for ent in entities:
        most_sim = df[df['Word'] == ent.text].values.tolist()[0]
        df_list_new.append(most_sim)
    df_new = pd.DataFrame(df_list_new, columns = ['Speciality', 'Word', 'Similarity']).sort_values(['Similarity'], ascending = False)
    return df_new.values.tolist()

def create_datetime(df):
    if df['date present'] == False:
        return datetime(df['start year'], df['start month'], 30)
    else:
        return datetime(df['start year'], df['start month'], int(df['start date']))

def events_html_generator(df):
    html = ""
    df_list = df.values.tolist()
    for item in df_list:
        description = BeautifulSoup(item[16], "html.parser")
        description = description.text
        date = ""
        months_list = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        if item[5] == True:
            date = f'{int(item[9])} {months_list[int(item[8]) - 1]} {item[7]} - {int(item[12])} {months_list[int(item[11]) - 1]} {item[10]}'
        else:
            date = f'{months_list[int(item[8]) - 1]} {item[7]} - {months_list[int(item[11]) - 1]} {item[10]}'
        price = ""
        if item[18] == "Free":
            price = "Free"
        else:
            price = "SG$" + item[19]
            price = price.replace("; ", "; SG$")
        time = ""
        if item[13] == True:
            time = f'{item[14]} - {item[15]}'
        else:
            time = 'To Be Determined'
        location = ""
        if item[22] == "Virtual":
            location = "Virtual"
        else:
            location = item[23]
        html += f"""
            <div class="row">
                <div class="col-3">
                    <img class="event_image" src="https://www.americanoceans.org/wp-content/uploads/2021/06/shutterstock_1807037047-scaled.jpg" alt="">
                </div>
                <div class="col-9">
                    <div class="event_container">
                        <div class="row">
                            <div class="col-10">
                                <p class="event_name">{item[0]}</p>
                                <p class="event_description">{(description[:75] + "...") if len(description) > 75 else description}</p>
                                <p class="event_details"><strong>Date:</strong>&nbsp;{date}&emsp;<strong>Time:</strong>&nbsp;{time}&emsp;<strong>Price:</strong>&nbsp;{price}&emsp;<strong>Location:</strong>&nbsp;{location}&emsp;<span class="event_organiser"><strong>Hosted by&nbsp;</strong>{item[1]}</span></p>
                            </div>
                            <div class="col-2" style="padding: 0px;">
                                <a href="/events-details/{item[0]}"><button class="event_button">Find Out More</button></a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <br><br>
        """
    return html

@app.route('/')
def index():
    ttsh_df = pd.read_csv("resources/ttsh.csv")
    kkh_df = pd.read_csv("resources/kkh.csv")
    nuhs_df = pd.read_csv("resources/nuhs.csv")
    events_df = events_df[[
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
        'add info',
        'fee type',
        'fees',
        'saot fees',
        'non saot fees',
        'mode',
        'venue',
        'contact person',
        'contact email'
    ]]
    ttsh_df['datetime'] = ttsh_df.apply(create_datetime, axis = 1)
    current_datetime = current_date.today()
    events_df = events_df[ttsh_df['datetime'].dt.date >= current_datetime]
    events_df = events_df.sort_values('datetime', ascending = True)
    events_df = events_df.drop_duplicates(subset = ['event name'])
    upcoming_events = ttsh_df.head(6)
    upcoming_events_html = events_html_generator(upcoming_events)
    return render_template("index.html", upcoming_events_html = upcoming_events_html)

def get_keyword_sim(x, keyword):
    nlp_x = nlp(x)
    nlp_keyword = nlp(keyword)
    return nlp_keyword.similarity(nlp_x)

def get_price_filter(x):
    x_int = 0
    try:
        x_int = float(x)
    except:
        x_int = float(x.split("; ")[-1].split(" ")[0])
    return x_int

@app.route("/browse-events/<start>", methods = ['GET', 'POST'])
def events_search(start):
    keyword = ""
    category = "Category"
    month = ""
    price = ""
    search_criteria = []
    mode = "Mode"
    if int(start) == 1:
        keyword = request.form.to_dict()['keyword']
        category = request.form.to_dict()['category']
        month = request.form.to_dict()['month']
        price = request.form.to_dict()['price']
        mode = request.form.to_dict()['mode']
    ttsh_df = pd.read_csv("resources/ttsh.csv")
    kkh_df = pd.read_csv("resources/kkh.csv")
    nuhs_df = pd.read_csv("resources/nuhs.csv")
    events_df = pd.concat([ttsh_df, kkh_df, nuhs_df], axis = 1)
    events_df = events_df[[
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
        'add info',
        'fee type',
        'fees',
        'saot fees',
        'non saot fees',
        'mode',
        'venue',
        'contact person',
        'contact email'
    ]]
    if keyword != "" and category != "Category":
        events_df = events_df[events_df['speciality'] == category.lower()]
        events_df['keyword similarity'] = events_df['keyword'].apply(lambda x: get_keyword_sim(x, keyword.lower()))
        events_df['overall similarity'] = (events_df['similarity'] + events_df['keyword similarity']) / 2
        events_df = events_df.sort_values('overall similarity', ascending = False)
        events_df = events_df[events_df['overall similarity'] >= 0.45]
        search_criteria.append(f"<strong>{keyword.lower()}</strong> (keyword)")
        search_criteria.append(f"<strong>{category}</strong> (category)")
    elif keyword != "" and category == "Category":
        events_df['keyword similarity'] = events_df['keyword'].apply(lambda x: get_keyword_sim(x, keyword.lower()))
        events_df = events_df.sort_values('keyword similarity', ascending = False)
        events_df = events_df[events_df['keyword similarity'] >= 0.5]
        search_criteria.append(f"<strong>{keyword.lower()}</strong> (keyword)")
    elif keyword == "" and category != "Category":
        events_df = events_df[events_df['speciality'] == category.lower()]
        events_df = events_df.sort_values('similarity', ascending = False)
        events_df = events_df[events_df['similarity'] >= 0.4]
        search_criteria.append(f"<strong>{category}</strong> (category)")
    if month != "":
        search_month = int(month.split("-")[1])
        search_year = int(month.split("-")[0])
        events_df = events_df[(events_df['start month'] >= search_month) & (events_df['start year'] >= search_year)]
        months_list = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        search_criteria.append(f"<strong>{months_list[search_month - 1]} {search_year}</strong> (month, year)")
    if mode != "Mode":
        events_df = events_df[ttsh_df['mode'] == mode]
        search_criteria.append(f"<strong>{mode}</strong> (mode)")
    if price != "":
        if int(price) == 0:
            events_df = events_df[events_df['fee type'] == "Free"]
        else:
            events_df['price'] = events_df['fees'].apply(lambda x: get_price_filter(x))
            events_df = events_df[events_df['price'] <= int(price)]
        search_criteria.append(f"<strong>SG${price}</strong> (price)")
    events_df = events_df.drop_duplicates(subset = ['event name'])
    events_html = events_html_generator(ttsh_df)
    search_criteria = "You have searched for " + ", ".join(search_criteria)
    if ttsh_df.empty:
        search_criteria = "No events found"
    if start == '0':
        search_type = 0
    elif start == '1':
        search_type = 1
    return render_template("search.html", events_html = events_html, search_criteria = search_criteria, search_type = search_type)

@app.route("/events-details/<event_name>", methods = ['POST', 'GET'])
def event_details(event_name):
    ttsh_df = pd.read_csv("resources/ttsh.csv")
    kkh_df = pd.read_csv("resources/kkh.csv")
    nuhs_df = pd.read_csv("resources/nuhs.csv")
    events_df = pd.concat([ttsh_df, kkh_df, nuhs_df], axis = 1)
    events_df = events_df[[
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
    ]]
    event_df = events_df[events_df['event name'] == event_name]
    event_df = event_df.drop_duplicates(subset = ['event name'])
    event = event_df.values.tolist()[0]
    description = event[16]
    date = ""
    months_list = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    if event[5] == True:
        date = f'{int(event[9])} {months_list[int(event[8]) - 1]} {event[7]} - {int(event[12])} {months_list[int(event[11]) - 1]} {event[10]}'
    else:
        date = f'{months_list[int(event[8]) - 1]} {event[7]} - {months_list[int(event[11]) - 1]} {event[10]}'
    price = ""
    if event[17] == "Free":
        price = "Free"
    else:
        price = "SG$" + event[18]
        price = price.replace("; ", "; SG$")
    time = ""
    if event[13] == True:
        time = f'{event[14]} - {event[15]}'
    else:
        time = 'To Be Determined'
    location = ""
    if event[19] == "Virtual":
        location = "Virtual"
    else:
        location = event[20]
    register_url = event[21]
    return render_template("events_details.html", event_name = event_name, description = description, date = date, time = time, price = price, venue = location, register_url = register_url)

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
