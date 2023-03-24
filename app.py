from flask import Flask, render_template, request, redirect, url_for, session
import os
from pymongo import MongoClient
import pandas as pd
import numpy as np
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

app.secret_key = '1E44M1ixSeNGzO3T0dqIoXra7De5B46n'
app.config['SESSION_PERMANENT'] = True
app.config["SESSION_TYPE"] = "filesystem"
uri = "mongodb+srv://Jahnvi203:Jahnvi203@cluster0.cn63w2k.mongodb.net/medimeets?retryWrites=true&w=majority"
connection = MongoClient(host = uri, connect = False)        
db = connection['medimeets']
col_users = db.users
col_bookmarks = db.bookmarks

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
    count = 0
    for item in df_list:
        count += 1
        description = BeautifulSoup(item[16], "html.parser")
        description = description.text
        date = ""
        months_list = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        if item[5] == True:
            date = f'{int(item[9])} {months_list[int(item[8]) - 1]} {item[7]} - {int(item[12])} {months_list[int(item[11]) - 1]} {item[10]}'
        else:
            date = f'{months_list[int(item[8]) - 1]} {item[7]} - {months_list[int(item[11]) - 1]} {item[10]}'
        price = ""
        if item[17] == "Free":
            price = "Free"
        else:
            price = "SG$" + str(item[18])
            price = price.replace("; ", "; SG$")
        time = ""
        if item[13] == True:
            time = f'{item[14]} - {item[15]}'
        else:
            time = 'To Be Determined'
        location = ""
        if item[18] == "Virtual":
            location = "Virtual"
        else:
            location = item[19]
        register_url = ""
        if str(item[21]) != "nan":
            register_url = item[21]
        if register_url == "":
            if 'user_name' in session and 'user_email' in session:
                user_bookmarks = col_bookmarks.find({ 'email': session['user_email'] })[0]['bookmarks']
                if item[0] in user_bookmarks:
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
                                            <p class="event_description">{description}</p>
                                            <p class="event_search_details"><strong>Date:</strong>&nbsp;{date}&emsp;<strong>Time:</strong>&nbsp;{time}&emsp;<strong>Price:</strong>&nbsp;{price}&emsp;<strong>Location:</strong>&nbsp;{location}&emsp;<span class="event_organiser"><strong>Hosted by&nbsp;</strong>{item[1]}</span></p>
                                        </div>
                                        <div class="col-2" style="padding: 0px;">
                                            <div class="bookmark_div">
                                                <a id="bookmark_{str(count)}" href="/bookmark/{item[0]}"><img class="bookmarked" src="/static/images/bookmarked.png" alt=""></a>
                                            </div>
                                            <br>
                                            <a href="/events-details/{item[0]}"><button class="event_find_button">Find Out More</button></a>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <br><br>
                    """
                else:
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
                                            <p class="event_description">{description}</p>
                                            <p class="event_search_details"><strong>Date:</strong>&nbsp;{date}&emsp;<strong>Time:</strong>&nbsp;{time}&emsp;<strong>Price:</strong>&nbsp;{price}&emsp;<strong>Location:</strong>&nbsp;{location}&emsp;<span class="event_organiser"><strong>Hosted by&nbsp;</strong>{item[1]}</span></p>
                                        </div>
                                        <div class="col-2" style="padding: 0px;">
                                            <div class="bookmark_div">
                                                <a id="bookmark_{str(count)}" href="/bookmark/{item[0]}"><img class="bookmark" src="/static/images/bookmark.png" alt=""></a>
                                            </div>
                                            <br>
                                            <a href="/events-details/{item[0]}"><button class="event_find_button">Find Out More</button></a>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <br><br>
                    """
            else:
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
                                        <p class="event_description">{description}</p>
                                        <p class="event_search_details"><strong>Date:</strong>&nbsp;{date}&emsp;<strong>Time:</strong>&nbsp;{time}&emsp;<strong>Price:</strong>&nbsp;{price}&emsp;<strong>Location:</strong>&nbsp;{location}&emsp;<span class="event_organiser"><strong>Hosted by&nbsp;</strong>{item[1]}</span></p>
                                    </div>
                                    <div class="col-2" style="padding: 0px;">
                                        <a href="/events-details/{item[0]}"><button class="event_find_button">Find Out More</button></a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <br><br>
                """
        else:
            if 'user_name' in session and 'user_email' in session:
                user_bookmarks = col_bookmarks.find({ 'email': session['user_email'] })[0]['bookmarks']
                if item[0] in user_bookmarks:
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
                                            <p class="event_description">{description}</p>
                                            <p class="event_details"><strong>Date:</strong>&nbsp;{date}&emsp;<strong>Time:</strong>&nbsp;{time}&emsp;<strong>Price:</strong>&nbsp;{price}&emsp;<strong>Location:</strong>&nbsp;{location}&emsp;<span class="event_organiser"><strong>Hosted by&nbsp;</strong>{item[1]}</span></p>
                                        </div>
                                        <div class="col-2" style="padding: 0px;">
                                            <div class="bookmark_div">
                                                <a id="bookmark_{str(count)}" href="/bookmark/{item[0]}"><img class="bookmarked" src="/static/images/bookmarked.png" alt=""></a>
                                            </div>
                                            <br>
                                            <a href="/events-details/{item[0]}"><button class="event_find_button">Find Out More</button></a>
                                            <br><br>
                                            <a href="{register_url}"><button class="event_register_button">Register</button></a>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <br><br>
                    """
                else:
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
                                            <p class="event_description">{description}</p>
                                            <p class="event_details"><strong>Date:</strong>&nbsp;{date}&emsp;<strong>Time:</strong>&nbsp;{time}&emsp;<strong>Price:</strong>&nbsp;{price}&emsp;<strong>Location:</strong>&nbsp;{location}&emsp;<span class="event_organiser"><strong>Hosted by&nbsp;</strong>{item[1]}</span></p>
                                        </div>
                                        <div class="col-2" style="padding: 0px;">
                                            <div class="bookmark_div">
                                                <a id="bookmark_{str(count)}" href="/bookmark/{item[0]}"><img class="bookmark" src="/static/images/bookmark.png" alt=""></a>
                                            </div>
                                            <br>
                                            <a href="/events-details/{item[0]}"><button class="event_find_button">Find Out More</button></a>
                                            <br><br>
                                            <a href="{register_url}"><button class="event_register_button">Register</button></a>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <br><br>
                    """
            else:
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
                                        <p class="event_description">{description}</p>
                                        <p class="event_details"><strong>Date:</strong>&nbsp;{date}&emsp;<strong>Time:</strong>&nbsp;{time}&emsp;<strong>Price:</strong>&nbsp;{price}&emsp;<strong>Location:</strong>&nbsp;{location}&emsp;<span class="event_organiser"><strong>Hosted by&nbsp;</strong>{item[1]}</span></p>
                                    </div>
                                    <div class="col-2" style="padding: 0px;">
                                        <a href="/events-details/{item[0]}"><button class="event_find_button">Find Out More</button></a>
                                        <br><br>
                                        <a href="{register_url}"><button class="event_register_button">Register</button></a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <br><br>
                """
    return html

