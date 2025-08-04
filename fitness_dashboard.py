
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

# ====== STREAMLIT CONFIG ======
st.set_page_config(page_title="Chillin’ with Chino – Fitness Tracker", layout="wide")
st.sidebar.image("chillin_with_chino_logo.png", use_container_width=True)
st.sidebar.markdown("<h2 style='color:gold;'>Chillin’ with Chino</h2>", unsafe_allow_html=True)

# ====== PROFILE & GOALS ======
st.sidebar.header("Profile & Goals")
start_weight = st.sidebar.number_input("Starting Weight (lbs)", min_value=50.0, max_value=600.0, step=0.1, value=max(float(profile_data.get('start_weight', 50.0)), 50.0))
current_weight = st.sidebar.number_input("Current Weight (lbs)", min_value=50.0, max_value=600.0, step=0.1, value=max(float(profile_data.get('current_weight', 50.0)), 50.0))
goal_weight = st.sidebar.number_input("Goal Weight (lbs)", min_value=50.0, max_value=600.0, step=0.1, value=max(float(profile_data.get('goal_weight', 50.0)), 50.0))
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

# ====== API CALLS ======
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

# ====== BACKUPS ======
debug_mode = st.sidebar.checkbox("Enable Debug Mode", value=False)

def cleanup_old_backups():
    files = sorted([os.path.join(BACKUP_DIR, f) for f in os.listdir(BACKUP_DIR)], key=os.path.getmtime, reverse=True)
    for old_file in files[BACKUP_LIMIT:]:
        os.remove(old_file)

if st.sidebar.button("Download All Data"):
    mem_zip = io.BytesIO()
    with zipfile.ZipFile(mem_zip, 'w') as zf:
        zf.write(PROFILE_FILE, arcname="profile.csv")
        zf.write(WEIGHT_LOG, arcname="weight_log.csv")
        zf.write(WORKOUT_LOG, arcname="workout_log.csv")
        if "meal_plan" in st.session_state:
            zf.writestr("meal_plan.json", json.dumps(st.session_state.meal_plan, indent=2))
    mem_zip.seek(0)
    today = datetime.now().strftime("%Y-%m-%d")
    st.sidebar.download_button("Download Backup ZIP", mem_zip, file_name=f"fitness_backup_{today}.zip")

uploaded_backup = st.sidebar.file_uploader("Restore From Backup (ZIP)", type="zip")
if uploaded_backup:
    # Auto-backup current data
    auto_backup_name = f"auto_backup_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.zip"
    auto_backup_path = os.path.join(BACKUP_DIR, auto_backup_name)
    with zipfile.ZipFile(auto_backup_path, 'w') as zf:
        zf.write(PROFILE_FILE, arcname="profile.csv")
        zf.write(WEIGHT_LOG, arcname="weight_log.csv")
        zf.write(WORKOUT_LOG, arcname="workout_log.csv")
        if "meal_plan" in st.session_state:
            zf.writestr("meal_plan.json", json.dumps(st.session_state.meal_plan, indent=2))
    cleanup_old_backups()
    with zipfile.ZipFile(uploaded_backup, 'r') as zf:
        zf.extractall(LOG_DIR)
    st.success(f"Data restored successfully! Auto-backup saved as {auto_backup_name}. Please refresh the app.")

st.sidebar.subheader("Previous Backups")
backup_files = sorted(os.listdir(BACKUP_DIR), key=lambda x: os.path.getmtime(os.path.join(BACKUP_DIR, x)), reverse=True)
if backup_files:
    selected_backup = st.sidebar.selectbox("Select a backup to download", backup_files)
    if selected_backup:
        with open(os.path.join(BACKUP_DIR, selected_backup), "rb") as f:
            st.sidebar.download_button("Download Selected Backup", f, file_name=selected_backup)

# Last backup date
last_backup_date = backup_files[0] if backup_files else "No backups yet"
st.sidebar.markdown(f"**Last Backup:** {last_backup_date}")

