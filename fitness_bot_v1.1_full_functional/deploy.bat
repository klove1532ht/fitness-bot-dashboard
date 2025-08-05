@echo off
echo Deploying v1.1...
git add .
git commit -m "Deploying v1.1"
git push
start https://fitness-bot-dashboard.streamlit.app
pause
