from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Response
from sqlalchemy.orm import Session
from typing import List
import models, schemas
from database import get_db
import auth

router = APIRouter()

@router.get("/", response_model=List[schemas.License])
def read_licenses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.License).offset(skip).limit(limit).all()

@router.post("/", response_model=schemas.License)
def create_license(license: schemas.LicenseCreate, db: Session = Depends(get_db), current_user: models.AdminUser = Depends(auth.get_current_user)):
    db_license = models.License(**license.model_dump())
    db.add(db_license)
    db.commit()
    db.refresh(db_license)
    return db_license

@router.put("/{license_id}", response_model=schemas.License)
def update_license(license_id: int, license: schemas.LicenseCreate, db: Session = Depends(get_db), current_user: models.AdminUser = Depends(auth.get_current_user)):
    db_license = db.query(models.License).filter(models.License.id == license_id).first()
    if not db_license:
        raise HTTPException(status_code=404, detail="License not found")
    for key, value in license.model_dump().items():
        setattr(db_license, key, value)
    db.commit()
    db.refresh(db_license)
    return db_license

@router.delete("/{license_id}")
def delete_license(license_id: int, db: Session = Depends(get_db), current_user: models.AdminUser = Depends(auth.get_current_user)):
    db_license = db.query(models.License).filter(models.License.id == license_id).first()
    if not db_license:
        raise HTTPException(status_code=404, detail="License not found")
    db.delete(db_license)
    db.commit()
    return {"ok": True}

@router.post("/{license_id}/image")
async def upload_license_image(license_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: models.AdminUser = Depends(auth.get_current_user)):
    db_license = db.query(models.License).filter(models.License.id == license_id).first()
    if not db_license:
        raise HTTPException(status_code=404, detail="License not found")
    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Maximum 5MB.")
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Only images allowed.")
    db_license.image_blob = contents
    db.commit()
    return {"ok": True}

@router.get("/{license_id}/image")
def get_license_image(license_id: int, db: Session = Depends(get_db)):
    db_license = db.query(models.License).filter(models.License.id == license_id).first()
    if not db_license or not db_license.image_blob:
        raise HTTPException(status_code=404, detail="Image not found")
    return Response(content=db_license.image_blob, media_type="image/jpeg")
