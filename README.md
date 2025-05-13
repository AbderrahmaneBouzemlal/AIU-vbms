# **Venue Booking Management System for AIU**  
*A brief description of your project (1-2 sentences).*  

## **Features**  
- List key features of your API  
- Example:  
  - JWT Authentication  
  - User registration & profile management  
  - CRUD operations for [your models]  

## **Setup & Installation**  
### **Prerequisites**  
- Python 3.10+  
- PostgreSQL (or SQLite for development)  

### **Installation**  
1. Clone the repo:  
   ```bash
   git clone https://github.com/abderrahmanebouzemlal/AIU-vbms
   cd project-name
   ```  
2. Create & activate a virtual environment:  
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```  
3. Install dependencies:  
   ```bash
   pip install -r requirements.txt
   ```  
4. Set up environment variables (rename `.env.example` to `.env` and configure):  
   ```bash
   cp .env.example .env
   ```  
5. Run migrations:  
   ```bash
   python manage.py migrate
   ```  
6. Start the development server:  
   ```bash
   python manage.py runserver
   ```  

## ** API Documentation**  
- **Interactive Docs (Swagger UI):** `http://localhost:8000/api/schema/swagger-ui/`  
- **ReDoc:** `http://localhost:8000/api/schema/redoc/`  
- **OpenAPI Schema:** `http://localhost:8000/api/schema/`  

## **🛠 Development**  
- **Run tests:**  
  ```bash
  python manage.py test
  ```  
- **Generate migrations:**  
  ```bash
  python manage.py makemigrations
  ```  
- **Create a superuser (admin):**  
  ```bash
  python manage.py createsuperuser
  ```  
