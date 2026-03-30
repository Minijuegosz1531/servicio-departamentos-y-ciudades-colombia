from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
from database import engine, get_db

# Try to create tables if they don't exist yet
try:
    models.Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Warning: Could not create tables yet, DB might be down: {e}")

app = FastAPI(title="Colombia Departments & Cities API")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Colombia Departments & Cities API. See /docs for the API documentation."}

@app.get("/departments", response_model=List[schemas.DepartmentOut])
def read_departments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    departments = db.query(models.Department).offset(skip).limit(limit).all()
    return departments

@app.get("/departments/{department_id}/cities", response_model=List[schemas.CityOut])
def read_cities_by_department(department_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    department = db.query(models.Department).filter(models.Department.id == department_id).first()
    if department is None:
        raise HTTPException(status_code=404, detail="Department not found")
    
    cities = db.query(models.City).filter(models.City.department_id == department_id).offset(skip).limit(limit).all()
    return cities

@app.get("/cities", response_model=List[schemas.CityOut])
def read_all_cities(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    cities = db.query(models.City).offset(skip).limit(limit).all()
    return cities
