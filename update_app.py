import backend
import streamlit as st
import pandas as pd
import plotly.express as px


def search(city):
    try:
        lat, lon = backend.lookup_coord(city)
        if lat is None or lon is None:
            st.error("City not found. Please check the city name.")
            return None, None, None
        data = backend.authenticate(lat, lon)
        if data is None:
            return None, None, None
        extracted_data = backend.sort_data(data)
        return extracted_data, lat, lon
    except Exception as e:
        st.error(f"Cannot locate this city. Reason: {e}")
        return None, None, None


def emoji(emoji):
    weather_emoji = {
        'Clouds': ':cloud:',
        'Clear': ':sun_behind_cloud:',
        'Rain': ':rain_cloud:',
        'Snow': ':snowflake:'
    }
    if emoji in weather_emoji:
        return weather_emoji[emoji]
    else:
        return ''


def temp_time_series(df):
    """Container for temperature time series"""
    temp_time_df = pd.DataFrame({'Actual Temp': df['actual_temp'], 'Feels Like': df['feels_like_temp'], 'Timestamp': df['timestamp']})
    fig = px.line(temp_time_df, x='Timestamp', y=['Actual Temp', 'Feels Like'],
                  title='Temperature Time Series',
                  template='plotly_dark',
                  color_discrete_map={'Actual Temp': 'blue', 'Feels Like': 'red'})
    
    fig.update_layout(
        font=dict(family="Arial", size=14),
        xaxis_title="Date & Time",
        yaxis_title="Temperature (°C)",
        legend_title_text='Temperature Types',
        hovermode="x unified"
    )
    
    return fig  # Return the figure object


def weather_pie(df):
    """Container for pie chart of weather conditions"""
    labels = list(set(df['weather_desc']))
    values = [sum([i == j for i in df['weather_desc']]) for j in labels]
    fig = px.pie(values=values, labels=labels, title="Distribution of Weather Types", hover_name=labels, names=labels)
    st.plotly_chart(fig, use_container_width=True)


def min_max(df):
    """Container for minimum and maximum temperatures"""
    fig = px.scatter(title='Minimum and Maximum Temperature')
    fig.add_scatter(x=df['date'].unique(), y=df.groupby('date')['max_temp'].max(), name='Maximum Temperature')
    fig.add_scatter(x=df['date'].unique(), y=df.groupby('date')['min_temp'].min(), name='Minimum Temperature')
    fig.update_yaxes(title="Temperature (°C)")
    st.plotly_chart(fig, use_container_width=True)


def temp_pressure_humidity(df):
    time_pres_df = pd.DataFrame({'Temperature': df['actual_temp'], 'Pressure': df['pressure'], 'Humidity': df['humidity']})
    fig = px.scatter(time_pres_df, x='Temperature', y='Pressure', color='Humidity', title='Temperature and Pressure')
    st.plotly_chart(fig, use_container_width=True)


st.set_page_config(page_title='Suleman Weather App', page_icon=':sunrise_over_mountains:', layout='wide', initial_sidebar_state='expanded')

# Page header
st.title("SkyWatch :sunrise_over_mountains:")
st.text('Get the forecast for your city, plus a 5-day outlook.')
st.divider()

with st.sidebar.container():
    city = st.sidebar.text_input('**Enter City Name** :city_sunrise:', placeholder='Pune').lower()
    button = st.sidebar.button('Search :microscope:')
    units = st.sidebar.radio("##Select temperature units:", ["Celsius", "Fahrenheit", "Kelvin"], label_visibility='collapsed')
    st.sidebar.divider()
    show_map = st.sidebar.checkbox('Show map')

if button or city:
    if not city:
        pass
    result, lat, lon = search(city)
    if result:
        df = pd.DataFrame(result)
        df.rename(columns={0: 'city', 1: 'country', 2: 'date', 3: 'time', 4: 'actual_temp', 5: 'feels_like_temp', 6: 'min_temp', 7: 'max_temp',
                           8: 'pressure', 9: 'sea_level', 10: 'grnd_level', 11: 'humidity', 12: 'weather_desc'}, inplace=True)
        df['timestamp'] = df['date'] + ' ' + df['time']

        if units == 'Celsius':
            df['actual_temp'] -= 273.15
            df['feels_like_temp'] -= 273.15
            df['max_temp'] -= 273.15
            df['min_temp'] -= 273.15
        elif units == 'Fahrenheit':
            df['actual_temp'] = df['actual_temp'] * 9/5 - 459.67
            df['feels_like_temp'] = df['feels_like_temp'] * 9/5 - 459.67
            df['max_temp'] = df['max_temp'] * 9/5 - 459.67
            df['min_temp'] = df['min_temp'] * 9/5 - 459.67

        with st.container():
            st.header(f"{city.capitalize()}, {df['country'].iloc[0]} {emoji(df['weather_desc'].iloc[0])}")
            col1, col2, col3 = st.columns(3)
            with col1:
                col1.metric("Temperature", f"{round(df['actual_temp'].iloc[0], 3)} °C")
                col1.metric("Humidity", f"{df['humidity'].iloc[0]} %")
            with col2:
                col2.metric("Feels Like", f"{round(df['feels_like_temp'].iloc[0], 3)} °C")
                col2.metric("Pressure", f"{df['pressure'].iloc[0]} mbar")
            with col3:
                col3.metric("Status", f"{df['weather_desc'].iloc[0]}")

            with st.container():
                col1, col2 = st.columns((6, 4))
                with col1:
                    col1.plotly_chart(temp_time_series(df), use_container_width=True)
                with col2:
                    weather_pie(df)

                col3, col4 = st.columns((6, 4))
                with col3:
                    min_max(df)
                with col4:
                    temp_pressure_humidity(df)

            if show_map and city:
                st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}), use_container_width=True)

            with st.expander(label="Get the dataset here:"):
                st.table(df)
