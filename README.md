
TaskFlow

TaskFlow is a full-stack AI-assisted task management platform.

Project Structure

- "backend/app" - FastAPI backend
- "database.py" - Database configuration
- "models.py" - SQLAlchemy database models
- "schemas.py" - Pydantic schemas
- "main.py" - FastAPI application
- "algorithms.py" - Sorting and searching algorithms
- "check_algorithms.py" - Automated algorithm tests
- "benchmark.py" - Algorithm benchmark
- "frontend" - HTML, CSS and JavaScript frontend

Algorithms

TaskFlow implements:

- Insertion Sort
- Binary Search
- Linear Search

Priority ranking:

- low = 1
- medium = 2
- high = 3

API

Important endpoints:

- "GET /"
- "POST /users"
- "GET /users"
- "POST /projects"
- "GET /projects"
- "POST /tasks"
- "GET /tasks"
- "GET /tasks/sorted"
- "GET /tasks/search"
- "GET /tasks/{task_id}"
- "PUT /tasks/{task_id}"
- "DELETE /tasks/{task_id}"
- "GET /projects/{project_id}/stats"
- "POST /tasks/quick-add"

AI Quick-Add

TaskFlow provides an AI-assisted Quick-Add endpoint that converts plain-English task descriptions into structured tasks.

Endpoint:

"POST /tasks/quick-add"

Request example:

{
  "description": "Fix inventory urgently tomorrow",
  "project_id": 1
}

The rule-based parser detects:

- Priority: low, medium or high
- Due-date hints: today, tomorrow, next Friday or next week
- Task title from the original description

Testing

Run the automated algorithm checks from the backend app directory:

python check_algorithms.py

The checks verify:

- Insertion sort
- Binary search
- Linear search
- Comparison counts

Running the Backend

From the "backend" directory:

uvicorn app.main:app --reload

The API will be available at:

"http://127.0.0.1:8000"

Swagger documentation:

"http://127.0.0.1:8000/docs"

Running the Frontend

From the "frontend" directory:

python -m http.server 5500

Then open:

"http://127.0.0.1:5500"

Frontend Features

- Add tasks
- Edit tasks
- Delete tasks
- Task validation
- Priority selection
- Due-date input
- LocalStorage task caching
- Backend API integration
- Responsive layout

CORS

The backend allows the frontend origins:

- "http://127.0.0.1:5500"
- "http://localhost:5500"

Project Status

TaskFlow backend and frontend have been tested for the required CRUD, algorithms, statistics and AI Quick-Add functionality.