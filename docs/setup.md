# CareLens AI Setup & Quickstart Guide (Windows PowerShell)

Developer: Varun Yadav T  
Repository: `https://github.com/tvarunyadav/carelens-ai-project.git`  
Local Path: `D:\carelens-ai project`

---

## 1. Prerequisites

- **Python**: 3.11+ (verify with `python --version`)
- **Node.js**: v18+ / v20+ (verify with `node --version`)
- **Docker Desktop** (optional for containerized execution)

---

## 2. Backend Setup & Run (FastAPI)

Open a PowerShell terminal in `D:\carelens-ai project`:

```powershell
# Navigate to backend directory
cd D:\carelens-ai project\backend

# Create virtual environment if not already created
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install backend dependencies
pip install -r requirements.txt

# Start FastAPI server on localhost:8000
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The server will start at `http://127.0.0.1:8000`.
- Health Endpoint: `http://127.0.0.1:8000/health`
- Interactive OpenAPI Docs: `http://127.0.0.1:8000/docs`

---

## 3. Frontend Setup & Run (React 19 + Vite)

Open a second PowerShell terminal in `D:\carelens-ai project`:

```powershell
# Navigate to frontend directory
cd D:\carelens-ai project\frontend

# Install dependencies
npm install

# Start Vite dev server on localhost:5173
npm run dev
```

Open your browser to `http://localhost:5173` to test the CareLens AI Setup Screen.

---

## 4. Run Automated Tests & Builds

### Backend Pytest Verification:

```powershell
cd D:\carelens-ai project\backend
.\venv\Scripts\Activate.ps1
pytest -v
```

### Frontend Typecheck & Production Build Verification:

```powershell
cd D:\carelens-ai project\frontend
npm run build
```

---

## 5. Containerized Execution (Docker)

To build and run the backend Docker container:

```powershell
cd D:\carelens-ai project\backend

# Build backend Docker image
docker build -t carelens-backend .

# Run container exposing port 8000
docker run -p 8000:8000 --env-file .env.example carelens-backend
```
