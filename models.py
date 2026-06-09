from sqlalchemy import Column, Integer, String, Text, LargeBinary, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)

    images = relationship("AchievementImage", back_populates="achievement", cascade="all, delete-orphan")

class AchievementImage(Base):
    __tablename__ = "achievement_images"

    id = Column(Integer, primary_key=True, index=True)
    achievement_id = Column(Integer, ForeignKey("achievements.id", ondelete="CASCADE"))
    image_blob = Column(LargeBinary)

    achievement = relationship("Achievement", back_populates="images")

class Circular(Base):
    __tablename__ = "circulars"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    pdf_blob = Column(LargeBinary)

class TeamMember(Base):
    __tablename__ = "team_members"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    designation = Column(String)
    email = Column(String, index=True)
    image_blob = Column(LargeBinary)

class CargoCategory(Base):
    __tablename__ = "cargo_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    images = relationship("CargoImage", back_populates="category", cascade="all, delete-orphan")

class CargoImage(Base):
    __tablename__ = "cargo_images"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("cargo_categories.id", ondelete="CASCADE"))
    image_blob = Column(LargeBinary)

    category = relationship("CargoCategory", back_populates="images")

class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    image_blob = Column(LargeBinary)

class License(Base):
    __tablename__ = "licenses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    image_blob = Column(LargeBinary)

class Branch(Base):
    __tablename__ = "branches"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    address = Column(Text)
    iframe_input = Column(Text)
    image_blob = Column(LargeBinary)
