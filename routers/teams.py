from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Response
from sqlalchemy.orm import Session
from typing import List
import models, schemas
from database import get_db
import auth

router = APIRouter()

@router.get("/", response_model=List[schemas.TeamMember])
def read_teams(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.TeamMember).offset(skip).limit(limit).all()

@router.post("/", response_model=schemas.TeamMember)
def create_team(team: schemas.TeamMemberCreate, db: Session = Depends(get_db), current_user: models.AdminUser = Depends(auth.get_current_user)):
    db_team = models.TeamMember(**team.model_dump())
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    return db_team

@router.put("/{team_id}", response_model=schemas.TeamMember)
def update_team(team_id: int, team: schemas.TeamMemberCreate, db: Session = Depends(get_db), current_user: models.AdminUser = Depends(auth.get_current_user)):
    db_team = db.query(models.TeamMember).filter(models.TeamMember.id == team_id).first()
    if not db_team:
        raise HTTPException(status_code=404, detail="TeamMember not found")
    for key, value in team.model_dump().items():
        setattr(db_team, key, value)
    db.commit()
    db.refresh(db_team)
    return db_team

@router.delete("/{team_id}")
def delete_team(team_id: int, db: Session = Depends(get_db), current_user: models.AdminUser = Depends(auth.get_current_user)):
    db_team = db.query(models.TeamMember).filter(models.TeamMember.id == team_id).first()
    if not db_team:
        raise HTTPException(status_code=404, detail="TeamMember not found")
    db.delete(db_team)
    db.commit()
    return {"ok": True}

@router.post("/{team_id}/image")
async def upload_team_image(team_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: models.AdminUser = Depends(auth.get_current_user)):
    db_team = db.query(models.TeamMember).filter(models.TeamMember.id == team_id).first()
    if not db_team:
        raise HTTPException(status_code=404, detail="TeamMember not found")
    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Maximum 5MB.")
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Only images allowed.")
    db_team.image_blob = contents
    db.commit()
    return {"ok": True}

@router.get("/{team_id}/image")
def get_team_image(team_id: int, db: Session = Depends(get_db)):
    db_team = db.query(models.TeamMember).filter(models.TeamMember.id == team_id).first()
    if not db_team or not db_team.image_blob:
        raise HTTPException(status_code=404, detail="Image not found")
    return Response(content=db_team.image_blob, media_type="image/jpeg")
