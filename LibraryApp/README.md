
# LibraryApp
A modern library automation system with admin features, user management, and book tracking.

# 📚 LibraryApp

**LibraryApp** is a modern library automation system that manages book borrowing and returning processes, as well as book and user management, in a digital environment. It provides role-based authorization, allowing users to manage library operations digitally.

---

## 🎯 Purpose

LibraryApp is designed to create an easy-to-use system where users can borrow and return books, and administrators can manage books and users.

---

## 🛠️ Technologies Used

### Backend
- **Python**
- **Django** (REST API)
- **MySQL**
- **JWT** (Authentication)
- **Postman** (API testing)

### Frontend
- **HTML + CSS**
- **JavaScript**

---

## 🧩 Project Steps

1. **Set Up Project Structure**
   - Backend structure will be created using Django and FastAPI.
   
2. **Set Up MySQL Connection**
   - MySQL will be used and configured for the database connection.
   
3. **Create User Roles**
   - **Super Admin**: Can manage all system settings and control users and books.
   - **Admin**: Can manage books but cannot change user information.
   - **Student**: Can borrow books, view their borrowed books. They will receive an email notification when the borrowing period ends.

4. **Hash User Passwords**
   - User passwords will be securely hashed for storage.

5. **Implement Authentication (JWT)**
   - JWT-based authentication will be set up for users.

6. **Email Notification**
   - The borrowing period for books is 30 days. Users will receive an email notification when their borrowing period ends.

---

## 👤 User Roles
### 🔵 Admin
- Can manage books.
- Can manage users (add, delete, update).
- Can manage system settings.

### 🟢 Student
- Can borrow books.
- Can view their borrowed books.
- Borrowing period is 30 days, and they will receive an email notification when the period ends.

---

## 📬 Email Notification

Each book has a 30-day borrowing period. Once the period ends, the system will automatically send an email notification to the user.

---

## 🔐 Authentication

JWT (JSON Web Token) authentication will be used. After logging in, users will receive a JWT token, which they will use for access to the system.

---

## 🚀 Installation

1. **Clone the Repo:**
   ```bash
   git clone https://github.com/username/LibraryApp.git
2.**Create a Virtual Environment and Install Dependencies:
python -m venv env
source env/bin/activate  

# For Windows: env\Scripts\activate
pip install -r requirements.txt

3.Set Up .env File
Create a .env file and enter your database credentials.

4.Run Migrations:
python manage.py runserver
>>>>>>> d426018685b2c2f24dc11a7d3874240c0c9c503f
