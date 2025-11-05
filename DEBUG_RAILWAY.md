# Railway 502 Error - Debugging Steps

## Step 1: Check Railway Logs (CRITICAL)

The 502 error means your app is crashing. We need to see the actual error:

1. Go to Railway Dashboard → Your Project
2. Click on "Deployments" tab
3. Click on the **latest deployment** (the one that's failing)
4. Scroll down to see the **Logs** section
5. Look for errors like:
   - `ImportError`
   - `ModuleNotFoundError`
   - `OperationalError` (database connection)
   - `django.core.exceptions.ImproperlyConfigured`
   - Any Python traceback

**Copy and share the error logs** - This is the most important step!

## Step 2: Fix CORS_ALLOWED_ORIGINS (Remove trailing slash)

In Railway Variables:
- ❌ Current: `CORS_ALLOWED_ORIGINS="https://anime-store-frontend-mdka.vercel.app/"`
- ✅ Change to: `CORS_ALLOWED_ORIGINS="https://anime-store-frontend-mdka.vercel.app"`

## Step 3: Verify Database Connection

Your Supabase connection might be failing. Check:

1. **Connection Pooling**: You're using `pooler.supabase.com` with port `6543` - this is correct for transaction pooling
2. **SSL Mode**: Should be `require` (already set in code)
3. **Credentials**: Verify they're correct in Railway

## Step 4: Check if Migrations Run

Railway might be failing during migrations. Check logs for:
- `Applying migrations...`
- `django.db.utils.OperationalError`
- `relation "users_user" does not exist`

## Step 5: Test Database Connection Locally

If possible, test the connection with these credentials:
```python
import psycopg2
conn = psycopg2.connect(
    host="aws-1-eu-north-1.pooler.supabase.com",
    port=6543,
    database="postgres",
    user="postgres.ugkjxmjrnhjcfhkwomiz",
    password="ABDelaz@20251",
    sslmode="require"
)
```

## Common Issues:

### Issue 1: Database Connection Timeout
- Check if Supabase allows connections from Railway IPs
- Try using direct connection instead of pooler

### Issue 2: Missing Static Files
- Railway should run `collectstatic` automatically
- Check if `whitenoise` is configured correctly

### Issue 3: Port Binding
- Gunicorn should use `$PORT` environment variable
- Railway sets this automatically

## What to Share:

1. **Full error logs** from Railway (most important!)
2. The exact error message
3. Any traceback/stack trace

Without seeing the actual logs, we're guessing. The logs will tell us exactly what's failing.

