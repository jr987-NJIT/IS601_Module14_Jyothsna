# Secure User Management API with Calculation Model

A FastAPI application implementing secure user management with password hashing, PostgreSQL database integration, calculation model with factory pattern, comprehensive testing, and CI/CD pipeline.

## 🚀 Features

### Module 10 Features
- **Secure User Registration**: User accounts with hashed passwords using bcrypt
- **SQLAlchemy ORM**: Database models with unique constraints for username and email
- **Pydantic Validation**: Request/response validation with type safety
- **Comprehensive Testing**: Unit and integration tests with pytest
- **CI/CD Pipeline**: Automated testing and Docker image deployment via GitHub Actions
- **Docker Support**: Containerized application with Docker and Docker Compose
- **RESTful API**: FastAPI endpoints for user CRUD operations

### Module 11 Features (New)
- **Calculation Model**: SQLAlchemy model for storing mathematical operations (Add, Subtract, Multiply, Divide)
- **Factory Pattern**: Extensible calculation factory for operation handling
- **Calculation Schemas**: Pydantic validation with division-by-zero protection
- **User-Calculation Relationship**: Foreign key relationship with cascade deletion
- **Comprehensive Calculation Tests**: Unit and integration tests for calculations
- **Enhanced CI/CD**: Updated pipeline to test all calculation functionality

### Module 12 Features (New)
- **User Endpoints**: Registration and Login endpoints.
- **Calculation Endpoints**: BREAD (Browse, Read, Edit, Add, Delete) operations for calculations.
- **Integration Testing**: Comprehensive integration tests for User and Calculation routes.
- **CI/CD Maintenance**: Continuous integration and deployment to Docker Hub.

### Module 13 Features
- **JWT Authentication**: Secure login and registration with JWT tokens.
- **Front-End Pages**: HTML/JS pages for user registration and login with client-side validation.
- **Playwright E2E Tests**: End-to-end testing for user flows.
- **Static Files**: Serving static assets with FastAPI.

### Module 14 Features (New)
- **Complete BREAD Endpoints for Calculations**: Browse, Read, Edit, Add, Delete operations with user authentication.
- **User-Scoped Calculations**: All calculation endpoints filtered by logged-in user.
- **Calculations Front-End**: Full-featured HTML/JS interface for managing calculations.
- **Comprehensive E2E Tests**: Playwright tests covering positive and negative scenarios for all BREAD operations.
- **Security**: JWT-based authentication required for all calculation operations.
- **Client-Side Validations**: Input validation for numeric values, operation types, and division by zero.

## 📋 Prerequisites

- Python 3.11+
- Docker and Docker Compose
- PostgreSQL (or use Docker Compose)
- Git

## 🛠️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/jr987-NJIT/IS601_Module10_Jyothsna.git
cd IS601_Module10_Jyothsna
```

### 2. Create Environment File

```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/userdb
SECRET_KEY=your-secret-key-here
ENVIRONMENT=development
```

### 3. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

## 🏃 Running the Application

### Option 1: Using Docker Compose (Recommended)

```bash
docker-compose up --build
```

The API will be available at `http://localhost:8000`

### Option 2: Local Development

```bash
# Start PostgreSQL (or use Docker)
docker run -d --name postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=userdb \
  -p 5432:5432 \
  postgres:15-alpine

# Run the application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🧪 Running Tests

### Run All Tests

```bash
pytest
```

### Run Specific Test Categories

```bash
# Unit tests only (security, schemas, calculation factory, and calculation schemas)
pytest tests/test_security.py tests/test_schemas.py tests/test_calculation_factory.py tests/test_calculation_schemas.py -v

# Integration tests only (includes calculation database operations)
pytest tests/test_integration.py -v

