from flask import Flask, render_template
import os
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from datetime import date as current_date

app = Flask(__name__)

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
    ttsh_df = ttsh_df[[
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
    ttsh_df = ttsh_df[ttsh_df['datetime'].dt.date >= current_datetime]
    ttsh_df = ttsh_df.sort_values('datetime', ascending = True)
    ttsh_df = ttsh_df.drop_duplicates(subset = ['event name'])
    upcoming_events = ttsh_df.head(6)
    upcoming_events_html = events_html_generator(upcoming_events)
    return render_template("index.html", upcoming_events_html = upcoming_events_html)

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
