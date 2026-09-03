# FastAPI Notes & Cheat Sheet

> Beginner-friendly notes for learning and revising FastAPI.

---

# 1. What is FastAPI?

**FastAPI** is a modern Python framework for building **APIs**.

An API allows different applications to communicate with each other.

Example:

```text
Frontend
   ↓
HTTP Request
   ↓
FastAPI
   ↓
Python Code
   ↓
Database
   ↓
JSON Response
   ↓
Frontend
```

### Why FastAPI?

* Fast and high-performance
* Easy to learn
* Uses standard Python type hints
* Automatic request validation
* Automatic API documentation
* Supports asynchronous programming
* Good for REST APIs
* Works well with databases and authentication

---

# 2. Installation

Install FastAPI:

```bash
pip install "fastapi[standard]"
```

Check Python:

```bash
python --version
```

---

# 3. Basic FastAPI Application

Create:

```text
main.py
```

Code:

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

Open:

```text
http://127.0.0.1:8000
```

Response:

```json
{
    "message": "Hello World"
}
```

---

# 4. Important FastAPI Concepts

The basic structure is:

```python
@app.get("/path")
def function():
    return {"data": "value"}
```

For example:

```python
@app.get("/hello")
def hello():
    return {"message": "Hello"}
```

This creates:

```text
GET /hello
```

---

# 5. HTTP Methods

The most commonly used HTTP methods are:

| Method | Purpose               |
| ------ | --------------------- |
| GET    | Read data             |
| POST   | Create data           |
| PUT    | Replace/update data   |
| PATCH  | Partially update data |
| DELETE | Delete data           |

These are commonly used to build **CRUD APIs**.

```text
C → Create → POST
R → Read   → GET
U → Update → PUT/PATCH
D → Delete → DELETE
```

---

# 6. GET Request

Used to retrieve data.

```python
@app.get("/users")
def get_users():
    return {
        "users": [
            {"id": 1, "name": "John"},
            {"id": 2, "name": "Sarah"}
        ]
    }
```

Request:

```text
GET /users
```

Response:

```json
{
    "users": [
        {"id": 1, "name": "John"},
        {"id": 2, "name": "Sarah"}
    ]
}
```

---

# 7. Path Parameters

A path parameter is a value included directly in the URL.

Syntax:

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

### Multiple path parameters

```python
@app.get("/users/{user_id}/posts/{post_id}")
def get_post(user_id: int, post_id: int):
    return {
        "user_id": user_id,
        "post_id": post_id
    }
```

Request:

```text
GET /users/5/posts/20
```

---

# 8. Query Parameters

Query parameters appear after `?`.

Example URL:

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

### Multiple query parameters

```python
@app.get("/products")
def products(category: str, limit: int):
    return {
        "category": category,
        "limit": limit
    }
```

Request:

```text
GET /products?category=books&limit=10
```

---

# 9. Optional Query Parameters

Use `None` when a parameter is optional.

```python
@app.get("/users")
def get_users(name: str | None = None):
    if name:
        return {"name": name}

    return {"users": []}
```

Now both are valid:

```text
GET /users
```

and:

```text
GET /users?name=John
```

---

# 10. POST Request

`POST` is generally used to create data.

```python
@app.post("/users")
def create_user():
    return {"message": "User created"}
```

Request:

```text
POST /users
```

---

# 11. Request Body

A request body contains data sent by the client.

FastAPI commonly uses **Pydantic models** for request bodies.

```python
from pydantic import BaseModel


class User(BaseModel):
    name: str
    age: int
```

Use it in an endpoint:

```python
@app.post("/users")
def create_user(user: User):
    return user
```

Client sends:

```json
{
    "name": "John",
    "age": 25
}
```

Response:

```json
{
    "name": "John",
    "age": 25
}
```

---

# 12. Pydantic Models

Pydantic models define the expected structure of data.

```python
from pydantic import BaseModel


class Product(BaseModel):
    name: str
    price: float
    quantity: int
```

