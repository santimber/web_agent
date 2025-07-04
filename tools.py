# =========================
# Imports and Environment
# =========================
import os
from dotenv import load_dotenv
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.tools import Tool
from langchain_community.document_loaders import WikipediaLoader
import pandas as pd
from typing import List
from langchain.tools import tool
from playwright.sync_api import sync_playwright
import asyncio
import pandas as pd
from playwright.async_api import async_playwright
import pandas as pd

# Load environment variables
print("Current working directory:", os.getcwd())

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))


# =========================
# 1. Web Search Tools
# =========================
def tavily_search(query: str) -> str:
    """Searches the web using Tavily and return max 3 result.

    Args:
        query: The search query.

    """
    search = TavilySearchResults(max_results=3)
    results = search.run(query)

    formatted_results = []
    for result in results:
        title = result.get('title', 'No title')
        content = result.get('content', 'No content')

        formatted_result = f"Title: {title}\n{content}"
        formatted_results.append(formatted_result)

    return "\n\n---\n\n".join(formatted_results)


def multiply(a: int, b: int) -> int:
    """Multiply a and b.

    Args:
        a: first int
        b: second int
    """
    return a * b


def wiki_search(query: str, year: str = None) -> str:
    """
    Search Wikipedia for a query and return the URL of the most relevant page. 
    """
    if year:
        search_query = f"{query} {year} Wikipedia"
    else:
        search_query = query

    try:
        docs = WikipediaLoader(
            query=search_query,
            load_max_docs=1,
            doc_content_chars_max=100
        ).load()
        if docs and len(docs) > 0:
            url = docs[0].metadata["source"]
            return url
        else:
            return "No Wikipedia pages found for this query."
    except Exception as e:
        return f"Error searching Wikipedia: {e}"


async def fetch_page_async(url: str) -> str:
    """
    Asynchronously fetch the full HTML content of a webpage using Playwright.

    Args:
        url (str): The URL of the web page to browse.

    Returns:
        str: The full rendered HTML content of the page after waiting for tables to load.

    Notes:
        - This function uses a headless Chromium browser.
        - It waits specifically for a 'table.wikitable' element to be present.
        - Make sure 'playwright install' has been run before using this.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)
        await page.wait_for_selector("table.wikitable", timeout=10000)
        html = await page.content()
        await browser.close()
    return html


def extract_tables_tool(html: str):
    """
    Extract tables from HTML using pandas.read_html. Use this after fetch_page_sync to extract structured data from Wikipedia or other web pages.

    Args:
        html (str): Full HTML string of a webpage.

    Returns:
        List[str]: A list of tables (in Markdown format) that include an 'Album details' column.

    Notes:
        - Only tables with the column 'Album details' are included.
        - This filters specifically for tables like Mercedes Sosa's discography section.
        - Markdown format is used for readable display or downstream text applications.
    """
    try:
        tables = pd.read_html(html)
        filtered = []
        for df in tables:
            if "Album details" in df.columns:
                filtered.append(df.to_markdown(index=False))
        if not filtered:
            return ["No discography tables found."]
        return filtered
    except Exception as e:
        return [f"Error extracting tables: {e}"]


def fetch_page_sync(url: str) -> str:
    """
    Synchronously fetch the full HTML content of a web page using Playwright. Use this to retrieve the HTML of a Wikipedia page for table extraction with extract_tables_tool.
    """
    return asyncio.run(fetch_page_async(url))


# Testing the function
"""
html = await fetch_page_async("https://en.wikipedia.org/wiki/Mercedes_Sosa")
tables = extract_tables_tool(html)
print("\n\n---\n\n".join(tables))
"""
