import pandas as pd
import streamlit as st
import datetime
import math
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import numpy as np

st.title('Auto Accidents in Hamden, CT')

st.markdown('Data obtained from [Connecticut Crash Data Repository](https://www.ctcrash.uconn.edu).')

st.markdown('---')

#Prevents loading the file every time the user interacts with widgets
@st.cache_data
def load_data():
    df = pd.read_csv('https://raw.githubusercontent.com/a-sweet/hamden-accidents/main/crashes_cleaned2.csv', 
                     parse_dates=['full_date','Date Of Crash'])
    #df = pd.read_csv('crashes_cleaned2.csv', parse_dates=['full_date','Date Of Crash'])
    indexed_df = df.set_index('full_date')
    sorted_df = indexed_df.sort_index()
    sorted_df.drop(columns=['Unnamed: 0','Light Condition','Road Surface Condition','Type of Intersection'], inplace=True)
    return sorted_df

#load the dataset, parsing the date & time column as a date object
crashes = load_data()

#create the date range input slider
st.subheader('Dates')
d_range = st.date_input(
    "Date range",
    value = (crashes.index[0], crashes.index[-1]),
    min_value = min(crashes.index),
    max_value = max(crashes.index))


#limit to the specified date range if it has a start and end
if len(d_range) > 1:
   crashes = crashes.loc[d_range[0]:d_range[1], :]

st.markdown('---')

#severity of accident set of checkboxes
st.subheader('Crash Severity')

injury_list = []
if st.checkbox('Property Damage Only', value=True):
    injury_list.append('Property Damage Only')
if st.checkbox('Injury of Any Type (Excluding Fatalities)', value=True):
    injury_list.append('Injury of any type (Serious, Minor, Possible)')
if st.checkbox('Fatality', value=True):
    injury_list.append('Fatal (Kill)')

#filter dataframe to contain only rows with the checked crash severities
crashes = crashes.loc[crashes['Crash Severity'].isin(injury_list)]

st.markdown('---')

#weather conditions set of checkboxes
st.subheader('Weather Conditions')
weather_list = []

col1, col2 = st.columns(2)

with col1:
    if st.checkbox('Clear', value=True):
        weather_list.append('Clear')
    if st.checkbox('Rain', value=True):
        weather_list.append('Rain')
    if st.checkbox('Cloudy', value=True):
        weather_list.append('Cloudy')
    if st.checkbox('Sleet or Hail ', value=True):
        weather_list.append('Sleet or Hail ')
    if st.checkbox('Snow', value=True):
        weather_list.append('Snow')
    if st.checkbox('Blowing Snow', value=True):
        weather_list.append('Blowing Snow')

with col2:
    if st.checkbox('Freezing Rain or Freezing Drizzle', value=True):
        weather_list.append('Freezing Rain or Freezing Drizzle')
    if st.checkbox('Fog, Smog, Smoke', value=True):
        weather_list.append('Fog, Smog, Smoke')
    if st.checkbox('Blowing Sand, Soil, Dirt', value=True):
        weather_list.append('Blowing Sand, Soil, Dirt')
    if st.checkbox('Severe Crosswinds', value=True):
        weather_list.append('Severe Crosswinds')
    if st.checkbox('Other', value=True):
        weather_list.append('Other')
    if st.checkbox('Unknown', value=True):
        weather_list.append('Unknown')

#filter dataframe to contain only rows with the checked weather conditions
crashes = crashes.loc[crashes['Weather Condition'].isin(weather_list)]

st.markdown('---')

#add the map last, so it is the last element of the page
st.subheader('Map')
st.map(crashes)

st.markdown('---')

st.subheader('Streets and Accidents Table')

#count accidents for each street name
street_list = crashes['Roadway Name'].unique()


av_d_trf_df = pd.DataFrame()
d_trf_list = []
av_trf_dict = {}

for street in street_list:
  #calculate the mean of the daily traffic values, since it changes over time
  av_d_trf = crashes.loc[crashes['Roadway Name'] == street, ['Average Daily Traffic']].mean()[0]
  #print(f'Street: {street}, Av. Traffic: {av_d_trf}')
  #add to a dictionary with street name and calculated mean daily traffic unless trf is NaN 
  if math.isnan(av_d_trf) == False:
    av_trf_dict[street] = av_d_trf