Example JSON:

```json
{
    "name": "Laptop",
    "price": 999.99,
    "quantity": 5
}
```

FastAPI automatically validates the data.

For example, this is invalid:

```json
{
    "name": "Laptop",
    "price": "hello",
    "quantity": 5
}
```

because `price` should be a `float`.

---

# 13. Common Python Types

You can use Python type hints:

```python
name: str
age: int
price: float
active: bool
```

Example:

```python
class User(BaseModel):
    name: str
    age: int
    email: str
    active: bool
```

---

# 14. Default Values

```python
class User(BaseModel):
    name: str
    age: int = 18
```

If `age` isn't provided, it defaults to:

```text
18
```

---

# 15. PUT Request

`PUT` is commonly used to update/replace an existing resource.

```python
@app.put("/users/{user_id}")
def update_user(user_id: int, user: User):
    return {
        "user_id": user_id,
        "user": user
    }
```

Request:

```text
PUT /users/10
```

Body:

```json
{
    "name": "Alex",
    "age": 30
}
```

---

# 16. PATCH Request

`PATCH` is generally used for a partial update.

Example:

```python
@app.patch("/users/{user_id}")
def update_user(user_id: int):
    return {
        "message": "User partially updated",
        "user_id": user_id
    }
```

Difference:

```text
PUT
→ Usually replace/update the resource

PATCH
→ Usually update only selected fields
```

---

# 17. DELETE Request

Used to delete data.

```python
@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    return {
        "message": "User deleted",
        "user_id": user_id
    }
```

Request:

```text
DELETE /users/10
```

---

# 18. CRUD Example

A simple CRUD API:

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class User(BaseModel):
    name: str
    age: int


@app.get("/users")
def get_users():
    return {"message": "Get users"}


@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id}


@app.post("/users")
def create_user(user: User):
    return {
        "message": "User created",
        "user": user
    }


@app.put("/users/{user_id}")
def update_user(user_id: int, user: User):
    return {
        "message": "User updated",
        "user_id": user_id,
        "user": user
    }


@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    return {
        "message": "User deleted",
        "user_id": user_id
    }
```

---

# 19. Automatic API Documentation

FastAPI automatically generates API documentation.

### Swagger UI

```text
http://127.0.0.1:8000/docs
```

Swagger lets you:

* See endpoints
* Test GET requests
* Test POST requests
* Enter parameters
* Send JSON bodies
* View responses

### ReDoc

```text
http://127.0.0.1:8000/redoc
```

---

# 20. HTTP Status Codes

Common status codes:

| Code | Meaning               |
| ---- | --------------------- |
| 200  | OK                    |
| 201  | Created               |
| 204  | No Content            |
| 400  | Bad Request           |
| 401  | Unauthorized          |
| 403  | Forbidden             |
| 404  | Not Found             |
| 422  | Validation Error      |
| 500  | Internal Server Error |

---

# 21. Returning a Status Code

You can specify a status code:

```python
from fastapi import FastAPI, status

app = FastAPI()


@app.post("/users", status_code=status.HTTP_201_CREATED)
def create_user():
    return {"message": "User created"}
```

The API returns:

```text
201 Created
```

---

# 22. Error Handling

FastAPI provides `HTTPException`.

```python
from fastapi import HTTPException


@app.get("/users/{user_id}")
def get_user(user_id: int):

    if user_id != 1:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return {
        "id": 1,
        "name": "John"
    }
```

If the user doesn't exist:

```json
{
    "detail": "User not found"
}
```

---

# 23. async Functions

FastAPI supports asynchronous functions.

Normal:

```python
@app.get("/users")
def get_users():
    return {"users": []}
```

Async:

```python
@app.get("/users")
async def get_users():
    return {"users": []}
```

Use `async` when working with asynchronous operations such as certain database or external API calls.

---

# 24. Response Models

You can define the structure of the response.

```python
class User(BaseModel):
    name: str
    age: int


