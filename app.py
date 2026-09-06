import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Restaurant Ratings Analysis", layout="wide", page_icon="🍽️")

# ---------- Data loading ----------
@st.cache_data
def load_data():
    ratings = pd.read_csv("data/ratings.csv")
    restaurants = pd.read_csv("data/restaurants.csv")
    cuisines = pd.read_csv("data/restaurant_cuisines.csv")
    consumers = pd.read_csv("data/consumers.csv")
    prefs = pd.read_csv("data/consumer_preferences.csv")

    df = (
        ratings
        .merge(restaurants, on="Restaurant_ID", how="left")
        .merge(cuisines, on="Restaurant_ID", how="left")
        .merge(consumers, on="Consumer_ID", how="left", suffixes=("_restaurant", "_consumer"))
    )
    return df, restaurants, cuisines, consumers, prefs

df, restaurants, cuisines, consumers, prefs = load_data()

# ---------- Sidebar filters ----------
st.sidebar.header("Filters")

cities = sorted(df["City_restaurant"].dropna().unique())
selected_cities = st.sidebar.multiselect("City", cities, default=cities)

cuisine_options = sorted(df["Cuisine"].dropna().unique())
selected_cuisines = st.sidebar.multiselect("Cuisine", cuisine_options, default=cuisine_options)

price_options = sorted(df["Price"].dropna().unique())
selected_prices = st.sidebar.multiselect("Price level", price_options, default=price_options)

age_options = sorted(df["AgeGroup"].dropna().unique())
selected_ages = st.sidebar.multiselect("Consumer age group", age_options, default=age_options)

filtered = df[
    df["City_restaurant"].isin(selected_cities)
    & df["Cuisine"].isin(selected_cuisines)
    & df["Price"].isin(selected_prices)
    & df["AgeGroup"].isin(selected_ages)
]

# ---------- Header ----------
st.title("🍽️ Restaurant Ratings Analysis")
st.caption("Interactive rebuild of the original Power BI report, built with Streamlit + Plotly.")

# ---------- KPI row ----------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Ratings in view", f"{len(filtered):,}")
col2.metric("Avg overall rating", f"{filtered['Overall_Rating'].mean():.2f}" if len(filtered) else "–")
col3.metric("Avg food rating", f"{filtered['Food_Rating'].mean():.2f}" if len(filtered) else "–")
col4.metric("Restaurants in view", f"{filtered['Restaurant_ID'].nunique():,}")

st.divider()

# ---------- Row 1: rating by cuisine + rating distribution ----------
c1, c2 = st.columns(2)

with c1:
    st.subheader("Average overall rating by cuisine")
    by_cuisine = (
        filtered.groupby("Cuisine", as_index=False)["Overall_Rating"]
        .mean()
        .sort_values("Overall_Rating", ascending=False)
        .head(15)
    )
    fig = px.bar(by_cuisine, x="Overall_Rating", y="Cuisine", orientation="h",
                 color="Overall_Rating", color_continuous_scale="Sunset")
    fig.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("Rating category distribution")
    cat_counts = filtered["Overall_Rating_Category"].value_counts().reset_index()
    cat_counts.columns = ["Category", "Count"]
    fig = px.pie(cat_counts, names="Category", values="Count", hole=0.45)
    st.plotly_chart(fig, use_container_width=True)

# ---------- Row 2: top restaurants + ratings by city ----------
c3, c4 = st.columns(2)

with c3:
    st.subheader("Top rated restaurants (min. 3 ratings)")
    top = (
        filtered.groupby(["Name", "City_restaurant"], as_index=False)
        .agg(avg_rating=("Overall_Rating", "mean"), n_ratings=("Overall_Rating", "count"))
        .query("n_ratings >= 3")
        .sort_values("avg_rating", ascending=False)
        .head(10)
    )
    st.dataframe(
        top.rename(columns={"City_restaurant": "City", "avg_rating": "Avg rating", "n_ratings": "# ratings"}),
        use_container_width=True,
        hide_index=True,
    )

with c4:
    st.subheader("Average rating by city")
    by_city = (
        filtered.groupby("City_restaurant", as_index=False)["Overall_Rating"]
        .mean()
        .sort_values("Overall_Rating", ascending=False)
    )
    fig = px.bar(by_city, x="City_restaurant", y="Overall_Rating", color="Overall_Rating",
                 color_continuous_scale="Teal")
    fig.update_layout(xaxis_title="City", yaxis_title="Avg overall rating", coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

# ---------- Row 3: map ----------
st.subheader("Restaurant locations")
map_df = filtered.dropna(subset=["Latitude_restaurant", "Longitude_restaurant"]).drop_duplicates("Restaurant_ID")
if len(map_df):
    fig = px.scatter_map(
        map_df, lat="Latitude_restaurant", lon="Longitude_restaurant",
        hover_name="Name", hover_data=["Cuisine", "Price", "City_restaurant"],
        color="Overall_Rating", color_continuous_scale="RdYlGn", zoom=4, height=500,
        map_style="carto-positron",
    )
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No restaurants match the current filters.")

st.divider()

with st.expander("View filtered raw data"):
    st.dataframe(filtered, use_container_width=True)

st.caption("Data source: restaurant consumer ratings dataset, originally modeled in Power BI, rebuilt here in Python.")
