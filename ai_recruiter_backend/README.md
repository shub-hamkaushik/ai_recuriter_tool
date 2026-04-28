# AI Recruiter Backend

A Flask-based backend for an AI-powered resume and candidate evaluation tool.

## Features

- **User Management**: JWT-based authentication with role-based access control (Admin/HR)
- **Candidate Management**: Upload and parse resumes, store candidate data
- **Job Management**: CRUD operations for job descriptions
- **Matching Engine**: Calculate skill and experience match scores
- **AI Integration**: LLM-powered resume parsing and summary generation
- **PostgreSQL Database**: Robust data storage with SQLAlchemy ORM

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up PostgreSQL database and update `.env` file with your database URL.

3. Run the application:
   ```bash
   python run.py
   ```

## API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - Register new user (Admin only, requires JWT token)

### Candidates
- `POST /candidates/upload` - Upload resume (multipart/form-data)
- `GET /candidates/` - List candidates
- `GET /candidates/{id}` - Get candidate details
- `DELETE /candidates/{id}` - Delete candidate

### Jobs
- `POST /jobs/` - Create job
- `GET /jobs/` - List jobs
- `GET /jobs/{id}` - Get job details
- `PUT /jobs/{id}` - Update job
- `DELETE /jobs/{id}` - Delete job

### Matching
- `POST /matching/candidate/{id}` - Match candidate to all jobs
- `POST /matching/job/{id}` - Match job to all candidates
- `GET /matching/results` - Get match results
- `POST /matching/ai-summary/{candidate_id}/{job_id}` - Generate AI summary

## Database Models

- **User**: Authentication and roles
- **Candidate**: Resume data and parsed information
- **JobDescription**: Job requirements
- **MatchResult**: Stored matching scores

## Security

- JWT token authentication
- Role-based access control
- Input validation and error handling
- File upload restrictions and storage

## Authentication

All endpoints except `/auth/login` require a JWT token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```