@app.get("/user", response_model=User)
def get_user():
    return {
        "name": "John",
        "age": 25
    }
```

This helps document and validate the response.

---

# 25. Headers

You can access HTTP headers.

```python
from fastapi import Header


@app.get("/items")
def get_items(user_agent: str | None = Header(default=None)):
    return {
        "user_agent": user_agent
    }
```

---

# 26. Cookies

FastAPI can read cookies.

```python
from fastapi import Cookie


@app.get("/items")
def get_items(session_id: str | None = Cookie(default=None)):
    return {
        "session_id": session_id
    }
```

---

# 27. Dependency Injection

FastAPI has a dependency injection system.

Basic example:

```python
from fastapi import Depends


def get_current_user():
    return {"name": "John"}


@app.get("/profile")
def profile(user=Depends(get_current_user)):
    return user
```

Here:

```text
Depends()
    ↓
get_current_user()
    ↓
profile()
```

Dependencies are commonly used for:

* Authentication
* Database sessions
* Shared logic
* Permissions
* Common parameters

---

# 28. Routers

As an application gets bigger, don't put everything in `main.py`.

Use routers.

Example structure:

```text
project/
│
├── main.py
│
└── routers/
    ├── users.py
    └── products.py
```

### `routers/users.py`

```python
from fastapi import APIRouter

router = APIRouter()


@router.get("/users")
def get_users():
    return {"users": []}
```

### `main.py`

```python
from fastapi import FastAPI
from routers import users

app = FastAPI()

app.include_router(users.router)
```

Now the `/users` endpoint is available.

---

# 29. Prefixes

You can add a prefix to a router.

```python
app.include_router(
    users.router,
    prefix="/api"
)
```

Then:

```text
GET /api/users
```

---

# 30. Tags

Tags organize endpoints in Swagger documentation.

```python
app.include_router(
    users.router,
    prefix="/api",
    tags=["Users"]
)
```

Swagger will group the endpoints under:

```text
Users
```

---

# 31. Environment Variables

Don't hard-code sensitive configuration such as:

```text
DATABASE_PASSWORD
API_KEY
SECRET_KEY
```

Use environment variables.

Example:

```python
import os

DATABASE_URL = os.getenv("DATABASE_URL")
```

A `.env` file can be used with appropriate configuration tooling.

Example:

```text
DATABASE_URL=postgresql://...
SECRET_KEY=my-secret
```

Never commit real secrets to Git.

---

# 32. Database

FastAPI doesn't force you to use a particular database.

Common choices include:

* PostgreSQL
* MySQL
* SQLite
* MongoDB

A typical application looks like:

```text
FastAPI
   ↓
Service / Business Logic
   ↓
Database Layer
   ↓
PostgreSQL
```

Popular Python database tools include SQLAlchemy and SQLModel.

---

# 33. Typical Project Structure

Small project:

```text
project/
│
├── main.py
└── requirements.txt
```

Larger project:

```text
project/
│
├── main.py
│
├── routers/
│   ├── users.py
│   ├── products.py
│   └── auth.py
│
├── models/
│   ├── user.py
│   └── product.py
│
├── schemas/
│   ├── user.py
│   └── product.py
│
├── services/
│   ├── user_service.py
│   └── product_service.py
│
├── database/
│   └── database.py
│
└── tests/
    └── test_users.py
```

---

# 34. API URL Design

Good:

```text
GET    /users
GET    /users/10
POST   /users
PUT    /users/10
PATCH  /users/10
DELETE /users/10
```

Avoid unnecessarily complicated URLs such as:

```text
/getAllUsers
/createNewUser
/deleteUserById
```

Think in terms of **resources**.

```text
/users
/products
/orders
```

---

# 35. Request Flow

A typical POST request:

```text
Client
  │
  │ POST /users
  │
  │ JSON
  ↓
FastAPI
  │
  ↓
Pydantic Validation
  │
  ↓
