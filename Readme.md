# [Askcribe - AI-Powered Web Content Q&A Tool](https://askcribe.streamlit.app/)

Askcribe is an intelligent web application that allows users to extract information from web pages and ask questions about their content. Using advanced AI and vector search technology, it provides precise answers based on the ingested web content.

## Features

- 🌐 Web Content Extraction: Automatically scrapes and processes content from provided URLs
- 🔍 Semantic Search: Uses Pinecone vector database for efficient content retrieval
- 🤖 AI-Powered Answers: Leverages OpenAI's language models for accurate responses
- 💻 User-Friendly Interface: Clean Streamlit-based web interface
- 📑 Source Attribution: Provides references to source documents for transparency

## Prerequisites

- Python 3.8+
- Pinecone API Key
- OpenAI API Key
- Active Pinecone Index

## Tech Stack

🔧 **Python** | 🌐 **Streamlit** (UI) | 🤖 **OpenAI** (LLM & Embeddings) | 🔍 **Pinecone** (Vector DB) | 🔗 **LangChain** (AI Framework) | 🌿 **BeautifulSoup** (Web Scraping) | 📦 **Python-dotenv** (Environment Management)

## Installation

1. Clone the repository:<br>
   git clone https://github.com/yourusername/askcribe.git<br>

2. Install required packages:<br>
   pip install -r requirements.txt<br>

3. Create a `.env` file in the project root with the following variables:<br>
   PINECONE_API_KEY=your_pinecone_api_key<br>
   OPENAI_API_KEY=your_openai_api_key<br>
   PINECONE_INDEX_NAME=your_index_name<br>

## Usage

### Command Line Interface
Run the main script: <br>python main.py

### Web Interface
Launch the Streamlit app: <br>streamlit run app.py


## Project Structure
askcribe/
├── app.py # Streamlit web interface<br>
├── main.py # Command line interface<br>
├── search_pinecone.py # Search functionality<br>
├── upsert_pinecone.py # Content processing and storage<br>
├── requirements.txt # Project dependencies<br>
└── .env # Environment variables<br>

## In Action
<img width="1470" alt="Screenshot 2025-02-09 at 11 16 15 PM" src="https://github.com/user-attachments/assets/8455e6ca-a3ea-46e4-a18b-f6ca4b7c9445" />
