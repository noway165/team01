# SDP Starter

Starter application for **72ITDS30103 Software Development Platforms** (Van Lang University, FIT).
A small FastAPI web API that you will containerise, connect to a database, deploy and test
during the course.

## Get your own copy (Week 2, one member per team)

1. On this page, click **Use this template → Create a new repository**.
2. Owner: your account. Name: your team's repository name. Visibility: **Public**.
3. Click **Create repository**.
4. In the new repository: **Settings → Collaborators → Add people**, and add each teammate.
5. Everyone clones the new repository over SSH:

   ```bash
   git clone git@github.com:<owner>/<team-repo>.git
   ```

Do not fork this repository and do not push to it — work only in your team's copy.

## Run it on your machine

In Git Bash, from the repository folder:

```bash
python -m venv .venv
source .venv/Scripts/activate        # Windows Git Bash
# source .venv/bin/activate          # macOS / Linux
pip install -r requirements-dev.txt
python -m uvicorn app.main:app --port 8000
```

Open http://localhost:8000 — you should see a JSON greeting.
Also try http://localhost:8000/health and http://localhost:8000/docs.
Press Ctrl+C to stop.

## Run locally

Requirements: Podman 4 or later with a compose provider (or Docker Desktop).

1. `git clone git@github.com:noway165/team01.git`
2. `cd team01`
3. `cp .env.example .env` — then set `DB_PASSWORD` (letters and digits only)
4. `podman compose up --build`
5. Open http://127.0.0.1:3000 — database check: http://127.0.0.1:3000/health/db

Note: this machine needs `127.0.0.1:3000:8000` in `compose.yml` instead of `3000:8000` due to a Podman 6.0.2 port-publishing issue on Windows.

Stop: `podman compose down`
Reset the database (data lost): `podman compose down -v`

## Run the tests

```bash
pytest
```

## What is in here

| Path | What it is |
|---|---|
| `app/main.py` | The application. The FastAPI object is called `app`, so the start command is `app.main:app`. |
| `requirements.txt` | Packages the app needs to run. This is what the Dockerfile installs. |
| `requirements-dev.txt` | Extra packages for testing only. |
| `tests/` | Tests run by `pytest`, and by the pipeline from Week 6. |
| `.env.example` | Every environment variable the app reads, with no secret values. |
| `TEAM.md` | Team members. |
| `notes/` | Personal notes, one file per person. |

## Endpoints

| Method | Path | Returns |
|---|---|---|
| GET | `/` | App name, version and a greeting |
| GET | `/health` | `{"status": "ok"}` — used by Render and the pipeline |
| GET | `/vehicles` | List all vehicles |
| POST | `/vehicles` | Create a vehicle |
| GET | `/maintenance-records` | List all maintenance records |
| POST | `/maintenance-records` | Create a maintenance record |
| POST | `/diagnose` | Placeholder — AI diagnosis, not yet implemented |
| GET | `/health/db` | `{"db": "ok", "notes": N}` — proves the database connection works |
| GET | `/docs` | Interactive API documentation |

## Environment variables

| Name | Needed from | Meaning |
|---|---|---|
| `APP_NAME` | optional | Name shown by `/` |
| `DATABASE_URL` | Week 4 | PostgreSQL connection string |
