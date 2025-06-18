# Project Dependencies

Since requirements.txt is managed by the environment, here are the dependencies for this project:

## Python Dependencies

```
flask==3.1.0
gunicorn==23.0.0
sqlparse==0.5.3
psycopg2-binary==2.9.10
email-validator==2.2.0
flask-sqlalchemy==3.1.1
```

## Frontend Dependencies (CDN)

- **Bootstrap 5**: UI framework with dark theme
  - `https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css`
  - `https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js`

- **Prism.js**: Syntax highlighting
  - `https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-dark.min.css`
  - `https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-core.min.js`
  - `https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/plugins/autoloader/prism-autoloader.min.js`

- **Feather Icons**: Icon library
  - `https://unpkg.com/feather-icons`

## Installation Commands

If setting up manually:

```bash
# Install Python dependencies
pip install flask==3.1.0
pip install gunicorn==23.0.0
pip install sqlparse==0.5.3
pip install psycopg2-binary==2.9.10
pip install email-validator==2.2.0
pip install flask-sqlalchemy==3.1.1
```

## Environment Variables

- `SESSION_SECRET`: Flask session secret (required)
- `DATABASE_URL`: PostgreSQL connection string (optional)