#count accidents, make a dataframe
dangerous_streets = crashes.groupby(['Roadway Name','Route Class'])['Roadway Name'].count().to_frame()

#convert the extra index from groupby to a column
dangerous_streets.reset_index(level='Route Class', inplace=True)

#remove the name label from the index
dangerous_streets.index.name = None

#rename the columns to reflect their actual data: 
dangerous_streets.rename(columns = {'Roadway Name':'Number of Accidents','Route Class':'Road Type'}, inplace=True)

#add a new column to the dataframe with values from the dictionary (df index and dict keys are both street names)
dangerous_streets['Average Daily Traffic'] = dangerous_streets.index.map(av_trf_dict)
dangerous_streets['Average Daily Traffic'] = round(dangerous_streets['Average Daily Traffic'], 2)

dangerous_streets['Accidents per 1000 Daily Vehicles'] = round(dangerous_streets['Number of Accidents'] / (dangerous_streets['Average Daily Traffic'] / 1000), 2)

sorter = 'Number of Accidents'

sorter = st.radio('Sort by', ('Number of Accidents', 'Average Daily Traffic', 'Accidents per 1000 Daily Vehicles'))

dangerous_streets.sort_values(by=sorter, ascending=False, inplace=True)

st.dataframe(dangerous_streets, width = 800, height = 200)

st.write("*Average Daily Traffic values of 'None' or '<NA>' mean there is no data for that street in the chosen date range.")


st.markdown('---')

st.subheader('Accident Frequency Over Time')

interval = st.radio(
    "",
    ('Daily', 'Weekly', 'Monthly'))

daily_crashes = crashes.groupby(['Date Of Crash'])['Date Of Crash'].count().to_frame()
fig = plt.figure(figsize=(10, 4))
ax = fig.add_subplot()
ax.set_xlabel('Date')
ax.set_ylabel('Total accidents')

if interval == 'Daily':
    ax.plot(daily_crashes.index, daily_crashes['Date Of Crash'])
    ax.set_title('Daily Auto Accidents in Hamden')
    ax.set_xlim(min(daily_crashes.index), max(daily_crashes.index))
elif interval == 'Weekly':
    weekly_crashes = daily_crashes.resample('W').sum()
    ax.plot(weekly_crashes.index, weekly_crashes['Date Of Crash'])
    ax.set_title('Weekly Auto Accidents in Hamden')
    ax.set_xlim(min(weekly_crashes.index), max(weekly_crashes.index))
else:
    monthly_crashes = daily_crashes.resample('M').sum()
    ax.plot(monthly_crashes.index, monthly_crashes['Date Of Crash'])
    ax.set_title('Monthly Auto Accidents in Hamden')
    ax.set_xlim(min(monthly_crashes.index), max(monthly_crashes.index))

# Define date format
date_form = DateFormatter('%m-%y')
ax.xaxis.set_major_formatter(date_form)
st.pyplot(fig)

st.markdown('---')

st.subheader('Accident Frequency by Time of Day')

hourly_crashes = crashes.groupby(['Hour of the Day'])['Hour of the Day'].count().to_frame()

fig = plt.figure(figsize=(10, 4))
ax = fig.add_subplot()

ax.bar(hourly_crashes.index, hourly_crashes['Hour of the Day'])
ax.set_title(f'Hourly Auto Accidents in Hamden, {d_range[0].strftime("%m/%d/%Y")}-{d_range[1].strftime("%m/%d/%Y")}')
ax.set_xlabel('Hour')
ax.set_ylabel('Total accidents')
ax.set_xlim(min(hourly_crashes.index)-.6, max(hourly_crashes.index)+.6)

ax.set_xticks(range(0, 24),['12am','1am','2am','3am','4am','5am','6am','7am','8am','9am','10am','11am',
                            '12pm','1pm','2pm','3pm','4pm','5pm','6pm','7pm','8pm','9pm','10pm','11pm'],
                            rotation=90)

st.pyplot(fig)