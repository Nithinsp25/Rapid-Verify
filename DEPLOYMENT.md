# 🚀 Deployment Guide (100% Free)

This guide will help you host **RapidVerify** for free using **Render** (Backend) and **Vercel** (Frontend).

## Prerequisites
1.  **GitHub Account**: You need to push this code to a GitHub repository.
2.  **Render Account**: [Sign up here](https://render.com) (Free).
3.  **Vercel Account**: [Sign up here](https://vercel.com) (Free).

---

## Part 1: Backend (Render)
*Hosts the Python/Flask API*

1.  **Push Code to GitHub**: Ensure your project is in a GitHub repo.
2.  **New Web Service**:
    *   Go to [Render Dashboard](https://dashboard.render.com).
    *   Click **New +** -> **Web Service**.
    *   Connect your GitHub repository.
3.  **Configure Settings**:
    *   **Name**: `rapidverify-api`
    *   **Runtime**: `Python 3`
    *   **Build Command**: `pip install -r requirements.txt`
    *   **Start Command**: `gunicorn api.app:app`
    *   **Instance Type**: Select **Free**.
4.  **Environment Variables** (Scroll down to "Environment"):
    *   Add the keys from your `.env` file:
        *   `GOOGLE_API_KEY`: (Your Gemini Key)
        *   `TELEGRAM_BOT_TOKEN`: (Your Bot Token)
        *   `BLOCKCHAIN_NETWORK`: `polygon_amoy` (or leave empty for demo mode)
5.  **Deploy**: Click **Create Web Service**.
    *   Wait for it to finish.
    *   **Copy the URL** (e.g., `https://rapidverify-api.onrender.com`). You need this for Part 2.

---

## Part 2: Frontend (Vercel)
*Hosts the React/Vite Website*

1.  **New Project**:
    *   Go to [Vercel Dashboard](https://vercel.com/dashboard).
    *   Click **Add New...** -> **Project**.
    *   Import the same GitHub repository.
2.  **Configure Project**:
    *   **Framework Preset**: It should auto-detect `Vite`.
    *   **Root Directory**: Click "Edit" and select `frontend`.
3.  **Environment Variables**:
    *   Click "Environment Variables".
    *   Add: `VITE_API_URL`
    *   Value: The **Render Backend URL** from Part 1 (e.g., `https://rapidverify-api.onrender.com`).
    *   *Note: Do NOT add a trailing slash `/` at the end of the URL.*
4.  **Deploy**: Click **Deploy**.

---

## Part 3: Final Check
1.  Open your new Vercel URL (e.g., `https://rapidverify.vercel.app`).
2.  Go to the **Dashboard** tab.
3.  If you see stats loading, **Success!** 🎉

### Troubleshooting
*   **Backend Sleeping**: On the free tier, Render spins down after inactivity. The first request might take 50 seconds. This is normal for free hosting.
*   **CORS Errors**: If the frontend can't talk to the backend, ensure your Render Backend Environment Variables include:
    *   `ALLOWED_ORIGINS`: `https://your-vercel-app-name.vercel.app` (The URL of your frontend).
