import os
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

try:
    from langchain_community.embeddings import HuggingFace
    EmbeddingsEMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = True

class RAGService:
    def __init__(self):
        # Initialize Local Embedding Model (no API key needed)
        print("Loading local embedding model...")
    
        self.embedding_model = None
        self.embeddings_available = False
    
        # Try to load embedding model
        if EMBEDDINGS_AVAILABLE:
            try:
                # Disable SSL verification for HuggingFace model download
                ssl._create_default_https_context = ssl._create_unverified_context
                
                # Monkeypatch httpx for SSL
                original_client_init = httpx.Client.__init__
                def patched_init(self, *args, **kwargs):
                    kwargs['verify'] = False
                    return original_client_init(self, *args, **kwargs)
                httpx.Client.__init__ = patched_init
                
                from langchain_community.embeddings import HuggingFaceEmbeddings
                self.embedding_model = HuggingFaceEmbeddings(
                    model_name="sentence-transformers/all-MiniLM-L6-v2",
                    model_kwargs={'device': 'cpu'},
                    encode_kwargs={'normalize_embeddings': True}
                )
                self.embeddings_available = True
                print("✓ Local embedding model loaded successfully")
            except Exception as e:
                print(f"⚠ Could not load embedding model: {str(e)[:100]}...")
                print("⚠ RAG document upload will be disabled until model is available.")
                print("  This is likely due to corporate network restrictions.")
                self.embedding_model = None
        else:
            print("⚠ HuggingFace embeddings not available")
       
        # Check if GenAI API key is configured (only needed for LLM, not embeddings)
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
                    print("  No existing vector store found")
            except Exception as e:
                self.vectordb = None
                print(f"  Could not load vector store: {e}")
        else:
            print("  Vector store disabled (embeddings not available)")

    def upload_document(self, file_content: bytes, filename: str) -> Dict:
        """Upload and index a PDF document using local embeddings"""
       
        if not self.embeddings_available:
            return {
                "success": False,
                "message": "Embedding model not available. Cannot index documents due to network restrictions. Please see documentation for manual model download.",
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