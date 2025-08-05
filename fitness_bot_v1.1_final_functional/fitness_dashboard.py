
import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="Fitness Bot", layout="wide")
st.sidebar.title("Fitness Bot v1.1 – Final Functional")

# --- Onboarding Tooltip ---
if 'onboarded' not in st.session_state:
    st.info("Welcome! Edit your weights and timeline in the sidebar to personalize your plan. Explore your Meal Planner, Exercise library, and download weekly reports.")
    st.session_state['onboarded'] = True

# --- LOAD DATA ---
logs_dir = "logs"
weight_log_path = os.path.join(logs_dir, "weight_log.csv")
macros_path = os.path.join(logs_dir, "macros.csv")

def load_csv(path):
    return pd.read_csv(path) if os.path.exists(path) else pd.DataFrame()

weight_df = load_csv(weight_log_path)
macros_df = load_csv(macros_path)

# --- SIDEBAR EDITABLE INPUTS ---
st.sidebar.header("Profile Settings")
starting_weight = st.sidebar.number_input("Starting Weight (lbs)", value=float(weight_df['Starting Weight'].iloc[-1]) if not weight_df.empty else 230.0)
current_weight = st.sidebar.number_input("Current Weight (lbs)", value=float(weight_df['Current Weight'].iloc[-1]) if not weight_df.empty else 228.0)
goal_weight = st.sidebar.number_input("Goal Weight (lbs)", value=float(weight_df['Goal Weight'].iloc[-1]) if not weight_df.empty else 170.0)
timeline_months = st.sidebar.slider("Goal Timeline (months)", 1, 24, 6)
st.sidebar.write(f"Estimated goal date: {(datetime.now() + pd.DateOffset(months=timeline_months)).strftime('%b %d, %Y')}")

# --- TABS ---
tabs = st.tabs(["Dashboard", "Meal Planner", "Progress", "Exercise", "Settings"])

# --- DASHBOARD TAB ---
with tabs[0]:
    st.header("Quick Health Summary")
    st.metric("Starting Weight (lbs)", starting_weight)
    st.metric("Current Weight (lbs)", current_weight)
    st.metric("Goal Weight (lbs)", goal_weight)
    st.subheader("Net Calories Summary")
    st.write("Daily: 0 kcal (to be calculated)")
    st.write("Weekly Average: 0 kcal (to be calculated)")
    st.write("Target: 500-750 kcal deficit for 1–1.5 lbs/week loss")
    st.write(f"Last Backup Created: {datetime.now().strftime('%b %d, %Y')}")
    st.download_button("Download Weekly Summary PDF", data=b"PDF content placeholder", file_name="weekly_summary.pdf")

# --- MEAL PLANNER TAB ---
with tabs[1]:
    st.header("Meal Planner")
    st.write("Auto-generated daily meal plans with search, filters, thumbnails, and history.")

# --- PROGRESS TAB ---
with tabs[2]:
    st.header("Progress Tracking")
    st.write("Weight and body fat trend charts will be displayed here.")

# --- EXERCISE TAB ---
with tabs[3]:
    st.header("Exercise Library & Workout of the Day")
    st.write("Adaptive WOD with calorie burn estimates, search, filters, and instructional videos.")

# --- SETTINGS TAB ---
with tabs[4]:
    st.header("Settings & Backup Management")
    st.write("Restore from weekly backups with confirmation.")
