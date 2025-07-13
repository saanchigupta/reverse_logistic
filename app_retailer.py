
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

def show_retailer_dashboard():
    st.title("📦 Return Logs")

    # Sample data (replace with database integration)
    data = pd.DataFrame([
        {"User ID": "U001", "Item": "Laptop", "Condition": "Used", "Reason": "Slow", "Action": "Repair", "Points": 80, "Time": datetime.now()},
        {"User ID": "U002", "Item": "Shoes", "Condition": "Like New", "Reason": "Wrong size", "Action": "Reuse", "Points": 20, "Time": datetime.now()},
        {"User ID": "U003", "Item": "Phone", "Condition": "Not Working", "Reason": "Dead", "Action": "Recycle", "Points": 30, "Time": datetime.now()},
    ])

    st.dataframe(data)

    st.markdown("---")
    st.subheader("📊 Action Distribution")

    pie = px.pie(data, names="Action", title="Distribution of Actions")
    st.plotly_chart(pie)

    st.markdown("---")
    st.subheader("🧾 Download Report")
    st.download_button("Download CSV", data.to_csv(index=False), file_name="return_logs.csv", mime="text/csv")