def upcoming_events_html_generator(df):
    html = ""
    df_list = df.values.tolist()
    i = 0
    temp_html = '<div class="row my-4">'
    count = 0
    for item in df_list:
        count += 1
        description = BeautifulSoup(item[16], "html.parser")
        description = description.text
        date = ""
        months_list = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        if item[5] == True:
            date = f'{int(item[9])} {months_list[int(item[8]) - 1]} {item[7]} - {int(item[12])} {months_list[int(item[11]) - 1]} {item[10]}'
        else:
            date = f'{months_list[int(item[8]) - 1]} {item[7]} - {months_list[int(item[11]) - 1]} {item[10]}'
        price = ""
        if item[17] == "Free":
            price = "Free"
        else:
            price = "SG$" + str(item[18])
            price = price.replace("; ", "; SG$")
        time = ""
        if item[13] == True:
            time = f'{item[14]} - {item[15]}'
        else:
            time = 'To Be Determined'
        location = ""
        if item[18] == "Virtual":
            location = "Virtual"
        else:
            location = item[19]
        i += 1
        if i <= 3:
            if 'user_name' in session and 'user_email' in session:
                user_bookmarks = list(col_bookmarks.find({ 'email': session['user_email'] }))
                if len(user_bookmarks) > 0:
                    user_bookmarks = user_bookmarks[0]['bookmarks']
                    if item[0] in user_bookmarks:
                        temp_html += f"""
                            <div class="col-4">
                                <div class="upcoming_event_card">
                                    <a href="/events-details/{item[0]}" class="event_name">{item[0]}</a>
                                    <p class="upcoming_event_details" style="color:#C3272D !important;">{date}</p>
                                    <p class="upcoming_event_details">{time}</p>
                                    <p class="upcoming_event_details">{location}</p>
                                    <p class="upcoming_event_details"><u><strong>Price</strong></u>&emsp;{price}</p>
                                    <div class="bookmark_div">
                                        <a id="bookmark_{str(count)}" href="/bookmark/{item[0]}"><img class="bookmarked" src="/static/images/bookmarked.png" alt=""></a>
                                    </div>
                                </div>
                            </div>
                        """
                    else:
                        temp_html += f"""
                            <div class="col-4">
                                <div class="upcoming_event_card">
                                    <a href="/events-details/{item[0]}" class="event_name">{item[0]}</a>
                                    <p class="upcoming_event_details" style="color:#C3272D !important;">{date}</p>
                                    <p class="upcoming_event_details">{time}</p>
                                    <p class="upcoming_event_details">{location}</p>
                                    <p class="upcoming_event_details"><u><strong>Price</strong></u>&emsp;{price}</p>
                                    <div class="bookmark_div">
                                        <a id="bookmark_{str(count)}" href="/bookmark/{item[0]}"><img class="bookmark" src="/static/images/bookmark.png" alt=""></i></a>
                                    </div>
                                </div>
                            </div>
                        """
                else:
                    temp_html += f"""
                            <div class="col-4">
                                <div class="upcoming_event_card">
                                    <a href="/events-details/{item[0]}" class="event_name">{item[0]}</a>
                                    <p class="upcoming_event_details" style="color:#C3272D !important;">{date}</p>
                                    <p class="upcoming_event_details">{time}</p>
                                    <p class="upcoming_event_details">{location}</p>
                                    <p class="upcoming_event_details"><u><strong>Price</strong></u>&emsp;{price}</p>
                                    <div class="bookmark_div">
                                        <a id="bookmark_{str(count)}" href="/bookmark/{item[0]}"><img class="bookmark" src="/static/images/bookmark.png" alt=""></i></a>
                                    </div>
                                </div>
                            </div>
                        """
            else:
                temp_html += f"""
                    <div class="col-4">
                        <div class="upcoming_event_card">
                            <a href="/events-details/{item[0]}" class="event_name">{item[0]}</a>
                            <p class="upcoming_event_details" style="color:#C3272D !important;">{date}</p>
                            <p class="upcoming_event_details">{time}</p>
                            <p class="upcoming_event_details">{location}</p>
                            <p class="upcoming_event_details"><u><strong>Price</strong></u>&emsp;{price}</p>
                        </div>
                    </div>
                """
        if i == 3:
            temp_html += '</div>'
            html += temp_html
            i = 0
            temp_html = '<div class="row my-4">'
    return html

