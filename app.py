import streamlit as st
from search_pinecone import PineconeSearcher
from upsert_pinecone import PineconeUpserter
from typing import List
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get environment variables
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
INDEX_NAME = os.getenv('PINECONE_INDEX_NAME')

# Page configuration
st.set_page_config(
    page_title="Askcribe",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-title {
        text-align: center;
        color: #1E88E5x;
        font-size: 2.5em;
        margin-bottom: 0;
    }
    .subtitle {
        text-align: center;
        color: #7b00b6;
        font-size: 1.2em;
        margin-bottom: 2em;
    }
    .feature-text {
        background-color: #7b00b6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        text-align: center
    }
    </style>
    """, unsafe_allow_html=True)

# Main title and description
st.markdown("<h1 class='main-title'>Askcribe – Your AI-Powered Web Content Q&A Tool</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Extract. Ask. Answer.</p>", unsafe_allow_html=True)

# Description
st.markdown("""
<div class='feature-text'>
Ever wished you could get instant answers from a webpage without digging through endless text? Askcribe makes it effortless.<br><br>

**How It Works:**<br>
🔗 Enter URLs – Provide one or more web pages to analyze.<br>
❓ Ask Questions – Query specific details from the content.<br>
✅ Get Answers – Receive precise, to-the-point responses based only on the ingested information.
</div>
""", unsafe_allow_html=True)

# Initialize session state for URLs if it doesn't exist
if 'urls' not in st.session_state:
    st.session_state.urls = [""]

# URL input section
st.subheader("🔗 Enter URLs to Analyze")
col1, col2 = st.columns([6, 1])
with col1:
    # Display URL input fields
    for i, url in enumerate(st.session_state.urls):
        cols = st.columns([10, 1, 1])
        with cols[0]:
            st.session_state.urls[i] = st.text_input(
                f"URL {i+1}",
                value=url,
                key=f"url_{i}",
                label_visibility="collapsed"
            )
        with cols[1]:
            if st.button("🗑️", key=f"delete_{i}") and len(st.session_state.urls) > 1:
                st.session_state.urls.pop(i)
                st.rerun()
        with cols[2]:
            if st.button("➕", key=f"add_{i}"):
                st.session_state.urls.append("")
                st.rerun()

# Chat interface
st.subheader("💬 Ask Your Question")
user_question = st.text_input("Enter your question about the content")

if st.button("Get Answer"):
    if not any(st.session_state.urls):
        st.error("Please enter at least one URL")
    elif not user_question:
        st.error("Please enter a question")
    else:
        # Filter out empty URLs
        valid_urls = [url for url in st.session_state.urls if url.strip()]

        # Validate URLs
        invalid_urls = []
        for url in valid_urls:
            if not url.startswith(('http://', 'https://')):
                invalid_urls.append(url)
        
        if invalid_urls:
            st.error(f"Invalid URL format for: {', '.join(invalid_urls)}\nURLs must start with http:// or https://")

        with st.spinner("Processing URLs and generating answer..."):
            try:
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

                # Process URLs and get answer
                if upserter.process_and_upsert(valid_urls):
                    answer, source_docs = searcher.query_pinecone(user_question, valid_urls)
                    
                    if answer and source_docs:
                        st.success("Answer generated successfully!")
                        st.markdown("### Answer:")
                        st.write(answer)
                        
                        with st.expander("View Source Documents"):
                            for i, doc in enumerate(source_docs, 1):
                                st.markdown(f"**Document {i}:**")
                                st.markdown(f"- URL: {doc['url']}")
                                st.markdown(f"- Content: {doc['text']}")
                    else:
                        st.warning("Sorry, I couldn't find relevant information to answer your question.")
                else:
                    st.error("I am sorry, URL doesn't allow scraping content")
                    
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

# Footer
st.markdown("---")
st.markdown("Made with ❤️ by Peeyush Gaur")