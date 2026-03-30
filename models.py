from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    code = Column(String, unique=True, index=True, nullable=True) # Optional code, e.g., DANE code

    cities = relationship("City", back_populates="department", cascade="all, delete-orphan")

class City(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    code = Column(String, unique=True, index=True, nullable=True) # Optional DANE code for city

    department = relationship("Department", back_populates="cities")
