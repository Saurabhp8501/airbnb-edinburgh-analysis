import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Airbnb Edinburgh Dashboard", layout="wide")

# ---------------------------------------------------------------------------
# Data loading & cleaning (mirrors the cleaning steps from the EDA notebook)
# ---------------------------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("data/listings.csv")
    df = df.drop(columns=["neighbourhood_group", "license"], errors="ignore")
    df["price"] = df["price"].fillna(df["price"].median())
    df["reviews_per_month"] = df["reviews_per_month"].fillna(0)
    df["last_review"] = pd.to_datetime(df["last_review"], errors="coerce")
    df["calculated_host_listings_count"] = df["calculated_host_listings_count"].fillna(0)
    df["host_name"] = df["host_name"].fillna("Unknown")
    df["minimum_nights"] = df["minimum_nights"].fillna(df["minimum_nights"].median())
    return df

@st.cache_data
def load_reviews():
    try:
        rev = pd.read_csv("data/reviews.csv")
        rev["date"] = pd.to_datetime(rev["date"], errors="coerce")
        return rev
    except FileNotFoundError:
        return None

df = load_data()
reviews = load_reviews()


# ---------------------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------------------
st.sidebar.header("Filters")

neighbourhoods = sorted(df["neighbourhood"].dropna().unique())
selected_neigh = st.sidebar.multiselect("Neighbourhood", neighbourhoods)

room_types = sorted(df["room_type"].dropna().unique())
selected_room = st.sidebar.multiselect("Room Type", room_types)

price_min, price_max = int(df["price"].min()), int(df["price"].quantile(0.99))
price_range = st.sidebar.slider("Price Range (£/night)", price_min, price_max, (price_min, price_max))

min_reviews = st.sidebar.slider("Minimum number of reviews", 0, int(df["number_of_reviews"].quantile(0.95)), 0)

st.sidebar.markdown("---")
st.sidebar.caption("Data: Inside Airbnb - Edinburgh listings.csv")

filtered = df.copy()
if selected_neigh:
    filtered = filtered[filtered["neighbourhood"].isin(selected_neigh)]
if selected_room:
    filtered = filtered[filtered["room_type"].isin(selected_room)]
filtered = filtered[filtered["price"].between(*price_range)]
filtered = filtered[filtered["number_of_reviews"] >= min_reviews]

# ---------------------------------------------------------------------------
# Header & key metrics
# ---------------------------------------------------------------------------
st.title("🏠 Airbnb Edinburgh - Interactive Dashboard")
st.caption(f"Showing {len(filtered):,} of {len(df):,} listings based on current filters")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Average Price", f"£{filtered['price'].mean():.0f}" if len(filtered) else "—")
c2.metric("Median Price", f"£{filtered['price'].median():.0f}" if len(filtered) else "—")
c3.metric("Total Listings", f"{len(filtered):,}")
c4.metric("Avg. Reviews / Listing", f"{filtered['number_of_reviews'].mean():.1f}" if len(filtered) else "—")

st.markdown("---")

# ---------------------------------------------------------------------------
# Row 1: Room type mix + Price distribution
# ---------------------------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("Listings by Room Type")
    if len(filtered):
        room_counts = filtered["room_type"].value_counts().reset_index()
        room_counts.columns = ["room_type", "count"]
        fig = px.pie(room_counts, names="room_type", values="count", hole=0.4,
                     color_discrete_sequence=px.colors.sequential.Teal)
        st.plotly_chart(fig, width="stretch")
    else:
        st.info("No listings match the current filters.")

with col2:
    st.subheader("Price Distribution")
    if len(filtered):
        trimmed = filtered[filtered["price"] <= filtered["price"].quantile(0.99)]
        fig = px.histogram(trimmed, x="price", nbins=40, color_discrete_sequence=["#3E7CB1"])
        fig.update_layout(xaxis_title="Price (£)", yaxis_title="Number of Listings")
        st.plotly_chart(fig, width="stretch")
    else:
        st.info("No listings match the current filters.")

# ---------------------------------------------------------------------------
# Row 2: Neighbourhood price + Price vs reviews scatter
# ---------------------------------------------------------------------------
col3, col4 = st.columns(2)

with col3:
    st.subheader("Median Price - Top 10 Neighbourhoods (in current filter)")
    if len(filtered):
        top10 = filtered["neighbourhood"].value_counts().head(10).index
        med_price = (filtered[filtered["neighbourhood"].isin(top10)]
                     .groupby("neighbourhood")["price"].median()
                     .sort_values(ascending=False))
        fig = px.bar(med_price, orientation="h", color_discrete_sequence=["#FF5A5F"])
        fig.update_layout(showlegend=False, xaxis_title="Median Price (£)", yaxis_title="")
        st.plotly_chart(fig, width="stretch")
    else:
        st.info("No listings match the current filters.")

with col4:
    st.subheader("Price vs. Number of Reviews")
    if len(filtered):
        sample = filtered.sample(min(1500, len(filtered)), random_state=42)
        fig = px.scatter(sample, x="number_of_reviews", y="price", color="room_type",
                          opacity=0.6, color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_layout(xaxis_title="Number of Reviews", yaxis_title="Price (£)")
        st.plotly_chart(fig, width="stretch")
    else:
        st.info("No listings match the current filters.")

# ---------------------------------------------------------------------------
# Row 3: Map
# ---------------------------------------------------------------------------
st.subheader("Listings Map - Colored by Price")
if len(filtered):
    map_sample = filtered.sample(min(3000, len(filtered)), random_state=42)
    fig = px.scatter_mapbox(
        map_sample, lat="latitude", lon="longitude", color="price",
        size_max=8, zoom=10.5, height=550,
        color_continuous_scale="Plasma",
        hover_name="name", hover_data=["room_type", "price", "neighbourhood"],
        mapbox_style="open-street-map"
    )
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    st.plotly_chart(fig, width="stretch")
else:
    st.info("No listings match the current filters.")

# ---------------------------------------------------------------------------
# Row 4: Review activity trend (from reviews.csv)
# ---------------------------------------------------------------------------
if reviews is not None:
    st.subheader("Review Activity Over Time")
    ids_in_filter = set(filtered["id"])
    rev_filtered = reviews[reviews["listing_id"].isin(ids_in_filter)]
    if len(rev_filtered):
        monthly = rev_filtered.set_index("date").resample("ME").size().reset_index(name="reviews")
        fig = px.line(monthly, x="date", y="reviews", color_discrete_sequence=["#16233F"])
        fig.update_layout(xaxis_title="Month", yaxis_title="Number of Reviews")
        st.plotly_chart(fig, width="stretch")
        st.caption("Note: reviews.csv contains review dates only (no comment text), so this reflects "
                   "review volume/activity, not sentiment.")
    else:
        st.info("No review data for the current filter selection.")

# ---------------------------------------------------------------------------
# Row 5: Data table + export
# ---------------------------------------------------------------------------
st.subheader("Listing Details")
display_cols = ["name", "neighbourhood", "room_type", "price", "number_of_reviews",
                 "availability_365", "minimum_nights"]
st.dataframe(filtered[display_cols].sort_values("price", ascending=False), width="stretch", height=350)

st.download_button(
    label="⬇️ Download filtered data as CSV",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="airbnb_edinburgh_filtered.csv",
    mime="text/csv",
)
