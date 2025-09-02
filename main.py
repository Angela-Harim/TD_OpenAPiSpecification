from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime



app = FastAPI(title="OAS3 Exercices API")


# Exercice 1 - GET /ping

@app.get("/ping", response_class=PlainTextResponse)
def ping():
    return "pong"


# Exercice 2 - GET /users?page=&size=

class User(BaseModel):
    id: int
    name: str
    email: EmailStr

fake_users = [
    User(id=1, name="Alice", email="alice@example.com"),
    User(id=2, name="Bob", email="bob@example.com"),
]

@app.get("/users", response_model=List[User])
def get_users(page: int = 1, size: int = 20):
    start = (page - 1) * size
    end = start + size
    return fake_users[start:end]


# Exercice 3 - Task API

class Task(BaseModel):
    id: int
    title: str
    completed: bool

fake_tasks = [
    Task(id=1, title="Faire les courses", completed=False),
    Task(id=2, title="Envoyer email", completed=True),
]

@app.get("/tasks", response_model=List[Task])
def get_tasks():
    return fake_tasks

@app.post("/tasks", response_model=List[Task], status_code=201)
def create_tasks(tasks: List[Task]):
    fake_tasks.extend(tasks)
    return tasks

@app.get("/tasks/{id}", response_model=Task)
def get_task(id: int):
    for task in fake_tasks:
        if task.id == id:
            return task
    raise HTTPException(status_code=404, detail="Task not found")

@app.delete("/tasks/{id}", response_model=Task)
def delete_task(id: int):
    for i, task in enumerate(fake_tasks):
        if task.id == id:
            return fake_tasks.pop(i)
    raise HTTPException(status_code=404, detail="Task not found")

@app.delete("/tasks", response_model=List[Task])
def delete_tasks(ids: List[int]):
    deleted = []
    global fake_tasks
    remaining = []
    for task in fake_tasks:
        if task.id in ids:
            deleted.append(task)
        else:
            remaining.append(task)
    fake_tasks = remaining
    return deleted


# Exercice 4 - Product API

class Product(BaseModel):
    name: str
    expiration_datetime: datetime
    price: float

fake_products = [
    Product(name="Lait", expiration_datetime=datetime(2025,9,30,12,0), price=1.5),
    Product(name="Pain", expiration_datetime=datetime(2025,9,25,12,0), price=0.8),
]

@app.get("/products", response_model=List[Product])
def get_products(limit: Optional[int] = 10, q: Optional[str] = None):
    result = fake_products
    if q:
        result = [p for p in result if q.lower() in p.name.lower()]
    return result[:limit]


# Exercice 5 - Order API avec Basic Auth simulé

class Order(BaseModel):
    identifier: int
    customer_name: str
    creation_datetime: datetime
    total_amount: float

fake_orders: List[Order] = []

@app.get("/orders", response_model=List[Order])
def get_orders(page: int = 1, size: int = 20):
    start = (page - 1) * size
    end = start + size
    return fake_orders[start:end]

@app.post("/orders", response_model=Order)
def create_order(order: Order, username: str = "", password: str = ""):
    # Auth basique simulée
    if username != "admin" or password != "secret":
        raise HTTPException(status_code=401, detail="Unauthorized")
    fake_orders.append(order)
    return order


# Exercice 6 - UserProfile avancé

class PersonalInfo(BaseModel):
    first_name: str
    last_name: str
    birthdate: date
    email: EmailStr

class Address(BaseModel):
    address_street: str
    address_city: str
    address_country: str
    address_postal_code: int

class Preferences(BaseModel):
    needs_newsletter: bool
    language: str  # mg, fr, eng

class CreateUserProfile(PersonalInfo, Address, Preferences):
    pass

class UserProfile(CreateUserProfile):
    identifier: str

fake_user_profiles: List[UserProfile] = []

@app.get("/users/{id}", response_model=UserProfile)
def get_user_profile(id: str):
    for user in fake_user_profiles:
        if user.identifier == id:
            return user
    raise HTTPException(status_code=404, detail="User not found")

@app.post("/users", response_model=List[UserProfile], status_code=201)
def create_user_profiles(users: List[CreateUserProfile]):
    created_users = []
    for i, u in enumerate(users, start=len(fake_user_profiles)+1):
        profile = UserProfile(identifier=f"u{i:03}", **u.dict())
        fake_user_profiles.append(profile)
        created_users.append(profile)
    return created_users

@app.put("/users/{id}/personalInfo", response_model=UserProfile)
def update_personal_info(id: str, info: PersonalInfo):
    for i, user in enumerate(fake_user_profiles):
        if user.identifier == id:
            updated = user.copy(update=info.dict())
            fake_user_profiles[i] = updated
            return updated
    raise HTTPException(status_code=404, detail="User not found")

@app.put("/users/{id}/address", response_model=UserProfile)
def update_address(id: str, addr: Address):
    for i, user in enumerate(fake_user_profiles):
        if user.identifier == id:
            updated = user.copy(update=addr.dict())
            fake_user_profiles[i] = updated
            return updated
    raise HTTPException(status_code=404, detail="User not found")
feat: add main.py implementing exercises 1-6