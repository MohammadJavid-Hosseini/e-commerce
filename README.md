# E-Commerce Backend (Django + DRF)

A modular, scalable backend for an e-commerce website, designed to manage products, customer accounts, orders, discounts, and more.  
The backend is built with **Django** and **Django REST Framework (DRF)**, providing a complete API layer for a React-based frontend (currently under development).  

## 📖 Overview

This project focuses on delivering a **robust backend API** for an e-commerce platform.  

**Key capabilities:**
- Manage products, categories, and stores  
- Handle customer accounts, addresses, and orders  
- Support carts, payments, reviews, and discounts  
- Background task processing (e.g., email notifications)  
- JWT-based authentication for secure API access  

Although the frontend is not yet connected, the backend is **fully functional** and ready to integrate with a React frontend.



## 🛠️ Technologies Involved

### **Backend**
- **Django** — Web framework
- **Django REST Framework (DRF)** — API development
- **PostgreSQL** — Database
- **Redis** — OTP generation, caching, Celery queues
- **Celery** — Background tasks (email sending, async processing)
- **JWT** — Authentication
- **Docker** — Containerization
- **Nginx** — Reverse proxy & static file handling

### **Frontend**
- **React** — UI framework
- **JavaScript, HTML, CSS**
- **TailwindCSS** or **Bootstrap** (optional styling)



## ⚙️ Installation & Setup

### **Requirements**
- Python 3.10+
- PostgreSQL 14+
- Redis 6+
- Docker (optional but recommended)
- Node.js 18+ (for frontend later)

---

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/MohammadJavid-Hosseini/e-commerce
cd e-commerce
```

### 2️⃣ Create & Activate Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate     # Linux/Mac
.venv\Scripts\activate        # Windows
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Create a .env File
Copy these constants into your .env file and fill them in.
Email and SMS config are optional but supported in the project.

```env
SECRET_KEY=your_secret_key
DB_NAME=your_database  
DB_USER=your_username  
DB_PASSWORD=your_password  
DB_HOST=localhost  
DB_PORT=5432  
REDIS_HOST=localhost  
REDIS_PORT=6379  
KAVENEGAR_API=if_you_want_sms_sending(optional)  
KAVENEGAR_SENDER=related_to_above  
PHONE=your_company_phone  
EMAIL_HOST=smtp.gmail.com  
EMAIL_PORT=587  
EMAIL_USE_TLS=True  
EMAIL_HOST_USER=your_email
```
To create the file:

```bash
touch .env
```

### 5️⃣ Apply Migrations
```bash
python manage.py migrate
```

### 6️⃣ Run the Development Server
```bash
python manage.py runserver
```

### 7️⃣ Start Redis and Celery (in separate terminals)
Start Redis:

```bash
redis-server
```

Start Celery worker:

```bash
celery -A ecommerce worker --loglevel=info
```

### 📚 API Usage
Backend API: http://localhost:8000/api/

API Documentation: Available at /swagger/ when the server is running.

JWT Authentication: Obtain tokens via:
/api/account/get_otp/  
/api/account/login/

### 🚀 Deployment
If deployed, access here:
Live URL: (will add soon)

### 🧪 Tests
Run unit tests with:

```bash
python manage.py test
```

### 📄 License
MIT License
Copyright (c) 2025 Mohammad Javid Hosseini