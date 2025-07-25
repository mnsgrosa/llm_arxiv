# LLM Papers with Code

## DISCLAIMER/AVISO

Project discontinued due to the page being down for now

Projeto descontinuado devido a queda do site paperswithcode no momento

## Português Brasileiro

Um projeto que faz scraping e pega papers do PapersWithCode, permitindo que usuários busquem por papers relacionados usando consultas em linguagem natural.

No momento está implementado um scheduler que irá popular o banco de dados assim que inicializado e fará um novo post apenas as 1 da manhã seguinte

### Requisitos

O projeto utiliza os seguintes pacotes principais do Python:
- **prefect**: Para orquestrar as ferramentas de scraping
- **chromadb**: Para funcionalidade de banco de dados vetorial
- **Pydantic**: Para validação de dados
- **FastAPI**: Para possibilitar o envio de dados para o banco
- **httpx**: Para fazer requisições HTTP
- **BeautifulSoup4**: Para web scraping
- **uuid**: Para gerar identificadores únicos

#### Instalando os Requisitos

Para instalar todos os pacotes necessários, você pode usar:
```bash
pip install python-dotenv smolagents chromadb httpx beautifulsoup4
```

### Estrutura do Projeto

- `backend/`: Contém as funcionalidades para poder enviar dados para o banco
- `orchestrator/`: Contém a lógica para o agendamento das ferramentas de orquestração
- `db/`: Contém o cliente ChromaDB para operações de banco de dados vetorial
- `scraper/`: Contém o PaperScraper para buscar papers do PapersWithCode

### Uso

O projeto permite que você:
1. Faça scraping de papers em tendência e mais recentes do PapersWithCode
2. Armazene informações dos papers em um banco de dados vetorial
3. Consulte papers relacionados usando linguagem natural

### Nota

Este projeto está atualmente em desenvolvimento. Documentação adicional será adicionada conforme o projeto evolui.

---

## English

A project that scrapes and retrieves papers from PapersWithCode, allowing users to search for related papers using natural language queries.

### Requirements

The project uses the following main Python packages:
- **prefect**: For the orchestrating the scraping tools
- **chromadb**: For vector database functionality
- **Pydantic**: For data validation
- **FastAPI**: So it is possible to post the data to the db
- **httpx**: For making HTTP requests
- **BeautifulSoup4**: For web scraping
- **uuid**: For generating unique identifiers

#### Installing Requirements

To install all required packages, you can use:
```bash
pip install python-dotenv smolagents chromadb httpx beautifulsoup4
```

### Project Structure

- `backend/`: Contains the features so it can post to the db
- `orchestrator/`: Contains the logic for the schedule of orchestration tools
- `db/`: Contains the ChromaDB client for vector database operations
- `scraper/`: Contains the PaperScraper for fetching papers from PapersWithCode

### Usage

The project allows you to:
1. Scrape trending and latest papers from PapersWithCode
2. Store paper information in a vector database
3. Query related papers using natural language

### Note

This project is currently in development. Additional documentation will be added as the project evolves.