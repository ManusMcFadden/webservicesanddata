# ATP Tennis Data API

A high-performance REST API built with FastAPI and SQLAlchemy to manage and analyze professional tennis data from the ATP Tour. This project transforms raw CSV datasets into a normalized relational database with advanced analytical endpoints and secure access controls.

---

## Project Overview

This API provides a centralized interface for querying player profiles, match statistics, and historical rankings. Beyond standard CRUD operations, it features custom analytical engines to calculate Head-to-Head rivalries and all-time Hall of Fame leaderboards.

### Key Features

- **Normalized Database (3NF)**: Optimized SQLite schema that eliminates data redundancy by separating player metadata from match records.
- **OAuth2 & JWT Security**: Role-based access control protecting write operations (POST, PATCH, DELETE) using industry-standard JSON Web Tokens.
- **Professional Error Handling**: Explicitly documented HTTP status codes (200, 201, 401, 404, 422) for clear client-side debugging.
- **Interactive Documentation**: Fully documented with Swagger UI and ReDoc, featuring an integrated "Authorize" flow for testing secure routes.

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | FastAPI |
| ORM | SQLAlchemy |
| Security | OAuth2 (Password Flow) & JWT |
| Hashing | Bcrypt (passlib) |
| Database | SQLite |
| Validation | Pydantic |

---

## Setup & Installation

### 1. Clone the Repository

```bash
git clone https://github.com/ManusMcFadden/webservicesanddata.git
cd tennis-atp-api
```

### 2. Create a Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the API

```bash
fastapi dev main.py
```

The server will start at `http://127.0.0.1:8000`.

---

## Web Access

This API has been deployed on Google Cloud.

Web Access is available at https://webservicesanddata-1083314966502.europe-west9.run.app/docs

## Usage

On the /docs webpage, you should click the Authorize button and enter the username "admin" and password "tennis_password_2024" for access to all endpoints. To use them click the try me out button, enter input details where necessary, and click execute. If you only want access to GET endpoints, use the public signup endpoint to create a username and password, then use it to login with the authorize button.

## API Documentation

The full technical specification for this API, including example payloads and response schemas, is available in the [API_Documentation.pdf](./API_Documentation.pdf) file included in this repository.

Once the server is running, you can access the interactive documentation at:

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

---

## Advanced Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /matches/h2h/{p1}/{p2}` | Comprehensive rivalry analysis between two players |
| `GET /players/stats/service-kings` | Leaderboard of players with the highest average aces |
| `GET /players/stats/giant-slayers` | Identifying players with the most high-ranking upset wins |
| `GET /rankings/stats/hall-of-fame` | All-time leaders for most weeks spent at World No. 1 |

---

## Database Design

The project adheres to relational database best practices. By utilizing SQLAlchemy Relationships, the API can serve complex, nested JSON objects (e.g., a Match object containing full Player objects) while maintaining a clean, non-redundant database back-end.

## User Access Levels

The API implements a tiered permission system to ensure data integrity while allowing for public analysis.

| Role            | Access Level   | Permissions                                                                                  |
|-----------------|---------------|---------------------------------------------------------------------------------------------|
| Guest           | Public        | View API Documentation (Swagger/ReDoc).                                                      |
| Standard User   | Authenticated | Read-only access to all player, match, and ranking data.                                     |
| Administrator   | Elevated      | Full CRUD capabilities (Create, Update, Delete) for matches, players, and rankings.          |

**Note:** Administrative actions require a valid JWT with the `is_admin` claim set to `True`.

## Model Context Protocol (MCP) Compatibility

This API is fully compatible with the Model Context Protocol (MCP), allowing AI agents (like Claude Desktop) to interact directly with the tennis database as a tool-calling backend.

**Connection Details:**

- **Transport Type:** STDIO
- **Endpoint:** http://127.0.0.1:8000/mcp
- **Bridge Library:** mcp-fastapi

**To connect the MCP Inspector:**

1. Start the FastAPI server:
	```bash
	fastapi dev main.py
	```
2. Launch the Inspector:
	```bash
	npx @modelcontextprotocol/inspector python mcp.py
	```

---

## Manual Testing

Manual testing was performed using the interactive Swagger UI (`/docs`) and the MCP Inspector tool. Endpoints were verified for correct responses, authentication, and advanced analytical functionality.