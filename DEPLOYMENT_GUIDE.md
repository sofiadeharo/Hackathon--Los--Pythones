# 🚀 Electro-call Deployment Guide

## Quick Deployment Options

Your Electro-call app is ready to deploy! Here are the easiest free hosting options:

---

## Option 1: Deploy to Render (Recommended - FREE)

### Why Render?
- ✅ Free tier available
- ✅ Easy GitHub integration
- ✅ Automatic deployments
- ✅ Built-in HTTPS
- ✅ Environment variables support

### Step-by-Step Deployment:

#### 1. Commit & Push to GitHub
```bash
cd C:\Users\sofia\los-pythones\Hackathon--Los--Pythones
git add .
git commit -m "Prepare for deployment with Render"
git push origin Trained-Models
```

#### 2. Create Render Account
1. Go to: https://render.com/
2. Sign up with your GitHub account (free)
3. Authorize Render to access your repositories

#### 3. Create New Web Service
1. Click **"New +"** → **"Web Service"**
2. Connect your `los-pythones` repository
3. Configure the service:

**Settings:**
- **Name:** `electro-call` (or your choice)
- **Branch:** `Trained-Models`
- **Root Directory:** `Hackathon--Los--Pythones/BackENd`
- **Environment:** `Python 3`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT`
- **Instance Type:** `Free`

#### 4. Add Environment Variables
In the **Environment** section, add:

```
OPENAI_API_KEY = sk-your-actual-key-here
SUPABASE_URL = https://your-project.supabase.co
SUPABASE_KEY = your-supabase-key-here
```

#### 5. Deploy!
- Click **"Create Web Service"**
- Render will automatically build and deploy your app
- Wait 3-5 minutes for the first deploy
- Your app will be live at: `https://electro-call.onrender.com`

---

## Option 2: Deploy to Railway (Also FREE)

### Why Railway?
- ✅ Super simple deployment
- ✅ Free $5/month credits
- ✅ GitHub integration
- ✅ Automatic SSL

### Step-by-Step Deployment:

#### 1. Push to GitHub (if not done)
```bash
git add .
git commit -m "Ready for Railway deployment"
git push origin Trained-Models
```

#### 2. Deploy on Railway
1. Go to: https://railway.app/
2. Click **"Start a New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your `los-pythones` repository
5. Select the `Trained-Models` branch

#### 3. Configure Environment Variables
1. Go to your project → **Variables** tab
2. Add:
```
OPENAI_API_KEY=sk-your-key-here
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-key
PORT=8000
```

#### 4. Configure Settings
Railway auto-detects Python apps, but verify:
- **Start Command:** `cd BackENd && gunicorn app:app`
- **Python Version:** 3.7+

#### 5. Deploy!
- Railway automatically deploys your app
- Get your live URL from the **Settings** tab
- Your app will be at: `https://your-app.railway.app`

---

## Option 3: Deploy to Heroku

### Step-by-Step:

#### 1. Install Heroku CLI
Download from: https://devcenter.heroku.com/articles/heroku-cli

#### 2. Login to Heroku
```bash
heroku login
```

#### 3. Create Heroku App
```bash
cd C:\Users\sofia\los-pythones\Hackathon--Los--Pythones
heroku create electro-call-app
```

#### 4. Set Environment Variables
```bash
heroku config:set OPENAI_API_KEY="sk-your-key-here"
heroku config:set SUPABASE_URL="https://your-project.supabase.co"
heroku config:set SUPABASE_KEY="your-supabase-key"
```

#### 5. Deploy
```bash
git push heroku Trained-Models:main
```

Your app will be live at: `https://electro-call-app.herokuapp.com`

---

## Option 4: Deploy to Vercel (Frontend + Serverless API)

### Step-by-Step:

#### 1. Install Vercel CLI
```bash
npm install -g vercel
```

#### 2. Deploy
```bash
cd C:\Users\sofia\los-pythones\Hackathon--Los--Pythones
vercel
```

Follow the prompts:
- **Set up and deploy:** Yes
- **Scope:** Your account
- **Link to existing project:** No
- **Project name:** electro-call
- **Directory:** `./`

#### 3. Configure Environment Variables
```bash
vercel env add OPENAI_API_KEY
vercel env add SUPABASE_URL
vercel env add SUPABASE_KEY
```

Your app will be live at: `https://electro-call.vercel.app`

---

