# E-Portfolio Generator

## Overview

E-Portfolio Generator is a web application that allows users to quickly create a professional digital portfolio from their personal and academic information.

The platform provides:

- User authentication (registration and login)
- Role management (User / Admin)
- Portfolio generation from a form
- Portfolio visualization through a web interface
- Data storage using SQLite
- Administration features for managing users

This project was developed using **FastAPI** for the backend and **HTML/CSS/JavaScript** for the frontend.

---

## Features

### User Features
- Create an account
- Log in securely
- Generate an e-portfolio
- View generated portfolio information
- Manage personal profile data

### Admin Features
- Access an administration dashboard
- Manage registered users
- Monitor platform activity

---

## Technologies Used

### Backend
- FastAPI
- SQLModel
- SQLite
- Jinja2
- Uvicorn

### Frontend
- HTML
- CSS
- JavaScript

### Authentication
- Password hashing with bcrypt
- Session-based authentication

---

## Project Structure

```text
E-Portfolio/
│
├── main.py
├── database.py
├── models.py
├── auth.py
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   └── portfolio.html
│
├── test_database.db
│
├── requirements.txt
└── README.md
