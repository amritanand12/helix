# Helix Backend

Helix Backend is a REST API for a pharmacy point-of-sale and medicine price catalog. It is built with FastAPI and SQLAlchemy and is intended to provide backend services to a separate Android application.

The API currently supports medicine catalog maintenance and customer-linked bill creation and lookup. It uses PostgreSQL for persistent storage and exposes interactive API documentation through FastAPI.

> **Scope:** This repository contains the backend only; it does not include the Android client. The current medicine model stores a name and price, not stock quantities, batches, or expiry dates. There is no authentication or authorization implemented, so deploy it only in a trusted environment until those controls are added.

## Features

- Create, list, search, update, and delete medicines.
- Create bills with customer details and bill items.
- List bills, filter by customer name, retrieve a bill, and delete a bill.
- Paginate medicine and bill listings.
- Generate OpenAPI documentation and an interactive Swagger UI.
- Run locally with Uvicorn or package the service in Docker.

## Technology

- Python
- FastAPI and Uvicorn
- SQLAlchemy
- PostgreSQL (`psycopg2`)
- Pydantic

## Getting started

### Prerequisites

- Python 3.11 or later
- A reachable PostgreSQL database

### Configure the database

Create a local `.env` file from the example:

```powershell
Copy-Item .env.example .env
```

Set `POSTGRES_DB_URL` in `.env` to a SQLAlchemy PostgreSQL connection URL. For example:

```dotenv
POSTGRES_DB_URL=postgresql+psycopg2://USER:PASSWORD@HOST:5432/DATABASE
```

Replace the example values with your database credentials. URL-encode special characters in the username or password. Keep `.env` private; it is excluded from Git and Docker build contexts.

### Install and run

From the repository root, create and activate a virtual environment, install dependencies, and start the API:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app:app --reload --host 0.0.0.0 --port 9758
```

In Command Prompt, activate the environment with `.venv\Scripts\activate.bat`. On macOS or Linux, use `source .venv/bin/activate` instead.

The service is available at `http://localhost:9758`. On startup, the application creates the tables defined by its SQLAlchemy models if they do not already exist. Schema migrations are not currently configured.

## API reference

Interactive documentation is available at:

- Swagger UI: `http://localhost:9758/docs`
- ReDoc: `http://localhost:9758/redoc`
- OpenAPI JSON: `http://localhost:9758/openapi.json`

All endpoints are rooted at `/`.

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/medicines` | Add a medicine. |
| `GET` | `/medicines` | List medicines; supports `search`, `page`, and `limit`. |
| `GET` | `/medicines/{medicine_id}` | Get a medicine by ID. |
| `PATCH` | `/medicines/{medicine_id}` | Update a medicine's name and/or price. |
| `DELETE` | `/medicines/{medicine_id}` | Delete a medicine. |
| `POST` | `/bills` | Create a bill, customer (when not already found), and bill items. |
| `GET` | `/bills` | List bills; supports `customer_name`, `page`, and `limit`. |
| `GET` | `/bills/{bill_id}` | Get a bill by ID. |
| `DELETE` | `/bills/{bill_id}` | Delete a bill. |

Medicine search is case-insensitive and requires 3–100 characters when provided. Bill customer-name filtering also requires 3–100 characters. Both list endpoints default to page `1` and limit `10`; the maximum limit is `100`. Missing medicine or bill IDs return `404`.

### Example: add a medicine

```http
POST /medicines
Content-Type: application/json
```

```json
{
  "name": "Example Medicine",
  "price": 12.5
}
```

Medicine names are checked for case-insensitive duplicates.

### Example: create a bill

```http
POST /bills
Content-Type: application/json
```

```json
{
  "bill": {
    "total_amount": 25.0,
    "payment_mode": "cash",
    "date": "2026-10-31",
    "customer_id": 0
  },
  "customer": {
    "name": "Example Customer",
    "phone": "5550100",
    "email": "customer@example.com",
    "address": "Example address"
  },
  "bill_items": [
    {
      "bill_id": 0,
      "medicine_id": 1,
      "quantity": 2,
      "price": 12.5
    }
  ]
}
```

The current request schema requires `customer_id` on `bill` and `bill_id` on each item. During bill creation, the backend finds or creates the customer using the supplied phone/email, assigns that customer's ID to the bill, and assigns the new bill's ID to its items; the two submitted IDs are not used for those relationships. Replace `medicine_id` with an existing medicine ID. The bill total and item prices are accepted from the client and are not recalculated by the API.

## Docker

Build the image from the repository root:

```powershell
docker build -t helix-backend .
```

Run it with the local environment file:

```powershell
docker run --rm --env-file .env -p 9758:9758 helix-backend
```

The database must be reachable from the container. When using Docker Compose or a remote database, set `POSTGRES_DB_URL` to a hostname and port accessible from the container; `localhost` inside a container refers to that container.

## Project structure

```text
.
├── app.py           # FastAPI application and HTTP routes
├── crud.py          # Database operations
├── database.py      # PostgreSQL connection and SQLAlchemy session setup
├── models.py        # SQLAlchemy table models
├── schemas.py       # Pydantic request and response schemas
├── requirements.txt # Python dependencies
├── Dockerfile       # Container image definition
├── .dockerignore    # Excludes local and secret files from image builds
├── .env.example     # Safe database configuration template
└── README.md        # Setup, scope, and API documentation
```

## Deployment and security notes

- The API currently has no authentication, authorization, or rate limiting. Do not expose it publicly with real customer data until appropriate access controls are implemented.
- CORS currently allows all origins in `app.py`. Restrict allowed origins before deploying a production service.
- The API stores customer contact details and billing records. Protect the database and network traffic, and follow applicable privacy and retention requirements.
- Use a managed secret store or deployment environment variables for production credentials rather than committing `.env`.
- `Base.metadata.create_all()` creates missing tables but does not manage schema changes. Add a migration workflow before evolving a production database.

## Development status

There are no automated tests or database migration scripts in the repository yet. The Swagger UI at `/docs` can be used to explore and manually exercise the current API.
