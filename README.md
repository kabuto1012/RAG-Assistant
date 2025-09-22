# RDR2-RAG-Assistant

A Red Dead Redemption 2 assistant powered by RAG (Retrieval-Augmented Generation) technology. This project provides two systems for answering questions about Red Dead Redemption 2:

1. **Local RAG System** - Uses ChromaDB for local knowledge retrieval
2. **Web Search Crew System** - Uses CrewAI for web-based information gathering

## Features

- Comprehensive knowledge base about RDR2 weapons, horses, locations, tips, and more
- Two different AI agent systems for flexible information retrieval
- Powered by Google's Gemini AI model
- Local vector database storage with ChromaDB
- Web scraping capabilities for up-to-date information

## Setup

### Prerequisites

- Python 3.8 or higher
- Google Gemini API key

### Installation

#### Quick Setup (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/kabuto1012/RDR2-RAG-Assistant.git
cd RDR2-RAG-Assistant
```

2. Run the setup script:
```bash
chmod +x setup.sh
./setup.sh
```

3. Edit `.env` file and add your API keys:
```
GEMINI_API_KEY=your_actual_gemini_api_key_here
GOOGLE_API_KEY=your_google_api_key_here  # Optional, can use same as GEMINI_API_KEY
```

#### Manual Setup

1. Clone the repository:
```bash
git clone https://github.com/kabuto1012/RDR2-RAG-Assistant.git
cd RDR2-RAG-Assistant
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
```

4. Edit `.env` file and add your API keys

#### Test Your Setup

Run the test script to verify everything is working:
```bash
python3 test_setup.py
```

### Getting API Keys

- **Gemini API Key**: Get it from [Google AI Studio](https://aistudio.google.com/app/apikey)
- **Google API Key**: Same as Gemini API key (they use the same service)

## Usage

### Local RAG System

```bash
cd RedDeadRemeption2
python agent.py
```

This system uses the local knowledge base stored in the `info/` directory and ChromaDB for vector storage.

### Web Search Crew System

```bash
cd RedDeadRemeption2/Search_Crew_Agent_System
python crew_agent.py
```

This system uses web search to find current information about RDR2.

## Project Structure

```
RDR2-RAG-Assistant/
├── RedDeadRemeption2/
│   ├── agent.py                    # Main RAG agent
│   ├── info/                       # Knowledge base files
│   │   ├── weapons.txt
│   │   ├── horses.txt
│   │   ├── locations.txt
│   │   └── ...
│   └── Search_Crew_Agent_System/   # Web search system
│       ├── crew_agent.py
│       ├── search_tool.py
│       └── scraper_tool.py
├── requirements.txt
├── .env.example
└── README.md
```

## Security

- Never commit your `.env` file to version control
- Keep your API keys secure and don't share them publicly
- The `.gitignore` file is configured to exclude sensitive files

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is for educational purposes. Please respect Rockstar Games' intellectual property rights regarding Red Dead Redemption 2 content.