# Run only calculation-related tests
pytest tests/test_calculation_factory.py tests/test_calculation_schemas.py -v
```

### Run Tests with Coverage

```bash
pip install pytest-cov
pytest --cov=app --cov-report=html --cov-report=term-missing
```

View coverage report by opening `htmlcov/index.html` in your browser.

### Test Categories

- **Unit Tests**: 
  - `test_security.py`: Password hashing and verification
  - `test_schemas.py`: User schema validation
  - `test_calculation_factory.py`: Calculation factory pattern and operations (Module 11)
  - `test_calculation_schemas.py`: Calculation schema validation with division by zero checks (Module 11)

- **Integration Tests**: `test_integration.py`
  - User creation with database constraints
  - Calculation model database operations with factory pattern (Module 11)
  - User-Calculation relationship and cascade deletion (Module 11)
  - Email uniqueness validation
  - Username uniqueness validation
  - API endpoint functionality
  - Password security in database

## 📚 API Documentation

Once the application is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### API Endpoints

#### Public Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root endpoint |
| GET | `/health` | Health check |
| POST | `/users/register` | Register new user |
| POST | `/users/login` | Login user and get JWT token |

#### Protected Endpoints (Requires JWT Token)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/calculations/` | Browse: List all calculations for logged-in user |
| GET | `/calculations/{id}` | Read: Get specific calculation by ID |
| POST | `/calculations/` | Add: Create new calculation |
| PUT | `/calculations/{id}` | Edit: Update calculation (full update) |
| PATCH | `/calculations/{id}` | Edit: Update calculation (partial update) |
| DELETE | `/calculations/{id}` | Delete: Remove calculation |

### Example Usage

**Register a User:**
```bash
curl -X POST "http://localhost:8000/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "johndoe@example.com",
    "password": "securepassword123"
  }'
```

**Login and Get Token:**
```bash
curl -X POST "http://localhost:8000/users/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "password": "securepassword123"
  }'
```

**Create a Calculation (Requires Token):**
```bash
curl -X POST "http://localhost:8000/calculations/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "a": 10.5,
    "b": 5.2,
    "type": "Add"
  }'
```

**Get All Calculations (Requires Token):**
```bash
curl "http://localhost:8000/calculations/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 📊 Calculation Model (Module 11)

The Calculation model stores mathematical operations with the following fields:
- `id`: Primary key
- `a`: First operand (float)
- `b`: Second operand (float)
- `type`: Operation type (Add, Subtract, Multiply, Divide)
- `result`: Computed result
- `user_id`: Optional foreign key to users table
- `created_at`: Timestamp

### Factory Pattern Implementation

The `CalculationFactory` implements the Factory design pattern:

```python
from app.utils import CalculationFactory
from app.schemas.calculation import CalculationType

# Execute calculation using factory
result = CalculationFactory.calculate(CalculationType.ADD, 10.5, 5.2)
print(result)  # 15.7

# Get supported operations
operations = CalculationFactory.get_supported_operations()
print(operations)  # ['Add', 'Subtract', 'Multiply', 'Divide']
```

### Pydantic Validation

The `CalculationCreate` schema includes validation:
- Division by zero is prevented
- Valid operation types enforced (Add, Subtract, Multiply, Divide)
- Type safety for operands

```python
from app.schemas import CalculationCreate, CalculationType

# Valid calculation
calc = CalculationCreate(a=10.0, b=5.0, type=CalculationType.DIVIDE)

# This will raise ValidationError
calc = CalculationCreate(a=10.0, b=0.0, type=CalculationType.DIVIDE)
```

## 🐳 Docker Hub

The Docker image is automatically built and pushed to Docker Hub via GitHub Actions.

**Docker Hub Repository**: Replace with your Docker Hub repository link

### Pull and Run the Image

```bash
# Pull the latest image
docker pull [your-dockerhub-username]/secure-user-api:latest

# Run the container
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://postgres:postgres@host.docker.internal:5432/userdb \
  [your-dockerhub-username]/secure-user-api:latest
