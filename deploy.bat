
@echo off
echo Deploying Fitness Bot v1.0 Stable to Streamlit Cloud...
git add .
git commit -m "Deploying v1.0 Stable Build"
git push
echo.
echo =====================================================
echo  Deployment complete!
echo  Opening your app in the browser:
echo  https://fitness-bot-dashboard.streamlit.app/
echo =====================================================
start https://fitness-bot-dashboard.streamlit.app/
pause
