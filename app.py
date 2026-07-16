import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="World Bank Development Dashboard",
    layout="wide"
)

st.title("Beyond GDP: Balanced and Unbalanced Development Across Countries")

st.write(
    "This dashboard explores national development using World Bank indicators."
)

df = pd.read_csv("world_bank_cleaned.csv")

st.subheader("Dataset Preview")
st.dataframe(df.head())

st.subheader("World Map by Indicator")

year = st.selectbox(
    "Select a year",
    sorted(df["year"].dropna().unique(), reverse=True)
)

indicator = st.selectbox(
    "Select an indicator",
    [
        "gdp_per_capita",
        "population",
        "life_expectancy",
        "internet_users",
        "electricity_access",
        "secondary_school_enrollment",
        "unemployment",
        "forest_area"
    ]
)

year_data = df[df["year"] == year].dropna(subset=[indicator])

fig = px.choropleth(
    year_data,
    locations="country_code",
    color=indicator,
    hover_name="country",
    title=f"{indicator} Across Countries in {year}",
    color_continuous_scale="Viridis"
)

fig.update_layout(
    template="plotly_white",
    geo=dict(
        showframe=False,
        showcoastlines=True,
        projection_type="natural earth"
    )
)

st.plotly_chart(fig, use_container_width=True)