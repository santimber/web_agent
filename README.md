# GAIA Benchmark LangGraph Agent

A LangGraph-based AI agent for answering questions using web search, Wikipedia, and web scraping capabilities, in line with GAIA benchmarks.

## Features

- Web search using Tavily
- Wikipedia content retrieval
- Web page scraping with Playwright
- Table extraction from HTML
- Tool-based reasoning with LangGraph

## Setup

### Prerequisites

1. **Environment Variables**: Create a `.env` file in the project root with your API keys:
   ```bash
   # Required API Keys
   OPENAI_API_KEY=your_openai_api_key_here
   TAVILY_API_KEY=your_tavily_api_key_here
   
   # Optional: LangSmith tracing (for debugging and monitoring)
   LANGCHAIN_API_KEY=your_langsmith_api_key_here
   LANGSMITH_TRACING=true
   LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
   LANGSMITH_PROJECT=your_project_name
   ```

2. **Python Environment**: Ensure you have Python 3.8+ installed

### Installation

Run the automated setup script:

```bash
# Run the Python setup script (installs dependencies + Playwright browsers)
python setup.py
```

That's it! The setup script will:
- Install all Python dependencies from `requirements.txt`
- Install Playwright browser binaries for web scraping
- Verify the installation

### Alternative Setup Methods

If you prefer manual setup:

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browser binaries (REQUIRED)
playwright install
```

## Usage

```python
# Run the agent
python agent.py
```

## Dependencies

- **LangGraph**: Graph-based workflow orchestration
- **LangChain**: LLM integration and tool management
- **Playwright**: Web scraping and browser automation
- **Pandas**: Data manipulation and table extraction
- **Tavily**: Web search API
- **Wikipedia**: Wikipedia content retrieval

## Important Notes

- **API Keys Required**: You must set up your API keys in the `.env` file before running the agent
- **Playwright Browser Binaries**: The setup script automatically installs browser binaries for web scraping functionality
- **Browser Dependencies**: Playwright requires system-level browser dependencies on Linux systems

## Troubleshooting

### API Key Issues
- **Missing API Keys**: Ensure your `.env` file exists and contains valid API keys
- **Invalid API Keys**: Verify your API keys are correct and have sufficient credits

### Playwright Installation Issues

If you encounter Playwright installation issues:

1. **Linux**: Install additional dependencies:
   ```bash
   sudo apt-get update
   sudo apt-get install -y libwoff1 libopus0 libwebp7 libwebpdemux2 libenchant1c2a libgudev-1.0-0 libsecret-1-0 libhyphen0 libgdk-pixbuf2.0-0 libegl1-mesa libnotify4 libxslt1.1 libevent-2.1-7 libgles2-mesa libvpx7
   ```

2. **macOS**: Usually works out of the box

3. **Windows**: Usually works out of the box

### Manual Playwright Installation
If the setup script fails to install Playwright browsers, run manually:
```bash
playwright install
```

## Project Structure

```
├── agent.py          # Main LangGraph agent
├── tools.py          # Custom tools implementation
├── requirements.txt  # Python dependencies
├── setup.py         # Automated setup script
└── README.md        # This file
``` 
