from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Response
from typing import List
from sqlalchemy.orm import Session
from typing import List
import models, schemas
from database import get_db
import auth

router = APIRouter()

@router.get("/", response_model=List[schemas.CargoCategory])
def read_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.CargoCategory).offset(skip).limit(limit).all()

@router.post("/", response_model=schemas.CargoCategory)
def create_category(category: schemas.CargoCategoryCreate, db: Session = Depends(get_db), current_user: models.AdminUser = Depends(auth.get_current_user)):
    db_category = models.CargoCategory(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.put("/{category_id}", response_model=schemas.CargoCategory)
def update_category(category_id: int, category: schemas.CargoCategoryCreate, db: Session = Depends(get_db), current_user: models.AdminUser = Depends(auth.get_current_user)):
    db_category = db.query(models.CargoCategory).filter(models.CargoCategory.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    for key, value in category.model_dump().items():
        setattr(db_category, key, value)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db), current_user: models.AdminUser = Depends(auth.get_current_user)):
    db_category = db.query(models.CargoCategory).filter(models.CargoCategory.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(db_category)
    db.commit()
    return {"ok": True}

@router.post("/{category_id}/images", response_model=List[schemas.CargoImage])
async def upload_cargo_images(category_id: int, files: List[UploadFile] = File(...), db: Session = Depends(get_db), current_user: models.AdminUser = Depends(auth.get_current_user)):
    db_category = db.query(models.CargoCategory).filter(models.CargoCategory.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    uploaded_images = []
    for file in files:
        contents = await file.read()
        if len(contents) > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="One of the files is too large. Maximum 5MB.")
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Invalid file type. Only images allowed.")
        db_image = models.CargoImage(category_id=category_id, image_blob=contents)
        db.add(db_image)
        uploaded_images.append(db_image)
        
    db.commit()
    for img in uploaded_images:
        db.refresh(img)
    return uploaded_images

@router.get("/images/{image_id}/content")
def get_cargo_image_content(image_id: int, db: Session = Depends(get_db)):
    db_image = db.query(models.CargoImage).filter(models.CargoImage.id == image_id).first()
    if not db_image or not db_image.image_blob:
        raise HTTPException(status_code=404, detail="Image not found")
    return Response(content=db_image.image_blob, media_type="image/jpeg")

@router.delete("/images/{image_id}")
def delete_cargo_image(image_id: int, db: Session = Depends(get_db), current_user: models.AdminUser = Depends(auth.get_current_user)):
    db_image = db.query(models.CargoImage).filter(models.CargoImage.id == image_id).first()
    if not db_image:
        raise HTTPException(status_code=404, detail="Image not found")
    db.delete(db_image)
    db.commit()
    return {"ok": True}
