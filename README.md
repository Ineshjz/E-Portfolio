# E-Portfolio Generator

## Overview

E-Portfolio Generator is a web application that allows users to create and publish a professional digital portfolio from their academic and personal information.
The application provides authentication, portfolio generation, role management, and an administration interface.

## Technologies

### Backend
- FastAPI
- SQLModel
- Postgres
- Jinja2
- Uvicorn

### Frontend
- HTML
- CSS
- JavaScript

### Security
- Bcrypt password hashing
- Session-based authentication
- Role-based access control

---

## Project Structure

```text
E-Portfolio/
│
├── main.py
├── make_admin.py
├── Templates/
│   ├── index.html
│   ├── auth.html
│   ├── dashboard.html
│   ├── parametrage.html
│   ├── admin.html
│   └── portfolio.html
│
├── .env
├── requirements.txt
└── README.md
```

---

## Architecture

```text
Browser (HTML/CSS/JS)
          │
          ▼
       FastAPI
          │
          ▼
      SQLModel
          │
          ▼
      PostgreSQL
```

## Deployment

```text
GitHub
   │
   ▼
Render
   │
   ▼
FastAPI Application online
```

## Database Structure

```text
AppUser
├── UserSession
└── Portfolio
    ├── PersonalInfo
    └── Project
        └── ProjectVisual
```


## Main Features

### User
- Register and login
- Create an e-portfolio
- View generated portfolios
- Manage personal information

### Admin
- Access administration dashboard
- Manage users
- Assign roles
- Delete users

---

## Main Routes

| Method | Route | Description |
|----------|----------|-------------|
| GET | / | Home page |
| GET | /auth | Login/Register page |
| GET | /dashboard | User dashboard |
| GET | /generator | Portfolio generator |
| GET | /admin | Admin dashboard |
| POST | /register | User registration |
| POST | /login | User authentication |
| GET | /logout | User logout |
| POST | /eportfolio | Portfolio creation |
| GET | /portfolio/{slug} | Public portfolio |
| GET | /api/me | Current user |
| GET | /api/my-portfolios | User portfolios |
| GET | /api/admin/users | List users |
| POST | /api/admin/users | Create user |
| POST | /api/admin/users/{id}/role | Update role |
| DELETE | /api/admin/users/{id} | Delete user |

---

## Installation

```bash
git clone https://github.com/Ineshjz/E-Portfolio.git
cd E-Portfolio

python -m venv .env
source .env/bin/activate
# Windows: .env\Scripts\activate

pip install -r requirements.txt

uvicorn main:app --reload
```

Application available on:

```text
http://127.0.0.1:8000
```
Deployed version link : https://e-portfolio-iffx.onrender.com/
---

## Future Improvements

- Portfolio editing
- PDF export
- File upload support
- Better medias managment
- Portfolio customization
- OAuth authentication (Google, GitHub, LinkedIn)
