import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="World Bank Development Dashboard",
    layout="wide"
)

st.title("Beyond GDP: Balanced and Unbalanced Development Across Countries")

st.write(
    "This dashboard explores whether national development can be explained by GDP alone, "
    "or whether it should be understood as a multidimensional concept involving health, "
    "education, technology access, infrastructure, labor market conditions, population, and environment."
)

df = pd.read_csv("world_bank_cleaned.csv")

indicator_cols = [
    "gdp_per_capita",
    "population",
    "life_expectancy",
    "internet_users",
    "electricity_access",
    "secondary_school_enrollment",
    "unemployment",
    "forest_area"
]

st.sidebar.header("Dashboard Controls")

available_years = sorted(df["year"].dropna().unique(), reverse=True)

year = st.sidebar.selectbox(
    "Select year",
    available_years
)

indicator = st.sidebar.selectbox(
    "Select indicator for map",
    indicator_cols
)

year_data = df[df["year"] == year].copy()

st.header("1. Dataset Preview")

st.write(
    "The dataset contains World Bank development indicators across countries and years."
)

st.dataframe(year_data.head(20), use_container_width=True)

st.header("2. Development Indicator Map")

map_data = year_data.dropna(subset=[indicator])

fig_map = px.choropleth(
    map_data,
    locations="country_code",
    color=indicator,
    hover_name="country",
    title=f"{indicator} Across Countries in {year}",
    color_continuous_scale="Viridis"
)

fig_map.update_layout(
    template="plotly_white",
    geo=dict(
        showframe=False,
        showcoastlines=True,
        projection_type="natural earth"
    ),
    height=550
)

st.plotly_chart(fig_map, use_container_width=True)

st.write(
    "This map allows users to explore how each development indicator differs across countries."
)

st.header("3. Relationship Between Two Development Indicators")

col1, col2 = st.columns(2)

with col1:
    x_indicator = st.selectbox(
        "Select X-axis indicator",
        indicator_cols,
        index=0
    )

with col2:
    y_indicator = st.selectbox(
        "Select Y-axis indicator",
        indicator_cols,
        index=2
    )

scatter_data = year_data.dropna(subset=[x_indicator, y_indicator])

corr_value = scatter_data[x_indicator].corr(scatter_data[y_indicator])

fig_scatter = px.scatter(
    scatter_data,
    x=x_indicator,
    y=y_indicator,
    hover_name="country",
    title=f"{x_indicator} vs {y_indicator} in {year}",
    labels={
        x_indicator: x_indicator,
        y_indicator: y_indicator
    },
    color_discrete_sequence=px.colors.qualitative.Set2
)

fig_scatter.update_traces(
    marker=dict(
        size=8,
        opacity=0.7,
        line=dict(width=0.5, color="white")
    )
)

fig_scatter.update_layout(
    template="plotly_white",
    height=500,
    title_x=0.5
)

fig_scatter.add_annotation(
    x=0.05,
    y=0.95,
    xref="paper",
    yref="paper",
    text=f"Correlation: {corr_value:.2f}",
    showarrow=False,
    font=dict(size=14),
    bgcolor="white",
    bordercolor="gray",
    borderwidth=1
)

st.plotly_chart(fig_scatter, use_container_width=True)

st.write(
    "This scatter plot shows whether two development indicators move together across countries."
)

st.header("4. Unbalanced Development Patterns")

development_cols = [
    "gdp_per_capita",
    "life_expectancy",
    "internet_users",
    "electricity_access",
    "secondary_school_enrollment",
    "unemployment",
    "forest_area"
]

imbalance_data = year_data.dropna(subset=development_cols).copy()

positive_cols = [
    "gdp_per_capita",
    "life_expectancy",
    "internet_users",
    "electricity_access",
    "secondary_school_enrollment",
    "forest_area"
]

for col in positive_cols:
    imbalance_data[col + "_score"] = (
        (imbalance_data[col] - imbalance_data[col].min()) /
        (imbalance_data[col].max() - imbalance_data[col].min()) * 100
    )

imbalance_data["unemployment_score"] = (
    (imbalance_data["unemployment"].max() - imbalance_data["unemployment"]) /
    (imbalance_data["unemployment"].max() - imbalance_data["unemployment"].min()) * 100
)

