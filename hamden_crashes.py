import pandas as pd
import streamlit as st
import datetime

st.title('Auto Accidents in Hamden, CT')

st.markdown('---')

#Prevents loading the file every time the user interacts with widgets
@st.cache
def load_data():
    df = pd.read_csv('crashes_cleaned2.csv', parse_dates=['full_date'])
    #df.set_index('Date Of Crash')
    return df

#load the dataset, parsing the date & time column as a date object
crashes = load_data()

#set the date & time column as the index
crashes.set_index('full_date', inplace=True)

#create the date range input slider
st.subheader('Dates')
d_range = st.date_input(
    "Date range",
    value = (datetime.date(2018,1,1), datetime.date(2023,3,11)),
    min_value = datetime.date(2018,1,1),
    max_value = datetime.date(2023,3,11))

#limit to the specified date range if it has a start and end
if len(d_range) > 1:
   crashes = crashes.loc[d_range[0]:d_range[1], :]

st.markdown('---')

#severity of accident set of checkboxes
st.subheader('Crash Severity')

injury_list = []
if st.checkbox('Property Damage Only', value=True):
    injury_list.append('O')
if st.checkbox('Injury of Any Type (Excluding Fatalities)', value=True):
    injury_list.append('A')
if st.checkbox('Fatality', value=True):
    injury_list.append('K')

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
crashes = crashes.loc[crashes['Weather Condition Text Format'].isin(weather_list)]

st.markdown('---')

#add the map last, so it is the last element of the page
st.subheader('Map')
st.map(crashes)
