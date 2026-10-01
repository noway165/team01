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

## Run locally

Requirements: Podman 4 or later with a compose provider (`podman compose version` must print a version),
or Docker Desktop. On Windows / macOS the Podman machine must be running (`podman machine start`).

1. `git clone https://github.com/noway165/team01.git`
2. `cd team01`
3. `cp .env.example .env` (PowerShell: `Copy-Item .env.example .env`), then open `.env` and set
   `DB_PASSWORD` — letters and digits only. Leave the other lines as they are.
4. `podman compose up --build`
5. Open http://localhost:3000 — database check: http://localhost:3000/health/db
   should return `{"db":"ok","notes":1}` on the first start.

The first build can take several minutes; wait until the `web` service logs `Uvicorn running on http://0.0.0.0:8000`.

The web port is published as `127.0.0.1:3000:8000` (only this laptop can reach it). Plain `3000:8000`
did not work on one teammate's Windows machine with Podman 6.0.2.

| Action | Command |
|---|---|
| Start in the background | `podman compose up --build -d` |
| Status | `podman compose ps` |
| Logs | `podman compose logs web` |
| Stop (data kept) | `podman compose down` |
| Reset the database (data lost) | `podman compose down -v` |

Choose `DB_PASSWORD` before the first start and keep it: PostgreSQL stores the password when the volume is
created, so changing it later gives `password authentication failed` until you run `down -v`.

## Run it without containers

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
| `Dockerfile`, `.dockerignore` | Builds the `web` image (Lab 2). |
| `compose.yml` | Starts `web` and a PostgreSQL `db` with one command (Week 4). |
| `db/init.sql` | Creates the `notes` table the first time the database volume is created. |
| `tests/` | Tests run by `pytest`, and by the pipeline from Week 6. |
| `.env.example` | Every environment variable the app reads, with no secret values. |
| `TEAM.md` | Team members. |
| `notes/` | Personal notes, one file per person. |

## Endpoints

| Method | Path | Returns |
|---|---|---|
| GET | `/` | App name, version and a greeting |
| GET | `/health` | `{"status": "ok"}` — used by Render and the pipeline |
| GET | `/health/db` | `{"db": "ok", "notes": N}` — proves the app can reach PostgreSQL |
| GET / POST | `/vehicles` | List / add vehicles |
| GET / POST | `/maintenance-records` | List / add maintenance records |
| POST | `/diagnose` | Symptom diagnosis (placeholder) |
| GET | `/docs` | Interactive API documentation |

## Environment variables

| Name | Needed from | Meaning |
|---|---|---|
| `APP_NAME` | optional | Name shown by `/` |
| `DB_PASSWORD` | Week 4 | PostgreSQL password, read by `compose.yml` from `.env` |
| `DATABASE_URL` | Week 4 | PostgreSQL connection string. Set by `compose.yml` (host `db`); set it yourself only when running without containers |
