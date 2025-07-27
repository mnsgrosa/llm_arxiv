# LLM Arxiv Explorer

This project is a research paper exploration tool that uses a Large Language Model (LLM) to help users discover and understand academic papers from the arXiv repository.

## Features

*   **Semantic Search:** Find relevant papers based on natural language queries.
*   **Automated Summarization:** Get concise summaries of research papers.
*   **Topic Modeling:** Explore the main topics and themes in a collection of papers.
*   **Interactive Interface:** A user-friendly web interface for browsing and searching papers.

## File Structure

```
.
├── .env.example
├── .gitignore
├── Dockerfile.gradio
├── Dockerfile.mcp
├── README.md
├── docker-compose.yml
├── llm
│   ├── __init__.py
│   ├── agent.py
│   ├── app.py
│   ├── db
│   │   ├── __init__.py
│   │   └── chroma.py
│   ├── scraper
│   │   ├── __init__.py
│   │   └── paperscraper.py
│   └── shared_paper_tools.py
└── requirements.txt
```

## Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/your-repository.git
    cd your-repository
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

4.  **Set up the environment variables:**
    Create a `.env` file from the `.env.example`:
    ```bash
    cp .env.example .env
    ```
    You will need to add your Groq API key to the `.env` file.

## Usage

1.  **Start the application:**
    ```bash
    python -m llm.app
    ```

2.  **Open your web browser** and navigate to `http://localhost:7860`.

3.  **Start exploring!**
    You can use the search bar to find papers by keyword or topic. Click on a paper to see more details and a summary.

## How to Contribute

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Make your changes and commit them.
4.  Push your changes to your fork.
5.  Create a pull request.
