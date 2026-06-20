# User Management Service

## Project Overview

User Management Service is a RESTful API developed using FastAPI and PostgreSQL.

The application provides CRUD operations for user management.

---

## Technologies Used

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Pydantic
- Uvicorn
- Postman
- GitHub

---

## Database Details

Database Name:

user_management

Schema Name:

user_service

Table Name:

users

---

## Table Columns

- id
- phone_number
- role
- full_name
- tenant_id
- is_active
- email_id
- address
- dob
- bio_details
- created_by
- updated_by
- created_at
- updated_at

---

## API Endpoints

### Create User

POST /users

### Get All Users

GET /users

### Get User By ID

GET /users/{user_id}

### Update User

PUT /users/{user_id}

### Delete User

DELETE /users/{user_id}

---

## Run Project

Activate Virtual Environment

```bash
venv\Scripts\activate
```

Install Dependencies

```bash
pip install -r requirements.txt
```

Run Application

```bash
uvicorn main:app --reload
```

---

## Swagger URL

http://127.0.0.1:8000/docs

---

## Author

Shahul Hameed
