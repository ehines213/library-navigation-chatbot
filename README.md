# Library Website Navigation Chatbot

A custom-built navigation chatbot designed to help library patrons quickly find information on a WordPress-based library website.  
The chatbot uses the public WordPress REST API to guide users to existing pages such as hours, printing, events, and library card information.

This project was built as a read-only, fault-tolerant enhancement that does not affect core website functionality.

---

## Features

- Natural-language navigation assistance (e.g., "printing", "hours", "library card")
- Direct links to existing WordPress pages
- Read-only access using the WordPress REST API
- Decoupled architecture (frontend and backend)
- API key protection for backend access
- Graceful failure if the chatbot service is unavailable

---

## Architecture Overview

### Frontend
- Lightweight JavaScript chat widget
- Embedded via HTML, CSS, and JavaScript
- Designed to be packaged as a WordPress plugin
- Does not collect cookies, tracking data, or patron information

### Backend
- Python FastAPI REST service
- Indexes publicly available WordPress content
- Handles search, ranking, and response generation
- Hosted independently from the WordPress site

### Data Flow
1. User enters a query in the chat widget
2. Frontend sends the request to the FastAPI backend
3. Backend queries the WordPress REST API
4. Relevant pages are ranked and returned
5. User is directed to official library website pages

---

## Security and Privacy

- No authentication data, personal information, or ILS access
- Read-only WordPress REST API usage
- API key required for backend access
- Secrets managed using environment variables
- Environment files excluded from version control

This design aligns with MSP-managed WordPress environments and public-sector IT security practices.

---

## Project Structure

```
library-nav-bot/
├── app/
│   ├── main.py          # FastAPI application
│   └── wp_index.py      # WordPress content indexing and search
├── demo/
│   ├── index.html       # Local demo page
│   ├── chatbot.js       # Chat widget logic
│   └── chatbot.css     # Chat widget styling
├── requirements.txt
├── .gitignore
└── README.md
```

## License

This project is intended for educational and internal library use only.
