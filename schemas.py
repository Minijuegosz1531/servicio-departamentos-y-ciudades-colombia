from pydantic import BaseModel
from typing import List, Optional

class CityBase(BaseModel):
    name: str
    code: Optional[str] = None

class CityCreate(CityBase):
    department_id: int

class CityOut(CityBase):
    id: int
    department_id: int

    class Config:
        from_attributes = True

class DepartmentBase(BaseModel):
    name: str
    code: Optional[str] = None

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentOut(DepartmentBase):
    id: int

    class Config:
        from_attributes = True

class DepartmentWithCitiesOut(DepartmentOut):
    cities: List[CityOut] = []