Endpoint
  │
  ↓
Business Logic
  │
  ↓
Database
  │
  ↓
Response
  │
  ↓
Client
```

---

# 36. Complete Beginner Example

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


class User(BaseModel):
    name: str
    age: int


users = []


@app.get("/")
def home():
    return {"message": "API is running"}


@app.get("/users")
def get_users():
    return users


@app.post("/users", status_code=201)
def create_user(user: User):
    users.append(user)

    return {
        "message": "User created",
        "user": user
    }


@app.get("/users/{user_id}")
def get_user(user_id: int):

    if user_id >= len(users):
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return users[user_id]
```

> This example uses an in-memory list for learning. Real applications normally use a database.

---

# 37. Useful Commands

Install:

```bash
pip install "fastapi[standard]"
```

Run development server:

```bash
fastapi dev main.py
```

Run production server:

```bash
fastapi run main.py
```

---

# 38. Important Decorators

Remember these:

```python
@app.get("/")
@app.post("/")
@app.put("/")
@app.patch("/")
@app.delete("/")
```

They create API endpoints.

---

# 39. Quick Syntax Cheat Sheet

### Basic API

```python
@app.get("/items")
def get_items():
    return {"items": []}
```

### Path parameter

```python
@app.get("/items/{item_id}")
def get_item(item_id: int):
    return {"id": item_id}
```

### Query parameter

```python
@app.get("/items")
def get_items(limit: int = 10):
    return {"limit": limit}
```

### Request body

```python
class Item(BaseModel):
    name: str
    price: float


@app.post("/items")
def create_item(item: Item):
    return item
```

### Error

```python
raise HTTPException(
    status_code=404,
    detail="Not found"
)
```

### Response model

```python
@app.get("/user", response_model=User)
def get_user():
    return user
```

### Dependency

```python
@app.get("/profile")
def profile(user=Depends(get_current_user)):
    return user
```

---

# 40. Learning Roadmap

Learn FastAPI in this order:

```text
1. Python basics
      ↓
2. HTTP basics
      ↓
3. REST API concepts
      ↓
4. FastAPI basics
      ↓
5. GET / POST
      ↓
6. Path & Query Parameters
      ↓
7. Pydantic
      ↓
8. PUT / PATCH / DELETE
      ↓
9. Error Handling
      ↓
10. Routers
      ↓
11. Dependencies
      ↓
12. Database
      ↓
13. Authentication / JWT
      ↓
14. Testing
      ↓
15. Deployment
```

---

# 41. One-Minute Revision

```text
FastAPI
→ Python framework for APIs

FastAPI app
→ FastAPI()

GET
→ Read

POST
→ Create

PUT
→ Update/replace

PATCH
→ Partial update

DELETE
→ Delete

Path parameter
→ /users/{user_id}

Query parameter
→ /users?name=John

Pydantic
→ Data validation / schemas

HTTPException
→ API errors

Depends
→ Dependency injection

APIRouter
→ Organize endpoints

/docs
→ Swagger API documentation

/redoc
→ ReDoc API documentation

CRUD
→ Create, Read, Update, Delete
```

---

# 42. Minimal FastAPI Template

When starting a new project, remember this:

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str
    price: float


@app.get("/")
def home():
    return {"message": "Hello World"}


@app.get("/items")
def get_items():
    return []


@app.post("/items")
def create_item(item: Item):
    return item
```

Run:

```bash
fastapi dev main.py
```

Then test your API at:

```text
http://127.0.0.1:8000/docs
```

---

# Final Mental Model

Think of FastAPI as:

```text
             FASTAPI
                │
        ┌───────┴────────┐
        ↓                ↓
     Request          Response
        │                ↑
        ↓                │
   Validation            │
        │                │
        ↓                │
   Python Logic ─────────┘
        │
        ↓
    Database
```

The most important things to understand first are:

**Routes → HTTP methods → Parameters → Pydantic → Validation → CRUD → Database → Authentication**