```

## 🔄 CI/CD Pipeline

The project uses GitHub Actions for continuous integration and deployment:

### Workflow Steps

1. **Test Job**
   - Runs on every push and pull request
   - Sets up Python 3.11 environment
   - Spins up PostgreSQL test database
   - Runs unit tests (security, schemas, calculation factory, calculation schemas)
   - Runs integration tests (user and calculation database operations)
   - Generates coverage report
   - Uploads coverage to Codecov

2. **Build and Push Job** (main branch only)
   - Builds Docker image with latest code
   - Pushes to Docker Hub with tags:
     - `latest`
     - Git SHA
     - Semantic version (if tagged)
   - Uses caching for faster builds

### Setting Up CI/CD

Add the following secrets to your GitHub repository (Settings → Secrets → Actions):

- `DOCKER_USERNAME`: Your Docker Hub username
- `DOCKER_PASSWORD`: Your Docker Hub access token

## 🏗️ Project Structure

```
IS601_Module10_Jyothsna/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI application
│   ├── database.py                  # Database configuration
│   ├── models/
│   │   ├── __init__.py              # User and Calculation models
│   │   ├── user.py                  # Model exports
│   │   └── calculation.py           # Calculation model (Module 11)
│   ├── schemas/
│   │   ├── __init__.py              # Pydantic schemas
│   │   ├── user.py                  # Schema exports
│   │   └── calculation.py           # Calculation schemas (Module 11)
│   └── utils/
│       ├── __init__.py              # Utilities exports
│       ├── security.py              # Password hashing
│       └── calculation_factory.py   # Factory pattern (Module 11)
├── tests/
│   ├── __init__.py
│   ├── test_security.py             # Unit tests for security
│   ├── test_schemas.py              # Unit tests for user schemas
│   ├── test_calculation_factory.py  # Unit tests for factory (Module 11)
│   ├── test_calculation_schemas.py  # Unit tests for calc schemas (Module 11)
│   └── test_integration.py          # Integration tests (includes calculations)
├── .github/
│   └── workflows/
│       └── ci-cd.yml                # GitHub Actions workflow
├── .env.example                     # Environment variables template
├── .gitignore
├── docker-compose.yml               # Docker Compose configuration
├── Dockerfile                       # Docker image definition
├── pytest.ini                       # Pytest configuration
├── requirements.txt                 # Python dependencies
├── README.md
└── REFLECTION.md                    # Module 11 reflection
```

## 🔒 Security Features

- **Password Hashing**: All passwords are hashed using bcrypt before storage
- **No Plain Text**: Passwords never stored or returned in plain text
- **Unique Constraints**: Database-level uniqueness for usernames and emails
- **Input Validation**: Pydantic schemas validate all input data
- **SQL Injection Protection**: SQLAlchemy ORM prevents SQL injection
- **Environment Variables**: Sensitive data stored in environment variables

## 🧩 Technologies Used

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **PostgreSQL**: Relational database
- **Pydantic**: Data validation using Python type hints
- **Passlib**: Password hashing library with bcrypt
- **Pytest**: Testing framework
- **Docker**: Containerization
- **GitHub Actions**: CI/CD automation
- **Trivy**: Security vulnerability scanning

## 📝 Testing Strategy

### Unit Tests
- Test individual functions in isolation
- Mock external dependencies
- Focus on business logic and validation

### Integration Tests
- Test full request/response cycle
- Use real database (SQLite for tests)
- Verify database constraints
- Test API endpoints end-to-end

## 🧪 Running Tests

To run the integration tests locally:

```bash
pytest tests/test_integration.py
```

## 🔍 Manual Checks via OpenAPI

1.  Start the application:
    ```bash
    uvicorn app.main:app --reload
    ```
2.  Open your browser and navigate to `http://localhost:8000/docs`.
3.  **User Registration**: Use `POST /users/register` to create a new user.
4.  **User Login**: Use `POST /users/login` to authenticate.
5.  **Calculations**:
    *   Use `POST /calculations` to create a calculation.
    *   Use `GET /calculations` to list all calculations.
    *   Use `GET /calculations/{id}` to view a specific calculation.
    *   Use `PUT /calculations/{id}` to update a calculation.
    *   Use `DELETE /calculations/{id}` to delete a calculation.

## 🖥️ Front-End Access

1.  Start the application:
    ```bash
    uvicorn app.main:app --reload
    ```
