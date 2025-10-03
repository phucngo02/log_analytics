# streamlit_dashboard.py
import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

DB_FILE = "db/security_logs.db"

st.title("Security Log Dashboard (Demo)")

conn = sqlite3.connect(DB_FILE)
df_logs = pd.read_sql_query("SELECT * FROM logs ORDER BY ts DESC LIMIT 1000", conn)
df_alerts = pd.read_sql_query("SELECT * FROM alerts ORDER BY ts DESC LIMIT 100", conn)

st.header("Recent logs")
st.dataframe(df_logs)

st.header("Failed login counts by IP (top 20)")
fails = df_logs[df_logs["status"]=="FAIL"].groupby("ip").size().reset_index(name="fails").sort_values("fails", ascending=False).head(20)
st.dataframe(fails)

fig, ax = plt.subplots()
ax.bar(fails["ip"], fails["fails"])
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
st.pyplot(fig)

st.header("Alerts")
st.dataframe(df_alerts)
