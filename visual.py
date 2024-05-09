import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pycountry

# Read data
@st.cache_data
def load_data():
    return pd.read_csv("result_csv.csv")

df = load_data()

st.sidebar.header('Select countries, colleges, and cities to filter the data') 

filter_df = df.copy()

# Column province
countries = df['countryName'].unique()
colleges = df['universityName'].unique()
cities = df['cityName'].unique()


# ==================== Sidebar ==============================

# Expander sidebar
with st.sidebar.expander("Select Countries"):
    option_countries = st.multiselect("Select countries", countries, countries)
filter_df = filter_df[(filter_df['countryName'].isin(option_countries))]

# Sidebar for college
with st.sidebar.expander("Select Colleges"):
    option_college = st.multiselect("Select colleges", colleges, colleges)
    
filter_df = filter_df[(filter_df['universityName'].isin(option_college))]

# Sidebar for city
with st.sidebar.expander("Select Cities"):
    option_city = st.multiselect("Select cities", cities, cities)

filter_df = filter_df[(filter_df['cityName'].isin(option_city))]



# ==================== Create Map ====================

def get_country_code(country_name):
    try:
        return pycountry.countries.lookup(country_name).alpha_3
    except LookupError:
        return None

def country_map(top_df_group_by_country):
    # Load world map data
    world_map = go.Figure(data=go.Choropleth(
        locations = top_df_group_by_country.index.map(get_country_code),
        z = top_df_group_by_country.values,
        text = top_df_group_by_country.index,
        colorscale = 'Viridis',
        reversescale = True,
        marker_line_color='darkgray',
        marker_line_width=0.5,
        colorbar_title = 'Reference Count',
    ))

    world_map.update_layout(
        title_text='Map showing how often each country is referenced in the paper.',
        geo=dict(
            showcoastlines=True,
            projection_type='equirectangular'
        ),
        height=600,
        width=700,
    )

    st.plotly_chart(world_map)

    
# ==================== Summary Texts ====================

def generate_summary_text(data, title, top_data, top=5, sort_order='descending'):
    total_items = len(data)
    unique_items = data.nunique()
    most_referenced = top_data.index[0]
    most_referenced_count = top_data.iloc[0]

    top_items = top_data.head(top)
    top_items_text = "\n".join([f"- {item}: {count}" for item, count in zip(top_items.index, top_items.values)])

    if sort_order == 'descending':
        sort_order_text = "descending order"
    else:
        sort_order_text = "ascending order"

    summary_text = f"""
    **{title} Analysis Summary:**
    - Total {title.lower()} analyzed: {total_items}
    - Unique {title.lower()} analyzed: {unique_items}
    - Most referenced {title.lower()}: {most_referenced} ({most_referenced_count} references)
    - Top {top} {title.lower()} ({sort_order_text}):
    {top_items_text}
    """
    return summary_text
    
    
# ==================== Display Dataframe ====================

def display_dataframe(data, title):
    st.write(f"<p style='font-weight:bold;'>{title} Dataframe</p>", unsafe_allow_html=True)

    st.dataframe(data)

    

# ==================== Create Pie Chart ====================

def pie_chart(data, title, threshold=15, width=800, height=500):
    # Calculate total sum
    total_sum = data.sum()

    # Sort the data by values in descending order
    sorted_data = data.sort_values(ascending=False)

    # Calculate the cumulative sum and percentage
    sorted_data_cumsum = sorted_data.cumsum()
    sorted_data_percentage = (sorted_data_cumsum / total_sum) * 100

    # Find the index where the percentage exceeds 85%
    idx = sorted_data_percentage.gt(85).idxmax()

    # Convert index label to integer index
    idx_int = sorted_data.index.get_loc(idx)

    # Split the data into two parts: the first 85% and the remaining
    first_85_percent = sorted_data.iloc[:idx_int + 1]
    remaining_data = sorted_data.iloc[idx_int + 1:]

    # Sum up the remaining data and add it as a single category
    remaining_sum = remaining_data.sum()
    if remaining_sum > 0:
        first_85_percent['Others'] = remaining_sum

    fig = go.Figure(data=[go.Pie(labels=first_85_percent.index, values=first_85_percent.values)])
    fig.update_traces(textinfo='percent', name='')  # Show percentage values
    fig.update_layout(title=title)

    # Set width and height
    fig.update_layout(width=width, height=height)

    st.plotly_chart(fig)
    
# ==================== Create Chart ====================



#----------------- College -----------------
def bar_college():
    # Select top
    top_college_filter = st.number_input("Top colleges to display" + "  | max: " + str(len(colleges)), 1, len(colleges), 10)
    df_group_by_college = filter_df.groupby('universityName').size().sort_values(ascending=False)
    top_df_group_by_college = df_group_by_college.head(int(top_college_filter))  
    
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
        title=("Total number of papers that refer to each university."),
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
    
    
    # College percentile
    college_percentile = top_df_group_by_college_sorted / top_df_group_by_college_sorted.sum() * 100
    pie_chart(college_percentile, "Percentage of the total number of papers that refer to each university from the total number of papers.")
    
    # Dataframe
    college_data = pd.DataFrame({'Total': top_df_group_by_college_sorted, 'Percentage': college_percentile})
    college_data = college_data.sort_values(by='Total', ascending=False)
    display_dataframe(college_data, "College")
    
    # Generate summary text for college
    college_summary = generate_summary_text(filter_df['universityName'], "College", top_df_group_by_college_sorted, top=10, sort_order='descending')
    st.markdown(college_summary)
    
    
    
    
