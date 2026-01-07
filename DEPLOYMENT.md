# LawAI Deployment Guide

## Architecture
- **Frontend**: React app deployed on Netlify
- **Backend**: FastAPI deployed on Render (or Railway/Heroku)

## Current Deployment Status

### Frontend (Netlify) ✅
- **URL**: https://jolly-taiyaki-40208d.netlify.app
- **Status**: Deployed
- **Auto-deploy**: Enabled (pushes to main branch)

### Backend (Not yet deployed) ⏳
Choose one of the following platforms:

---

## Backend Deployment Options

### Option 1: Render (Recommended - Free tier available)

1. **Sign up**: Go to https://render.com and sign up with GitHub

2. **Create New Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository: `tanaybasak/lawai`
   - Configure:
     - **Name**: lawai-backend
     - **Region**: Choose closest to you
     - **Branch**: main
     - **Root Directory**: backend
     - **Runtime**: Python 3
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3. **Environment Variables** (Add in Render dashboard):
   ```
   OPENAI_API_KEY=your-actual-openai-api-key
   ENVIRONMENT=production
   PYTHON_VERSION=3.11.0
   ```

4. **Deploy**: Click "Create Web Service"

5. **Get Backend URL**: After deployment, copy the URL (e.g., `https://lawai-backend.onrender.com`)

6. **Update Frontend**: 
   - Go to Netlify: https://app.netlify.com/projects/jolly-taiyaki-40208d/settings/env
   - Set `REACT_APP_API_URL` to your Render backend URL
   - Redeploy frontend

---

### Option 2: Railway

1. **Sign up**: https://railway.app
2. **New Project** → Deploy from GitHub repo
3. **Configure**:
   - Root directory: `backend`
   - Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. **Environment Variables**: Add `OPENAI_API_KEY`
5. **Copy the Railway URL** and update Netlify env variable

---

### Option 3: Heroku

1. **Install Heroku CLI**: `brew tap heroku/brew && brew install heroku`
2. **Login**: `heroku login`
3. **Create app**:
   ```bash
   cd backend
   heroku create lawai-backend
   git push heroku main:main
   ```
4. **Set environment variables**:
   ```bash
   heroku config:set OPENAI_API_KEY=your-key
   ```

---

## Important Notes

### Vector Store Data
- Vector stores (FAISS indices) are NOT in the repo (gitignored)
- You need to either:
  1. Build them on the backend server using the scripts
  2. Upload pre-built indices to persistent storage
  3. Rebuild on each deployment (not recommended for production)

### Building Vector Stores on Server

After backend deployment, SSH into your server or use the platform's console:

```bash
cd backend
python scripts/build_ipc_vectorstore.py
```

This will create the necessary FAISS indices.

---

## Testing the Full Stack

1. **Backend Health Check**: Visit `https://your-backend-url.com/`
2. **Frontend**: Visit https://jolly-taiyaki-40208d.netlify.app
3. **Test a query** in the chat interface

---

## Troubleshooting

### Backend Issues
- Check logs in your deployment platform
- Verify `OPENAI_API_KEY` is set correctly
- Ensure CORS includes Netlify URL

### Frontend Issues
- Verify `REACT_APP_API_URL` points to correct backend
- Check browser console for CORS errors
- Redeploy after env variable changes

### CORS Errors
Backend is configured to allow:
- http://localhost:3000 (development)
- https://jolly-taiyaki-40208d.netlify.app (production)

If you change the Netlify URL, update `backend/app/core/config.py`

---

## Cost Estimates

- **Netlify**: Free (up to 100GB bandwidth/month)
- **Render**: Free tier available (sleeps after 15 min inactivity)
- **Railway**: $5/month usage-based
- **Heroku**: $7/month for basic dyno

---

## Next Steps

1. ✅ Frontend deployed on Netlify
2. ⏳ Deploy backend to Render/Railway/Heroku
3. ⏳ Build vector stores on backend
4. ⏳ Update frontend environment variable with backend URL
5. ⏳ Test end-to-end functionality
