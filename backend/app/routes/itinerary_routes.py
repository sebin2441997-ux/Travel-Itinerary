from flask import Blueprint, request, jsonify
from app.services.itinerary_service import ItineraryService
from app.services.tourism_api_service import TourismAPIService
from app.models import TripPreferences, ChatMessage

itinerary_bp = Blueprint('itinerary', __name__)
itinerary_service = ItineraryService()
tourism_service = TourismAPIService()

@itinerary_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "Travel Itinerary Assistant"}), 200

@itinerary_bp.route('/generate', methods=['POST'])
def generate_itinerary():
    """Generate a new itinerary from preferences"""
    try:
        data = request.json
        print("Data from frontend", data)
        preferences = TripPreferences(**data)
        print("preferences from frontend", preferences)
        itinerary = itinerary_service.create_itinerary(preferences)
        
        return jsonify({
            "success": True,
            "itinerary": itinerary
        }), 200
        
    except Exception as e:
        print("This is working")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@itinerary_bp.route('/chat', methods=['POST'])
def chat():
    """Handle conversational refinement"""
    try:
        data = request.json
        chat_message = ChatMessage(**data)
        
        response = itinerary_service.refine_itinerary(
            chat_message.message,
            chat_message.conversation_history or [],
            chat_message.trip_context.dict() if chat_message.trip_context else None
        )
        
        return jsonify({
            "success": True,
            "response": response
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@itinerary_bp.route('/places/search', methods=['GET'])
def search_places():
    """Search for places of interest"""
    try:
        destination = request.args.get('destination', '')
        category = request.args.get('category', 'tourist_attraction')
        
        places = tourism_service.search_places(destination, category)
        
        return jsonify({
            "success": True,
            "places": places
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@itinerary_bp.route('/export', methods=['POST'])
def export_itinerary():
    """Export itinerary in various formats"""
    try:
        data = request.json
        itinerary = data.get('itinerary')
        format_type = data.get('format', 'text')
        
        exported = itinerary_service.export_itinerary(itinerary, format_type)
        
        return jsonify({
            "success": True,
            "exported": exported
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
