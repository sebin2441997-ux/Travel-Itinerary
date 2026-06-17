import os
import sys
import tempfile
import pickle
import ssl
import traceback
import certifi
from typing import List, Dict
from pdfminer.high_level import extract_text
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
import httpx
from config import Config
from config import Config

from tcs_embeddings import TCSGenAIEmbeddings

class RAGService:
    def __init__(self):
        # Initialize TCS GenAI Embedding Model (uses GenAI API)
        print("Loading TCS GenAI embedding model...")
    
        self.embedding_model = None
        self.embeddings_available = False
    
        # Try to initialize TCS GenAI embeddings
        try:
            if Config.GENAI_API_KEY and Config.GENAI_API_KEY not in ["YOUR_KEY_HERE", "your_api_key_here", ""]:
                self.embedding_model = TCSGenAIEmbeddings()
                self.embeddings_available = True
                print("✓ TCS GenAI embedding model initialized successfully")
            else:
                print("⚠ GenAI API key not configured")
                print("⚠ RAG document upload will be disabled")
        except Exception as e:
            print(f"⚠ Could not initialize TCS GenAI embeddings: {str(e)}")
            print("⚠ RAG document upload will be disabled")
            self.embedding_model = None
       
        # Check if GenAI API key is configured (needed for both LLM and embeddings)
        self.use_llm = Config.GENAI_API_KEY and Config.GENAI_API_KEY not in ["YOUR_KEY_HERE", "your_api_key_here", ""]
       
        if self.use_llm:
            # Create HTTP client with SSL verification disabled for LLM API
            self.client = httpx.Client(verify=False)
           
            # Initialize LLM for generating itineraries
            self.llm = ChatOpenAI(
                base_url=Config.GENAI_BASE_URL,
                model=Config.CHAT_MODEL,
                api_key=Config.GENAI_API_KEY,
                http_client=self.client
            )
            #REFEENA edit
            print("=== LLM CONFIG ===")
            print("BASE URL:", Config.GENAI_BASE_URL)
            print("MODEL:", Config.CHAT_MODEL)
            print("API KEY PRESENT:", bool(Config.GENAI_API_KEY))
            print("==================")
        else:
            self.llm = None
            self.client = None
           
        # Vector store directory
        self.persist_directory = "./data/faiss_travel_docs"
        os.makedirs(self.persist_directory, exist_ok=True)
        self.vectordb_path = os.path.join(self.persist_directory, "vectordb.faiss")
        #refeena edit
        print("to check error",self.vectordb_path)
        print(os.path.exists(self.vectordb_path))
       
        # Try to load existing vector store (only if embeddings available)
        self.vectordb = None
        if self.embeddings_available:
            try:
                if os.path.exists(self.vectordb_path):
                    self.vectordb = FAISS.load_local(
                        self.persist_directory,
                        self.embedding_model,
                        "vectordb",
                        allow_dangerous_deserialization=True
                    )
                    print(f"✓ Loaded existing FAISS vector store")
                else:
                    print("  No existing vector store found")
            except Exception as e:
                self.vectordb = None
                print(f"  Could not load vector store: {e}")
        else:
            print("  Vector store disabled (embeddings not available)")

    def upload_document(self, file_content: bytes, filename: str) -> Dict:
        """Upload and index a PDF document using TCS GenAI embeddings"""
       
        if not self.embeddings_available:
            return {
                "success": False,
                "message": "Embedding model not available. Please check GenAI API key configuration.",
                "chunks_indexed": 0
            }
       
        try:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name
           
            # Extract text from PDF
            print(f"Extracting text from {filename}...")
            raw_text = extract_text(temp_file_path)
           
            # Clean up temp file
            os.unlink(temp_file_path)
           
            if not raw_text or len(raw_text.strip()) < 100:
                return {
                    "success": False,
                    "message": "Could not extract meaningful text from PDF",
                    "chunks_indexed": 0
                }
           
            # Split text into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            chunks = text_splitter.split_text(raw_text)
           
            print(f"Split document into {len(chunks)} chunks")
           
            # Add metadata to chunks
            metadatas = [{"source": filename, "chunk": i} for i in range(len(chunks))]
           
            # Create or update vector store
            if self.vectordb is None:
                print("Creating new FAISS vector store...")
                self.vectordb = FAISS.from_texts(
                    chunks,
                    self.embedding_model,
                    metadatas=metadatas
                )
            else:
                print("Adding to existing vector store...")
                self.vectordb.add_texts(chunks, metadatas=metadatas)
           
            # Save the vector store
            self.vectordb.save_local(self.persist_directory, "vectordb")
            print("Vector store saved successfully")
           
            return {
                "success": True,
                "message": f"Successfully indexed {filename}",
                "chunks_indexed": len(chunks),
                "filename": filename
            }
           
        except Exception as e:
            print(f"Error uploading document: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "chunks_indexed": 0
            }        
    def generate_rag_itinerary(self, preferences: Dict) -> str:
        """Generate itinerary using RAG with uploaded documents"""
       
        if not self.use_llm or self.vectordb is None:
            return self._get_mock_rag_response(preferences)
       
        try:
            # Create retriever
            retriever = self.vectordb.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 5}
            )
            # Create RAG chain
            rag_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                retriever=retriever,
                return_source_documents=True
            )

            # Create prompt
            destination = preferences.get("destination", "")
            start_date = preferences.get("start_date", "")
            end_date = preferences.get("end_date", "")
            budget = preferences.get("budget", "moderate")
            interests = ", ".join(preferences.get("interests", []))

            prompt = f"""Based on the travel documents provided, create a detailed travel itinerary for:
                        Destination: {destination}
                        Dates: {start_date} to {end_date}
                        Budget: {budget}
                        Interests: {interests}

                        Use specific information from the documents about {destination} including:
                        - Recommended attractions and activities
                        - Local tips and insights
                        - Restaurant and dining recommendations
                        - Transportation options
                        - Cultural information
                        - Practical tips

                        Provide a day-by-day itinerary with morning, afternoon, and evening activities. Include specific timings and estimated costs."""
            
            # Run RAG query
            print("Generating RAG-based itinerary...")
            result = rag_chain.invoke(prompt)
            # Extract result
            if isinstance(result, dict):
                answer = result.get("result", "")
                sources = result.get("source_documents", [])
                # Format response with sources
                formatted_result = f"""# {destination} Travel Itinerary (RAG-Enhanced){start_date} to {end_date}{answer}
                        ---
                        Sources: Based on {len(sources)} document excerpts from uploaded travel guides.
                        """
                return formatted_result
            else:
                return str(result)
          #refeenas edit  
        except Exception as e:
            print("\n=== FULL ERROR ===")
            print("TYPE:", type(e).__name__)
            print("ERROR:", str(e))
            print("REPR:", repr(e))
            traceback.print_exc()
            print("==================\n")

            return f"Error generating RAG itinerary: {str(e)}\n\nFalling back to standard generation."
                    
        #except Exception as e:
                    #print(f"Error in RAG generation: {str(e)}")
                    #return f"Error generating RAG itinerary: {str(e)}\n\nFalling back to standard generation."
