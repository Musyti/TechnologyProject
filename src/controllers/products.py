from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
import json
import os

router = APIRouter(prefix="/employees", tags=["employees"])

class Employee(BaseModel):
    id: Optional[int] = None
    fio: str
    position: str
    department: str
    salary: int
    hire_date: str

# Простая глобальная переменная как в оригинале
employees = []

def load_employees():
    global employees
    try:
        if os.path.exists("employees.json"):
            with open("employees.json", "r", encoding="utf-8") as f:
                employees = json.load(f)
    except:
        employees = []

def save_employees():
    with open("employees.json", "w", encoding="utf-8") as f:
        json.dump(employees, f, ensure_ascii=False, indent=2)

# Инициализация при первом запуске
def init_data():
    global employees
    if not employees:
        employees = [
            {"id": 1, "fio": "Иванов И.И.", "position": "Разработчик", "department": "IT", "salary": 150000, "hire_date": "2025-01-15"},
            {"id": 2, "fio": "Петров П.П.", "position": "Менеджер", "department": "HR", "salary": 80000, "hire_date": "2025-03-10"},
            {"id": 3, "fio": "Сидорова А.С.", "position": "Дизайнер", "department": "IT", "salary": 120000, "hire_date": "2025-06-01"}
        ]
        save_employees()

@router.post("/")
async def create_employee(emp: Employee):
    init_data()
    load_employees()
    new_id = max([e.get("id", 0) for e in employees], default=0) + 1
    new_emp = emp.model_dump()
    new_emp["id"] = new_id
    employees.append(new_emp)
    save_employees()
    return new_emp

@router.get("/")
async def get_employees(sorting: Optional[str] = Query(None), department: Optional[str] = Query(None)):
    init_data()
    load_employees()
    
    # Фильтрация
    if department:
        employees[:] = [e for e in employees if department.lower() in e["department"].lower()]
    
    # Сортировка по ФИО
    if sorting == "asc":
        employees.sort(key=lambda x: x["fio"].lower())
    elif sorting == "desc":
        employees.sort(key=lambda x: x["fio"].lower(), reverse=True)
    
    return {"employees": employees, "total": len(employees)}

@router.get("/{emp_id}")
async def get_employee(emp_id: int):
    init_data()
    load_employees()
    for emp in employees:
        if emp["id"] == emp_id:
            return emp
    raise HTTPException(404, "Сотрудник не найден")

@router.put("/{emp_id}")
async def update_employee(emp_id: int, emp: Employee):
    init_data()
    load_employees()
    for i, e in enumerate(employees):
        if e["id"] == emp_id:
            updated = emp.model_dump()
            updated["id"] = emp_id
            employees[i] = updated
            save_employees()
            return updated
    raise HTTPException(404, "Сотрудник не найден")

@router.delete("/{emp_id}")
async def delete_employee(emp_id: int):
    init_data()
    load_employees()
    global employees
    employees = [e for e in employees if e["id"] != emp_id]
    save_employees()
    return {"message": "Удалено"}
