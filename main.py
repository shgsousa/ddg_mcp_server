from duckduckgo_search import DDGS
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify
import time
import gradio as gr

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
        theme=gr.themes.Soft(),
        api_name="search"
    )
    
    return interface

def main():
    # Create and launch the Gradio interface
    interface = create_search_interface()
    interface.launch(
        mcp_server=True,
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
    )

if __name__ == "__main__":
    main()
