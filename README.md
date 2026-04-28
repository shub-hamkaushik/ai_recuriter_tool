# AI Resume Tool

This project is a web application that evaluates resumes based on job descriptions using AI.

- Frontend: Angular
- Backend: Flask (Python)
## Screenshots
<img width="1360" height="684" alt="loginpage" src="https://github.com/user-attachments/assets/009e2e4b-463b-43d6-b026-22891f4f76fb" />
<img width="1334" height="628" alt="Dashboard" src="https://github.com/user-attachments/assets/e56ef0bc-4c2c-4d32-975a-a20a51975e40" />
<img width="1341" height="637" alt="Candidates" src="https://github.com/user-attachments/assets/76d6f3a6-5d42-4438-a45c-4aec20b83a6b" />
<img width="1230" height="651" alt="Jobs" src="https://github.com/user-attachments/assets/de99f02b-6a50-44d2-a638-794366389471" />
<img width="1355" height="638" alt="matching" src="https://github.com/user-attachments/assets/4c01c61e-678e-47fe-82d7-9c2b5eed2452" />
<img width="1351" height="618" alt="matching1" src="https://github.com/user-attachments/assets/2f9e5203-85b6-4571-8e28-4fc725d44e5f" />
<img width="1338" height="614" alt="Usermanagemnt" src="https://github.com/user-attachments/assets/11059645-43b9-4fae-962f-42b0fb87fc15" />
<img width="1344" height="628" alt="admin" src="https://github.com/user-attachments/assets/8bb086ac-9932-4802-a990-9c2dd1fd1e12" />







## Features

- Upload resumes
- Match resumes with job descriptions
- Store candidate data
- Display results in UI

- ## Tech Stack

- Angular
- Flask
- PostgreSQL
- REST API

- ## Setup Instructions

### 1. Clone the repository
git clone https://github.com/shub-hamkaushik/ai_recuriter_tool

---

### 2. Backend Setup
cd backend
pip install -r requirements.txt

Create .env file:
DB_HOST=localhost
DB_USER=postgres
DB_PASSWORD=yourpassword

Run server:
flask run

---

### 3. Frontend Setup
cd frontend
npm install
ng serve

## Database Setup

- Create PostgreSQL database
- Update credentials in .env file

## Common Issues

- Make sure PostgreSQL is running
- Run backend before frontend
