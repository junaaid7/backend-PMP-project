# PMP Project — Backend
This repository contains the backend of the PMP (Project Management Platform), built with Python and FastAPI.
The backend provides REST APIs for authentication, organizations, projects, tasks, team members, role-based permissions, dashboard data, and the AI Assistant.

## Features
* User registration and login
* JWT authentication
* Secure password hashing
* User profile API
* Multi-tenant organization system
* Tenant-level data isolation
* Role-based access control
* Organization management
* Team member management
* Project CRUD operations
* Task CRUD operations
* Task assignment and status management
* Comments and activity tracking
* Dashboard APIs
* AI Assistant
* AI-powered project and task tools
* PostgreSQL database integration
* Async database operations
* API documentation with Swagger

## Technology Stack
* Python
* FastAPI
* SQLAlchemy
* Pydantic
* PostgreSQL
* AsyncPG
* JWT
* Argon2
* Uvicorn
* Docker

## Database
The application uses PostgreSQL as its database.
SQLAlchemy is used as the ORM and supports asynchronous database operations.

Main data areas include:
* Users
* Organizations
* Projects
* Tasks
* Comments
* Activity records
* Roles and permissions

## Authentication
The backend uses JWT-based authentication.
Passwords are hashed before being stored in the database.

## Multi-Tenant Security
The backend is designed around organization-level tenant isolation.
Application queries are scoped to the authenticated user's organization to prevent unauthorized access to data belonging to another organization.
The system also uses role-based permissions for different user roles.

Supported roles include:
* Owner
* Admin
* Manager
* Developer
* Viewer

## AI Assistant
The backend provides the AI Assistant with controlled tools for project management operations.
Available operations include:
* Create task
* Update task
* List projects
* Get project summary
* Assign user
* Generate report

AI tool operations are processed through the backend so that authentication, permissions, and tenant isolation can be applied.

## API Documentation
When the backend is running, FastAPI automatically provides Swagger documentation at:
http://localhost:8000/docs

Alternative API documentation:
http://localhost:8000/redoc


## Running Locally

Create and activate a virtual environment:
python -m venv venv
.\venv\Scripts\Activate.ps1

Install dependencies:
pip install -r requirements.txt

Configure the required environment variables.

Start the FastAPI server:
python -m uvicorn app.main:app --reload

The backend will normally be available at:
http://localhost:8000

## Running with Docker
The backend includes a Dockerfile and can be started through the project's Docker Compose configuration:
docker compose up -d --build

The API runs on:
http://localhost:8000

## Environment Variables
Sensitive values should be stored in environment variables and should not be committed to GitHub.
Example:
DATABASE_URL=
JWT_SECRET=
JWT_ALGORITHM=HS256
OPENAI_API_KEY=


## AI-Assisted Development
AI tools were used during development as a guidance and learning resource.
They were used to understand FastAPI concepts, debug errors, explore solutions, and improve implementation approaches.
The backend code was not simply copied and pasted from AI. The implementation was understood, written, modified, tested, and integrated as part of the development process.

## Related Repositories

The frontend source code is maintained separately in:
frontend-PMP-project

The combined frontend and backend source code is also available in:
PMP-project

## Author
**Muhammad Junaid**

BS Software Engineering
Full-Stack / MERN Developer