2.  Open your browser:
    *   **Register**: `http://localhost:8000/static/register.html`
    *   **Login**: `http://localhost:8000/static/login.html`
    *   **Calculations Dashboard** (after login): `http://localhost:8000/static/calculations.html`

### Front-End Features

The Calculations Dashboard (`calculations.html`) provides:
- **Add New Calculation**: Form to create calculations with operation selection (Add, Subtract, Multiply, Divide)
- **Browse Calculations**: Table displaying all calculations with results and timestamps
- **Edit Calculation**: Modal form to update existing calculations
- **Delete Calculation**: Remove calculations with confirmation
- **Client-Side Validation**: Numeric input validation and division by zero prevention
- **Real-Time Updates**: Automatic table refresh after operations
- **User Authentication**: JWT token-based access control with automatic redirect to login if not authenticated

## 🎭 Running E2E Tests

To run the Playwright end-to-end tests:

1.  Install Playwright browsers:
    ```bash
    playwright install
    ```
2.  Ensure the server is running in a separate terminal:
    ```bash
    uvicorn app.main:app --reload
    ```
3.  Run the tests:
    ```bash
    pytest tests/test_e2e.py
    ```

## 🐳 Docker Hub Repository

[Link to Docker Hub Repository](https://hub.docker.com/repository/docker/YOUR_USERNAME/secure-user-api)

## 🎓 Learning Outcomes Addressed

### Module 10
- **CLO3**: Automated testing with pytest
- **CLO4**: GitHub Actions CI/CD pipeline
- **CLO9**: Docker containerization
- **CLO11**: SQL database integration with SQLAlchemy
- **CLO12**: JSON serialization with Pydantic
- **CLO13**: Secure authentication with password hashing

### Module 11
- **CLO3**: Extended automated testing for calculation models
- **CLO4**: Enhanced CI/CD pipeline with calculation tests
- **CLO9**: Updated Docker image with calculation functionality
- **CLO11**: Calculation model with foreign key relationships
- **CLO12**: Calculation schema validation and serialization
- **Design Patterns**: Factory pattern implementation for extensibility

### Module 12
- **CLO10**: Complete REST API with BREAD operations
- **CLO11**: Enhanced database relationships and operations
- **CLO3**: Comprehensive integration tests for API endpoints

### Module 13
- **CLO13**: JWT-based authentication and authorization
- **CLO10**: Secure REST API endpoints with token validation
- **CLO3**: End-to-end testing with Playwright

### Module 14 (New)
- **CLO3**: Create Python applications with automated testing (comprehensive E2E tests)
- **CLO4**: GitHub Actions for CI with automated tests and Docker builds
- **CLO9**: Containerization with Docker for complete BREAD application
- **CLO10**: Create, consume, and test REST APIs with complete BREAD operations
- **CLO11**: Integrate with SQL databases for user-scoped calculation data
- **CLO12**: Serialize, deserialize, and validate JSON using Pydantic
- **CLO13**: Secure authentication and authorization with JWT, encryption, hashing, and encoding

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 👤 Author

Jyothsna Reddy
- GitHub: [@jr987-NJIT](https://github.com/jr987-NJIT)
- Repository: [IS601_Module10_Jyothsna](https://github.com/jr987-NJIT/IS601_Module10_Jyothsna)

## 🙏 Acknowledgments

- Course: IS601 - Web Systems Development
- Institution: NJIT
- Module 10: Secure User Authentication
- Module 11: Calculation Model with Factory Pattern
- Module 12: BREAD API Endpoints
- Module 13: JWT Authentication & Front-End
- Module 14: Complete BREAD Functionality with Authentication

---

**Note**: This application demonstrates a complete full-stack application with:
- Secure JWT-based authentication
- User-scoped data management
- Complete BREAD operations for calculations
- Comprehensive testing (unit, integration, and E2E)
- CI/CD pipeline with automated testing and Docker deployment
- Modern, responsive front-end interface

---

**Note**: Remember to update the Docker Hub repository URL and add your Docker Hub credentials to GitHub secrets before pushing to the main branch.