score_cols = [
    "gdp_per_capita_score",
    "life_expectancy_score",
    "internet_users_score",
    "electricity_access_score",
    "secondary_school_enrollment_score",
    "unemployment_score",
    "forest_area_score"
]

imbalance_data["imbalance_score"] = imbalance_data[score_cols].std(axis=1)

if len(imbalance_data) > 0:
    imbalance_data["imbalance_group"] = pd.qcut(
        imbalance_data["imbalance_score"],
        q=4,
        labels=[
            "Low imbalance",
            "Moderate imbalance",
            "High imbalance",
            "Very high imbalance"
        ],
        duplicates="drop"
    )

    color_map = {
        "Low imbalance": "#2ca25f",
        "Moderate imbalance": "#fee08b",
        "High imbalance": "#fdae61",
        "Very high imbalance": "#d7191c"
    }

    fig_imbalance = px.choropleth(
        imbalance_data,
        locations="country_code",
        color="imbalance_group",
        hover_name="country",
        hover_data={
            "imbalance_score": ":.1f",
            "gdp_per_capita_score": ":.1f",
            "life_expectancy_score": ":.1f",
            "internet_users_score": ":.1f",
            "electricity_access_score": ":.1f",
            "secondary_school_enrollment_score": ":.1f",
            "unemployment_score": ":.1f",
            "forest_area_score": ":.1f",
            "country_code": False
        },
        title=f"Unbalanced Development Patterns in {year}",
        color_discrete_map=color_map,
        category_orders={
            "imbalance_group": [
                "Low imbalance",
                "Moderate imbalance",
                "High imbalance",
                "Very high imbalance"
            ]
        }
    )

    fig_imbalance.update_layout(
        template="plotly_white",
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type="natural earth"
        ),
        height=550
    )

    st.plotly_chart(fig_imbalance, use_container_width=True)

st.write(
    "This map shows countries with uneven development profiles. A higher imbalance score means that a country performs very differently across development dimensions."
)

st.header("5. Most Balanced Development Profiles")

balanced_data = imbalance_data.copy()

balanced_data["average_development_score"] = balanced_data[score_cols].mean(axis=1)
balanced_data["development_balance_gap"] = balanced_data[score_cols].std(axis=1)

balanced_data["balanced_development_score"] = (
    balanced_data["average_development_score"] - balanced_data["development_balance_gap"]
)

top_n = st.slider(
    "Select number of countries to display",
    min_value=5,
    max_value=20,
    value=10
)

top_balanced = balanced_data.sort_values(
    "balanced_development_score",
    ascending=False
).head(top_n)

fig_balanced = px.bar(
    top_balanced.sort_values("balanced_development_score"),
    x="balanced_development_score",
    y="country",
    orientation="h",
    color="balanced_development_score",
    hover_data={
        "average_development_score": ":.1f",
        "development_balance_gap": ":.1f",
        "balanced_development_score": ":.1f"
    },
    title=f"Most Balanced Development Profiles in {year}",
    labels={
        "balanced_development_score": "Balanced Development Score",
        "country": "Country"
    },
    color_continuous_scale="Blues"
)

fig_balanced.update_layout(
    template="plotly_white",
    height=500,
    title_x=0.5,
    coloraxis_showscale=False
)

st.plotly_chart(fig_balanced, use_container_width=True)

st.write(
    "This chart highlights countries that perform consistently well across multiple development dimensions."
)

st.header("6. Correlation Between Development Indicators")

corr_data = year_data[indicator_cols].dropna()

corr_matrix = corr_data.corr()

fig_corr = px.imshow(
    corr_matrix,
    text_auto=".2f",
    color_continuous_scale="RdBu",
    zmin=-1,
    zmax=1,
    title=f"Correlation Matrix of Development Indicators in {year}"
)

fig_corr.update_layout(
    template="plotly_white",
    height=700,
    title_x=0.5
)

st.plotly_chart(fig_corr, use_container_width=True)

st.write(
    "The heatmap summarizes which development indicators are closely connected and which indicators behave more independently."
)

st.header("Conclusion")

st.write(
    "Overall, the dashboard shows that development indicators are connected, but not perfectly aligned. "
    "GDP is important, but it does not fully represent health, education, technology access, infrastructure, "
    "employment, and environmental conditions. Therefore, national development should be understood as a multidimensional and balanced process."
)