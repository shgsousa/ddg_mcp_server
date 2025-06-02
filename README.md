# DuckDuckGo MCP Server

A web-based search interface using DuckDuckGo's search API, built with Python and Gradio.

## Docker Setup

### Prerequisites

- Docker installed on your system
- Git (optional, for cloning the repository)

### Building the Docker Image

1. Clone the repository (if you haven't already):

```bash
git clone <repository-url>
cd ddg_mcp_server
```

2. Build the Docker image:

```bash
docker build -t ddg-mcp-server .
```

### Running the Container

Run the container with port 7860 mapped to your host:

```bash
docker run -p 7860:7860 ddg-mcp-server
```

The application will be available at:

- [http://localhost:7860](http://localhost:7860)
- [http://127.0.0.1:7860](http://127.0.0.1:7860)

### Troubleshooting

If you cannot connect to the application:

1. Verify the container is running:

```bash
docker ps
```

2. Check the container logs:

```bash
docker logs $(docker ps -q)
```

3. Try stopping any existing containers and starting fresh:

```bash
docker stop $(docker ps -q)
docker run -p 7860:7860 ddg-mcp-server
```

## Features

- Web-based search interface using DuckDuckGo
- Real-time search results with full content
- Markdown-formatted output
- Configurable number of results
- AI-powered content summarization (see [SUMMARIZATION.md](SUMMARIZATION.md) for details)

## Development

The application is built with:

- Python 3.10
- Gradio for the web interface
- DuckDuckGo Search API
- BeautifulSoup4 for web scraping
- Markdownify for content conversion

## API Configuration for Summarization

This application supports content summarization using OpenAI's API or any compatible API service. To enable this feature:

1. Copy the `.env.example` file to `.env`:

```bash
cp .env.example .env
```

2. Edit the `.env` file and set your API credentials:

```
OPENAI_API_URL=https://api.openai.com/v1
ACCESS_TOKEN=your_api_key_here
```

Notes:
- `OPENAI_API_URL` defaults to the official OpenAI API server if not specified
- `ACCESS_TOKEN` is required for the summarization feature to work
- You can use any OpenAI-compatible API by changing the `OPENAI_API_URL`

### Running with Docker and API Credentials

To run the Docker container with your API credentials:

```bash
docker run -p 7860:7860 \
  -e OPENAI_API_URL="https://api.openai.com/v1" \
  -e ACCESS_TOKEN="your_api_key_here" \
  ddg-mcp-server
```

### Testing the API Connection

After configuring your API credentials, you can test if the connection works correctly:

```bash
python main.py --test-api
```

This will validate your API credentials without starting the full server.

### Model Configuration

The AI model used for summarization can be configured in the `config.py` file:

```python
# Default model to use for summarization
DEFAULT_MODEL = "gpt-4.1-turbo"
```

For detailed instructions on model configuration, see [SUMMARIZATION.md](SUMMARIZATION.md).
