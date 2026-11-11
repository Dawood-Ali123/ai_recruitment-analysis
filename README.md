# TalentFlow AI – AI-Powered Recruitment Platform

TalentFlow AI is an AI-powered recruitment platform designed to simplify
the hiring process. It helps HR teams manage job postings, candidate
applications, CV processing, AI-based candidate evaluation, and final
hiring decisions.

## Key Features

### HR Features
- Create and manage job postings.
- Define job requirements and experience criteria.
- View applications for assigned jobs.
- Process candidate CVs.
- Generate AI-powered candidate evaluation reports.
- Review skill and experience matching.
- Make final hiring decisions.
- View application audit logs.
- Track email notifications.

### Candidate Features
- Register and log in securely.
- Browse available jobs.
- View job descriptions and requirements.
- Apply for jobs.
- Upload CVs in PDF and DOCX formats.
- Track application status.
- View available evaluation results and hiring updates.

### AI Features
- AI-powered CV evaluation using Groq LLM.
- Structured evaluation reports.
- Skill and experience matching.
- Missing requirement identification.
- Evidence-based recommendations.
- CV processing and evaluation status tracking.

## Technology Stack

### Backend
- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Pydantic
- JWT Authentication

### AI / LLM
- LangChain
- Groq API
- Structured LLM Output

### Frontend
- React
- TypeScript
- Vite
- Tailwind CSS
- Axios

### Infrastructure
- Docker
- Docker Compose
- Git

## Project Architecture

```text
TalentFlow AI
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   ├── services/
│   │   └── App.tsx
│   └── package.json
│
├── backend/
│   ├── app/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── prompts/
│   │   ├── routers/
│   │   ├── schemas/
│   │   └── services/
│   ├── requirements.txt
│   └── .env.example
│
├── database/
│   └── docker-compose.yml
│
├── docs/
├── tests/
├── .gitignore
└── README.md