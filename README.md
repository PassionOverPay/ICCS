# CommonGround Lite

CommonGround Lite is a small community proposal and voting platform for university groups. It uses React/TypeScript/Vite/Tailwind on the frontend and FastAPI/SQLAlchemy/PostgreSQL on the backend.

## Run locally

```bash
docker compose up --build
```

The frontend is available at http://localhost:5173 and the API at http://localhost:8000. For local development without Docker, install `backend/requirements.txt`, set `DATABASE_URL` and `SECRET_KEY` in `backend/.env`, run `uvicorn app.main:app --reload` from `backend`, and run `npm install && npm run dev` from `frontend`.

## Design choices

- **Freedom and order:** members can submit proposals and participate in discussion, while administrators can remove inappropriate comments and manage membership. Authorization is enforced by the API.
- **Openness and privacy:** proposals, comments, and aggregate votes are visible to community members; only the minimum account data (username, email, password hash) is stored.
- **Productivity and synergy:** proposals turn discussion into decisions, while comments provide a space to improve ideas before voting.
- **Ownership:** proposals, comments, and votes are associated with their authors; passwords are never returned by the API.

## Data model

Users create communities and join them through unique memberships. Communities contain proposals; proposals contain comments and one vote per user. PostgreSQL uniqueness and check constraints prevent duplicate memberships, duplicate votes, and invalid vote values. Alembic is included for schema migrations; the application also creates tables on startup for a simple first-run experience.
