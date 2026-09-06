# 🍽️ Restaurant Ratings Analysis — Streamlit Dashboard

An interactive rebuild of a Power BI restaurant ratings report, using Python, pandas, and Plotly inside Streamlit.

## What it shows
- KPI summary: ratings in view, average overall/food rating, restaurant count
- Average rating by cuisine (top 15)
- Rating category distribution (Highly Satisfactory / etc.)
- Top rated restaurants (min. 3 ratings)
- Average rating by city
- Interactive map of restaurant locations, colored by rating
- Filterable by city, cuisine, price level, and consumer age group

## Data
Five tables extracted from the original `.pbix` data model:
`ratings`, `restaurants`, `restaurant_cuisines`, `consumers`, `consumer_preferences`
(all in `/data`, joined at runtime in `app.py`).

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

