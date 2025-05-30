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

def search(query: str, n: int = 5) -> str:
    """
    Perform a web search using DuckDuckGo and return the first n results.
    
    Args:
        query (str): The search query
        n (int, optional): Number of results to return. Defaults to 5.
    
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
    for result in valid_results:
        formatted_result = f"""
        ## {result['title']}
        
        **Link:** {result['href']}
        
        **Summary:** {result['summary']}
        
        **Full Content:**
        {result['body']}
        
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
    
    # Get timezone name and offset
    timezone_name = datetime.datetime.now(datetime.timezone.utc).astimezone().tzname()
    timezone_offset = datetime.datetime.now(datetime.timezone.utc).astimezone().strftime('%z')
    
    # Format offset to be more readable (e.g., +0100 to +01:00)
    if timezone_offset:
        formatted_offset = f"{timezone_offset[:3]}:{timezone_offset[3:]}"
    else:
        formatted_offset = ""
    
    # Format the datetime
    formatted_datetime = now.strftime("%A, %B %d, %Y %I:%M:%S %p")
    
    return f"## Current Date and Time\n\n**{formatted_datetime}**\n\n**Timezone:** {timezone_name} ({formatted_offset})"

def scrape(url: str) -> str:
    """
    Scrape a webpage and convert its content to markdown format.
    
    Args:
        url (str): The URL of the webpage to scrape
    
    Returns:
        str: Markdown formatted content of the webpage
    """
    content = fetch_webpage_content(url)
    if content is None:
        return "## Error\n\nCould not access the webpage. It might be blocking our request or the URL might be invalid."
    
    return f"""
    ## Scraped Content from {url}
    
    **URL:** {url}
    
    **Content:**
    {content}
    """

def create_search_interface():
    """
    Create and launch the Gradio interface for the search function.
    """
    # Create the Gradio interface
    interface = gr.Interface(
        fn=search,
        inputs=[
            gr.Textbox(label="Search Query", placeholder="Enter your search query here..."),
            gr.Slider(minimum=1, maximum=10, value=5, step=1, label="Number of Results")
        ],
        outputs=gr.Markdown(label="Search Results"),
        title="DuckDuckGo Web Search",
        description="Enter a search query to find relevant web pages. Results will include summaries and full content in markdown format.",
        examples=[
            ["What is the latest news on Pope Leo XIV?", 3],
            ["Python programming best practices", 5],
            ["Latest developments in AI", 4]
        ],
        theme=Soft(),
        api_name="search"
    )
    
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
        inputs=gr.Textbox(label="URL", placeholder="Enter the URL to scrape (e.g., https://example.com)"),
        outputs=gr.Markdown(label="Scraped Content"),
        title="Web Page Scraper",
        description="Enter a URL to fetch and convert its content to markdown format.",
        examples=[
            ["https://en.wikipedia.org/wiki/Python_(programming_language)"],
            ["https://www.example.com"],
            ["https://gradio.app/"]
        ],
        theme=Soft(),
        api_name="scrape"
    )
    
    return interface

def main():
    print("Starting server...")
    # Create the interfaces
    search_interface = create_search_interface()
    datetime_interface = create_datetime_interface()
    scrape_interface = create_scrape_interface()
    
    # Create a Blocks app with multiple tabs
    with gr.Blocks(theme=Soft()) as demo:
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
        server_name="0.0.0.0",  # Allow external connections
        server_port=7860,
        share=False,
        debug=True,  # Enable debug mode
        show_error=True  # Show detailed errors
    )
    print("Server launched!")

if __name__ == "__main__":
    main()
