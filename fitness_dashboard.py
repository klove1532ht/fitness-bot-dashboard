
import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# --- Setup ---
LOG_DIR = "logs"
WEIGHT_LOG = os.path.join(LOG_DIR, "weight_log.csv")
WORKOUT_LOG = os.path.join(LOG_DIR, "workout_log.csv")
os.makedirs(LOG_DIR, exist_ok=True)

# --- Initialize Logs if Missing ---
if not os.path.exists(WEIGHT_LOG):
    pd.DataFrame(columns=["Date", "Weight", "Blood Pressure", "Meal Notes"]).to_csv(WEIGHT_LOG, index=False)
if not os.path.exists(WORKOUT_LOG):
    pd.DataFrame(columns=["Date", "Duration"]).to_csv(WORKOUT_LOG, index=False)

# --- Branding ---
st.set_page_config(page_title="Chillin’ with Chino – Fitness Tracker", layout="wide")
st.sidebar.image("chillin_with_chino_logo.png", use_column_width=True)
st.sidebar.markdown("<h2 style='color:gold;'>Chillin’ with Chino</h2>", unsafe_allow_html=True)

# --- Sidebar: Profile & Goals ---
st.sidebar.header("Profile & Goals")
start_weight = st.sidebar.number_input("Starting Weight (lbs)", min_value=50.0, max_value=600.0, step=0.1)
current_weight = st.sidebar.number_input("Current Weight (lbs)", min_value=50.0, max_value=600.0, step=0.1)
goal_weight = st.sidebar.number_input("Goal Weight (lbs)", min_value=50.0, max_value=600.0, step=0.1)

# Calculate progress
if start_weight and goal_weight:
    progress = ((start_weight - current_weight) / (start_weight - goal_weight)) * 100 if start_weight != goal_weight else 0
    st.sidebar.metric("Progress Toward Goal", f"{progress:.2f}%")

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["📖 Daily Logs", "⏳ Fasting & Workout", "📊 Progress Charts"])

# --- Tab 1: Daily Logs ---
with tab1:
    st.subheader("Daily Logs")
    today = datetime.now().strftime("%Y-%m-%d")
    weight = st.number_input("Today's Weight (lbs)", min_value=50.0, max_value=600.0, step=0.1)
    bp = st.text_input("Blood Pressure (e.g., 120/80)")
    notes = st.text_area("Meal Notes (optional)")

    if st.button("Save Daily Log"):
        df = pd.read_csv(WEIGHT_LOG)
        new_entry = {"Date": today, "Weight": weight, "Blood Pressure": bp, "Meal Notes": notes}
        df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
        df.to_csv(WEIGHT_LOG, index=False)
        st.success("Log saved successfully!")

    if st.checkbox("View Weight Logs"):
        st.dataframe(pd.read_csv(WEIGHT_LOG))

    st.download_button("Download Weight Logs", pd.read_csv(WEIGHT_LOG).to_csv(index=False), "weight_logs.csv")

# --- Tab 2: Fasting & Workout ---
with tab2:
    st.subheader("Fasting Window Countdown")
    eating_start = datetime.now().replace(hour=11, minute=0, second=0, microsecond=0)
    eating_end = datetime.now().replace(hour=19, minute=0, second=0, microsecond=0)
    now = datetime.now()
    if eating_start <= now <= eating_end:
        remaining = eating_end - now
        st.success(f"Eating window is OPEN. Time left: {str(remaining).split('.')[0]}")
    else:
        next_window = (eating_start + timedelta(days=1)) if now > eating_end else eating_start
        until_open = next_window - now
        st.warning(f"Eating window is CLOSED. Opens in: {str(until_open).split('.')[0]}")

    st.subheader("Workout Timer")
    if "workout_start" not in st.session_state:
        st.session_state.workout_start = None

    if st.button("Start Workout"):
        st.session_state.workout_start = time.time()
    if st.button("Stop Workout"):
        if st.session_state.workout_start:
            duration = (time.time() - st.session_state.workout_start) / 60  # minutes
            df = pd.read_csv(WORKOUT_LOG)
            df = pd.concat([df, pd.DataFrame([{"Date": today, "Duration": duration}])], ignore_index=True)
            df.to_csv(WORKOUT_LOG, index=False)
            st.success(f"Workout logged: {duration:.1f} minutes")
            st.session_state.workout_start = None

    if st.checkbox("View Workout Logs"):
        st.dataframe(pd.read_csv(WORKOUT_LOG))

    st.download_button("Download Workout Logs", pd.read_csv(WORKOUT_LOG).to_csv(index=False), "workout_logs.csv")

# --- Tab 3: Progress Charts ---
with tab3:
    st.subheader("Weight Progress")
    weight_df = pd.read_csv(WEIGHT_LOG)
    if not weight_df.empty:
        weight_df["Date"] = pd.to_datetime(weight_df["Date"])
        plt.figure(figsize=(8, 4))
        plt.plot(weight_df["Date"], weight_df["Weight"], marker='o', color='gold')
        plt.title("Weight Over Time")
        plt.xlabel("Date")
        plt.ylabel("Weight (lbs)")
        plt.grid(True)
        st.pyplot(plt)

    st.subheader("Workout Minutes per Week")
    workout_df = pd.read_csv(WORKOUT_LOG)
    if not workout_df.empty:
        workout_df["Date"] = pd.to_datetime(workout_df["Date"])
        workout_df["Week"] = workout_df["Date"].dt.isocalendar().week
        weekly_totals = workout_df.groupby("Week")["Duration"].sum()
        plt.figure(figsize=(8, 4))
        plt.bar(weekly_totals.index, weekly_totals.values, color='gold')
        plt.title("Weekly Workout Minutes")
        plt.xlabel("Week Number")
        plt.ylabel("Minutes")
        st.pyplot(plt)
