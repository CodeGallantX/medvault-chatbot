# Medibot-AI

Medibot-AI is a powerful medical chatbot designed to provide accurate and relevant medical information. It is built with a robust technology stack, featuring a Django backend, a sophisticated RAG (Retrieval-Augmented Generation) model for intelligent responses, and a user-friendly API.

**Credit to the developer of Medibot-AI for the core application logic.**

## Features

- **Chatbot API:** Engage in a conversation with the medical chatbot to get detailed information about diseases, symptoms, and treatments.
- **Prediction API:** Get relevant medical information based on a specific query.
- **Health Check:** A dedicated endpoint to monitor the status of the API.
- **RAG Model:** The chatbot leverages a RAG model, which combines the power of a large language model with a knowledge base of medical documents. This ensures that the responses are not only fluent and conversational but also grounded in factual medical data.
- **Extensible:** The project is designed to be easily extensible. You can add more documents to the knowledge base to expand the chatbot's expertise.

## Technology Stack

- **Backend:** Django, Django Rest Framework
- **AI/ML:**
    - Ollama for serving the language model
    - FAISS for efficient similarity search
    - Pandas and NumPy for data manipulation
- **Database:** SQLite (for development)

## API Endpoints

The following are the primary API endpoints:

- `POST /api/chat/`: The main chatbot endpoint. Send a message and get a comprehensive response.
- `POST /api/predict/`: Get relevant medical information for a given message.
- `GET /api/health/`: A simple health check endpoint to confirm that the service is running.

### `/api/chat/`

**Request:**

```json
{
  "message": "What are the symptoms of diabetes?"
}
```

**Response:**

```json
{
  "response": "Diabetes is a chronic (long-lasting) health condition that affects how your body turns food into energy..."
}
```

### `/api/predict/`

**Request:**

```json
{
  "message": "diabetes"
}
```

**Response:**

```json
{
  "relevant_info": [
    "...",
    "..."
  ]
}
```

### `/api/health/`

**Request:**

```bash
curl http://localhost:8000/api/health/
```

**Response:**

```json
{
  "status": "ok"
}
```

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd medvault-copy
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the development server:**
    ```bash
    python3 manage.py runserver
    ```

The API will be available at `http://localhost:8000`.

## Usage

You can interact with the API using tools like `curl` or any API client (e.g., Postman, Insomnia).

**Example with `curl`:**

```bash
# Chat endpoint
curl -X POST -H "Content-Type: application/json" -d '{"message": "What is hypertension?"}' http://localhost:8000/api/chat/

# Predict endpoint
curl -X POST -H "Content-Type: application/json" -d '{"message": "hypertension"}' http://localhost:8000/api/predict/

# Health check
curl http://localhost:8000/api/health/
```
