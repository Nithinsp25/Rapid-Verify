@echo off
echo ===================================================
echo 🛡️  Starting RapidVerify System
echo ===================================================

echo.
echo [1/2] Starting Backend Server (Flask)...
start "RapidVerify Backend" cmd /k "python api/app.py"

echo.
echo [2/2] Starting Frontend (Vite)...
cd frontend
start "RapidVerify Frontend" cmd /k "npm run dev"

echo.
echo ✅ System starting...
echo    - Backend: http://localhost:5000
echo    - Frontend: http://localhost:5173
echo.
echo Press any key to exit this launcher (windows will stay open)
pause