## 📋 Pre-Deployment Checklist

Before deploying, ensure:

- [x] ✅ `requirements.txt` includes all dependencies
- [x] ✅ `Procfile` is created for web process
- [x] ✅ `runtime.txt` specifies Python version
- [x] ✅ Environment variables are documented
- [x] ✅ Code is committed to Git
- [x] ✅ GitHub repository is up to date
- [ ] ⚠️ OpenAI API key is obtained
- [ ] ⚠️ Supabase database is set up (optional)

---

## 🔐 Security Checklist

Before going live:

1. **Environment Variables:**
   - ✅ Never commit API keys to Git
   - ✅ Use platform environment variable settings
   - ✅ Check `.gitignore` includes `.env`

2. **API Keys:**
   - ✅ OpenAI API key is valid
   - ✅ Supabase keys are anon/public keys (not service keys)
   - ✅ Set usage limits on OpenAI dashboard

3. **CORS Configuration:**
   - ✅ Update CORS settings if needed for production domain

---

## 🛠️ Post-Deployment Configuration

### Update Frontend API URL

If deploying backend separately, update `frontend/app.js`:

```javascript
// Change from:
const API_BASE_URL = 'http://localhost:8000/api';

// To:
const API_BASE_URL = 'https://your-deployed-backend.com/api';
```

### Test Your Deployment

1. **Visit your deployed URL**
2. **Check the dashboard loads**
3. **Test network load graph**
4. **Try creating a new patch**
5. **Test the AI chatbot** (🤖 button)
6. **Click "Optimize Schedule"**

---

## 🔄 Continuous Deployment

### Automatic Deployments on Git Push

**Render & Railway:**
- Automatically redeploy when you push to GitHub
- No additional configuration needed!

**To Update Your App:**
```bash
# Make your changes
git add .
git commit -m "Update feature X"
git push origin Trained-Models

# Render/Railway will auto-deploy in 2-3 minutes
```

---

## 📊 Monitoring & Logs

### Render:
- View logs: Dashboard → Your Service → Logs tab
- Monitor health: Built-in health checks

### Railway:
- View logs: Project → Deployments → Click deployment
- Real-time logging available

### Heroku:
```bash
heroku logs --tail
```

---

## 💰 Cost Estimates

### Free Tier Limits:

**Render (Free):**
- 750 hours/month
- Sleeps after 15 min inactivity
- Wakes on request (~30s)

**Railway (Free):**
- $5 credit/month
- ~500 hours
- No sleep mode

**Heroku (Free tier discontinued, paid only):**
- Hobby plan: $7/month

**Recommendation:** Start with **Render** or **Railway** (both free!)

---

## 🚨 Troubleshooting

### "Application Error" on Deployed Site
→ Check logs for errors
→ Verify all environment variables are set
→ Ensure `requirements.txt` has all dependencies

### "Module Not Found" Error
→ Add missing package to `requirements.txt`
→ Redeploy

### Chatbot Not Working
→ Verify `OPENAI_API_KEY` is set in environment variables
→ Check API key has credits

### Database Connection Failed
→ Verify `SUPABASE_URL` and `SUPABASE_KEY` are correct
→ App will fallback to sample data if Supabase unavailable

### App is Slow
→ Free tiers may have cold starts
→ First request after sleep takes ~30s
→ Consider upgrading to paid tier for always-on

---

## 🎉 Success!

Once deployed, share your app:
- **Live URL:** `https://your-app.onrender.com`
- **GitHub Repo:** https://github.com/yourusername/los-pythones
- **Documentation:** Include in README.md

---

## 📚 Additional Resources

- **Render Docs:** https://render.com/docs
- **Railway Docs:** https://docs.railway.app/
- **Flask Production Best Practices:** https://flask.palletsprojects.com/en/2.3.x/deploying/
- **Gunicorn Configuration:** https://docs.gunicorn.org/

---

## 🔧 Advanced: Custom Domain

### On Render:
1. Go to Settings → Custom Domain
2. Add your domain (e.g., `electro-call.yourdomain.com`)
3. Update DNS records as instructed
4. SSL certificate automatically provisioned

### On Railway:
1. Settings → Domains
2. Add custom domain
3. Update DNS CNAME record
4. Automatic SSL

---

**🚀 You're ready to deploy! Choose Render or Railway for the easiest free deployment.**

*Los Pythones Team* 🐍⚡

