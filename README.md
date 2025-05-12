# Web Blackjack (Restructured)

A multiplayer online blackjack game built with Flask and Socket.IO.

## Project Structure

The project has been restructured to follow best practices:

```
web-blackjack/
├── blackjack/              # Main package
│   ├── __init__.py         # Application factory
│   ├── models/             # Database models
│   ├── game/               # Game logic
│   ├── api/                # API routes
│   ├── web/                # Web routes
│   ├── auth/               # Authentication
│   ├── templates/          # Templates
│   └── static/             # Static files
├── config.py               # Configuration
├── requirements.txt        # Dependencies
└── run.py                  # Application runner
```

## Setup Instructions

### 1. Create Environment File

Create a `.env` file in the root directory with the following contents:

```
# Flask Configuration
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secure-secret-key

# Database Configuration
DATABASE_URL=mysql+mysqlconnector://user:password@localhost/blackjack
DEV_DATABASE_URL=sqlite:///dev-blackjack.db
TEST_DATABASE_URL=sqlite:///test-blackjack.db
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Application

```bash
python run.py
```

## API Documentation

API documentation is available at `/api/v1/doc` when the application is running.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| FLASK_APP | Application entry point | run.py |
| FLASK_ENV | Environment (development/production/testing) | development |
| SECRET_KEY | Secret key for sessions | None (required) |
| DATABASE_URL | Production database connection string | None (required for production) |
| DEV_DATABASE_URL | Development database connection string | sqlite:///dev-blackjack.db |
| TEST_DATABASE_URL | Test database connection string | sqlite:///test-blackjack.db |

## Testing

To run tests:

```bash
python -m pytest
``` 