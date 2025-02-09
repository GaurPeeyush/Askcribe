from search_pinecone import PineconeSearcher
from upsert_pinecone import PineconeUpserter
from typing import List
from dotenv import load_dotenv
import os
import streamlit as st
# Load environment variables from .env file
load_dotenv()

# Get environment variables
PINECONE_API_KEY = st.secrets["PINECONE_API_KEY"]
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
INDEX_NAME = st.secrets["PINECONE_INDEX_NAME"]

# Validate environment variables
if not all([PINECONE_API_KEY, OPENAI_API_KEY, INDEX_NAME]):
    raise ValueError("Missing required environment variables. Please check your .env file.")

def process_query(query: str, urls: List[str]) -> None:
    # Initialize our classes
    searcher = PineconeSearcher(
        pinecone_api_key=PINECONE_API_KEY,
        openai_api_key=OPENAI_API_KEY,
        index_name=INDEX_NAME
    )
    upserter = PineconeUpserter(
        pinecone_api_key=PINECONE_API_KEY,
        openai_api_key=OPENAI_API_KEY,
        index_name=INDEX_NAME
    )

    # # First, try to find relevant info in existing Pinecone DB
    # answer, source_docs = searcher.query_pinecone(query, urls)
    
    # if source_docs and len(source_docs) > 0:
    #     print("\nFound relevant information in existing database:")
    #     print("Answer:", answer)
    #     print("\nSource Documents:")
    #     for i, doc in enumerate(source_docs, 1):
    #         print(f"\nDocument {i}:")
    #         print(f"URL: {doc['url']}")
    #         print(f"Content: {doc['text']}")
    #     return

    # If no relevant docs found, process the URLs and try again
    print("\nNo relevant information found in existing database. Processing provided URLs...")
    if upserter.process_and_upsert(urls):
        answer, source_docs = searcher.query_pinecone(query, urls)
        
        if source_docs and len(source_docs) > 0:
            print("\nFound relevant information after processing new URLs:")
            print("Answer:", answer)
            print("\nSource Documents:")
            for i, doc in enumerate(source_docs, 1):
                print(f"\nDocument {i}:")
                print(f"URL: {doc['url']}")
                print(f"Content: {doc['text']}")
        else:
            print("\nSorry, I don't have enough knowledge to answer this query even after processing the provided URLs.")
    else:
        print("\nFailed to process and store the new URLs. Please try again later.")

if __name__ == "__main__":
    # Example usage
    urls = [
        "https://www.ikea.com/in/en/p/baggebo-shelving-unit-metal-white-60483873/",
        "https://www.furlenco.com/rent/products/mattress-king-size-foam-(78-x-72-x-6-inches)-51-rent",
        "https://www.rentomojo.com/bangalore/appliances/rent-fully-automatic-top-load-washing-machine/101630",
        "https://www.pepperfry.com/category/study-tables.html?type=hamburger-clp"
        # Add more URLs here
    ]
    query = "what are the dimensions of BAGGEBO?"
    
    process_query(query, urls)
