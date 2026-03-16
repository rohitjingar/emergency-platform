# 🚨 AI‑Powered Emergency Coordination Platform

When disasters occur---floods, fires, or accidents---response time saves
lives.\
This platform connects affected people with verified volunteers **within
seconds** using **agentic AI, geospatial matching, and asynchronous
processing**.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green?logo=fastapi)
![LangGraph](https://img.shields.io/badge/LangGraph-Agentic%20AI-orange)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17+PostGIS-blue?logo=postgresql)
![Redis](https://img.shields.io/badge/Redis-7-red?logo=redis)
![Docker](https://img.shields.io/badge/Docker-Compose-blue?logo=docker)
![ChromaDB](https://img.shields.io/badge/ChromaDB-VectorDB-purple)

------------------------------------------------------------------------

## Overview

The platform enables rapid coordination during emergencies by
automatically:

1.  **Analyzing incident reports**
2.  **Classifying severity using AI**
3.  **Finding the nearest qualified volunteer**
4.  **Notifying and assigning responders**
5.  **Routing uncertain cases to human reviewers**

All computationally heavy operations run in **background workers**,
allowing the API to respond instantly while processing continues
asynchronously.

------------------------------------------------------------------------

# What Happens When an Incident Is Reported

### 1. AI Triage Agent

The system evaluates the emergency description using **LangGraph with
Agentic RAG**.

The agent:

-   Classifies incident type (flood, fire, medical, accident)
-   Assigns severity level\
    `Critical | High | Medium | Low`
-   Produces a **confidence score**

### 2. Volunteer Matching

The system finds the nearest suitable volunteer using:

-   **PostGIS geospatial queries**
-   **Skill matching**
-   **Redis distributed locking**

### 3. Volunteer Notification

The matched volunteer receives the request and must:

-   **Accept**
-   **Decline**
-   **Respond within 60 seconds**

If declined or timed out, the system automatically assigns the next
volunteer.

### 4. Human Review

If AI confidence is below **70%**, the incident is routed to an **admin
review queue** for verification.

------------------------------------------------------------------------

# System Design Overview

                            ┌─────────────────────────┐
                            │        Clients          │
                            │ Users · Volunteers      │
                            │ Admins                  │
                            └─────────────┬───────────┘
                                          │ HTTP / REST
                                          ▼
                               ┌─────────────────────┐
                               │       FastAPI       │
                               │ Auth · Validation   │
                               │ Idempotency         │
                               └───────────┬─────────┘
                                           │
                          ┌────────────────┼────────────────┐
                          │                │                │
                          ▼                ▼                ▼
                 ┌─────────────┐   ┌─────────────┐  ┌─────────────┐
                 │ PostgreSQL  │   │    Redis    │  │   ChromaDB  │
                 │ + PostGIS   │   │ Queue/Cache │  │ Vector DB   │
                 │ Incidents   │   │ Locks       │  │ RAG Context │
                 │ Volunteers  │   │             │  │             │
                 └──────┬──────┘   └──────┬──────┘  └──────┬──────┘
                        │                 │                │
                        ▼                 ▼                ▼
               ┌─────────────────────────────────────────────────┐
               │              Background Workers                  │
               │                                                 │
               │ Incident Worker                                 │
               │ • LangGraph Triage Agent                        │
               │ • Severity Classification                       │
               │ • Agentic RAG Retrieval                         │
               │                                                 │
               │ Assignment Worker                               │
               │ • PostGIS Geo Matching                          │
               │ • Skill Filtering                               │
               │ • Redis Distributed Lock                        │
               │                                                 │
               │ Scheduler Worker                                │
               │ • Timeout Monitoring                            │
               │ • Auto Reassignment                             │
               └─────────────────────────────────────────────────┘
                                          │
                                          ▼
                               ┌────────────────────┐
                               │  Notification Flow │
                               │ Volunteer Accept   │
                               │ Volunteer Decline  │
                               │ Auto Reassign      │
                               └────────────────────┘

This architecture provides:

-   **Instant API responses**
-   **Reliable volunteer assignment**
-   **Asynchronous AI processing**
-   **Human oversight for uncertain AI decisions**

------------------------------------------------------------------------

# Agent Pipeline

    POST /incidents
          │
          ▼
    API returns instantly (201)
          │
          ▼
    Redis Queue
          │
          ▼
    LangGraph Triage Agent

    Node 1 → classify_type
    Node 2 → retrieve_context (Agentic RAG)
    Node 3 → score_severity

          │
          ▼
    confidence < 0.70
          │
          ▼
    Human Review Queue
          │
          ▼
    Assignment Worker

    PostGIS geo search
    → skill filter
    → Redis cache lookup
    → distributed lock

          │
          ▼
    Volunteer notified

    accept   → incident assigned
    decline  → next volunteer
    timeout  → volunteer skipped

------------------------------------------------------------------------

# 🛠️ Key Technical Decisions

| Component | Decision | Reason |
| :--- | :--- | :--- |
| **Agent Framework** | LangGraph StateGraph | Enables complex conditional routing and maintains persistent agent state. |
| **Vector Database** | ChromaDB | Lightweight, high-performance local vector storage for RAG operations. |
| **Async Processing** | Redis RQ | Decouples heavy tasks from the main thread to ensure immediate API responses. |
| **Geo Matching** | PostGIS | Leverages robust spatial indexing for high-performance geographic queries. |
| **Distributed Locking** | Redis SET NX | Implements atomic locking to prevent race conditions in volunteer assignments. |
| **LLM Inference** | Groq (LLaMA-3.1-8B) | Optimized for extremely low-latency inference and high throughput. |
| **Fallback System** | Rule-based Classifier | Provides a deterministic safety net to ensure stability if the LLM is unreachable. |

---

# ⚡ Performance Metrics

| Metric | Value |
| :--- | :--- |
| **API Response Time** | < 50 ms |
| **Triage Processing** | ~3–4 seconds |
| **Volunteer Matching** | < 100 ms |
| **Maximum Confidence** | ~0.95 |
| **Fallback Activation** | Triggered after repeated LLM failures |
| **Human Review Rate** | ~33% |
------------------------------------------------------------------------

# Scalability Considerations

The platform is designed for **horizontal scalability** and **high
availability**.

### Asynchronous Processing

All heavy processing runs in **Redis RQ workers**, ensuring the API
remains fast.

Example deployment:

    1 FastAPI instance
    5 incident workers
    5 assignment workers
    2 scheduler workers

------------------------------------------------------------------------

### Horizontal Worker Scaling

Workers are stateless and can scale independently.

    worker-incidents  x5
    worker-assignment x5
    worker-scheduler  x2

This allows the system to process **thousands of incidents
simultaneously**.

------------------------------------------------------------------------

### Distributed Locking

Redis prevents multiple workers from assigning the same volunteer.

    SET volunteer_lock:123 incident_456 NX EX 60

Benefits:

-   prevents race conditions
-   ensures exactly‑once assignment

------------------------------------------------------------------------

### Geo Query Optimization

Volunteer matching uses **PostGIS spatial indexing**.

    CREATE INDEX volunteers_location_idx
    ON volunteers
    USING GIST(location);

Query latency remains **under 100 ms**.

------------------------------------------------------------------------

### Circuit Breaker for LLM

External LLM calls are protected using a **Redis‑backed circuit
breaker**.

If the LLM API fails:

1.  Circuit opens
2.  System switches to rule‑based classifier
3.  LLM resumes automatically when healthy

This guarantees the platform **continues operating even during AI
outages**.

------------------------------------------------------------------------

# Quick Start

### Prerequisites

-   Docker Desktop

Clone the repository:

``` bash
git clone https://github.com/YOUR_USERNAME/emergency-platform.git
cd emergency-platform/backend
```

Create environment configuration:

``` bash
cp .env.docker.example .env.docker
```

Add values for:

-   `GROQ_API_KEY`
-   `SECRET_KEY`

Start the platform:

``` bash
docker-compose up --build
```

Open API documentation:

    http://localhost:8000/docs

------------------------------------------------------------------------

# Environment Variables

Example `.env.docker`

    DATABASE_URL=postgresql://postgres:postgres@postgres:5432/emergency_platform_db
    REDIS_HOST=redis
    REDIS_PORT=6379
    REDIS_DB=0
    CHROMA_HOST=chromadb
    SECRET_KEY=your-secret-key
    GROQ_API_KEY=your-groq-api-key
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=postgres
    POSTGRES_DB=emergency_platform_db

------------------------------------------------------------------------

# API Overview

### Authentication

    POST /auth/register
    POST /auth/login

Supported roles:

-   affected_user
-   volunteer
-   admin

------------------------------------------------------------------------

### Incidents

    POST /incidents
    GET /incidents
    GET /incidents/{id}/status

------------------------------------------------------------------------

### Volunteers

    POST /volunteers/register
    PATCH /volunteers/location
    PATCH /volunteers/status
    GET /volunteers/my-pending
    GET /volunteers/available
    POST /volunteers/incidents/{id}/accept
    POST /volunteers/incidents/{id}/decline

------------------------------------------------------------------------

### Admin

    GET /admin/review-queue
    PATCH /admin/review-queue/{id}/approve
    PATCH /admin/review-queue/{id}/override
    GET /admin/review-queue/stats

------------------------------------------------------------------------

### System / DevOps

    GET /system/health
    GET /system/circuit-breaker
    POST /system/circuit-breaker/reset
    GET /system/queues

------------------------------------------------------------------------

# 🐳 Docker Services

| Service | Purpose |
| :--- | :--- |
| `fastapi` | Primary API server and request handling. |
| `worker-incidents` | Core AI triage processing and analysis. |
| `worker-assignment` | Logic for matching incidents to volunteers. |
| `worker-scheduler` | Monitoring for timeouts and SLA breaches. |
| `rqscheduler` | Management of recurring and scheduled tasks. |
| `postgres` | Relational database storage with **PostGIS** extensions. |
| `redis` | Message queuing, result caching, and distributed locking. |
| `chromadb` | Vector database for RAG and semantic knowledge retrieval. |

------------------------------------------------------------------------

# Project Structure

    backend/
    ├── app/
    │   ├── agents/
    │   ├── api/routes/
    │   ├── core/
    |   ├── db/  
    │   ├── models/
    |   ├── repositories/
    |   ├── schemas/
    │   ├── services/
    │   └── workers/
    ├── knowledge_base/
    ├── tests/
    ├── scripts/
    ├── Dockerfile
    ├── docker-compose.yml
    └── requirements.txt

------------------------------------------------------------------------

# Running Tests

With Docker running:

``` bash
pip install requests

python tests/test_full_flow.py full
python tests/test_full_flow.py decline
python tests/test_full_flow.py admin
python tests/test_full_flow.py circuit
```

------------------------------------------------------------------------

# Author

**Rohit Kumar Jingar**

[GitHub](https://github.com/rohitjingar)

[LinkedIn](https://www.linkedin.com/in/rohit-jingar-9271a9222/)
