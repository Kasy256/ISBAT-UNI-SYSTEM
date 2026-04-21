# Render Deployment Setup Guide

## 🔴 Issue: 500 Errors on Backend

Your backend is getting 500 errors because **environment variables are not set on Render**.

## ✅ Fix: Set Environment Variables in Render Dashboard

### Step 1: Go to Render Dashboard

1. Open [https://dashboard.render.com](https://dashboard.render.com)
2. Select your **ISBAT Backend Service**
3. Go to **Settings** tab
4. Scroll to **Environment** section

### Step 2: Add Required Variables

Add these environment variables (**must set**):

| Variable | Example Value | Notes |
|----------|---------------|-------|
| `MONGO_URI` | `mongodb+srv://username:password@cluster0.xyz.mongodb.net/?retryWrites=true` | Your MongoDB Atlas connection string |
| `MONGO_DB_NAME` | `timetable_scheduler` | Database name |
| `JWT_SECRET_KEY` | `your-super-secret-key-here-min-32-chars` | Generate a strong random key |
| `SECRET_KEY` | `your-flask-secret-key-min-32-chars` | Flask secret key |
| `FLASK_DEBUG` | `False` | **Must be False in production** |

### Step 3: Get Your MongoDB Connection String

1. Go to [MongoDB Atlas](https://cloud.mongodb.com)
2. Select your cluster
3. Click **Connect** → **Drivers**
4. Copy the connection string
5. Replace `<username>` and `<password>` with actual values
6. Paste into `MONGO_URI` on Render

### Step 4: Redeploy

After setting variables:
1. Click **Manual Deploy** button on Render
2. Wait for deployment to complete
3. Test the backend: `https://isbat-uni-system.onrender.com/api/subjects/`

## 🔒 Security Notes

- **Never** commit `.env` files to GitHub
- **Always** use strong random keys for `JWT_SECRET_KEY` and `SECRET_KEY`
- Make sure **MongoDB IP whitelist** includes Render's IPs (use `0.0.0.0/0` for testing, restrict later)

## ✔️ Verify Connection

Once deployed, check logs:
1. Go to Render **Logs** tab
2. Look for: `✓ MongoDB connected successfully`
3. If you see errors, check your `MONGO_URI` is correct

## 🆘 Still Getting Errors?

If you still see 500 errors after setting variables:

1. **Check Render Logs** for `MongoDB connection failed` messages
2. **Verify MongoDB Atlas has Render's IP whitelisted** (Network Access → IP Whitelist)
3. **Test MONGO_URI locally** before using on Render
4. **Confirm database exists**: `timetable_scheduler`
