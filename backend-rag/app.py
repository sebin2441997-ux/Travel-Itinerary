from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from rag_service import RAGService
from config import Config

app = Flask(__name__)

# Enable CORS for Angular frontend
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:4200"], 
        "methods": ["GET", "POST", "PUT", "DELETE"], 
        "allow_headers": ["Content-Type"] 
    }
})
#checking linu

# Initialize RAG service
rag_service = RAGService()

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app. route('/api/rag/upload', methods=['POST']) 
def upload_document() :
    """Upload a PDF document for RAG indexing"""
    try:
        # Check if file is present
        if 'file' not in request.files: 
            return jsonify({
        "success": False,
        "error": "No file provided"
            }), 401
        file = request.files['file']
        # Check if filename is empty I
        if file.filename == '':
            return jsonify({
                "success": False,
                "error": "No file selected"
            }),402
        
        # Check file type
        if not allowed_file (file.filename):
            return jsonify({
                "success": False,
                "error": "Only PDF files are allowed"
            }), 403
        # Secure the filename
        filename = secure_filename(file.filename)
        # Read file content
        file_content = file.read()
        print(f"Received file: {filename}, size: {len(file_content)} bytes")
        # Upload and index document
        result = rag_service.upload_document(file_content, filename)
        print(f"Upload result: {result}")
        if result["success"]:
            return jsonify(result), 200
        else:
            # Check if it's a configuration issue
            if "RAG is disabled" in result.get("message", ''):
                return jsonify(result), 503 # Service Unavailable
            else:
                return jsonify(result), 400
    except Exception as e:
        print(f"Error in upload_document: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    
@app.route('/api/rag/generate', methods=['POST'])
def generate_rag_itinerary():
    """Generate itinerary using RAG with uploaded documents"""
    try:
        data = request.json
        preferences = data # Already in dict format

        # Generate RAG-based itinerary
        itinerary = rag_service.generate_rag_itinerary(preferences)
        return jsonify({ 
            "success": True,
            "itinerary": {
                "destination": preferences.get("destination"),
                "duration": f"{preferences.get('start_date')} to {preferences.get('end_date')}",
                "raw_itinerary": itinerary,
                "preferences": preferences
                }
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
