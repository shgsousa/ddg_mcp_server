# Content Summarization Feature

This guide explains how to use the AI-powered content summarization feature in the DuckDuckGo MCP Server.

## Setup

1. Configure your API credentials as described in the README.md file.
2. Test your API connection using `python main.py --test-api`.

## Using Summarization in Web Search

The web search interface now includes a checkbox for "Summarize Content using AI":

1. Enter your search query
2. Set the number of results you want
3. Check the "Summarize Content using AI" checkbox
4. Click "Submit"

The search results will include AI-generated summaries instead of the full content of each webpage.

## Using Summarization for Individual Webpages

The Web Page Scraper interface also includes a summarization option:

1. Enter the URL you want to scrape
2. Check the "Summarize Content using AI" checkbox
3. Click "Submit"

The results will include an AI-generated summary at the top, followed by the full content.

## Benefits of Summarization

- **Reduced Context Window**: Summarized content takes up less space in your context window
- **Faster Understanding**: Get the gist of web content quickly without reading the entire page
- **Improved Relevance**: Filter out noise and focus on the key information

## API Usage Considerations

- Each summarization request uses tokens from your API account
- The more content you summarize, the higher your API usage will be
- Large webpages are truncated to ~15,000 characters before summarization to control API costs
- The default model is gpt-4.1-nano, which can be changed in the config.py file

## Configuring the AI Model

The summarization feature uses a default model configured in the `config.py` file. To change the model used:

1. Open the `config.py` file
2. Find the `DEFAULT_MODEL` setting
3. Change it to your preferred model identifier
4. Restart the server

Examples:

```python
# For OpenAI models
DEFAULT_MODEL = "gpt-3.5-turbo"  # Most affordable option
DEFAULT_MODEL = "gpt-4"          # Higher quality but more expensive
DEFAULT_MODEL = "gpt-4-turbo"    # Latest model

# For OpenRouter models (requires OPENAI_API_URL to be set to OpenRouter)
DEFAULT_MODEL = "openai/gpt-4.1-nano"
DEFAULT_MODEL = "anthropic/claude-3-5-sonnet"
```

⚠️ **Important**: Ensure the model you select is accessible with your API key and the API service you're using.

## Troubleshooting

If summarization isn't working:

1. Verify your API credentials are correct in the .env file
2. Check the API connection status shown at the top of the application
3. Look for error messages in the terminal output
4. Make sure the API service you're using supports the models being used
