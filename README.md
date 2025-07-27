
# LLM Arxiv Explorer (Português)

Este projeto é uma ferramenta de exploração de artigos de pesquisa que utiliza um Modelo de Linguagem de Grande Escala (LLM) para ajudar usuários a descobrir e compreender artigos acadêmicos do repositório arXiv.

## Funcionalidades

*   **Busca Semântica:** Encontre artigos relevantes baseados em consultas em linguagem natural.
*   **Resumo Automatizado:** Obtenha resumos concisos de artigos de pesquisa.
*   **Modelagem de Tópicos:** Explore os principais tópicos e temas em uma coleção de artigos.
*   **Interface Interativa:** Uma interface web amigável para navegar e pesquisar artigos.

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

1. **Obter a chave da API Groq**
    [Chave da API Groq](https://console.groq.com/keys)

2.  **Clonar o repositório:**
    ```bash
    git clone https://github.com/mnsgrosa/llm_arxiv
    cd llm_arxiv
    ```
    
3. **Criar um arquivo .env**
    Crie um arquivo .env seguindo o exemplo do .env.example
    GROQ_API_KEY = sua_chave_api_aqui

4.  **Executar o docker compose**
    ```bash
    docker compose up -d
    ```

## Uso

1.  **Acesse o link hospedado em**
    [localhost:7860](http://localhost:7860)

2.  **Comece a explorar!**
    Você pode conversar com o agente e pedir para ele listar suas ferramentas.
    As ferramentas disponíveis são:
        scrape_arxiv
        get_files_from_database
        get_or_scrape
        get_topics
    Você pode conversar sobre os artigos coletados pelo sistema. 

 ---

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

1. **Get the groq API key**
    [Groq api key](https://console.groq.com/keys)

2.  **Clone the repository:**
    ```bash
    git clone https://github.com/mnsgrosa/llm_arxiv
    cd llm_arxiv
    ```
    
3. **Create a .env**
    Create a .env file just like the .env.example
    GROQ_API_KEY = you_api_key_here

4.  **Run the docker compose**
    ```bash
    docker compose up -d
    ```

## Usage

1.  **Go to the link hosted at**
    [localhost:7860](http://localhost:7860)

2.  **Start exploring!**
    You can chat with the agent, you can ask him to list its tools.
    the tools are:
        scrape_arxiv
        get_files_from_database
        get_or_scrape
        get_topics
    You can chat with it about the papers scraped