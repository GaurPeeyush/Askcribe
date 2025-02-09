from pinecone import Pinecone as PineconeClient
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Pinecone as LangchainPinecone
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA
from typing import List, Tuple, Optional

class PineconeSearcher:
    def __init__(self, pinecone_api_key: str, openai_api_key: str, index_name: str):
        self.openai_api_key = openai_api_key
        self.index_name = index_name
        self.pc = PineconeClient(api_key=pinecone_api_key)
        self.embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        self.index = self.pc.Index(index_name)
        self.llm = OpenAI(openai_api_key=openai_api_key)

    def query_pinecone(self, query: str, urls: List[str], top_k: int = 10) -> Tuple[Optional[str], Optional[List]]:
        try:
            print(f"\nProcessing query: '{query}'")
            
            # Generate embedding for the query
            print("Generating embedding for query...")
            query_embedding = self.embeddings.embed_query(query)
            print("Query embedding generated")

            # Create metadata filter for URLs
            metadata_filter = {"url": {"$in": urls}} if urls else None
            
            # Query Pinecone
            print(f"Querying Pinecone for top {top_k} matches...")
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter=metadata_filter
            )
            print(f"Found {len(results['matches'])} matches")
            
            # Prepare context from matches
            print("Preparing context from matches...")
            context = ""
            source_docs = []
            for match in results['matches']:
                metadata = match.metadata
                context += f"""Text: {metadata['text']}
                             URL: {metadata['url']}
                             \n\n"""
                source_docs.append(metadata)

            print("Context prepared")
            
            prompt = f"""You are Askribe, a very friendly and professional chatbot behaving like a human. Please analyze the following context and answer the query in detail:

Context:
{context}

Query:
{query}

Instructions:
1. STRICTLY respond using ONLY the information provided in the context above
2. If any part of the query cannot be answered using the given context, explicitly state: "I apologize, but I cannot answer [specific aspect] as it's not covered in the provided context."
3. Do not make assumptions or add information from outside the context
4. Break down your response to clearly indicate which parts of the context you are referencing (DO NOT tell the similarity score)
5. For partial matches, clarify what information is available and what is missing
"""

            print("\nQuerying OpenAI...")
            response = self.llm.predict(prompt)
            
            return response, source_docs

        except Exception as e:
            print(f"Error in query_pinecone: {str(e)}")
            return None, None
