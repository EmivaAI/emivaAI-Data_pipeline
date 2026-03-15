# Emiva Ingestion

A Flask-based webhook ingestion service for collecting raw data from GitHub, Slack, and Jira. This service follows a decoupled architecture ensuring data integrity and extensibility.

## 🚀 Features

- **Multi-Source Support**: Dedicated endpoints for GitHub, Slack, and Jira webhooks.
- **Service Layer Architecture**: Decoupled API and Database layers for better processing logic.
- **Configurable Storage**: Database URL can be set via environment variables.
- **Persistent Storage**: Uses SQLite with SQLAlchemy for robust data management.
- **Health Monitoring**: Integrated `/health` endpoint for status checks.
- **Diagnostics**: Built-in `view_data.py` tool for inspecting stored records.

## 🏗️ Architecture

The service follows a strict data flow:
**API Layer** (Flask) → **Service Layer** (WebhookService) → **Database Layer** (SQLAlchemy)

This ensures that the API endpoints are only responsible for receiving requests, while business logic and persistence are handled separately.

## 🛠️ Prerequisites

- Python 3.8+
- pip (Python package installer)

## 📦 Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd emiva-ingestion
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ Configuration

The application can be configured using environment variables:

| Variable | Description | Default |
| :--- | :--- | :--- |
| `DATABASE_URL` | SQLAlchemy connection string | `sqlite:///.../ingestion.db` |

## 🏃 Usage

Start the Flask application:

```bash
python main.py
```

The server will start on `http://localhost:5000`.

### Viewing Data
To inspect the latest records stored in the database, run:
```bash
python view_data.py
```

## 🛣️ Endpoints

| Endpoint | Method | Source | Description |
| :--- | :--- | :--- | :--- |
| `/webhooks/github` | `POST` | GitHub | Receives GitHub event webhooks |
| `/webhooks/slack` | `POST` | Slack | Receives Slack event webhooks |
| `/webhooks/jira` | `POST` | Jira | Receives Jira issue/sprint webhooks |
| `/health` | `GET` | N/A | Returns the service health status |

## 📁 Project Structure

```text
emiva-ingestion/
├── connectors/         # Webhook handler logic for each source
├── database/           # Database schema and SQLAlchemy setup
├── services/           # Service layer for business logic
├── config.py           # Configuration management
├── main.py             # Application entry point and routing
├── view_data.py        # Database inspection tool
├── requirements.txt    # Project dependencies
└── README.md           # This file
```

## 🔄 How to Restart

1. **Start the Flask Server**:
   ```bash
   .\venv\Scripts\activate
   python main.py
   ```

2. **Start ngrok**:
   ```bash
   ngrok http 5000
   ```
