
import streamlit as st
import pandas as pd
import os

# --- CONFIG ---
st.set_page_config(page_title="Fitness Bot", layout="wide")
st.sidebar.title("Fitness Bot v1.0 – Stable")

# --- LOAD PREPOPULATED DATA ---
logs_dir = "logs"
weight_log_path = os.path.join(logs_dir, "weight_log.csv")
macros_path = os.path.join(logs_dir, "macros.csv")

# Ensure files exist
if not os.path.exists(weight_log_path):
    st.error("Weight log not found.")
else:
    weight_df = pd.read_csv(weight_log_path)

if not os.path.exists(macros_path):
    st.error("Macros file not found.")
else:
    macros_df = pd.read_csv(macros_path)

# --- DASHBOARD ---
st.title("Quick Health Summary")

if 'weight_df' in locals():
    starting_weight = weight_df['Starting Weight'].iloc[-1]
    current_weight = weight_df['Current Weight'].iloc[-1]
    goal_weight = weight_df['Goal Weight'].iloc[-1]
    st.metric("Starting Weight (lbs)", starting_weight)
    st.metric("Current Weight (lbs)", current_weight)
    st.metric("Goal Weight (lbs)", goal_weight)

if 'macros_df' in locals():
    st.subheader("Macro Targets (%)")
    st.write(macros_df)
