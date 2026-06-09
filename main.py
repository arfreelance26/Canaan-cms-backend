from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from database import engine, Base, get_db, SessionLocal
import models, schemas, auth
from routers import achievements, circulars, teams, cargos, services, licenses, branches

import os
from dotenv import load_dotenv

load_dotenv()

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
IS_PRODUCTION = os.getenv("ENVIRONMENT") == "production"

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Canaan CMS Backend API",
    docs_url=None if IS_PRODUCTION else "/docs",
    redoc_url=None if IS_PRODUCTION else "/redoc",
    openapi_url=None if IS_PRODUCTION else "/openapi.json"
)

# Seed default admin user
@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        if ADMIN_USERNAME and ADMIN_PASSWORD:
            admin = db.query(models.AdminUser).filter(models.AdminUser.username == ADMIN_USERNAME).first()
            if not admin:
                hashed_pw = auth.get_password_hash(ADMIN_PASSWORD)
                new_admin = models.AdminUser(username=ADMIN_USERNAME, hashed_password=hashed_pw)
                db.add(new_admin)
                db.commit()
    finally:
        db.close()

# CORS setup
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000,https://canaan-portfolio.vercel.app").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/auth/login", response_model=schemas.Token, tags=["Auth"])
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Fallback: Seed admin if startup_event was bypassed by Phusion Passenger
    if ADMIN_USERNAME and ADMIN_PASSWORD:
        admin_check = db.query(models.AdminUser).filter(models.AdminUser.username == ADMIN_USERNAME).first()
        if not admin_check:
            try:
                hashed_pw = auth.get_password_hash(ADMIN_PASSWORD)
                new_admin = models.AdminUser(username=ADMIN_USERNAME, hashed_password=hashed_pw)
                db.add(new_admin)
                db.commit()
            except Exception as e:
                import traceback
                raise HTTPException(status_code=400, detail=f"Database or Hashing Error: {str(e)} | Trace: {traceback.format_exc()}")

    user = db.query(models.AdminUser).filter(models.AdminUser.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

app.include_router(achievements.router, prefix="/api/achievements", tags=["Achievements"])
app.include_router(circulars.router, prefix="/api/circulars", tags=["Circulars"])
app.include_router(teams.router, prefix="/api/teams", tags=["Teams"])
app.include_router(cargos.router, prefix="/api/cargos", tags=["Cargos"])
app.include_router(services.router, prefix="/api/services", tags=["Services"])
app.include_router(licenses.router, prefix="/api/licenses", tags=["Licenses"])
app.include_router(branches.router, prefix="/api/branches", tags=["Branches"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the CMS API"}
