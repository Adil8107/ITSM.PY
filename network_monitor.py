
import streamlit as st
import sqlite3
import pandas as pd
import speedtest
import datetime
import socket

# ---------------- Database ----------------
conn = sqlite3.connect("network_monitor.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    download REAL,
    upload REAL,
    ping REAL,
    status TEXT
)
""")
conn.commit()

# ---------------- App Config ----------------
st.set_page_config(page_title="Network Monitoring System", layout="wide")
st.title("🌐 Network Monitoring System")

menu = st.sidebar.selectbox("Menu", ["Check Network", "Dashboard"])

# ---------------- Network Check ----------------
if menu == "Check Network":
    st.subheader("📡 Check Internet Status & Speed")

    if st.button("Run Network Test"):
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=5)
            status = "UP"

            st.info("Running Speed Test... Please wait ⏳")
            test = speedtest.Speedtest()
            download = round(test.download() / 10**6, 2)
            upload = round(test.upload() / 10**6, 2)
            ping = round(test.results.ping, 2)

            st.success("Network is UP ✅")
            st.write(f"Download Speed: {download} Mbps")
            st.write(f"Upload Speed: {upload} Mbps")
            st.write(f"Ping: {ping} ms")

        except:
            status = "DOWN"
            download = 0
            upload = 0
            ping = 0
            st.error("Network is DOWN ❌")

        cursor.execute("""
            INSERT INTO logs (date, download, upload, ping, status)
            VALUES (?, ?, ?, ?, ?)
        """, (
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            download,
            upload,
            ping,
            status
        ))
        conn.commit()

# ---------------- Dashboard ----------------
elif menu == "Dashboard":
    st.subheader("📊 Network Performance Dashboard")

    df = pd.read_sql_query("SELECT * FROM logs", conn)

    if not df.empty:

        st.metric("Total Tests Run", len(df))
        st.metric("Average Download Speed", f"{round(df['download'].mean(), 2)} Mbps")
        st.metric("Average Upload Speed", f"{round(df['upload'].mean(), 2)} Mbps")

        downtime_count = len(df[df["status"] == "DOWN"])
        st.metric("Downtime Count", downtime_count)

        st.subheader("📈 Speed History")
        st.line_chart(df[["download", "upload"]])

        st.subheader("📋 All Logs")
        st.dataframe(df)

    else:
        st.info("No data available.")
