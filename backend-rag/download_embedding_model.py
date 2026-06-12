"""
Script to download the embedding model with SSL verification disabled
"""
import os
import ssl
import certifi
import httpx

# Monkeypatch httpx to disable SSL verification globally
original_client_init = httpx.Client.__init__

def patched_client_init(self, *args, **kwargs):
    kwargs['verify'] = False
    return original_client_init(self, *args, **kwargs)

httpx.Client.__init__ = patched_client_init

# Disable SSL verification
ssl._create_default_https_context = ssl._create_unverified_context

# Set environment variables to disable SSL for HuggingFace
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''
os.environ['SSL_CERT_FILE'] = ''
os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'

print("Downloading embedding model with SSL verification disabled...")

try:
    from sentence_transformers import SentenceTransformer

    # Download and cache the model
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2',
                                device='cpu',
                                trust_remote_code=True)
    print("✓ Model downloaded successfully!")
    print(f"Model cached in: {os.path.expanduser('~/.cache/huggingface/hub')}")

    # Test the model
    test_embedding = model.encode(["This is a test sentence"], show_progress_bar=False)
    print(f"✓ Model test successful! Embedding shape: {test_embedding.shape}")
    
except Exception as e:
    print(f"✗ Error downloading model: {e}")
    import traceback
    traceback.print_exc()
    print("\nTroubleshooting:")
    print("1. Check your internet connection")
    print("2. If behind a corporate proxy, you may need to configure proxy settings")
    print("3. The model may need to be downloaded manually from HuggingFace")