@app.route('/')
def index():
    ttsh_df = pd.read_csv("resources/ttsh.csv")
    kkh_df = pd.read_csv("resources/kkh.csv")
    nuhs_df = pd.read_csv("resources/nuhs.csv")
    ttsh_df = ttsh_df.iloc[:, 1:]
    kkh_df = kkh_df.iloc[:, 1:]
    nuhs_df = nuhs_df.iloc[:, 1:]
    events_results = ttsh_df.values.tolist() + kkh_df.values.tolist() + nuhs_df.values.tolist()
    events_df = pd.DataFrame(events_results, columns = [
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
    events_df['datetime'] = events_df.apply(create_datetime, axis = 1)
    current_datetime = current_date.today()
    events_df = events_df[events_df['datetime'].dt.date >= current_datetime]
    events_df = events_df.sort_values(by = ['datetime'], ascending = True)
    events_df = events_df.drop_duplicates(subset = ['event name'])
    upcoming_events = events_df.head(8)
    upcoming_events_html = upcoming_events_html_generator(upcoming_events)
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

@app.route("/browse-events", methods = ['GET', 'POST'])
def events_search():
    keyword = request.form.to_dict()['keyword']
    category = request.form.to_dict()['category']
    month = request.form.to_dict()['month']
    price = request.form.to_dict()['price']
    mode = request.form.to_dict()['mode']
    search_criteria = []
    no_results = ""
    ttsh_df = pd.read_csv("resources/ttsh.csv")
    kkh_df = pd.read_csv("resources/kkh.csv")
    nuhs_df = pd.read_csv("resources/nuhs.csv")
    ttsh_df = ttsh_df.iloc[:, 1:]
    kkh_df = kkh_df.iloc[:, 1:]
    nuhs_df = nuhs_df.iloc[:, 1:]
    events_results = ttsh_df.values.tolist() + kkh_df.values.tolist() + nuhs_df.values.tolist()
    events_df = pd.DataFrame(events_results, columns = [
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
        events_df = events_df[(events_df['start month'] == search_month) & (events_df['start year'] == search_year)]
        months_list = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        search_criteria.append(f"<strong>{months_list[search_month - 1]} {search_year}</strong> (month, year)")
    if mode != "Mode":
        events_df = events_df[events_df['mode'] == mode]
        search_criteria.append(f"<strong>{mode}</strong> (mode)")
    if price != "":
        if int(price) == 0:
            events_df = events_df[events_df['fee type'] == "Free"]
        else:
            events_df['price'] = events_df['fees'].apply(lambda x: get_price_filter(x))
            events_df = events_df[events_df['price'] <= int(price)]
        search_criteria.append(f"<strong>SG${price}</strong> (price)")
    events_df = events_df.drop_duplicates(subset = ['event name'])
    events_html = events_html_generator(events_df)
    search_criteria = "You have searched for " + ", ".join(search_criteria)
    if events_df.empty:
        no_results = "No events found"
    return render_template("search.html", events_html = events_html, search_criteria = search_criteria, no_results = no_results)

@app.route("/events-details/<event_name>", methods = ['POST', 'GET'])
def event_details(event_name):
    ttsh_df = pd.read_csv("resources/ttsh.csv")
    kkh_df = pd.read_csv("resources/kkh.csv")
    nuhs_df = pd.read_csv("resources/nuhs.csv")
    ttsh_df = ttsh_df.iloc[:, 1:]
    kkh_df = kkh_df.iloc[:, 1:]
    nuhs_df = nuhs_df.iloc[:, 1:]
    events_results = ttsh_df.values.tolist() + kkh_df.values.tolist() + nuhs_df.values.tolist()
    events_df = pd.DataFrame(events_results, columns = [
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
    event_df = events_df[events_df['event name'] == event_name]
    event_specialities = list(event_df['speciality'].unique())
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
        price = "SG$" + str(event[18])
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
    register_url = str(event[21])
    recommended_events_df = events_df[events_df['speciality'].isin(event_specialities)].sort_values(['similarity'], ascending = False).head(3)
    recommended_events_html = upcoming_events_html_generator(recommended_events_df)
    return render_template("events_details.html", event_name = event_name, description = description, date = date, time = time, price = price, venue = location, register_url = register_url, recommended_events_html = recommended_events_html)

@app.route("/login", methods = ['POST', 'GET'])
def login():
    if 'user_name' in session and 'user_email' in session:
        return redirect(location = url_for('index'))
    else:
        return render_template("login.html", email = "", pwd = "", new_error_code = "")

@app.route("/signup", methods = ['POST', 'GET'])
def signup():
    if 'user_name' in session and 'user_email' in session:
        return redirect(location = url_for('index'))
    else:
        return render_template("signup.html", email = "", pwd = "", new_error_code = "")

@app.route("/check-details/<error_code>", methods = ['POST', 'GET'])
def check_details(error_code):
    new_error_code = ""
    existing_users = col_users.find()
    existing_user_names = []
    existing_user_emails = []
    existing_user_pwds = []
    for item in existing_users:
        existing_user_names.append(item['name'])
        existing_user_emails.append(item['email'])
        existing_user_pwds.append(item['pwd'])
    if error_code == "login":
        email = request.form.to_dict()['user_email']
        pwd = request.form.to_dict()['user_pwd']
        if email == "" or pwd == "":
            new_error_code = "empty"
        elif email not in existing_user_emails:
            new_error_code = "not signed up"
        elif pwd != existing_user_pwds[existing_user_emails.index(email)]:
            new_error_code = "pwd no match"
        else:
            new_error_code = "proceed"
        if new_error_code == "proceed":
            session['user_name'] =  existing_user_names[existing_user_emails.index(email)]
            session['user_email'] = email
            return redirect(location = url_for('index'))
        else:
            return render_template("login.html", email = email, pwd = pwd, new_error_code = new_error_code)
    elif error_code == "signup":
        name = request.form.to_dict()['user_name']
        email = request.form.to_dict()['user_email']
        pwd = request.form.to_dict()['user_pwd']
        cpwd = request.form.to_dict()['user_cpwd']
        if name == "" or email == "" or pwd == "" or cpwd == "":
            new_error_code = "empty"
        elif email in existing_user_emails:
            new_error_code = "signed up"
        elif pwd != cpwd:
            new_error_code = "pwd mismatch"
        else:
            new_error_code = "proceed"
        if new_error_code == "proceed":
            session['user_name'] =  name
            session['user_email'] = email
            col_users.insert_one({
                'name': name,
                'email': email,
                'pwd': cpwd
            })
            return redirect(location = url_for('index'))
        else:
            return render_template("signup.html", email = email, pwd = pwd, new_error_code = new_error_code)

@app.route("/bookmark/<event_name>")
def bookmark(event_name):
    if 'user_name' in session and 'user_email' in session:
        print(f"{event_name}, {session['user_email']}")
        bookmarks = col_bookmarks.find()
        bookmark_emails = []
        bookmark_bookmarks = []
        for bookmark_event in bookmarks:
            bookmark_emails.append(bookmark_event['email'])
            bookmark_bookmarks.append(list(bookmark_event['bookmarks']))
        if session['user_email'] in bookmark_emails:
            user_index = bookmark_emails.index(session['user_email'])
            user_bookmarks = bookmark_bookmarks[user_index]
            if event_name in user_bookmarks:
                user_bookmarks.remove(event_name)
            else:
                user_bookmarks.append(event_name)
            col_bookmarks.update_one({ "email": session['user_email'] }, { "$set": { "bookmarks": user_bookmarks } })
        else:
            col_bookmarks.insert_one({
                'email': session['user_email'],
                'bookmarks': [event_name]
            })
        return '', 204
    else:
        return render_template("login.html", email = "", pwd = "", new_error_code = "")

@app.route("/bookmarked")
def bookmarked():
    user_email = session['user_email']
    user_bookmarked_events = list(col_bookmarks.find({ 'email': user_email }))
    bookmarked_events = "no"
    bookmarked_events_html = ""
    if len(user_bookmarked_events) > 0:
        user_bookmarked_events = user_bookmarked_events[0]['bookmarks']
        ttsh_df = pd.read_csv("resources/ttsh.csv")
        kkh_df = pd.read_csv("resources/kkh.csv")
        nuhs_df = pd.read_csv("resources/nuhs.csv")
        ttsh_df = ttsh_df.iloc[:, 1:]
        kkh_df = kkh_df.iloc[:, 1:]
        nuhs_df = nuhs_df.iloc[:, 1:]
        events_results = ttsh_df.values.tolist() + kkh_df.values.tolist() + nuhs_df.values.tolist()
        events_df = pd.DataFrame(events_results, columns = [
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
        events_df = events_df[events_df['event name'].isin(user_bookmarked_events)]
        events_df = events_df.drop_duplicates(subset = ['event name'])
        bookmarked_events = "yes"
        bookmarked_events_html = events_html_generator(events_df)
    return render_template("bookmarked.html", bookmarked_events_html = bookmarked_events_html, bookmarked_events = bookmarked_events)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

if __name__ == '__app__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
