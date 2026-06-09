from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Response
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import auth
import models, schemas

router = APIRouter()

@router.get("/", response_model=List[schemas.Branch])
def read_branches(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Branch).offset(skip).limit(limit).all()

@router.post("/", response_model=schemas.Branch)
def create_branch(branch: schemas.BranchCreate, db: Session = Depends(get_db), current_user: models.AdminUser = Depends(auth.get_current_user)):
    db_branch = models.Branch(**branch.model_dump())
    db.add(db_branch)
    db.commit()
    db.refresh(db_branch)
    return db_branch

@router.put("/{branch_id}", response_model=schemas.Branch)
def update_branch(branch_id: int, branch: schemas.BranchCreate, db: Session = Depends(get_db), current_user: models.AdminUser = Depends(auth.get_current_user)):
    db_branch = db.query(models.Branch).filter(models.Branch.id == branch_id).first()
    if not db_branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    for key, value in branch.model_dump().items():
        setattr(db_branch, key, value)
    db.commit()
    db.refresh(db_branch)
    return db_branch

@router.delete("/{branch_id}")
def delete_branch(branch_id: int, db: Session = Depends(get_db), current_user: models.AdminUser = Depends(auth.get_current_user)):
    db_branch = db.query(models.Branch).filter(models.Branch.id == branch_id).first()
    if not db_branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    db.delete(db_branch)
    db.commit()
    return {"ok": True}

@router.post("/{branch_id}/image")
def upload_image(branch_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    db_branch = db.query(models.Branch).filter(models.Branch.id == branch_id).first()
    if not db_branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    contents = file.file.read()
    db_branch.image_blob = contents
    db.commit()
    return {"filename": file.filename}

@router.get("/{branch_id}/image")
def get_image(branch_id: int, db: Session = Depends(get_db)):
    db_branch = db.query(models.Branch).filter(models.Branch.id == branch_id).first()
    if not db_branch or not db_branch.image_blob:
        raise HTTPException(status_code=404, detail="Image not found")
    return Response(content=db_branch.image_blob, media_type="image/jpeg")
