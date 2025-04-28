# LLM Papers with Code

A project that scrapes and retrieves papers from PapersWithCode, allowing users to search for related papers using natural language queries.

## Environment Setup

### Creating the .env File

This project requires a `.env` file in the root directory with the following environment variables:

1. Create a `.env` file in the project root:

```bash
touch .env
```

2. Add the following environment variables to the `.env` file:

```
# Hugging Face API Token
HF_TOKEN=your_huggingface_token_here
```

3. Replace `your_huggingface_token_here` with your actual Hugging Face API token.

### Getting a Hugging Face API Token

1. Create an account on [Hugging Face](https://huggingface.co/) if you don't have one.
2. Go to your profile settings and navigate to the "Access Tokens" section.
3. Create a new token with appropriate permissions.
4. Copy the token and paste it in your `.env` file.

## Requirements

The project uses the following main Python packages:

- **dotenv**: For loading environment variables
- **smolagents**: For creating and managing LLM-powered agents
- **chromadb**: For vector database functionality
- **httpx**: For making HTTP requests
- **BeautifulSoup4**: For web scraping
- **uuid**: For generating unique identifiers

### Installing Requirements

To install all required packages, you can use:

```bash
pip install python-dotenv smolagents chromadb httpx beautifulsoup4
```

## Project Structure

- `agents/`: Contains the LLM agent implementation
- `db/`: Contains the ChromaDB client for vector database operations
- `scraper/`: Contains the PaperScraper for fetching papers from PapersWithCode

## Usage

The project allows you to:

1. Scrape trending and latest papers from PapersWithCode
2. Store paper information in a vector database
3. Query related papers using natural language

## Note

This project is currently in development. Additional documentation will be added as the project evolves.
