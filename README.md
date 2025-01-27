# 21-Day Agent Series: Day 2 AGENT : On-the-Road-Museum-Travel-Agent

# On-the-Road-Museum-Travel-Agent
This agent A New AI Agent Every Day! Series  Day 2/21 - On-the-Road Museum Travel Agent's 🏛️ 🎉This agent that will make your travels richer using GoogleMaps MCP! 🚗✨  Shows you the must-visit museums in other cities you will pass through during your trip between two cities 🗺️

## Installation

### Prerequisites
- Python 3.9 or higher
- Git
- Virtual environment (recommended)

### Steps

# Don't forget to download nodejs for mcp

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the root directory and configure it as follows:
   ```env
   AZURE_OPENAI_ENDPOINT="your_azure_openai_endpoint
   AZURE_OPENAI_API_VERSION="your_azure_openai_api_version"
   AZURE_OPENAI_API_KEY="your_azure_openai_api_key"
   GOOGLE_MAPS_API_KEY="YOUR_GOOGLE_MAPS_API_KEY"
   ```

---

## Running the Application

1. Start the FastAPI server:
   ```bash
   uvicorn upsonicai:app --reload
   ```

2. Open the UI in your browser:
   ```
   http://127.0.0.1:8000/
   ```

3. Use the form to input:
   - **GitHub Release URL**
   - **Company URL**
   - **Product Aim**

4. Click "Generate" to see platform-specific announcements rendered in the UI. Each platform's content will be displayed in separate boxes with a "Copy" button for easy sharing.

---

## API Documentation

Interactive API docs are available at:
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---
