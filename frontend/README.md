# HR Frontend

React + Vite frontend. Talks to FastAPI backend at `/api` (proxied to `localhost:8000` in dev).

## Run

```bash
cd frontend
npm install
npm run dev
```

Opens at `http://localhost:5173`.

Make sure the backend is running first: `uvicorn app.main:app --reload --port 8000` from `backend/`.
