# Troubleshooting Guide

## Backend Issues

### 1. Module imports not working
**Problem**: `ImportError: No module named 'services'` or similar

**Solution**:
```powershell
cd backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Database errors
**Problem**: Tables don't exist or database is locked

**Solution**:
```powershell
# Delete the database and restart
cd backend
Remove-Item ai_tutor.db
python app.py
```

### 3. Testing the backend
```powershell
cd backend
python test_api.py
```

This will test:
- Health endpoint
- Authentication (signup/login)
- Module creation and retrieval

### 4. Common Backend Errors

**Error**: `ImportError: cannot import name 'db' from 'app'`
- Fixed: db is now in models.py

**Error**: `500 Internal Server Error when creating module`
- Check backend terminal for actual error
- Module creation now works without files
- Files are optional

**Error**: `CORS errors`
- Flask-CORS is configured to allow all origins in development
- If issues persist, check browser console

## Frontend Issues

### 1. PostCSS configuration error
**Problem**: `module is not defined in ES module scope`

**Solution**: Already fixed - postcss.config.js uses ES modules now

### 2. Module creation fails
**Problem**: "Error creating module" alert

**Debugging steps**:
1. Open browser Developer Tools (F12)
2. Go to Console tab
3. Try creating a module
4. Look for the actual error message
5. Check Network tab for the failed request

**Common causes**:
- Backend not running (start with `python app.py` in backend folder)
- Not logged in (token expired - logout and login again)
- File too large (max 500MB)
- Check backend terminal for errors

### 3. Axios/API errors

Check if backend is running:
```powershell
# In browser or PowerShell
curl http://localhost:5000/api/health
```

Should return: `{"status":"ok"}`

## Step-by-Step Debugging

### Backend
1. Activate virtual environment:
```powershell
cd backend
.\venv\Scripts\Activate.ps1
```

2. Check Python version (should be 3.12+):
```powershell
python --version
```

3. Install/update dependencies:
```powershell
pip install -r requirements.txt
```

4. Run the app:
```powershell
python app.py
```

5. Check for errors in terminal
6. Test with: `python test_api.py`

### Frontend
1. Install dependencies:
```powershell
cd frontend
npm install
```

2. Start dev server:
```powershell
npm run dev
```

3. Open browser to `http://localhost:3000`
4. Open Developer Tools (F12)
5. Check Console for errors
6. Check Network tab for failed requests

## Testing Flow

1. **Create Account**: 
   - Go to http://localhost:3000
   - Click "Sign Up"
   - Enter username and password
   - Should redirect to dashboard

2. **Create Module**:
   - Click "View Modules" or navigate to Modules page
   - Click "Create Module"
   - Enter name (e.g., "Test Module")
   - Optional: Upload files
   - Click "Create"
   - Should see module in grid

3. **Check Backend Terminal**:
   - Should see POST request to /api/modules/
   - Status 201 means success
   - Any 500 error will show traceback

## Known Issues & Solutions

### Issue: Module creation returns 500 error
**Cause**: LLM or vector service failing
**Solution**: Module now creates successfully without processing. Processing can be triggered separately.

### Issue: "Module not found" when clicking module
**Cause**: No lessons generated yet
**Solution**: 
- Modules without files get a demo lesson automatically
- Modules with files need processing (endpoint: `/api/modules/<id>/process`)

### Issue: Frontend shows "Error creating module"
**Solution**: 
1. Check browser console for actual error
2. Check backend terminal for traceback
3. Ensure backend is running on port 5000
4. Check you're logged in (token in localStorage)

### Issue: Gemini API errors
**Cause**: Rate limits or API key issues
**Solution**: 
- API key is in backend/.env
- LLM service has fallback logic
- Check `backend/services/llm_service.py` for errors

## Quick Reset

If everything is broken:

```powershell
# Backend
cd backend
Remove-Item ai_tutor.db -ErrorAction SilentlyContinue
Remove-Item -Recurse uploads -ErrorAction SilentlyContinue
Remove-Item -Recurse chroma_db -ErrorAction SilentlyContinue
python app.py

# Frontend (new terminal)
cd frontend
npm run dev
```

## Useful Commands

```powershell
# Check if backend is running
curl http://localhost:5000/api/health

# Check if frontend is running  
curl http://localhost:3000

# View backend logs
cd backend
python app.py

# View browser console
F12 in browser -> Console tab

# Kill process on port (if port is busy)
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

## Success Indicators

✅ Backend running: Terminal shows "Running on http://127.0.0.1:5000"
✅ Frontend running: Terminal shows "Local: http://localhost:3000"
✅ Health check: `curl http://localhost:5000/api/health` returns `{"status":"ok"}`
✅ Can create account and login
✅ Can create module (with or without files)
✅ Dashboard shows data

## Getting Help

If still having issues:
1. Check both terminal outputs (backend and frontend)
2. Check browser console (F12)
3. Run `python test_api.py` in backend folder
4. Look for specific error messages
5. Check the error is in backend (Python traceback) or frontend (JS error)
