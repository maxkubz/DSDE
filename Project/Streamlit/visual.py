
import streamlit as st
import numpy as np
import pandas as pd
import pydeck as pdk
import plotly.express as px
import json
import plotly.graph_objects as go

import math

#read data
@st.cache_data
def load_data():
    return pd.read_csv("result_csv.csv")

df = load_data()


st.sidebar.header('Select filters for the data') 
filter_layer_type = st.sidebar.radio('Filter by', ["College", "Country", "All"])


filter_df = df.copy()

#column province
countries = df['countryName'].unique()
colleges = df['universityName'].unique()
cities = df['cityName'].unique()

top_college_filter = st.sidebar.number_input("Top colleges to display" + " max: " + str(len(colleges)), 1, len(colleges), 10)
top_country_filter = st.sidebar.number_input("Top countries to display" + " max: " + str(len(countries)), 1, len(countries), 10)
top_city_filter = st.sidebar.number_input("Top cities to display"+ " max: " + str(len(cities)), 1, len(cities), 10)


# Expander sidebar
st.sidebar.markdown('### Selector')
with st.sidebar.expander("Select Countries"):
    option_countries = st.multiselect("Select countries", countries, countries)
filter_df = filter_df[(filter_df['countryName'].isin(option_countries))]

#Sidebar for college
with st.sidebar.expander("Select Colleges"):
    option_college = st.multiselect("Select colleges", colleges, colleges)
    
filter_df = filter_df[(filter_df['universityName'].isin(option_college))]

# Data after filter and grouping
df_group_by_college = filter_df.groupby('universityName').size().sort_values(ascending=False)
top_df_group_by_college = df_group_by_college.head(int(top_college_filter))  

df_group_by_country = filter_df.groupby('countryName').size().sort_values(ascending=False)
top_df_group_by_country = df_group_by_country.head(int(top_country_filter))

df_group_by_city = filter_df.groupby('cityName').size().sort_values(ascending=False)
top_df_group_by_city = df_group_by_city.head(int(top_city_filter))  



def bar_college():
    # Sort the data in descending order based on values
    top_df_group_by_college_sorted = top_df_group_by_college.sort_values(ascending=True)

    # Truncate college names
    truncated_college_names = [name[:20] + '...' if len(name) > 20 else name for name in top_df_group_by_college_sorted.index]

    fig = go.Figure(data=[go.Bar(
        x=top_df_group_by_college_sorted.values,
        y=truncated_college_names,
        orientation='h'
    )])

    fig.update_layout(
        title=("Top " + str(top_college_filter) + " colleges with the most papers in Scopus"),
        xaxis_title="Number of papers",
        yaxis_title="Colleges",
        template='plotly_dark'
    )

    fig.update_layout(
        width=800,  # Adjust width as needed
        height=500,  # Adjust height as needed
        margin=dict(l=150)  # Adjust left margin to accommodate longer labels
    )

    st.plotly_chart(fig)




# Main app
st.markdown(
    """
    <h1 style='text-align: center;'>Scopus papers</h1>
    """,
    unsafe_allow_html=True
)
st.write('#### Displaying results of being cited by academic papers in Scopus')



#bar chart
bar_college()


# Display Map
st.pydeck_chart(map)

# Display data
st.write('### Datafram') 
st.dataframe(filter_df)



