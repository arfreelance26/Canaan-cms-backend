from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Response
from sqlalchemy.orm import Session
from typing import List
import models, schemas
from database import get_db
import auth

router = APIRouter()

@router.get("/", response_model=List[schemas.Circular])
def read_circulars(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Circular).offset(skip).limit(limit).all()

@router.post("/", response_model=schemas.Circular)
def create_circular(circular: schemas.CircularCreate, db: Session = Depends(get_db), current_user: models.AdminUser = Depends(auth.get_current_user)):
    db_circular = models.Circular(**circular.model_dump())
    db.add(db_circular)
    db.commit()
    db.refresh(db_circular)
    return db_circular

@router.put("/{circular_id}", response_model=schemas.Circular)
def update_circular(circular_id: int, circular: schemas.CircularCreate, db: Session = Depends(get_db), current_user: models.AdminUser = Depends(auth.get_current_user)):
    db_circular = db.query(models.Circular).filter(models.Circular.id == circular_id).first()
    if not db_circular:
        raise HTTPException(status_code=404, detail="Circular not found")
    for key, value in circular.model_dump().items():
        setattr(db_circular, key, value)
    db.commit()
    db.refresh(db_circular)
    return db_circular

@router.delete("/{circular_id}")
def delete_circular(circular_id: int, db: Session = Depends(get_db), current_user: models.AdminUser = Depends(auth.get_current_user)):
    db_circular = db.query(models.Circular).filter(models.Circular.id == circular_id).first()
    if not db_circular:
        raise HTTPException(status_code=404, detail="Circular not found")
    db.delete(db_circular)
    db.commit()
    return {"ok": True}

@router.post("/{circular_id}/pdf")
async def upload_circular_pdf(circular_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: models.AdminUser = Depends(auth.get_current_user)):
    db_circular = db.query(models.Circular).filter(models.Circular.id == circular_id).first()
    if not db_circular:
        raise HTTPException(status_code=404, detail="Circular not found")
    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Maximum 5MB.")
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF allowed.")
    db_circular.pdf_blob = contents
    db.commit()
    return {"ok": True}

@router.get("/{circular_id}/pdf")
def get_circular_pdf(circular_id: int, db: Session = Depends(get_db)):
    db_circular = db.query(models.Circular).filter(models.Circular.id == circular_id).first()
    if not db_circular or not db_circular.pdf_blob:
        raise HTTPException(status_code=404, detail="PDF not found")
    return Response(content=db_circular.pdf_blob, media_type="application/pdf")
