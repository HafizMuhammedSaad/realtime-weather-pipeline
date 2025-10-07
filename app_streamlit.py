import streamlit as st
import pandas as pd
import sqlite3
import time
import altair as alt

st.set_page_config(page_title="🌦️ Real-Time Weather Dashboard", layout="centered")

st.title("🌤️ Real-Time Weather Data Dashboard")
st.caption("Updated automatically every 60 seconds")

DB_PATH = "weather_data.db"

def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM weather_data ORDER BY timestamp DESC LIMIT 50", conn)
    conn.close()
    return df

def safe_get(row, column):
    """Agar column missing ho to 'N/A' return kare"""
    return row[column] if column in row.index else "N/A"

refresh_interval = 60
placeholder = st.empty()

while True:
    df = load_data()

    with placeholder.container():
        st.subheader("📊 Latest Weather Data")
        st.dataframe(df)

        if not df.empty:
            latest = df.iloc[0]

            st.metric("🌡 Temperature (°C)", safe_get(latest, "temperature"))
            st.metric("💧 Humidity (%)", safe_get(latest, "humidity"))
            st.metric("🌪 Pressure (hPa)", safe_get(latest, "pressure"))
            st.metric("🏙 City", safe_get(latest, "city"))
            st.metric("⏰ Last Updated", safe_get(latest, "timestamp"))

            # 🔥 Analytics Section
            st.subheader("🔥 Analytics")

            # Hottest & Coldest City
            hottest = df.loc[df['temperature'].idxmax()]
            coldest = df.loc[df['temperature'].idxmin()]
            st.write(f"**Hottest City:** {hottest['city']} ({hottest['temperature']}°C)")
            st.write(f"**Coldest City:** {coldest['city']} ({coldest['temperature']}°C)")

            # 🌡 Average Temperature per City
            avg_temp = df.groupby('city')['temperature'].mean().reset_index()
            st.subheader("🌆 Average Temperature per City")
            bar_chart = alt.Chart(avg_temp).mark_bar(color='orange').encode(
                x='city',
                y='temperature',
                tooltip=['city', 'temperature']
            ).properties(width=600)
            st.altair_chart(bar_chart, use_container_width=True)

            # 📈 Temperature Trends Over Time
            st.subheader("📈 Temperature Trends Over Time")
            line_chart = alt.Chart(df).mark_line(point=True, color='skyblue').encode(
                x='timestamp:T',
                y='temperature:Q',
                color='city:N',
                tooltip=['timestamp', 'city', 'temperature']
            ).properties(width=600)
            st.altair_chart(line_chart, use_container_width=True)

            st.info("Dashboard auto-refreshes every 60 seconds.")
        else:
            st.warning("No data available yet. Please wait for updates.")
    
    time.sleep(refresh_interval)
