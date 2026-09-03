# FastAPI — Basic Tutorial

## 1. What is FastAPI?

**FastAPI** is a modern Python framework used to build **APIs and web applications**.

An API allows different applications to communicate with each other.

For example:

```text
Frontend (React)
      ↓
    API
      ↓
FastAPI (Python)
      ↓
   Database
```

FastAPI is commonly used for building **REST APIs**.

---

## 2. Why use FastAPI?

FastAPI is popular because it is:

* **Fast** — high performance
* **Easy to learn** — uses normal Python
* **Type-safe** — uses Python type hints
* **Automatic documentation** — provides Swagger/OpenAPI docs
* **Good for APIs** — especially REST APIs
* **Modern** — supports async programming

---

## 3. Installation

Install FastAPI using pip:

```bash
pip install "fastapi[standard]"
```

---

## 4. Create a FastAPI application

Create a file:

```text
main.py
```

Add:

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def home():
    return {"message": "Hello World"}
```

---

## 5. Run the application

Run:

```bash
fastapi dev main.py
```

The server will normally be available at:

```text
http://127.0.0.1:8000
```

Open it in your browser.

You should get:

```json
{
  "message": "Hello World"
}
```

---

# 6. What does `@app.get()` mean?

This:

```python
@app.get("/")
```

creates a **GET endpoint**.

`GET` is an HTTP method used to **retrieve data**.

For example:

```python
@app.get("/users")
def get_users():
    return {"users": ["John", "Sarah", "Alex"]}
```

The API endpoint is:

```text
GET /users
```

---

# 7. Path Parameters

You can receive values directly from the URL.

```python
@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id}
```

Request:

```text
GET /users/10
```

Response:

```json
{
  "user_id": 10
}
```

Here:

```python
user_id: int
```

means FastAPI expects `user_id` to be an integer.

---

# 8. Query Parameters

Query parameters are values after `?` in a URL.

Example:

```text
/users?name=John
```

Python:

```python
@app.get("/users")
def get_user(name: str):
    return {"name": name}
```

Request:

```text
GET /users?name=John
```

Response:

```json
{
  "name": "John"
}
```

---

# 9. POST Request

`POST` is commonly used to **create data**.

Example:

```python
from fastapi import FastAPI

app = FastAPI()


@app.post("/users")
def create_user():
    return {"message": "User created"}
```

Now:

```text
POST /users
```

creates a user.

---

# 10. Request Body with Pydantic

FastAPI commonly uses **Pydantic models** to validate incoming data.

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class User(BaseModel):
    name: str
    age: int


@app.post("/users")
def create_user(user: User):
    return user
```

The client can send:

```json
{
  "name": "John",
  "age": 25
}
```

FastAPI validates the data automatically.

---

# 11. PUT and DELETE

### PUT

Usually used to update data.

```python
@app.put("/users/{user_id}")
def update_user(user_id: int):
    return {"message": f"User {user_id} updated"}
```

### DELETE

Usually used to delete data.

```python
@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    return {"message": f"User {user_id} deleted"}
```

---

# 12. HTTP Methods

The most common HTTP methods are:

| Method | Common purpose        |
| ------ | --------------------- |
| GET    | Read data             |
| POST   | Create data           |
| PUT    | Update data           |
| PATCH  | Partially update data |
| DELETE | Delete data           |

Together, these are often used to create a **CRUD API**.

CRUD means:

```text
C → Create
R → Read
U → Update
D → Delete
```

---

# 13. Automatic Documentation

One of FastAPI's best features is automatic API documentation.

After starting the server, open:

```text
http://127.0.0.1:8000/docs
```

You will see an interactive Swagger UI.

You can use it to:

* See your API endpoints
* See request parameters
* Send requests
* See responses
* Test your API

FastAPI also provides another documentation page at:

```text
http://127.0.0.1:8000/redoc
```

---

# 14. Simple Project Structure

A beginner project can start like this:

```text
my_fastapi_project/
│
├── main.py
├── requirements.txt
└── README.md
```

Later, as the project becomes bigger:

```text
my_fastapi_project/
│
├── main.py
├── routers/
│   ├── users.py
│   └── products.py
│
├── models/
├── schemas/
├── services/
└── database/
```

---

# 15. Complete Beginner Example

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class User(BaseModel):
    name: str
    age: int


@app.get("/")
def home():
    return {"message": "FastAPI is working!"}


@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id}


@app.post("/users")
def create_user(user: User):
    return {
        "message": "User created",
        "user": user
    }


@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    return {"message": "User deleted"}
```

---

# 16. Important Things to Learn Next

After understanding this basic example, learn FastAPI in this order:

1. **HTTP & REST API basics**
2. **GET requests**
3. **POST requests**
4. **Path parameters**
5. **Query parameters**
6. **Pydantic models**
7. **PUT / PATCH / DELETE**
8. **Error handling**
9. **Database integration**
10. **Authentication**
11. **Routers**
12. **Dependency injection**
13. **Async programming**
14. **Testing**
15. **Deployment**

---

# Quick Summary

**FastAPI** = Python framework for building APIs.

Basic application:

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def home():
    return {"message": "Hello World"}
```

Run:

```bash
fastapi dev main.py
```

Test:

```text
http://127.0.0.1:8000
```

Documentation:

```text
http://127.0.0.1:8000/docs
```

The core idea is:

```text
URL
 ↓
HTTP Method
 ↓
FastAPI Endpoint
 ↓
Python Function
 ↓
JSON Response
```
