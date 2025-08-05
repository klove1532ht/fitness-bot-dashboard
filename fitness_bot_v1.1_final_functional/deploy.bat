@echo off
echo Deploying v1.1 Final Functional...
git add .
git commit -m "Deploying v1.1 Final Functional"
git push
start https://fitness-bot-dashboard.streamlit.app
pause