#----------------- Country -----------------
    
def bar_country():
    # Top country
    top_country_filter = st.number_input("Top countries to display" + " | max: " + str(len(countries)), 1, len(countries), 10)
    df_group_by_country = filter_df.groupby('countryName').size().sort_values(ascending=False)
    top_df_group_by_country = df_group_by_country.head(int(top_country_filter))

    
    # Sort the data in descending order based on values
    top_df_group_by_country_sorted = top_df_group_by_country.sort_values(ascending=True)

    # Truncate country names
    truncated_country_names = [name[:20] + '...' if len(name) > 20 else name for name in top_df_group_by_country_sorted.index]
    
    # Display Map
    country_map(top_df_group_by_country_sorted)

    fig = go.Figure(data=[go.Bar(
        x=top_df_group_by_country_sorted.values,
        y=truncated_country_names,
        orientation='h'
    )])

    fig.update_layout(
        title=("Total number of papers that refer to each country."),
        xaxis_title="Number of papers",
        yaxis_title="Countries",
        template='plotly_dark'
    )

    fig.update_layout(
        width=800,  # Adjust width as needed
        height=500,  # Adjust height as needed
        margin=dict(l=150)  # Adjust left margin to accommodate longer labels
    )

    st.plotly_chart(fig)
    
    # Country percentile
    country_percentile = top_df_group_by_country_sorted / top_df_group_by_country_sorted.sum() * 100
    
    pie_chart(country_percentile, "Percentage of the total number of papers that refer to each country from the total number of papers.")
    
    #country df
    country_data = pd.DataFrame({'Total': top_df_group_by_country_sorted, 'Percentage': country_percentile})
    country_data = country_data.sort_values(by='Total', ascending=False)
    display_dataframe(country_data, "Country")
    
    country_summary = generate_summary_text(filter_df['countryName'], "Country", top_df_group_by_country_sorted, top=10, sort_order='descending')
    st.markdown(country_summary)

    
#----------------- City -----------------
    
def bar_city():
    
    # Top city
    top_city_filter = st.number_input("Top cities to display"+ " | max: " + str(len(cities)), 1, len(cities), 10)
    df_group_by_city = filter_df.groupby('cityName').size().sort_values(ascending=False)
    top_df_group_by_city = df_group_by_city.head(int(top_city_filter))  

    
    # Sort the data in descending order based on values
    top_df_group_by_city_sorted = top_df_group_by_city.sort_values(ascending=True)

    # Truncate city names
    truncated_city_names = [name[:20] + '...' if len(name) > 20 else name for name in top_df_group_by_city_sorted.index]

    fig = go.Figure(data=[go.Bar(
        x=top_df_group_by_city_sorted.values,
        y=truncated_city_names,
        orientation='h'
    )])

    fig.update_layout(
        title=("Total number of papers that refer to each country."),
        xaxis_title="Number of papers",
        yaxis_title="Cities",
        template='plotly_dark'
    )

    fig.update_layout(
        width=800,  # Adjust width as needed
        height=500,  # Adjust height as needed
        margin=dict(l=150)  # Adjust left margin to accommodate longer labels
    )

    st.plotly_chart(fig)
    
    # City percentile
    
    city_percentile = top_df_group_by_city_sorted / top_df_group_by_city_sorted.sum() * 100
    
    pie_chart(city_percentile, "Percentage of the total number of papers that refer to each city from the total number of papers.")
    
    #City df
    city_data = pd.DataFrame({'Total': top_df_group_by_city_sorted, 'Percentage': city_percentile})
    city_data = city_data.sort_values(by='Total', ascending=False)
    display_dataframe(city_data, "City")
    
    city_summary = generate_summary_text(filter_df['cityName'], "City", top_df_group_by_city_sorted, top=10, sort_order='descending')
    st.markdown(city_summary)




    

def percentile_analysis():
    

    # Country percentile
    country_percentile = filter_df['countryName'].value_counts(normalize=True) * 100
    pie_chart(country_percentile, "Country Percentile")

    # City percentile
    city_percentile = filter_df['cityName'].value_counts(normalize=True) * 100
    pie_chart(city_percentile, "City Percentile")
    

# Main app
st.markdown(
    """
    <h1 style='text-align: center;'>Scopus papers</h1>
    """,
    unsafe_allow_html=True
)
st.write('#### Analyze data on countries, cities, and universities referenced in the papers.')
st.markdown("***")

st.write('### Country analysis')


bar_country()
st.markdown("***")

st.write('### City analysis')
bar_city()
st.markdown("***")

st.write('### College analysis')
bar_college()
st.markdown("***")









