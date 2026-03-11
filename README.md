# ATP Tennis Data API

A high-performance REST API built with FastAPI and SQLAlchemy to manage and analyze professional tennis data from the ATP Tour. This project transforms raw CSV datasets into a normalized relational database with advanced analytical endpoints.

---

## Project Overview

This API provides a centralized interface for querying player profiles, match statistics, and historical rankings. Beyond standard CRUD operations, it features custom analytical engines to calculate Head-to-Head rivalries, "Giant Slayer" upsets, and all-time Hall of Fame leaderboards.

### Key Features

- **Normalized Database (3NF)**: Optimized SQLite schema that eliminates data redundancy by separating player metadata from match records.
- **Advanced Analytics**: Custom endpoints for H2H history, rank progression over time, and service performance leaderboards.
- **Automated Initialization**: A robust script to clean, filter, and ingest raw ATP CSV data into the relational model.
- **Interactive Documentation**: Fully documented with Swagger UI, allowing for real-time testing of all endpoints.

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | FastAPI |
| ORM | SQLAlchemy |
| Database | SQLite |
| Validation | Pydantic |
| Data Processing | Pandas (Initial ingestion) |

---

## Setup & Installation

### 1. Clone the Repository

```bash
git clone <your-repo-url>
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

### 4. Initialize the Database

Ensure your ATP CSV files are in the designated data folder, then run the initialization script to build your SQLite database:

```bash
python init_db.py
```

### 5. Run the API

```bash
fastapi dev main.py
```

The server will start at `http://127.0.0.1:8000`.

---

## API Documentation

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