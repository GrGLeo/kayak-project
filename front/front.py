import os
import streamlit as st
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
from sqlalchemy import create_engine

st.set_page_config(layout="wide")
load_dotenv()
postgres = os.getenv("POSTGRES")
engine = create_engine(postgres)

hotels = pd.read_sql("SELECT * FROM hotels", con=engine)
weather = pd.read_sql("SELECT * FROM weather", con=engine)
geo = hotels[["city", "lat", "lon"]]
geo = geo.drop_duplicates(subset="city")
weather = weather.merge(geo, on="city", how="left").dropna(axis=0)


def center_text(text, title):
    return f"<{title} style='text-align: center;'>{text}</{title}>"


st.markdown(center_text("Kayak Hotels Reservation", "h1"),
            unsafe_allow_html=True)

navigation = st.sidebar.radio(
    "Navigation", ["Home", "Weather", "Hotels information"])

if navigation == "Home":
    description = """

    Explore hotel ratings, popularity, and attributes across various cities. The dashboard provides insights into average ratings, popularity,
    and hotel amenities to help you make informed decisions when planning your trip.

    Navigate through different sections using the sidebar. Select cities and hotels to view detailed information. Discover rating distributions,
    popularity, and hotel attributes through interactive visualizations.

    Start your journey with Kayak Hotels Reservation and plan your next trip with ease!
    """

    st.markdown(description)

if navigation == "Hotels information":

    col1, col2 = st.columns([1, 1])
    with col1:
        city_rating = hotels.groupby(
            "city", as_index=False).agg({"rating": "mean"})
        city_rating = city_rating.sort_values(by="rating", ascending=True)
        fig = px.bar(city_rating, x="city", y="rating")
        fig.update_layout(
            title="Average rating per city", yaxis_title="Ratings", xaxis_title=None
        )
        st.plotly_chart(fig)

        mean_ratings = hotels.groupby("city")["rating"].median().reset_index()
        mean_ratings_sorted = mean_ratings.sort_values(by="rating")
        fig = px.box(
            hotels,
            x="city",
            y="rating",
            category_orders={"city": mean_ratings_sorted["city"]},
        )
        fig.update_layout(
            title="Distribution of ratings by city",
            yaxis_title="Rating",
            template="plotly_white",
        )
        st.plotly_chart(fig)

    with col2:
        sum_city_reviews = hotels.groupby("city", as_index=False).agg(
            {"reviews": "sum"}
        )
        sum_city_reviews = sum_city_reviews.sort_values(
            "reviews", ascending=False)
        fig = px.bar(sum_city_reviews, x="city", y="reviews")
        fig.update_layout(
            title="Popularity per city",
            yaxis_title="Number of reviews",
            xaxis_title=None,
        )
        st.plotly_chart(fig)

        rating_over_time = hotels.groupby('dt_partition', as_index=False).agg({'rating': 'mean','lat': 'mean','lon': 'mean'})
        fig = px.line(rating_over_time, x='dt_partition', y='rating')
        fig.update_layout(
                    title='Evolution of rating over time',
                    yaxis_title='Average rating',
                    xaxis_title=None
                )
        st.plotly_chart(fig)

    city = st.selectbox("Choose a city", sorted(hotels["city"].unique()))
    selected_city = hotels[hotels["city"] == city]
    fig = px.scatter_mapbox(
        selected_city,
        lat="lat",
        lon="lon",
        hover_name="name",
        hover_data=["rating"],
        color_discrete_sequence=["blue"],
        zoom=12,
        height=600,
    )
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    st.plotly_chart(fig)

    hotel = st.selectbox("Choose a hotel", sorted(
        selected_city["name"].unique()))
    selected_hotel = selected_city[selected_city["name"] == hotel]
    selected_hotel_latest = selected_hotel[
        selected_hotel["dt_partition"] == selected_hotel["dt_partition"].max()
    ]

    col1, col2 = st.columns([1, 1])
    with col1:
        pivot_hotel = selected_hotel_latest.drop(
            [
                "name",
                "description",
                "url",
                "dt_partition",
                "lat",
                "lon",
                "reviews",
                "city",
            ],
            axis=1,
        )
        pivot_hotel = pivot_hotel.T
        pivot_hotel.rename(
            {pivot_hotel.columns[0]: "hotel"}, axis=1, inplace=True)
        fig = px.bar(pivot_hotel, x=pivot_hotel.index, y="hotel")
        fig.update_layout(height=300)
        st.plotly_chart(fig)

        rating_over_time = selected_hotel.groupby("dt_partition", as_index=False).agg(
            {"rating": "mean"}
        )
        fig = px.line(rating_over_time, x="dt_partition", y="rating")
        fig.update_layout(height=300)
        mean = hotels.rating.mean()
        # fig.add_hline(y=mean)
        st.plotly_chart(fig, height=100)

    with col2:
        st.markdown(
            f"""<div style='font-size: 16px; white-space: pre-line;'>
            {selected_hotel_latest['description'].iloc[0]}</div>""",
            unsafe_allow_html=True,
        )

if navigation == "Weather":
    st.markdown(center_text("Weather Information", "h2"),
                unsafe_allow_html=True)

    selected_date = st.date_input("Select a date")

    col1, col2 = st.columns([1, 1])

    with col1:

        date = selected_date.strftime("%Y-%m-%d")

        date_weather = weather[weather["dt_partition"] == date]
        date_weather_grouped = date_weather.groupby("city", as_index=False).agg(
            {"temps": "mean", "feels_like": "mean", "lat": "first", "lon": "first"}
        )
        date_weather_grouped["point_size"] = 20

        fig = px.scatter_mapbox(
            date_weather_grouped,
            lat="lat",
            lon="lon",
            color="temps",
            hover_name="city",
            hover_data=["temps", "feels_like"],
            color_continuous_scale=px.colors.sequential.Rainbow,
            zoom=4,
            height=600,
            size="point_size",
        )
        fig.update_layout(mapbox_style="carto-positron")

        st.plotly_chart(fig)

    with col2:
        selected_city = st.selectbox(
            "Choose a city", sorted(date_weather["city"].unique())
        )

        st.text(f"""Here is the weather for {
                selected_city} over the next five days:""")
        filtered_df = date_weather[date_weather["city"] == selected_city]
        filtered_df = filtered_df.drop(
            ["sunrise", "sunset", "lat", "lon", "dt_partition"], axis=1
        )
        st.write(filtered_df)

        fig = px.line(filtered_df, x="dt_text", y=["temps", "feels_like"])
        fig.update_layout(
            title="Temperature forecast", yaxis_title="Temperature °C", xaxis_title=None
        )
        st.plotly_chart(fig)
