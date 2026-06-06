# import os
# from dotenv import load_dotenv

# load_dotenv()

# class Config:
#     # API Configuration - Will be provided during hackathon
#     GENAI_BASE_URL = "https://genailab.tcs.in"
#     GENAI_API_KEY = os.getenv("GENAI_API_KEY", "YOUR_KEY_HERE")  # Set this during event
    
#     # Model Selection
#     CHAT_MODEL = "azure_ai/genailab-maas-DeepSeek-V3-0324"
#     EMBEDDING_MODEL = "azure/genailab-maas-text-embedding-3-large"
    
#     # Alternative models available:
#     # "azure/genailab-maas-gpt-4o"
#     # "azure_ai/genailab-maas-Llama-3.3-70B-Instruct"
#     # "azure_ai/genailab-maas-Phi-4-reasoning"
    
#     # External APIs (Optional - can be added later)
#     GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY", "")
#     OPENTRIPMAP_API_KEY = os.getenv("OPENTRIPMAP_API_KEY", "")
    
#     # Flask Configuration
#     FLASK_PORT = 5000
#     FLASK_HOST = "0.0.0.0"
#     DEBUG = True

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Configuration - Will be provided during hackathon
    GENAI_BASE_URL = "https://genailab.tcs.in"
    GENAI_API_KEY = os.getenv("GENAI_API_KEY", "YOUR_KEY_HERE")

    # Hugging Face Configuration
    HF_TOKEN = os.getenv("HF_TOKEN")
    HF_API_URL = "https://router.huggingface.co/v1/chat/completions"
    HF_MODEL = "mistralai/Mistral-7B-Instruct-v0.2:featherless-ai"

    # Model Selection
    CHAT_MODEL = "azure_ai/genailab-maas-DeepSeek-V3-0324"
    EMBEDDING_MODEL = "azure/genailab-maas-text-embedding-3-large"

    # Alternative models available:
    # "azure/genailab-maas-gpt-4o"
    # "azure_ai/genailab-maas-Llama-3.3-70B-Instruct"
    # "azure_ai/genailab-maas-Phi-4-reasoning"

    # External APIs (Optional - can be added later)
    GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY", "")
    OPENTRIPMAP_API_KEY = os.getenv("OPENTRIPMAP_API_KEY", "")

    # Flask Configuration
    FLASK_PORT = 5000
    FLASK_HOST = "0.0.0.0"
    DEBUG = True