from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .db.session import engine
from .db.base import Base

# Import routers (we will create them soon)
from .api.endpoints import auth, employees, violations, rules

app = FastAPI(
    title="Travel Gate KSA HR Disciplinary System",
    version="2.0",
    docs_url="/docs"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(employees.router, prefix="/api/employees", tags=["employees"])
app.include_router(violations.router, prefix="/api/violations", tags=["violations"])
app.include_router(rules.router, prefix="/api/rules", tags=["rules"])

@app.get("/")
def root():
    return {"message": "✅ Travel Gate HR System API is Running!"}

# Create database tables on startup
@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)