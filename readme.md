# GoPostalSD E-commerce Application

This project is a full-stack e-commerce web application built with **React** for the frontend and **Flask** for the backend. The application uses SQLite for development and can be seamlessly upgraded to PostgreSQL for production.


## 🔧 Features

- **Frontend:** Built with React (Vite or CRA)
- **Backend:** Flask REST API with SQLAlchemy and Flask-Migrate
- **API Documentation:** Swagger UI available at `/docs`
- **Testing:** Pytest for backend testing with coverage reports
- **Database:** SQLite for development, easy upgrade to PostgreSQL for production
## 📁 Folder Structure

```
 gopostalsd/
│
├── frontend/                    # React Frontend (Created with Vite or CRA)
│   ├── public/
│   ├── src/
│   │   ├── components/          # Reusable React components
│   │   ├── pages/               # Page-level components
│   │   ├── services/            # API calls to Flask backend
│   │   ├── App.js
│   │   └── index.js
|   ├── .gitignore               # Front end ignore files for Git
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
│   │   ├── thirdparty/          # Third party adapters
│   │   │   ├── __init__.py
│   │   │   └── sinalite.py      # Sinalite Adapter      
│   │   └── server.py            # Application factory and setup
|   ├── .gitignore               # Backend ignore files for Git
│   ├── .env                     # Backend environment variables
|   ├── requirements.txt         # Backend dependencies
│   └── app.py                   # Entry point for running the server

├── taskmanager/                 # Open and view read me
├── README.md                    # Project documentation
└── docker-compose.yml           # For containerization (TBD)
```
## 🏗️ Architecture
The GoPostal SD E-commerce Web Application is built on a modular architecture that ensures scalability, maintainability, and ease of integration with third-party services. Here’s an overview of the key architectural components:

### Frontend
- **React Application:** The user interface is built with React, using reusable components for streamlined development.

- **API Calls:** All interactions with the backend are handled via RESTful API calls using services located in ```src/services/```.

### Backend
- **Flask Application:** The backend is a Flask REST API providing endpoints for user management, product retrieval, and more.

- **Controllers:** Implements business logic to process and respond to incoming requests (```server/controllers/```).

- **Routes:** Defines API endpoints for various features (```server/routes/```).

- **Database:** Handles data persistence using SQLAlchemy, supporting SQLite for development and PostgreSQL for production (```server/models/```).

- **Configurations:** Different environments (development, testing, production) are managed through ```config.py```.

- **Logging:** A centralized logging mechanism is implemented (```logging.py```) for monitoring and debugging across environments.

### Third-Party Integration
##### Sinalite API Integration: [Documentation](https://apifrontend_stage.sinaliteuppy.com/documentation.html)  
- An adapter design pattern (```SinaliteAdapter```) is used for secure, modular interactions with the Sinalite API through ```thirdparty/senalite.py```
- Handles authentication and request processing through ```thirdparty/helpers.py``` and makes authenticated API calls for external services like fetching products.


### Testing and Monitoring

## 🚀 Getting Started
- **Unit Testing:** The backend is thoroughly tested using pytest, with mocks for third-party API calls (```requests_mock```).

- **Coverage Reports:** Test coverage is generated using pytest-cov to ensure reliability and minimize regressions.

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
   python backend/app.py
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
pytest -v
```
### Viewing Test Coverage

To generate and view the coverage report in console:
```bash
pytest pytest --cov=backend/server
```

To generate and view the coverage report as html:
```bash
pytest --cov=backend/server --cov-report=html
```
- The report will be available in the `htmlcov/` directory.

## 🐳 Docker (Optional)

To run the application using Docker Compose:
```bash
docker-compose up --build
```

## 📄 License

This project is licensed under the MIT License.

