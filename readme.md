# GoPostal SD

GoPostal SD is a full-stack web application for print, shipping, pricing, and order workflows.

- Frontend: React + Vite + MUI
- Backend: Flask + SQLAlchemy + Flask-Migrate
- Integrations: Sinalite, Square, MailerSend/SMTP, Supabase

## Developer Setup

Use [docs/developer-onboarding.md](docs/developer-onboarding.md) for all local setup and run instructions.

That guide is the single source of truth for:
- Environment variables
- Backend/frontend startup
- Migrations and admin bootstrap scripts
- Local testing and validation
- Optional integrations

## Repository Structure

```text
gopostalsd/
├── backend/                # Flask API, models, routes, migrations, tests
│   ├── app.py
│   ├── requirements.txt
│   ├── migrations/
│   ├── scripts/
│   ├── utility_scripts/
│   └── server/
├── frontend/               # React application (Vite)
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── App.jsx
│       ├── main.jsx
│       ├── components/
│       ├── pages/
│       ├── services/
│       └── ...
├── docs/                   # Architecture and integration documentation
├── diagrams/
├── docker-compose.yaml
└── render.yaml
```

## Documentation

- Documentation index: [docs/README.md](docs/README.md)
- Developer onboarding: [docs/developer-onboarding.md](docs/developer-onboarding.md)
- API endpoints: [docs/api-endpoints.md](docs/api-endpoints.md)
- Server architecture: [docs/server-architecture.md](docs/server-architecture.md)
- Sinalite adapter: [docs/sinalite-adapter.md](docs/sinalite-adapter.md)
- Square adapter: [docs/square-adapter.md](docs/square-adapter.md)
- SMTP adapter: [docs/smtp-adapter.md](docs/smtp-adapter.md)
- MailerSend adapter: [docs/mailersend-adapter.md](docs/mailersend-adapter.md)
- Supabase adapter: [docs/supabase-adapter.md](docs/supabase-adapter.md)

## Local API Docs

When the backend is running locally, Swagger UI is available at:

- `http://localhost:5000/`

## Optional Docker Usage

```bash
docker compose up --build
```

## License

This project is licensed under the MIT License.