# ====== TABS ======
tab1, tab2, tab3, tab4 = st.tabs(["📖 Daily Logs", "⏳ Fasting & Workout", "📊 Progress Charts", "🍽 Meal Planner"])

# ====== TAB 1: Daily Logs ======
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

# ====== TAB 2: Fasting & Workout ======
with tab2:
    st.subheader("Fasting Window Countdown")
    now = datetime.now().time()
    if fasting_start <= now <= fasting_end:
        remaining = datetime.combine(datetime.today(), fasting_end) - datetime.now()
        st.success(f"Eating window is OPEN. Time left: {str(remaining).split('.')[0]}")
    else:
        st.warning(f"Eating window is CLOSED. Opens at {fasting_start.strftime('%I:%M %p')}")

    st.subheader("Workout Timer")
    if "workout_start" not in st.session_state:
        st.session_state.workout_start = None
    if st.button("Start Workout"):
        st.session_state.workout_start = time.time()
    if st.button("Stop Workout"):
        if st.session_state.workout_start:
            duration = (time.time() - st.session_state.workout_start) / 60
            df = pd.read_csv(WORKOUT_LOG)
            df = pd.concat([df, pd.DataFrame([{"Date": today, "Duration": duration}])], ignore_index=True)
            df.to_csv(WORKOUT_LOG, index=False)
            st.success(f"Workout logged: {duration:.1f} minutes")
            st.session_state.workout_start = None
    if st.checkbox("View Workout Logs"):
        st.dataframe(pd.read_csv(WORKOUT_LOG))
    st.download_button("Download Workout Logs", pd.read_csv(WORKOUT_LOG).to_csv(index=False), "workout_logs.csv")

# ====== TAB 3: Progress Charts ======
with tab3:
    st.subheader("Weight Progress")
    if os.path.exists(WEIGHT_LOG):
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
    if os.path.exists(WORKOUT_LOG):
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

# ====== TAB 4: Meal Planner ======
with tab4:
    st.subheader("7-Day Pescatarian Meal Plan (with Eggs/Dairy)")
    if "meal_plan" not in st.session_state or st.button("Regenerate Meal Plan"):
        with st.spinner("Loading Meal Plan..."):
            st.session_state.meal_plan = fetch_meal_plan()
            st.session_state.last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if st.session_state.get("meal_plan"):
        st.caption(f"Last updated: {st.session_state.last_updated}")
        for day, meals in st.session_state.meal_plan.get("week", {}).items():
            st.markdown(f"### {day.capitalize()} - Total Calories: {meals['nutrients']['calories']:.0f}")
            for meal in meals["meals"]:
                details = fetch_meal_details(meal['id'])
                st.markdown(f"**{meal['title']}**")
                if details:
                    st.image(details.get("image", ""), width=150)
                    if details.get("nutrition"):
                        try:
                            nutrients = {n['title']: n['amount'] for n in details['nutrition']['nutrients']}
                            st.markdown(f"Calories: {nutrients.get('Calories', 0):.0f} | Protein: {nutrients.get('Protein', 0):.0f}g | Carbs: {nutrients.get('Carbohydrates', 0):.0f}g | Fat: {nutrients.get('Fat', 0):.0f}g")
                        except:
                            st.markdown("Nutrition details unavailable.")
                else:
                    st.markdown("Nutrition details unavailable.")
            st.markdown("---")
        if st.button("Download Grocery List"):
            grocery_data = fetch_grocery_list(st.session_state.meal_plan)
            if grocery_data:
                ingredients = [item['name'] for aisle in grocery_data['aisles'] for item in aisle['items']]
                grocery_list = "\n".join(ingredients)
                st.download_button("Download Grocery List", grocery_list, "grocery_list.txt")
        if debug_mode:
            st.subheader("Debug Data")
            st.json(st.session_state.meal_plan)
    else:
        st.warning("No meal plan available. Check your API key or try regenerating.")
