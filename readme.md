# GoPostal E-commerce Web Application

This project is a full-stack e-commerce web application built with **React** for the frontend and **Flask** for the backend. The application uses SQLite for development and can be seamlessly upgraded to PostgreSQL for production.


## 🔧 Features

- **Frontend:** Built with React (Vite or CRA)
- **Backend:** Flask REST API with SQLAlchemy and Flask-Migrate
- **API Documentation:** Swagger UI available at `/docs`
- **Testing:** Pytest for backend testing with coverage reports
- **Database:** SQLite for development, easy upgrade to PostgreSQL for production
## 📁 Folder Structure

```
 gopostal/
│
├── frontend/                    # React Frontend (Created with Vite or CRA)
│   ├── public/
│   ├── src/
│   │   ├── components/          # Reusable React components
│   │   ├── pages/               # Page-level components
│   │   ├── services/            # API calls to Flask backend
│   │   ├── App.js
│   │   └── index.js
│   ├── .env                     # Frontend environment variables
│   ├── package.json             # React project dependencies
│   └── vite.config.js           # Vite configuration (if using Vite)
│
├── backend/                     # Flask Backend
│   ├── server/
│   │   ├── __init__.py          # Initializes the Flask app
│   │   ├── config.py            # Configuration (dev, prod, test)
│   │   ├── models/              # Database models
│   │   │   ├── __init__.py      # Import all models
│   │   │   └── model.py         # Custom models
│   │   ├── controllers/         # Business logic layer
│   │   │   ├── __init__.py      # Import all controllers
│   │   │   ├── controller.py    # Custom controllers
│   │   │   └── common.py        # Utilities for all controllers
│   │   ├── routes/              # Route definitions
│   │   │   ├── __init__.py      # Register all routes
│   │   │   └── route.py         # API endpoints
│   │   ├── migrations/          # Flask-Migrate files for DB migrations
│   │   ├── tests/               # Unit and integration tests
│   │   │   ├── __init__.py
│   │   │   ├── test_user_controller.py
│   │   │   └── conftest.py      # Pytest fixtures
│   │   ├── server.py            # Application factory and setup
│   │   └── requirements.txt     # Backend dependencies
│   ├── .env                     # Backend environment variables
│   └── run.py                   # Entry point for running the server
│
├── .gitignore                   # Ignore files for Git
├── README.md                    # Project documentation
└── docker-compose.yml           # For containerization (TBD)
```


## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- Node.js & npm (for React frontend)

### Backend Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r backend/server/requirements.txt
   ```
3. Run database migrations:
   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```
4. Start the server:
   ```bash
   python backend/run.py
   ```

### Frontend Setup

1. Navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev  # If using Vite
   ```

### Running Tests

To run backend tests:
```bash
pytest --cov=backend/server
```

### Viewing Test Coverage

To generate and view the coverage report:
```bash
pytest --cov=backend/server --cov-report=html
```
The report will be available in the `htmlcov/` directory.

## 🐳 Docker (Optional)

To run the application using Docker Compose:
```bash
docker-compose up --build
```

## 📄 License

This project is licensed under the MIT License.

