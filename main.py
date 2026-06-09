from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from database import engine, Base, get_db, SessionLocal
import models, schemas, auth
from routers import achievements, circulars, teams, cargos, services, licenses, branches

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Canaan CMS Backend API")

# Seed default admin user
@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        admin = db.query(models.AdminUser).filter(models.AdminUser.username == "admin").first()
        if not admin:
            hashed_pw = auth.get_password_hash("admin123")
            new_admin = models.AdminUser(username="admin", hashed_password=hashed_pw)
            db.add(new_admin)
            db.commit()
    finally:
        db.close()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://canaan-portfolio.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/auth/login", response_model=schemas.Token, tags=["Auth"])
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Fallback: Seed admin if startup_event was bypassed by Phusion Passenger
    admin_check = db.query(models.AdminUser).filter(models.AdminUser.username == "admin").first()
    if not admin_check:
        hashed_pw = auth.get_password_hash("admin123")
        new_admin = models.AdminUser(username="admin", hashed_password=hashed_pw)
        db.add(new_admin)
        db.commit()

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
