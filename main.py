from duckduckgo_search import DDGS
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify
import time
import gradio as gr
from gradio.themes import Soft
import datetime
from tzlocal import get_localzone
import pytz
import os
import openai
from dotenv import load_dotenv

# Import local configuration
try:
    from config import (
        DEFAULT_MODEL,
        MAX_SUMMARY_TOKENS,
        MAX_INPUT_CHARS,
        API_TIMEOUT,
        MIN_SUMMARIZATION_LENGTH
    )
except ImportError:
    # Default values if config.py is missing
    DEFAULT_MODEL = "gpt-3.5-turbo"
    MAX_SUMMARY_TOKENS = 1000
    MAX_INPUT_CHARS = 15000
    API_TIMEOUT = 30
    MIN_SUMMARIZATION_LENGTH = 500

# Load environment variables from .env file (if it exists)
load_dotenv()

# Get API configurations from environment variables with defaults
OPENAI_API_URL = os.getenv("OPENAI_API_URL", "https://api.openai.com/v1")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", "")

# Configure OpenAI client
openai_client = openai.OpenAI(
    base_url=OPENAI_API_URL,
    api_key=ACCESS_TOKEN
)

def fetch_webpage_content(url: str) -> str | None:
    """
    Fetch and convert webpage content to markdown.
    
    Args:
        url (str): The URL to fetch
        
    Returns:
        str | None: Markdown formatted content of the webpage or None if access is forbidden
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header']):
            element.decompose()
            
        # Convert to markdown
        markdown_content = markdownify(str(soup), heading_style="ATX")
        return markdown_content
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            return None
        return f"Error fetching content: {str(e)}"
    except Exception as e:
        return f"Error fetching content: {str(e)}"

def search(query: str, n: int = 5, summarize: bool = False) -> str:
    """
    Perform a web search using DuckDuckGo and return the first n results.
    
    Args:
        query (str): The search query
        n (int, optional): Number of results to return. Defaults to 5.
        summarize (bool, optional): Whether to summarize the content. Defaults to False.
    
    Returns:
        str: Formatted search results as a markdown string
    """
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=n*2))
    
    # Process each result to add full content
    valid_results = []
    for result in results:
        # Store the original snippet as summary
        result['summary'] = result['body']
        # Fetch and store the full content
        content = fetch_webpage_content(result['href'])
        if content is not None:  # Only include results that we can access
            result['body'] = content
            valid_results.append(result)
            if len(valid_results) >= n:  # Stop once we have enough valid results
                break
        time.sleep(0.25)
    
    # Format the results for display
    formatted_results = []
    for i, result in enumerate(valid_results):
        # If summarization is enabled and API key is available, summarize the content
        if summarize and ACCESS_TOKEN:
            print(f"Summarizing result {i+1}/{len(valid_results)}...")
            ai_summary = summarize_text(result['body'])
            content_section = f"""
        **AI Summary:**
        {ai_summary}
        
        **Original Snippet:**
        {result['summary']}
        """
        else:
            content_section = f"""
        **Summary:** {result['summary']}
        
        **Full Content:**
        {result['body']}
        """
            
        formatted_result = f"""
        ## {result['title']}
        
        **Link:** {result['href']}
        
        {content_section}
        
        ---
        """
        formatted_results.append(formatted_result)
    
    return "\n".join(formatted_results)

def get_datetime() -> str:
    """
    Get the current date and time with timezone information.
    
    Returns:
        str: Formatted date and time string with timezone
    """
    # Get current datetime with timezone info
    now = datetime.datetime.now()
    now = now.astimezone()  # Convert to local timezone
    formatted_datetime = now.strftime(f"%A, %B %d, %Y %I:%M:%S %p %Z")
    return f"## Current Date and Time\n\n**{formatted_datetime}**"

def scrape(url: str, summarize: bool = False) -> str:
    """
    Scrape a webpage and convert its content to markdown format.
    
    Args:
        url (str): The URL of the webpage to scrape
        summarize (bool, optional): Whether to summarize the content using AI. Defaults to False.
    
    Returns:
        str: Markdown formatted content of the webpage
    """
    content = fetch_webpage_content(url)
    if content is None:
        return "## Error\n\nCould not access the webpage. It might be blocking our request or the URL might be invalid."
        
    # If summarization is enabled and API key is available
    summary_section = ""
    if summarize and ACCESS_TOKEN:
        ai_summary = summarize_text(content)
        summary_section = f"""
    **AI Summary:**
    {ai_summary}
    
    """
    
    return f"""
    ## Scraped Content from {url}
    
    **URL:** {url}
    
    {summary_section}**Content:**
    {content}
    """

def summarize_text(text: str, max_tokens: int = MAX_SUMMARY_TOKENS) -> str:
    """
    Summarize text content using an OpenAI-compatible API.
    
    Args:
        text (str): The text content to summarize
        max_tokens (int): Maximum tokens in the summary
        
    Returns:
        str: Summarized text
    """
    try:
        if not ACCESS_TOKEN:
            return "⚠️ **API key not configured**. Please set ACCESS_TOKEN environment variable to enable summarization."
            
        # Check if text is too short to need summarization
        if len(text) < MIN_SUMMARIZATION_LENGTH:
            return f"*Content is already concise ({len(text)} characters) and doesn't need summarization.*\n\n{text}"
            
        # Truncate text if it's extremely long to avoid token limits
        truncated = False
        if len(text) > MAX_INPUT_CHARS:
            text = text[:MAX_INPUT_CHARS] + "..."
            truncated = True
            
        # Add timeout for API calls
        response = openai_client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes web content concisely."},
                {"role": "user", "content": f"Summarize the following text in a concise, informative way. Focus on the main points and key information:\n\n{text}"}
            ],
            max_tokens=max_tokens,
            timeout=API_TIMEOUT
        )
        
        # Ensure we have a string
        summary = str(response.choices[0].message.content) if response.choices[0].message.content else ""
        
        # Add note if content was truncated
        if truncated:
            summary = summary + "\n\n*Note: The original content was truncated due to length limitations before summarization.*"
            
        return summary
    except openai.APITimeoutError:
        return "⚠️ **API Timeout Error**: The request to the OpenAI API timed out. Please try again later or with shorter content."
    except openai.AuthenticationError:
        return "⚠️ **Authentication Error**: The provided API key is invalid or expired."
    except openai.RateLimitError:
        return "⚠️ **Rate Limit Exceeded**: You have exceeded your API usage limits. Please try again later."
    except openai.APIError as e:
        return f"⚠️ **API Error**: {str(e)}"
    except Exception as e:
        return f"⚠️ **Error summarizing content**: {str(e)}"

def check_api_connection() -> bool:
    """
    Check if the OpenAI API connection is working
    
    Returns:
        bool: True if connected, False otherwise
    """
    if not ACCESS_TOKEN:
        return False
        
    try:
        # Send a minimal request to verify connection
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Hello"}
            ],
            max_tokens=5
        )
        return True
    except Exception as e:
        print(f"API connection error: {str(e)}")
        return False

def create_search_interface():
    """
    Create and launch the Gradio interface for the search function.
    """
    # Create the Gradio interface
    interface = gr.Interface(
        fn=search,        
        inputs=[
            gr.Textbox(label="Search Query", placeholder="Enter your search query here..."),
            gr.Slider(minimum=1, maximum=10, value=5, step=1, label="Number of Results"),
            gr.Checkbox(label="Summarize Content using AI", value=False, info="Uses OpenAI API to summarize webpage content")
        ],
        outputs=gr.Markdown(label="Search Results"),
        title="DuckDuckGo Web Search",
        description="Enter a search query to find relevant web pages. Results will include summaries and full content in markdown format.",
        examples=[
            ["What is the latest news on Pope Leo XIV?", 3, False],
            ["Python programming best practices", 5, True],
            ["Latest developments in AI", 4, True]
        ],
        theme=Soft(),
        api_name="search"
    )
    
    # Show a warning if the API key is not configured
    if not ACCESS_TOKEN:
        gr.Warning("OpenAI API key not configured. AI summarization will not work. Set the ACCESS_TOKEN environment variable.")
    
    return interface

def create_datetime_interface():
    """
    Create and launch the Gradio interface for the datetime function.
    """
    # Create the Gradio interface
    interface = gr.Interface(
        fn=get_datetime,
        inputs=[],
        outputs=gr.Markdown(label="Date and Time"),
        title="Current Date and Time",
        description="Click the submit button to get the current date and time.",
        theme=Soft(),
        api_name="datetime"
    )
    
    return interface

def create_scrape_interface():
    """
    Create a Gradio interface for the scrape function.
    """
    # Create the Gradio interface
    interface = gr.Interface(
        fn=scrape,
        inputs=[
            gr.Textbox(label="URL", placeholder="Enter the URL to scrape (e.g., https://example.com)"),
            gr.Checkbox(label="Summarize Content using AI", value=False, info="Uses OpenAI API to summarize webpage content")
        ],
        outputs=gr.Markdown(label="Scraped Content"),
        title="Web Page Scraper",
        description="Enter a URL to fetch and convert its content to markdown format.",
        examples=[
            ["https://en.wikipedia.org/wiki/Python_(programming_language)", False],
            ["https://www.example.com", True],
            ["https://gradio.app/", True]
        ],
        theme=Soft(),
        api_name="scrape"
    )
    
    # Show a warning if the API key is not configured
    if not ACCESS_TOKEN:
        gr.Warning("OpenAI API key not configured. AI summarization will not work. Set the ACCESS_TOKEN environment variable.")
    
    return interface

def main():
    print("Starting server...")
    
    # Check API configuration
    api_status = "API connection: "
    if ACCESS_TOKEN:
        if check_api_connection():
            api_status += "✅ Connected"
            print(f"{api_status} - AI summarization is available")
        else:
            api_status += "❌ Error (invalid credentials or API URL)"
            print(f"{api_status} - AI summarization will not work correctly")
    else:
        api_status += "❌ Not configured"
        print(f"{api_status} - AI summarization will not be available")
    
    # Create the interfaces
    search_interface = create_search_interface()
    datetime_interface = create_datetime_interface()
    scrape_interface = create_scrape_interface()
    
    # Create a Blocks app with multiple tabs
    with gr.Blocks(theme=Soft()) as demo:
        # Show API status at the top
        gr.Markdown(f"**{api_status}**")
        
        with gr.Tabs():
            with gr.Tab("Web Search"):
                search_interface.render()
            with gr.Tab("Date & Time"):
                datetime_interface.render()
            with gr.Tab("Scrape"):
                scrape_interface.render()
    
    print("Interface created, launching server...")
    demo.launch(
        mcp_server=True,
        server_name="localhost",  # Allow external connections
        server_port=7860,
        share=False,
        debug=True,  # Enable debug mode
        show_error=True  # Show detailed errors
    )
    print("Server launched!")

if __name__ == "__main__":
    import sys
    
    # Check for command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--test-api":
        # Test API connection only
        if check_api_connection():
            print("✅ API connection successful! Your API is correctly configured.")
            sys.exit(0)
        else:
            print("❌ API connection failed. Please check your credentials and API URL.")
            sys.exit(1)
    else:
        # Run the full server
        main()
