import streamlit as st
import pandas as pd

from icalendar import Calendar
from datetime import datetime

import requests


st.set_page_config(
    page_icon='🗓️',
    page_title='iCalendar Converter'
)


def extract_dates_from_ical(url, partner, unit):
    try:
        response = requests.get(url)

        if response.status_code == 200:
            cal         = Calendar.from_ical(response.text)
            event_dates = []

            for event in cal.walk('vevent'):
                start_date = pd.to_datetime(event['dtstart'].dt).normalize().date()
                end_date   = pd.to_datetime(event['dtend'].dt).normalize().date()
                event_dates.append((partner, unit, start_date, end_date))

            return event_dates
        else:
            st.warning(f"Failed to retrieve data from {url}. Status code: {response.status_code}")
            return []

    except Exception as e:
        st.warning(f"Error extracting dates from {url}: {str(e)}")
        return []

st.title("iCalendar Converter")

uploaded_file = st.file_uploader("iCalendar Converter - SOURCES.csv", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    options = st.multiselect('Departments', df.DEPARTMENT.unique(), default=df.DEPARTMENT.unique())

    def is_options_in_data(row):
        return row.DEPARTMENT in options
    
    df['option'] = df.apply(is_options_in_data, axis=1)

    if st.button('Pull Occupancy Data', use_container_width=True):
        df = df[df.option]
        st.caption("RELEVANT CALENDARS")
        st.dataframe(df, use_container_width=True)

        output_dates = []

        for index, row in df.iterrows():
            url         = row["CALENDAR"]
            partner     = row["PARTNER"]
            unit        = row["UNIT"]
            event_dates = extract_dates_from_ical(url, partner, unit)

            if event_dates:
                output_dates.extend(event_dates)

        if output_dates:
            output_df = pd.DataFrame(output_dates, columns=["Partner", "Unit", "Start Date", "End Date"])

            st.download_button("Download", output_df.to_csv(index=False).encode(), "extracted_dates.csv", "text/csv", use_container_width=True, type='primary')