import os
import datetime
import streamlit as st
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
from sqlalchemy import create_engine

st.set_page_config(layout='wide')
load_dotenv()
postgres = os.getenv('POSTGRES')
engine = create_engine(postgres)

hotels = pd.read_sql('SELECT * FROM hotels', con=engine)
weather = pd.read_sql('SELECT * FROM weather', con=engine)
geo = hotels[['city','lat','lon']]
geo = geo.drop_duplicates(subset='city')
weather = weather.merge(geo, on='city', how='left').dropna(axis=0)


def center_text(text, title):
    return f"<{title} style='text-align: center;'>{text}</{title}>"

st.markdown(center_text('Kayak Hotels Reservation', 'h1'), unsafe_allow_html=True)

navigation = st.sidebar.radio("Navigation", ['Home', 'Weather', 'Hotels information'])

if navigation == 'Hotels information':
    st.markdown(center_text('Hotels information', 'h2'), unsafe_allow_html=True)

if navigation == 'Weather':
    st.markdown(center_text('Weather Information', 'h2'), unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1])
    
    with col1:

        # Get today's date
        today_date = datetime.datetime.now().strftime('%Y-%m-%d')
        
        today_weather = weather[weather['dt_partition'] == today_date]
        today_weather_grouped = today_weather.groupby('city', as_index=False).agg({'temps':'mean', 'feels_like':'mean','lat':'first','lon':'first'})
        today_weather_grouped['point_size'] = 20
        # Plotly Express scatter mapbox plot
        fig = px.scatter_mapbox(today_weather_grouped, lat="lat", lon="lon", color="temps",
                                hover_name="city", hover_data=['temps','feels_like'],
                                color_continuous_scale=px.colors.sequential.Rainbow,
                                zoom=4, height=600, size='point_size')
        fig.update_layout(mapbox_style="carto-positron")

        # Display the map
        st.plotly_chart(fig)
    
        with col2:
            selected_city = st.selectbox("Choose a city", sorted(today_weather['city'].unique()))
            
            st.text(f'Here is the weather for {selected_city} over the next five days:')
            filtered_df = today_weather[today_weather['city'] == selected_city]
            filtered_df = filtered_df.drop(['sunrise','sunset','lat','lon','dt_partition'], axis=1)
            st.write(filtered_df)
