from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


# Data model
class User(BaseModel):
    name: str
    age: int


# GET request
@app.get("/")
def home():
    return {"message": "Hello World"}


# GET all users
@app.get("/users")
def get_users():
    return [
        {"id": 1, "name": "John", "age": 25},
        {"id": 2, "name": "Sarah", "age": 30}
    ]


# GET one user using path parameter
@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {
        "user_id": user_id,
        "message": "User found"
    }


# POST request
@app.post("/users")
def create_user(user: User):
    return {
        "message": "User created successfully",
        "user": user
    }


# DELETE request
@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    return {
        "message": "User deleted",
        "user_id": user_id
    }