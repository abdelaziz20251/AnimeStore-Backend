# Railway 502 Error Fix Guide

## Issue
Railway is returning 502 errors, which typically means:
1. The application is crashing on startup
2. The application isn't binding to the correct port
3. Environment variables are misconfigured

## Fix Your Railway Environment Variables

### Current Issues in Your Variables:

1. **ALLOWED_HOSTS** - Has full URL with protocol (WRONG)
   - ❌ Current: `ALLOWED_HOSTS="https://animestore-backend-production.up.railway.app"`
   - ✅ Should be: `ALLOWED_HOSTS="animestore-backend-production.up.railway.app"`

2. **CORS_ALLOWED_ORIGINS** - Has trailing slash (WRONG)
   - ❌ Current: `CORS_ALLOWED_ORIGINS="https://anime-store-frontend-mdka.vercel.app/"`
   - ✅ Should be: `CORS_ALLOWED_ORIGINS="https://anime-store-frontend-mdka.vercel.app"`

### Corrected Railway Environment Variables:

Update these in Railway Dashboard → Your Project → Variables:

```
ALLOWED_HOSTS=animestore-backend-production.up.railway.app
CSRF_TRUSTED_ORIGINS=https://animestore-backend-production.up.railway.app
CORS_ALLOWED_ORIGINS=https://anime-store-frontend-mdka.vercel.app
DB_CONN_MAX_AGE=60
DB_HOST=aws-1-eu-north-1.pooler.supabase.com
DB_NAME=postgres
DB_PASSWORD=ABDelaz@20251
DB_PORT=6543
DB_USER=postgres.ugkjxmjrnhjcfhkwomiz
DEBUG=False
POOL_MODE=transaction
SECRET_KEY=django-insecure-j5t&qj1$!n-(70%gusg4yartrvk=x!gt$bi&)=ynk=js-mrn9s
```

### Changes Made:
- ✅ Removed `https://` from ALLOWED_HOSTS
- ✅ Removed trailing `/` from CORS_ALLOWED_ORIGINS
- ✅ Removed unnecessary variables (PIP_*, PYTHON_* are handled by Railway)

## Check Railway Logs

1. Go to Railway Dashboard → Your Project
2. Click on "Deployments" tab
3. Click on the latest deployment
4. Check the "Logs" section

Look for errors like:
- Database connection errors
- Import errors
- Port binding issues
- Missing environment variables

## Common Issues & Solutions

### Issue 1: Application Not Starting
- Check if gunicorn is installed: `pip install gunicorn`
- Verify Procfile exists: `web: gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --access-logfile - --error-logfile -`

### Issue 2: Database Connection Failed
- Verify DB credentials are correct
- Check if Supabase allows connections from Railway's IP
- Verify SSL mode is enabled (should be in code)

### Issue 3: Port Binding
- Railway automatically sets `$PORT` environment variable
- Gunicorn should bind to `0.0.0.0:$PORT`
- Don't hardcode port numbers

## After Fixing Variables:

1. Save the variables in Railway
2. Railway will automatically redeploy
3. Check the logs to see if it starts successfully
4. Test the health endpoint: `https://animestore-backend-production.up.railway.app/health/`

## Verification Steps:

1. ✅ Health check: `https://animestore-backend-production.up.railway.app/health/`
2. ✅ Root endpoint: `https://animestore-backend-production.up.railway.app/`
3. ✅ API docs: `https://animestore-backend-production.up.railway.app/api/schema/swagger-ui/`

