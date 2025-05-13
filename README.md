# Barbeque Nation Chatbot

A chatbot implementation for Barbeque Nation restaurant chain handling inquiries and bookings.

## Knowledge Base API

This API provides structured information about Barbeque Nation to power the chatbot:

- `/api/outlets` - Information about restaurant locations
  - Query parameters:
    - `location`: Filter outlets by location (delhi, bangalore)
    - `chunk`: Pagination for response chunking

- `/api/menu` - Menu information
  - Query parameters:
    - `category`: Filter by menu category
    - `chunk`: Pagination for response chunking

- `/api/faq` - Frequently asked questions
  - Query parameters:
    - `keyword`: Filter FAQs by keyword
    - `chunk`: Pagination for response chunking

- `/api/query` - Unified query endpoint
  - Query parameters:
    - `q`: Natural language query about outlets, menu, or general questions

### Token Management

The API implements chunking to ensure responses stay under the 800 token limit required by the RetellAI platform.

## Running Locally

1. Install dependencies: `pip install -r requirements.txt`
2. Run the server: `python run.py`
3. Access the API at `http://localhost:5000`