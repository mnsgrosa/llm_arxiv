# LLM Arxiv Explorer (Português)

Este projeto é uma ferramenta de exploração de artigos de pesquisa que utiliza um Modelo de Linguagem de Grande Escala (LLM) para ajudar usuários a descobrir e compreender artigos acadêmicos do repositório arXiv. A interface do usuário é construída com Streamlit.

## Funcionalidades

*   **Busca Conversacional:** Encontre artigos relevantes baseados em consultas em linguagem natural.
*   **Resumo Automatizado:** Obtenha resumos concisos de artigos de pesquisa.
*   **Descoberta de Tópicos:** Explore os principais tópicos e temas em uma coleção de artigos.
*   **Interface Interativa:** Uma interface web amigável construída com Streamlit para navegar e pesquisar artigos.

## Estrutura de Arquivos

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
│   ├── mcp_server.py
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

## Configuração

1.  **Obter a chave da API Groq**
    [Chave da API Groq](https://console.groq.com/keys)

2.  **Clonar o repositório:**
    ```bash
    git clone https://github.com/mnsgrosa/llm_arxiv
    cd llm_arxiv
    ```

3.  **Criar um arquivo .env**
    Crie um arquivo `.env` seguindo o exemplo do `.env.example` e adicione sua chave da API Groq.
    ```
    GROQ_API_KEY=sua_chave_api_aqui
    ```

4.  **Executar com Docker Compose**
    Isso irá construir e executar o servidor MCP e a interface Streamlit.
    ```bash
    docker compose up -d
    ```

## Uso

1.  **Acesse a interface Streamlit**
    Abra seu navegador e acesse [http://localhost:8501](http://localhost:8501). (A porta pode variar, verifique seu arquivo `docker-compose.yml`).

2.  **Comece a explorar!**
    Você pode conversar com o agente. Peça para ele listar suas ferramentas para ver o que ele pode fazer. As ferramentas disponíveis são:
    *   `scrape_arxiv_papers`: Coleta artigos do arXiv para um determinado tópico.
    *   `search_stored_papers`: Procura por artigos no banco de dados local.
    *   `get_or_scrape_papers`: Tenta encontrar artigos no banco de dados primeiro e, se não encontrar, coleta do arXiv.
    *   `list_available_topics`: Lista os tópicos dos artigos já armazenados no banco de dados.

    Você pode conversar sobre os artigos coletados pelo sistema.

---

# LLM Arxiv Explorer

This project is a research paper exploration tool that uses a Large Language Model (LLM) to help users discover and understand academic papers from the arXiv repository. It uses Streamlit for the user interface.

## Features

*   **Conversational Search:** Find relevant papers based on natural language queries.
*   **Automated Summarization:** Get concise summaries of research papers.
*   **Topic Discovery:** Explore the main topics and themes in a collection of papers.
*   **Interactive Interface:** A user-friendly web interface built with Streamlit for browsing and searching papers.

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
│   ├── mcp_server.py
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

1.  **Get the Groq API key**
    [Groq API key](https://console.groq.com/keys)

2.  **Clone the repository:**
    ```bash
    git clone https://github.com/mnsgrosa/llm_arxiv
    cd llm_arxiv
    ```

3.  **Create a .env file**
    Create a `.env` file following the example in `.env.example` and add your Groq API key.
    ```
    GROQ_API_KEY=your_api_key_here
    ```

4.  **Run with Docker Compose**
    This will build and run the MCP server and the Streamlit UI.
    ```bash
    docker compose up -d
    ```

## Usage

1.  **Access the Streamlit UI**
    Open your browser and go to [http://localhost:8501](http://localhost:8501). (The port may vary, check your `docker-compose.yml` file).

2.  **Start exploring!**
    You can chat with the agent. Ask it to list its tools to see what it can do. The available tools are:
    *   `scrape_arxiv_papers`: Scrapes papers from arXiv for a given topic.
    *   `search_stored_papers`: Searches for papers in the local database.
    *   `get_or_scrape_papers`: Tries to find papers in the database first, and if not found, scrapes them from arXiv.
    *   `list_available_topics`: Lists the topics of papers already stored in the database.

    You can chat about the papers collected by the system.