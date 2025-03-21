"""
CrossRef Article Search and HTML Output Script

This script retrieves academic articles from the CrossRef API based on a user-provided search query and displays the results in an HTML format. 
The script is designed for efficient data gathering and presentation, using Python libraries such as requests for HTTP communication, logging for event tracking, 
and webbrowser for displaying results. Key features include:

- A function to query the CrossRef API and process the retrieved article metadata (title, authors, publication date, and summary).
- Helper functions to truncate long text fields and generate a clean, clickable HTML output.
- Error handling for API requests and user input validation.

Intended for use in research workflows, the script automates the process of searching and viewing academic articles.
"""


import os
import requests
from typing import List, Optional
import logging
import pandas as pd
import webbrowser

# ---------------------------
# Configuration and Setup
# ---------------------------

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------
# Define the CrossRef Search Function
# ---------------------------

def search_crossref(query: str, rows: int = 5) -> List[dict]:
    """
    Searches the CrossRef API for articles matching the query.

    Args:
        query (str): The search query.
        rows (int): Number of results to return.

    Returns:
        List[dict]: A list of article metadata dictionaries.
    """
    logger.info(f"Searching CrossRef for query: '{query}' with rows: {rows}")
    url = "https://api.crossref.org/works"
    params = {
        "query": query,
        "rows": rows,
        "filter": "type:journal-article",
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"CrossRef API request failed: {e}")
        return []

    articles = [
        {
            "title": item.get("title", ["No title available"])[0],
            "authors": ", ".join(
                f"{author.get('given', '')} {author.get('family', '')}".strip()
                for author in item.get("author", [])
            ) or "No authors available",
            "published": (
                (item.get("published-print") or item.get("published-online") or {})
                .get("date-parts", [[None]])[0][0]
            ),
            "URL": item.get("URL", "#"),
            "summary": item.get("abstract", None),
        }
        for item in data.get("message", {}).get("items", [])
    ]

    logger.info(f"Found {len(articles)} articles.")
    return articles

# ---------------------------
# Define Helper Functions
# ---------------------------

def truncate(text: str, max_length: int = 50) -> str:
    """Truncate text if it's longer than max_length, appending '...'."""
    return text if len(text) <= max_length else f"{text[:max_length - 3]}..."

def save_to_html(articles: List[dict], filename: str = "output.html") -> None:
    """Convert articles to HTML and open in the default web browser."""
    if not articles:
        logger.info("No articles to save.")
        return

    # Create clickable titles and truncate fields
    for article in articles:
        article['title'] = f'<a href="{article["URL"]}" target="_blank" style="font-size: 18px; color: #1a0dab; text-decoration: none;">{truncate(article["title"], 70)}</a>'
        article['authors'] = truncate(article['authors'], 50)
        article['summary'] = truncate(article['summary'], 500) if article['summary'] else ""

    # Generate HTML content
    html_results = "".join(
        f"""
        <div class="result">
            <div class="title">{article['title']}</div>
            <div class="authors">{article['authors']}</div>
            {'<div class="published">Published: ' + str(article['published']) + '</div>' if article['published'] else ''}
            {'<div class="summary">Summary: ' + article['summary'] + '</div>' if article['summary'] else ''}
        </div>
        """
        for article in articles
    )

    html_content = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
            }}
            .result {{
                margin-bottom: 20px;
                padding-bottom: 10px;
                border-bottom: 1px solid #e0e0e0;
            }}
            .title {{
                font-size: 18px;
                color: #1a0dab;
                text-decoration: none;
            }}
            .authors, .published, .summary {{
                font-size: 14px;
                color: #545454;
            }}
            .authors {{
                color: #006621;
            }}
        </style>
    </head>
    <body>
        {html_results}
    </body>
    </html>
    """

    # Save and open HTML file
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)
    webbrowser.open(f"file://{os.path.realpath(filename)}")
    logger.info(f"Results saved to {filename} and opened in web browser.")

# ---------------------------
# Main Execution Function
# ---------------------------

def main():
    try:
        user_query = input("Enter your search query: ").strip()
        if not user_query:
            raise ValueError("Search query cannot be empty.")

        num_rows_input = input("Enter the number of articles to retrieve: ").strip()
        num_rows = int(num_rows_input) if num_rows_input.isdigit() else 5
        logger.info(f"Retrieving {num_rows} articles for query: '{user_query}'.")

        articles = search_crossref(user_query, rows=num_rows)
        save_to_html(articles)

    except ValueError as ve:
        logger.error(f"Input error: {ve}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
