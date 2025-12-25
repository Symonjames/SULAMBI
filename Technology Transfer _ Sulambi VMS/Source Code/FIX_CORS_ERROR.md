# Fix CORS and 404 Errors

## Problem
When trying to login, you see:
- CORS error: `Access to XMLHttpRequest at 'https://sulambi-backend.onrender.com/auth/login' from origin 'https://sulambi-frontend.onrender.com' has been blocked by CORS policy`
- The request goes to `/auth/login` instead of `/api/auth/login`

## Root Cause
The `VITE_API_URI` environment variable is either:
1. Not set in Render
2. Set incorrectly (missing `/api` suffix)

## Solution

### Step 1: Set VITE_API_URI in Render

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click on your **`sulambi-frontend`** service
3. Go to **Environment** tab
4. Add or update the environment variable:
   - **Key**: `VITE_API_URI`
   - **Value**: `https://sulambi-backend.onrender.com/api`
   - ⚠️ **IMPORTANT**: The value MUST end with `/api`

5. Click **Save Changes**

### Step 2: Rebuild Frontend

**⚠️ CRITICAL**: Since Vite embeds environment variables at build time, you MUST rebuild the frontend after setting/changing `VITE_API_URI`.

1. Go to your **`sulambi-frontend`** service in Render
2. Click **Manual Deploy** → **Deploy latest commit**
3. Wait for the build to complete

### Step 3: Verify

After rebuild, the frontend should now:
- Call `/api/auth/login` correctly
- Not show CORS errors
- Allow login to work properly

## How It Works

- Backend routes are registered with `/api` prefix: `/api/auth/login`
- Frontend uses `VITE_API_URI` as base URL
- When frontend calls `login()`, it uses: `VITE_API_URI + /auth/login`
- So `VITE_API_URI` must be: `https://sulambi-backend.onrender.com/api`

## Test Login Credentials

After fixing, use these credentials:

- **Admin**:
  - Username: `Admin`
  - Password: `sulambi@2024`

- **Officer**:
  - Username: `Sulambi-Officer`
  - Password: `password@2024`

