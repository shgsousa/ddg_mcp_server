
# ddg-mcp-server

A web search tool and API powered by DuckDuckGo, Gradio, and MCP, providing both a user-friendly web interface and Claude Desktop tool integration.  
It fetches web search results, extracts summaries, and retrieves the full content of web pages in markdown format.

## Features

- **DuckDuckGo Web Search:**  
  Search the web using DuckDuckGo and retrieve the top N results.
- **Full Content Extraction:**  
  For each result, fetches the full web page, cleans it, and converts it to markdown.
- **Summaries:**  
  Each result includes a summary (snippet) and the full content.
- **Gradio Web Interface:**  
  User-friendly interface for interactive searching.
- **MCP Server Integration:**  
  Exposes the search tool to Claude Desktop and other MCP-compatible clients.
- **403 Filtering:**  
  Automatically excludes results that return HTTP 403 (forbidden) errors.

## Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd ddg-mcp-server
   ```

2. **Create a virtual environment (optional but recommended):**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Run the Server

```bash
python main.py
```

- The Gradio web interface will be available at:  
  [http://127.0.0.1:7860](http://127.0.0.1:7860)
- The MCP server will be available at:  
  `http://127.0.0.1:7860/gradio_api/mcp/sse`

### Using the Web Interface

- Enter your search query and select the number of results.
- Each result will display:
  - Title
  - Link
  - Summary (snippet)
  - Full content (markdown)

### Using with Claude Desktop

- Open Claude Desktop and add the MCP server if not auto-detected:
  ```
  http://127.0.0.1:7860/gradio_api/mcp/sse
  ```
- The tool will appear as `search` in the Claude Desktop tool list.

## Example

**Search Query:**  
`What is the latest news on Pope Leo XIV?`

**Result:**  
- Title, link, summary, and full markdown content for each accessible result.

## Configuration

- **Number of Results:** Adjustable via the web interface slider or the `n` parameter in the MCP tool.
- **403 Filtering:** Results that return HTTP 403 are skipped and replaced with the next available result.

## Dependencies

- duckduckgo-search
- requests
- beautifulsoup4
- markdownify
- gradio[mcp]

(See `requirements.txt` for exact versions.)

## License

[Apache 2.0](LICENSE)
