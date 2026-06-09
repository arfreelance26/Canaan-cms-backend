from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Response
from sqlalchemy.orm import Session
from typing import List
import models, schemas
from database import get_db
import auth

router = APIRouter()

@router.get("/", response_model=List[schemas.Achievement])
def read_achievements(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Achievement).offset(skip).limit(limit).all()

@router.post("/", response_model=schemas.Achievement)
def create_achievement(achievement: schemas.AchievementCreate, db: Session = Depends(get_db), current_user: models.AdminUser = Depends(auth.get_current_user)):
    db_achievement = models.Achievement(**achievement.model_dump())
    db.add(db_achievement)
    db.commit()
    db.refresh(db_achievement)
    return db_achievement

@router.put("/{achievement_id}", response_model=schemas.Achievement)
def update_achievement(achievement_id: int, achievement: schemas.AchievementCreate, db: Session = Depends(get_db), current_user: models.AdminUser = Depends(auth.get_current_user)):
    db_achievement = db.query(models.Achievement).filter(models.Achievement.id == achievement_id).first()
    if not db_achievement:
        raise HTTPException(status_code=404, detail="Achievement not found")
    for key, value in achievement.model_dump().items():
        setattr(db_achievement, key, value)
    db.commit()
    db.refresh(db_achievement)
    return db_achievement

@router.delete("/{achievement_id}")
def delete_achievement(achievement_id: int, db: Session = Depends(get_db), current_user: models.AdminUser = Depends(auth.get_current_user)):
    db_achievement = db.query(models.Achievement).filter(models.Achievement.id == achievement_id).first()
    if not db_achievement:
        raise HTTPException(status_code=404, detail="Achievement not found")
    db.delete(db_achievement)
    db.commit()
    return {"ok": True}

@router.post("/{achievement_id}/images", response_model=schemas.AchievementImage)
async def upload_achievement_image(achievement_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: models.AdminUser = Depends(auth.get_current_user)):
    db_achievement = db.query(models.Achievement).filter(models.Achievement.id == achievement_id).first()
    if not db_achievement:
        raise HTTPException(status_code=404, detail="Achievement not found")
    
    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Maximum 5MB.")
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Only images allowed.")
    db_image = models.AchievementImage(achievement_id=achievement_id, image_blob=contents)
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image

@router.get("/images/{image_id}/content")
def get_achievement_image_content(image_id: int, db: Session = Depends(get_db)):
    db_image = db.query(models.AchievementImage).filter(models.AchievementImage.id == image_id).first()
    if not db_image or not db_image.image_blob:
        raise HTTPException(status_code=404, detail="Image not found")
    return Response(content=db_image.image_blob, media_type="image/jpeg")

@router.delete("/images/{image_id}")
def delete_achievement_image(image_id: int, db: Session = Depends(get_db), current_user: models.AdminUser = Depends(auth.get_current_user)):
    db_image = db.query(models.AchievementImage).filter(models.AchievementImage.id == image_id).first()
    if not db_image:
        raise HTTPException(status_code=404, detail="Image not found")
    db.delete(db_image)
    db.commit()
    return {"ok": True}
