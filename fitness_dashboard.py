
import streamlit as st
import pandas as pd
import os, time, requests, zipfile, io, json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_KEY = os.getenv("SPOONACULAR_API_KEY") or st.secrets.get("SPOONACULAR_API_KEY")

# File paths
LOG_DIR = "logs"
PROFILE_FILE = os.path.join(LOG_DIR, "profile.csv")
WEIGHT_LOG = os.path.join(LOG_DIR, "weight_log.csv")
WORKOUT_LOG = os.path.join(LOG_DIR, "workout_log.csv")
os.makedirs(LOG_DIR, exist_ok=True)

# Auto-create files if missing
if not os.path.exists(PROFILE_FILE):
    pd.DataFrame(columns=["field", "value"]).to_csv(PROFILE_FILE, index=False)
if not os.path.exists(WEIGHT_LOG):
    pd.DataFrame(columns=["Date", "Weight", "Blood Pressure", "Meal Notes"]).to_csv(WEIGHT_LOG, index=False)
if not os.path.exists(WORKOUT_LOG):
    pd.DataFrame(columns=["Date", "Duration"]).to_csv(WORKOUT_LOG, index=False)

# Initialize profile storage
def load_profile():
    if os.path.exists(PROFILE_FILE):
        df = pd.read_csv(PROFILE_FILE)
        return {row['field']: row['value'] for _, row in df.iterrows()}
    return {}

def save_profile(data):
    df = pd.DataFrame([{'field': k, 'value': v} for k, v in data.items()])
    df.to_csv(PROFILE_FILE, index=False)

profile_data = load_profile()

# Branding
st.set_page_config(page_title="Chillin’ with Chino – Fitness Tracker", layout="wide")
st.sidebar.image("chillin_with_chino_logo.png", use_container_width=True)
st.sidebar.markdown("<h2 style='color:gold;'>Chillin’ with Chino</h2>", unsafe_allow_html=True)

# Sidebar Profile
st.sidebar.header("Profile & Goals")
start_weight = st.sidebar.number_input("Starting Weight (lbs)", min_value=50.0, max_value=600.0, step=0.1, value=float(profile_data.get('start_weight', 0)) if profile_data.get('start_weight') else 0.0)
current_weight = st.sidebar.number_input("Current Weight (lbs)", min_value=50.0, max_value=600.0, step=0.1, value=float(profile_data.get('current_weight', 0)) if profile_data.get('current_weight') else 0.0)
goal_weight = st.sidebar.number_input("Goal Weight (lbs)", min_value=50.0, max_value=600.0, step=0.1, value=float(profile_data.get('goal_weight', 0)) if profile_data.get('goal_weight') else 0.0)
profile_data.update({'start_weight': start_weight, 'current_weight': current_weight, 'goal_weight': goal_weight})

# Fasting window (time pickers)
st.sidebar.subheader("Fasting Window")
default_start = datetime.strptime(profile_data.get('fasting_start', '11:00'), "%H:%M").time()
default_end = datetime.strptime(profile_data.get('fasting_end', '19:00'), "%H:%M").time()
fasting_start = st.sidebar.time_input("Start Time", value=default_start)
fasting_end = st.sidebar.time_input("End Time", value=default_end)
profile_data.update({'fasting_start': fasting_start.strftime("%H:%M"), 'fasting_end': fasting_end.strftime("%H:%M")})
save_profile(profile_data)

# Progress
if start_weight and goal_weight:
    progress = ((start_weight - current_weight) / (start_weight - goal_weight)) * 100 if start_weight != goal_weight else 0
    st.sidebar.metric("Progress Toward Goal", f"{progress:.2f}%")
    lbs_left = abs(current_weight - goal_weight)
    color = "green" if lbs_left <= 5 else "white"
    st.sidebar.markdown(f"<p style='color:{color};'>You're {lbs_left:.1f} lbs away from your goal!</p>", unsafe_allow_html=True)

# API calls with caching
@st.cache_data(show_spinner=False)
def fetch_meal_plan():
    if not API_KEY:
        return None
    try:
        url = "https://api.spoonacular.com/mealplanner/generate"
        params = {"apiKey": API_KEY, "timeFrame": "week", "diet": "pescetarian", "targetCalories": 1800}
        resp = requests.get(url, params=params, timeout=10)
        return resp.json() if resp.status_code == 200 else None
    except:
        return None

@st.cache_data(show_spinner=False)
def fetch_meal_details(meal_id):
    try:
        url = f"https://api.spoonacular.com/recipes/{meal_id}/information"
        params = {"apiKey": API_KEY, "includeNutrition": True}
        resp = requests.get(url, params=params, timeout=10)
        return resp.json() if resp.status_code == 200 else None
    except:
        return None

def fetch_grocery_list(meal_plan):
    try:
        url = "https://api.spoonacular.com/mealplanner/shopping-list/compute"
        params = {"apiKey": API_KEY}
        headers = {"Content-Type": "application/json"}
        resp = requests.post(url, params=params, json=meal_plan, headers=headers, timeout=10)
        return resp.json() if resp.status_code == 200 else None
    except:
        return None

# Debug toggle
debug_mode = st.sidebar.checkbox("Enable Debug Mode", value=False)

# --- Download All Data ---
if st.sidebar.button("Download All Data"):
    mem_zip = io.BytesIO()
    with zipfile.ZipFile(mem_zip, 'w') as zf:
        zf.write(PROFILE_FILE, arcname="profile.csv")
        zf.write(WEIGHT_LOG, arcname="weight_log.csv")
        zf.write(WORKOUT_LOG, arcname="workout_log.csv")
        if "meal_plan" in st.session_state:
            meal_json = json.dumps(st.session_state.meal_plan, indent=2)
            zf.writestr("meal_plan.json", meal_json)
    mem_zip.seek(0)
    today = datetime.now().strftime("%Y-%m-%d")
    st.sidebar.download_button("Download Backup ZIP", mem_zip, file_name=f"fitness_backup_{today}.zip")

# (Rest of tabs unchanged: Daily Logs, Fasting, Charts, Meal Planner)
