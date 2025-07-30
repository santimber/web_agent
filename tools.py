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
from playwright.async_api import async_playwright
# Importing PDF loader from Langchain
from langchain.document_loaders.pdf import PyPDFDirectoryLoader
# Importing text splitter from Langchain
from langchain.text_splitter import RecursiveCharacterTextSplitter
# Importing OpenAI embeddings from Langchain
from langchain.embeddings import OpenAIEmbeddings
# Importing Document schema from Langchain
from langchain.schema import Document
from langchain.vectorstores.chroma import Chroma

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


# =========================
# 2. Multiply Tool
# =========================
def multiply(a: int, b: int) -> int:
    """Multiply a and b.

    Args:
        a: first int
        b: second int
    """
    return a * b


# =========================
# 3. Wikipedia Search Tool
# =========================
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


# =========================
# 4. Fetch Page Tool
# =========================
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


# =========================
# 5. Extract Tables Tool
# =========================
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


# =========================
# 6. Fetch Page Tool
# =========================
def fetch_page_sync(url: str) -> tuple[str, str]:
    """
    Synchronously fetch the full HTML content of a web page using Playwright.
    Returns both the HTML content and the URL for processing.
    """
    html_content = asyncio.run(fetch_page_async(url))
    return html_content, url


# Testing the function
"""
html = await fetch_page_async("https://en.wikipedia.org/wiki/Mercedes_Sosa")
tables = extract_tables_tool(html)
print("\n\n---\n\n".join(tables))
"""
# =========================
# 6. RAG Tools
# =========================


def split_text(web_content: str, source_url: str = None):
    """
    Split web content into smaller chunks and convert to Document objects.
    Args:
        web_content (str): The scraped web content (HTML/text) to split.
        source_url (str, optional): The source URL for metadata.
    Returns:
        list[Document]: List of Document objects representing the split text chunks.
    """
    # Initialize text splitter with specified parameters
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,  # Size of each chunk in characters
        chunk_overlap=100,  # Overlap between consecutive chunks
        length_function=len,  # Function to compute the length of the text
        add_start_index=True,  # Flag to add start index to each chunk
    )

    # Split the text into chunks and convert to Document objects
    chunks = splitter.split_text(web_content)
    documents = [Document(page_content=chunk, metadata={
                          "source": source_url}) for chunk in chunks]
    return documents


# Path to directory
CHROMA_DB_PATH = "chroma_db"


def save_to_chroma(chunks: List[Document]):
    """
    Save text to Chroma database.
    """
    try:
        # Clear out the existing database directory if it exists
        if os.path.exists(CHROMA_DB_PATH):
            shutil.rmtree(CHROMA_DB_PATH)

        # Create a new Chroma database from the documents using OpenAI embeddings
        db = Chroma.from_documents(
            chunks,
            OpenAIEmbeddings(),
            persist_directory=CHROMA_DB_PATH
        )

        # Persist the database to disk
        db.persist()
        print(f"Saved {len(chunks)} chunks to {CHROMA_DB_PATH}.")
    except Exception as e:
        print(f"Error saving to Chroma: {e}")
        return

# Generate Data Store


def generate_data_store(fetch_result: tuple[str, str]):
    """
    Function to generate vector database in chroma from scraped web content.

    Args:
        fetch_result (tuple[str, str]): Tuple containing (html_content, url) from fetch_page_sync
    """
    html_content, url = fetch_result
    # Split web content into Document objects
    documents = split_text(html_content, url)
    save_to_chroma(documents)  # Save the processed data to a data store

# Build Retriever


def retrieve_from_chroma(query: str) -> List[Document]:
    """
    Retrieve documents from Chroma database.
    """
    db = Chroma(persist_directory=CHROMA_DB_PATH,
                embedding_function=OpenAIEmbeddings())
    return db.similarity_search(query)

