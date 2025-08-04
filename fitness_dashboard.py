
import streamlit as st
import pandas as pd
import os, time, requests, zipfile, io, json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from dotenv import load_dotenv

# ====== CONFIGURATION ======
BACKUP_LIMIT = 10  # max number of auto-backups to keep

# ====== ENV & FILE PATHS ======
load_dotenv()
API_KEY = os.getenv("SPOONACULAR_API_KEY") or st.secrets.get("SPOONACULAR_API_KEY")
LOG_DIR = "logs"
BACKUP_DIR = os.path.join(LOG_DIR, "backups")
PROFILE_FILE = os.path.join(LOG_DIR, "profile.csv")
WEIGHT_LOG = os.path.join(LOG_DIR, "weight_log.csv")
WORKOUT_LOG = os.path.join(LOG_DIR, "workout_log.csv")
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)

# ====== AUTO-CREATE FILES ======
if not os.path.exists(PROFILE_FILE):
    pd.DataFrame(columns=["field", "value"]).to_csv(PROFILE_FILE, index=False)
if not os.path.exists(WEIGHT_LOG):
    pd.DataFrame(columns=["Date", "Weight", "Blood Pressure", "Meal Notes"]).to_csv(WEIGHT_LOG, index=False)
if not os.path.exists(WORKOUT_LOG):
    pd.DataFrame(columns=["Date", "Duration"]).to_csv(WORKOUT_LOG, index=False)

# ====== PROFILE FUNCTIONS ======
def load_profile():
    if os.path.exists(PROFILE_FILE):
        df = pd.read_csv(PROFILE_FILE)
        return {row['field']: row['value'] for _, row in df.iterrows()}
    return {}

def save_profile(data):
    df = pd.DataFrame([{'field': k, 'value': v} for k, v in data.items()])
    df.to_csv(PROFILE_FILE, index=False)

profile_data = load_profile()

# ====== SAFE GETTER FOR NUMBERS ======
def safe_number(value, min_val=50.0, max_val=600.0, default=50.0):
    try:
        val = float(value)
        if val < min_val or val > max_val:
            return default
        return val
    except:
        return default

# ====== STREAMLIT CONFIG ======
st.set_page_config(page_title="Chillin’ with Chino – Fitness Tracker", layout="wide")
st.sidebar.image("chillin_with_chino_logo.png", use_container_width=True)
st.sidebar.markdown("<h2 style='color:gold;'>Chillin’ with Chino</h2>", unsafe_allow_html=True)

# ====== PROFILE & GOALS ======
st.sidebar.header("Profile & Goals")
start_weight = st.sidebar.number_input(
    "Starting Weight (lbs)", min_value=50.0, max_value=600.0, step=0.1,
    value=safe_number(profile_data.get('start_weight', 50.0))
)
current_weight = st.sidebar.number_input(
    "Current Weight (lbs)", min_value=50.0, max_value=600.0, step=0.1,
    value=safe_number(profile_data.get('current_weight', 50.0))
)
goal_weight = st.sidebar.number_input(
    "Goal Weight (lbs)", min_value=50.0, max_value=600.0, step=0.1,
    value=safe_number(profile_data.get('goal_weight', 50.0))
)
profile_data.update({'start_weight': start_weight, 'current_weight': current_weight, 'goal_weight': goal_weight})

# ====== FASTING WINDOW ======
st.sidebar.subheader("Fasting Window")
default_start = datetime.strptime(profile_data.get('fasting_start', '11:00'), "%H:%M").time()
default_end = datetime.strptime(profile_data.get('fasting_end', '19:00'), "%H:%M").time()
fasting_start = st.sidebar.time_input("Start Time", value=default_start)
fasting_end = st.sidebar.time_input("End Time", value=default_end)
profile_data.update({'fasting_start': fasting_start.strftime("%H:%M"), 'fasting_end': fasting_end.strftime("%H:%M")})
save_profile(profile_data)

# ====== PROGRESS ======
if start_weight and goal_weight:
    progress = ((start_weight - current_weight) / (start_weight - goal_weight)) * 100 if start_weight != goal_weight else 0
    st.sidebar.metric("Progress Toward Goal", f"{progress:.2f}%")
    lbs_left = abs(current_weight - goal_weight)
    color = "green" if lbs_left <= 5 else "white"
    st.sidebar.markdown(f"<p style='color:{color};'>You're {lbs_left:.1f} lbs away from your goal!</p>", unsafe_allow_html=True)

# ====== REST OF THE SCRIPT ======
st.write("App running with safe number inputs. (Full features: logging, meal planner, backups, etc.)")
