# LLM Papers with Code

A project that scrapes and retrieves papers from PapersWithCode, allowing users to search for related papers using natural language queries through an agentic interface.

## Project Overview

This application consists of:

1. A FastAPI backend that handles paper scraping and database operations
2. A Streamlit frontend for user interaction
3. An agent-based system using Google ADK for natural language processing
4. ChromaDB for vector storage and semantic search

## Environment Setup

### Creating the .env File

This project requires a `.env` file in the root directory with the following environment variables:

1. Create a `.env` file in the project root:

```bash
touch .env
```

2. Add the following environment variables to the `.env` file:

```
# Whether you want to use the vertexai or not, by default it is False
GOOGLE_GENAI_USE_VERTEXAI = False

# OpenRouter API Token (for LiteLLM)
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Google API Key (for Gemini models)
GOOGLE_API_KEY=your_google_api_key_here
```

3. Replace the placeholder values with your actual API keys.

### Getting API Keys

1. **OpenRouter API Key**: Sign up at [OpenRouter](https://openrouter.ai/) to get an API key for accessing various LLM models.
2. **Google API Key**: Get a key from [Google AI Studio](https://makersuite.google.com/app/apikey) for Gemini model access.

## Installation

### Prerequisites

- Python 3.10+
- pip

### Installing Dependencies

The project uses a requirements.txt file for dependency management:

```bash
pip install -r requirements.txt
```

## Project Structure

- `agents/`: Contains the agent implementation using Google ADK
- `backend/`: FastAPI server implementation
  - `main.py`: API endpoints for paper operations
  - `schemas.py`: Pydantic models for request/response validation
- `db/`: ChromaDB client for vector database operations
- `scraper/`: Contains the PaperScraper for fetching papers from PapersWithCode
- `app.py`: Streamlit frontend application

## Running the Application

1. Start the backend server:

```bash
cd backend
uvicorn main:app --reload --port 8000
```

2. In a separate terminal, start the Streamlit frontend:

```bash
streamlit run app.py
```

3. Access the application at http://localhost:8501

## Usage

The application provides two main functionalities:

1. **Adding Papers to Database**:
   - You can add trending or latest papers from PapersWithCode to the database
   - Example prompt: "Add the latest papers to the database" or "Get trending papers"

2. **Querying Papers**:
   - Search for papers by topic using natural language
   - Example prompt: "Show me 5 papers about reinforcement learning" or "Find 3 trending papers on computer vision"

3. **Chatting About Papers**:
   - After retrieving papers, you can ask questions about them
   - The researcher agent will provide information based on the paper content

## API Endpoints

- `POST /papers/post/trending`: Scrapes and adds trending papers to the database
- `POST /papers/post/lattest`: Scrapes and adds latest papers to the database
- `GET /papers/get/trending`: Retrieves trending papers based on a query
- `GET /papers/get/lattest`: Retrieves latest papers based on a query
- WebSocket endpoints for real-time agent communication

## Note

This project is actively being developed. Features and documentation will be updated regularly.
