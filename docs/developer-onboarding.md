# GoPostal SD Developer Onboarding

This is the canonical local setup guide for this repository.

## Prerequisites

- Python 3.12+
- Node.js 18+
- npm
- PostgreSQL (recommended for full local parity)

## 1. Clone and Create Environment Files

1. Clone the repository.
2. Create backend environment file:
   - Copy `backend/env.example` to `backend/.env`.
3. Create frontend environment file:
   - Create `frontend/.env`.

Do not commit `.env` files.

## 2. Configure Environment Variables

### Backend (`backend/.env`)

Required for app startup:

- `DATABASE_URL`
- `SINALITE_CLIENT_ID`
- `SINALITE_CLIENT_SECRET`

Recommended for local:

- `ENVIRONMENT=development`
- `FRONTEND_URL=http://localhost:5173`

Example:

```env
ENVIRONMENT=development
DATABASE_URL=postgresql://username:password@localhost:5432/gopostalsd_dev
FRONTEND_URL=http://localhost:5173

SINALITE_CLIENT_ID=your_sinalite_client_id
SINALITE_CLIENT_SECRET=your_sinalite_client_secret

SINALITE_BASE_URL_DEV=https://api.sinaliteuppy.com
SINALITE_BASE_URL=https://api.sinaliteuppy.com
```

Optional integrations:

- Email provider (choose one):
  - `MAILERSEND_API_KEY`
  - or `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`
- Square:
  - `SQUARE_ACCESS_TOKEN`
  - `SQUARE_APPLICATION_ID`
  - `SQUARE_LOCATION_ID`
  - `SQUARE_ENVIRONMENT=sandbox`

### Frontend (`frontend/.env`)

Minimum:

```env
VITE_API_BASE_URL=http://localhost:5000/api
```

For Square checkout UI:

```env
VITE_SQUARE_APPLICATION_ID=your_square_application_id
VITE_SQUARE_LOCATION_ID=your_square_location_id
```

## 3. Backend Setup and Run

From `backend/`:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Run migrations:

```bash
python scripts/run_migrations.py
```

Initialize seed/admin helpers (optional but useful):

```bash
python utility_scripts/setup_database.py
python utility_scripts/create_simple_admin.py
```

Start backend API:

```bash
python app.py
```

Backend base URL: `http://localhost:5000`

## 4. Frontend Setup and Run

From `frontend/`:

```bash
npm install
npm run dev
```

Frontend URL: `http://localhost:5173`

## 5. Common Local Validation

Build frontend:

```bash
cd frontend
npm run build
```

Run backend tests:

```bash
cd backend
pytest -v
```

## 6. Known Local Behavior

- If `SINALITE_CLIENT_ID` and `SINALITE_CLIENT_SECRET` are missing, backend startup fails.
- If Sinalite credentials are placeholders or invalid, external sync endpoints can return failure while app and local routes still run.
- Supabase is not required for basic local development; local uploads can be used.

## 7. Useful Links

- Documentation index: [README.md](README.md)
- Repository: https://github.com/gopostalsddev/gopostalsd
- Docs folder (GitHub): https://github.com/gopostalsddev/gopostalsd/tree/main/docs
