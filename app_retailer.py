import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os


def show_retailer_dashboard():
    st.title("📦 Return Logs")

    # Credit Multiplier
    st.markdown("---")
    st.subheader("⚙️ Credit Multiplier")
    if "credit_multiplier" not in st.session_state:
        st.session_state.credit_multiplier = 0.5

    multiplier = st.number_input(
        "Set the multiplier for GreenPoints calculation:",
        min_value=0.0,
        value=st.session_state.credit_multiplier,
        step=0.1,
        format="%.2f"
    )

    if st.button("💾 Update Multiplier"):
        st.session_state.credit_multiplier = multiplier
        st.success(f"Multiplier updated to {multiplier:.2f}")

    # Load return log
    if os.path.exists("return_logs.csv") and os.path.getsize("return_logs.csv") > 0:
        try:
            data = pd.read_csv("return_logs.csv", parse_dates=["Time"])
        except Exception as e:
            st.error(f"Error reading return_logs.csv: {e}")
            return
    else:
        st.info("No returns have been submitted yet.")
        return

    # Recalculate GreenPoints in case multiplier has changed
    if "Weight" in data.columns:
        data["GreenPoints"] = data["Weight"] * st.session_state.credit_multiplier
        # Save updated values back to CSV
        data.to_csv("return_logs.csv", index=False)

    # Show data
    st.subheader("📋 Return Records with GreenPoints")
    st.dataframe(data)

    st.markdown("---")
    st.subheader("📊 Action Distribution")

    if not data.empty:
        pie = px.pie(data, names="action", title="Distribution of Actions")
        st.plotly_chart(pie)

    st.markdown("---")
    st.subheader("🧾 Download Report")
    st.download_button("Download CSV", data.to_csv(index=False), file_name="return_logs.csv", mime="text/csv")

    st.markdown("---")
    if st.button("🚪 Logout Admin"):
        st.session_state.admin_mode = False
        st.success("Logged out successfully. Please reload the page.")
        st.stop()
