# Emiva Ingestion

A Flask-based webhook ingestion service for collecting raw data from GitHub, Slack, and Jira. This service acts as a centralized collector, receiving events via webhooks and storing them in a persistent database for further processing.

## 🚀 Features

- **Multi-Source Support**: Dedicated endpoints for GitHub, Slack, and Jira webhooks.
- **Persistent Storage**: Uses SQLite with SQLAlchemy for robust data management.
- **Health Monitoring**: Integrated `/health` endpoint for status checks.
- **Modular Architecture**: Separate connectors for each data source for easy extensibility.

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

## 🏃 Usage

Start the Flask application:

```bash
python main.py
```

The server will start on `http://localhost:5000`.

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
│   ├── github_connector.py
│   ├── slack_connector.py
│   └── jira_connector.py
├── database/           # Database schema and initialization
│   └── db.py
├── main.py             # Application entry point and routing
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

3. **Update Endpoints**:
   Take the new URL from the ngrok terminal and update your Webhook settings in GitHub, Slack, and Jira.

## 📌 Pro Tip: Use a Free Static Domain
To avoid updating your endpoints every time you restart, ngrok now offers **one free static domain** for all accounts.

1. Go to your [ngrok Dashboard > Domains](https://dashboard.ngrok.com/cloud-edge/domains).
2. Create your free domain (e.g., `your-name.ngrok-free.app`).
3. Start ngrok with this domain instead:
   ```bash
   ngrok http --domain=your-name.ngrok-free.app 5000
   ```
4. Update your webhooks **once** with this static URL, and you'll never have to change them again!

## 🤝 Contributing
