import json
from typing import Dict, List
from app.services.llm_service import LLMService
from app.models import TripPreferences, TripItinerary

class ItineraryService:
    def __init__(self):
        self.llm_service = LLMService()
    
    def create_itinerary(self, preferences: TripPreferences) -> Dict:
        """Create a complete itinerary from preferences"""
        
        # Convert preferences to dict
        prefs_dict = preferences.dict()
        # print("Insided prefs_dict", prefs_dict)
        # Generate itinerary using LLM
        raw_itinerary = self.llm_service.generate_itinerary(prefs_dict)
        # print("Insided raw_itinerary", raw_itinerary)
        # Parse and structure the response
        structured_itinerary = self._parse_itinerary(raw_itinerary, preferences)
        # print("Insided structured itinerary", structured_itinerary)
        
        return structured_itinerary
    
    def refine_itinerary(self, message: str, conversation_history: List[dict], 
                        trip_context: Dict = None) -> str:
        """Refine itinerary through conversation"""
        print("trip context", trip_context)
        response = self.llm_service.chat_refinement(
            message, 
            conversation_history, 
            trip_context
        )
        print("Refine Itinerary response", response)
        return response
    
    def _parse_itinerary(self, raw_text: str, preferences: TripPreferences) -> Dict:
        """Parse the LLM response into structured format"""
        
        # This is a simplified parser - you can enhance it
        return {
            "destination": preferences.destination,
            "duration": f"{preferences.start_date} to {preferences.end_date}",
            "raw_itinerary": raw_text,
            "preferences": preferences.dict()
        }
    
    def export_itinerary(self, itinerary: Dict, format: str = "text") -> str:
        """Export itinerary in various formats"""
        
        if format == "json":
            return json.dumps(itinerary, indent=2)
        elif format == "text":
            return self._format_as_text(itinerary)
        else:
            return str(itinerary)
    
    def _format_as_text(self, itinerary: Dict) -> str:
        """Format itinerary as readable text"""
        
        text = f"Travel Itinerary for {itinerary['destination']}\n"
        text += f"Duration: {itinerary['duration']}\n\n"
        text += itinerary.get('raw_itinerary', '')
        
        return text
