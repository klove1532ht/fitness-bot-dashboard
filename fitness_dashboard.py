
import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="Fitness Bot", layout="wide")
st.sidebar.title("Fitness Bot v1.0 – Stable")

# --- LOAD DATA ---
logs_dir = "logs"
weight_log_path = os.path.join(logs_dir, "weight_log.csv")
macros_path = os.path.join(logs_dir, "macros.csv")

def load_csv(path):
    return pd.read_csv(path) if os.path.exists(path) else pd.DataFrame()

weight_df = load_csv(weight_log_path)
macros_df = load_csv(macros_path)

# --- TABS ---
tabs = st.tabs(["Dashboard", "Meal Planner", "Progress", "Exercise", "Settings"])

# --- DASHBOARD TAB ---
with tabs[0]:
    st.header("Quick Health Summary")
    if not weight_df.empty:
        starting_weight = weight_df['Starting Weight'].iloc[-1]
        current_weight = weight_df['Current Weight'].iloc[-1]
        goal_weight = weight_df['Goal Weight'].iloc[-1]
        st.metric("Starting Weight (lbs)", starting_weight)
        st.metric("Current Weight (lbs)", current_weight)
        st.metric("Goal Weight (lbs)", goal_weight)
        st.write(f"Last Updated: {datetime.now().strftime('%b %d, %Y')}")
    if not macros_df.empty:
        st.subheader("Macro Targets (%)")
        st.write(macros_df)
    st.subheader("Net Calories Summary")
    st.write("Net Calories: 0 (Example - will calculate from meal & workout logs)")
    st.write("Target: 500-750 kcal deficit for 1–1.5 lbs/week loss")
    st.button("Refresh Data")
    st.download_button("Download Weekly Summary PDF", data=b"PDF content placeholder", file_name="weekly_summary.pdf")

# --- MEAL PLANNER TAB ---
with tabs[1]:
    st.header("Meal Planner")
    st.write("Meal planner content with exclusions, custom macros, meal history, and PDF export will be here.")

# --- PROGRESS TAB ---
with tabs[2]:
    st.header("Progress Tracking")
    st.write("Color-coded weight & body fat trend charts will be displayed here.")

# --- EXERCISE TAB ---
with tabs[3]:
    st.header("Exercise Library & Workout of the Day")
    st.write("Adaptive difficulty workout library, calorie burn estimates, and logging will be here.")

# --- SETTINGS TAB ---
with tabs[4]:
    st.header("Settings")
    st.write("Adjust macros, exclusions, and units (lbs/kg). Settings persist across sessions.")
