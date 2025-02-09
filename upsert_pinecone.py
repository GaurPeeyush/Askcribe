from pinecone import Pinecone as PineconeClient
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
import requests
from bs4 import BeautifulSoup
from typing import List, Optional

class PineconeUpserter:
    def __init__(self, pinecone_api_key: str, openai_api_key: str, index_name: str):
        self.openai_api_key = openai_api_key
        self.index_name = index_name
        self.pc = PineconeClient(api_key=pinecone_api_key)
        self.index = self.pc.Index(index_name)

    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = ' '.join(text.split())
        # Remove multiple newlines
        text = text.replace('\n\n', '\n').strip()
        return text

    def extract_text_from_url(self, url: str) -> Optional[str]:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Remove unwanted elements
                for element in soup.find_all(['script', 'style', 'nav', 'footer', 'header']):
                    element.decompose()
                
                # Get main content elements
                content = []
                
                # Try to find main content container
                main_content = soup.find(['main', 'article', 'div', 'section'], 
                                       class_=lambda x: x and any(word in str(x).lower() 
                                       for word in ['content', 'main', 'article', 'product']))
                
                if main_content:
                    # Extract structured content
                    # Title
                    title = soup.find('h1')
                    if title:
                        content.append(f"Title: {title.get_text().strip()}")
                    
                    # Description/paragraphs
                    for p in main_content.find_all('p'):
                        text = p.get_text().strip()
                        if text and len(text) > 20:  # Filter out short snippets
                            content.append(text)
                    
                    # Product specific information
                    # Features/Specifications
                    features = main_content.find_all(['ul', 'ol'])
                    for feature_list in features:
                        items = [item.get_text().strip() for item in feature_list.find_all('li')]
                        if items:
                            content.append("Features/Specifications:")
                            content.extend([f"- {item}" for item in items if item])
                    
                    # Price information
                    price = soup.find(class_=lambda x: x and 'price' in str(x).lower())
                    if price:
                        content.append(f"Price: {price.get_text().strip()}")
                    
                    return '\n'.join(content)
                else:
                    # Fallback to basic paragraph extraction
                    return '\n'.join([p.get_text().strip() for p in soup.find_all('p') 
                                    if p.get_text().strip()])
            return None
        except Exception as e:
            print(f"Error extracting text from {url}: {str(e)}")
            return None

    def process_and_upsert(self, urls: List[str]) -> bool:
        try:
            embeddings = OpenAIEmbeddings(openai_api_key=self.openai_api_key)
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=50,
                separators=["\n\n", "\n", ". ", " ", ""]  # More intelligent splitting
            )
            
            for url in urls:
                text = self.extract_text_from_url(url)
                if not text:
                    print(f"Failed to extract text from {url}")
                    continue
                
                # Clean the text
                text = self.clean_text(text)
                
                # Split text into chunks
                texts = text_splitter.split_text(text)
                
                # Generate embeddings
                print(f"Generating embeddings for {len(texts)} chunks from {url}")
                embeddings_list = embeddings.embed_documents(texts)
                
                vectors = []
                for i, (text_chunk, embedding) in enumerate(zip(texts, embeddings_list)):
                    # Create a more descriptive ID
                    chunk_id = f"{url.split('/')[-1]}_{i}"
                    
                    vector = {
                        'id': chunk_id,
                        'values': embedding,
                        'metadata': {
                            'text': text_chunk,
                            'url': url,
                            'chunk_index': i,
                            'total_chunks': len(texts)
                        }
                    }
                    vectors.append(vector)
                
                # Upsert to Pinecone in batches
                batch_size = 100
                for i in range(0, len(vectors), batch_size):
                    batch = vectors[i:i + batch_size]
                    self.index.upsert(vectors=batch)
                    print(f"Upserted batch {i//batch_size + 1} of {(len(vectors)-1)//batch_size + 1}")
                
                print(f"Successfully processed and upserted data from {url}")
            return True
        except Exception as e:
            print(f"Error in process_and_upsert: {str(e)}")
            return False

    # def extract_text_from_url(self, url: str) -> Optional[str]:
    #     try:
    #         response = requests.get(url)
    #         if response.status_code == 200:
    #             soup = BeautifulSoup(response.text, 'html.parser')
    #             return '\n'.join([p.get_text() for p in soup.find_all('p')])
    #         return None
    #     except Exception as e:
    #         print(f"Error extracting text from {url}: {str(e)}")
    #         return None

    # def process_and_upsert(self, urls: List[str]) -> bool:
    #     try:
    #         embeddings = OpenAIEmbeddings(openai_api_key=self.openai_api_key)
    #         text_splitter = RecursiveCharacterTextSplitter(
    #             chunk_size=500,
    #             chunk_overlap=50
    #         )
            
    #         for url in urls:
    #             text = self.extract_text_from_url(url)
    #             if not text:
    #                 print(f"Failed to extract text from {url}")
    #                 continue
                    
    #             texts = text_splitter.split_text(text)
    #             embeddings_list = embeddings.embed_documents(texts)
                
    #             vectors = []
    #             for i, (text_chunk, embedding) in enumerate(zip(texts, embeddings_list)):
    #                 vector = {
    #                     'id': f"{url}_{i}",
    #                     'values': embedding,
    #                     'metadata': {
    #                         'text': text_chunk,
    #                         'url': url
    #                     }
    #                 }
    #                 vectors.append(vector)
                
    #             # Upsert to Pinecone in batches
    #             batch_size = 100
    #             for i in range(0, len(vectors), batch_size):
    #                 batch = vectors[i:i + batch_size]
    #                 self.index.upsert(vectors=batch)
                
    #             print(f"Successfully processed and upserted data from {url}")
    #         return True
    #     except Exception as e:
    #         print(f"Error in process_and_upsert: {str(e)}")
    #         return False