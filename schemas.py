from pydantic import BaseModel, ConfigDict, computed_field
from typing import List, Optional
from datetime import date as DateType
import os
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "https://api.popememorialhss.org")

class Token(BaseModel):
    access_token: str
    token_type: str

class AchievementImageBase(BaseModel):
    pass

class AchievementImage(AchievementImageBase):
    id: int
    achievement_id: int
    model_config = ConfigDict(from_attributes=True)
    
    @computed_field
    @property
    def image_url(self) -> str:
        return f"{API_BASE_URL}/api/achievements/images/{self.id}/content"

class AchievementBase(BaseModel):
    title: str
    description: str

class AchievementCreate(AchievementBase):
    pass

class Achievement(AchievementBase):
    id: int
    images: List[AchievementImage] = []
    model_config = ConfigDict(from_attributes=True)

class CircularBase(BaseModel):
    title: str
    description: str
    circular_name: Optional[str] = None
    date: Optional[DateType] = None

class CircularCreate(CircularBase):
    pass

class Circular(CircularBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

    @computed_field
    @property
    def pdf_url(self) -> str:
        return f"{API_BASE_URL}/api/circulars/{self.id}/pdf"

class TeamMemberBase(BaseModel):
    name: str
    designation: str
    email: str

class TeamMemberCreate(TeamMemberBase):
    pass

class TeamMember(TeamMemberBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

    @computed_field
    @property
    def image_url(self) -> str:
        return f"{API_BASE_URL}/api/teams/{self.id}/image"

class CargoImageBase(BaseModel):
    pass

class CargoImage(CargoImageBase):
    id: int
    category_id: int
    model_config = ConfigDict(from_attributes=True)
    
    @computed_field
    @property
    def image_url(self) -> str:
        return f"{API_BASE_URL}/api/cargos/images/{self.id}/content"

class CargoCategoryBase(BaseModel):
    name: str

class CargoCategoryCreate(CargoCategoryBase):
    pass

class CargoCategory(CargoCategoryBase):
    id: int
    images: List[CargoImage] = []
    model_config = ConfigDict(from_attributes=True)

class ServiceBase(BaseModel):
    title: str
    description: str

class ServiceCreate(ServiceBase):
    pass

class Service(ServiceBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
    
    @computed_field
    @property
    def image_url(self) -> str:
        return f"{API_BASE_URL}/api/services/{self.id}/image"

class LicenseBase(BaseModel):
    title: str
    description: str

class LicenseCreate(LicenseBase):
    pass

class License(LicenseBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
    
    @computed_field
    @property
    def image_url(self) -> str:
        return f"{API_BASE_URL}/api/licenses/{self.id}/image"

class BranchBase(BaseModel):
    title: str
    address: str
    iframe_input: str

class BranchCreate(BranchBase):
    pass

class Branch(BranchBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
    
    @computed_field
    @property
    def image_url(self) -> str:
        return f"{API_BASE_URL}/api/branches/{self.id}/image"
