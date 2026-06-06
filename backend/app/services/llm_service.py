import openai
import httpx
from app.config import Config
import requests
import json

class LLMService:
    def __init__(self):
        # Configure OpenAI with GenAI Lab settings
        openai.api_base = Config.GENAI_BASE_URL
        openai.api_key = Config.GENAI_API_KEY
        
        # Disable SSL verification for internal network
        import urllib3
        urllib3.disable_warnings()
        
        self.model = Config.CHAT_MODEL
        self.use_mock = not Config.GENAI_API_KEY or Config.GENAI_API_KEY in ["YOUR_KEY_HERE", "your_api_key_here", ""]
        
        # Hugging Face Inference API setup
        self.use_huggingface = True  # Set to True to use HuggingFace free API

        self.hf_api_token = Config.HF_TOKEN
        self.hf_api_url = Config.HF_API_URL
        self.hf_model = Config.HF_MODEL
        
        print(f"LLM Service initialized - Using HuggingFace: {self.use_huggingface}")
    
    def _generate_with_huggingface(self, prompt: str, max_length: int = 1024) -> str:
        """Generate text using Hugging Face Inference API"""
       
        try:
            headers = {
                "Authorization": f"Bearer {self.hf_api_token}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": self.hf_model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": max_length,
                "temperature": 0.7,
                "top_p": 0.9
            }

            
            response = requests.post(self.hf_api_url, headers=headers, json=payload, timeout=60)
            print("RESPONSE!!!!!!!!!!", response)
            if response.status_code == 200:
                result = response.json()
                print("result", result)
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("generated_text", "")
                return str(result)
            elif response.status_code == 503:
                # Model is loading, use fallback
                print("HuggingFace model loading, using mock data...")
                return None
            else:
                print(f"HuggingFace API error {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            print(f"Error with HuggingFace API: {str(e)}")
            return None
    
    def _get_mock_itinerary(self, preferences: dict) -> str:
        """Return mock itinerary data for testing without API key"""
        destination = preferences.get("destination", "Paris")
        start_date = preferences.get("start_date", "2026-06-01")
        end_date = preferences.get("end_date", "2026-06-05")
        interests = preferences.get("interests", ["Culture", "Food"])
        budget = preferences.get("budget", "moderate")
        
        return f"""# {destination} Travel Itinerary
**{start_date} to {end_date}** | Budget: {budget.title()} | Interests: {", ".join(interests)}

## Day 1: {start_date} - Arrival & City Orientation

**Morning (9:00 AM - 12:00 PM)**
- Arrive at {destination} and check into your hotel
- Take a leisurely walk around your neighborhood to get oriented
- Stop by a local café for breakfast/brunch
- *Estimated cost: $20-30*

**Afternoon (2:00 PM - 6:00 PM)**
- Visit the main city center and iconic landmarks
- Explore local markets and shops
- Join a free walking tour to learn about the city's history
- *Estimated cost: $15-25 (tips and snacks)*

**Evening (7:00 PM - 10:00 PM)**
- Dinner at a recommended local restaurant
- Evening stroll through illuminated streets
- *Estimated cost: $40-60*

**Travel Tips:** 
- Purchase a multi-day transit pass for convenience
- Download offline maps
- Exchange some local currency

---

## Day 2: {start_date} - Cultural Immersion

**Morning (9:00 AM - 12:30 PM)**
- Visit the main museum or art gallery
- Guided tour of historical sites
- Coffee break at a traditional café
- *Estimated cost: $35-50*

**Afternoon (2:00 PM - 6:00 PM)**
- Explore local neighborhoods with authentic character
- Visit artisan workshops or craft markets
- Photography walk through scenic areas
- *Estimated cost: $20-30*

**Evening (7:00 PM - 10:00 PM)**
- Attend a cultural performance or local event
- Dinner featuring regional specialties
- *Estimated cost: $50-75*

**Travel Tips:**
- Book museum tickets online to skip lines
- Best lighting for photos: golden hour (6-8 PM)

---

## Day 3: {start_date} - Hidden Gems & Local Experiences

**Morning (8:00 AM - 12:00 PM)**
- Early visit to local farmers market
- Cooking class or food tour
- Sample regional delicacies
- *Estimated cost: $60-80*

**Afternoon (2:00 PM - 5:00 PM)**
- Visit lesser-known attractions away from tourist crowds
- Relax in a scenic park or garden
- Local café for afternoon tea/coffee
- *Estimated cost: $15-25*

**Evening (6:00 PM - 10:00 PM)**
- Sunset viewing from the best vantage point
- Dinner at a rooftop restaurant
- Evening entertainment or nightlife exploration
- *Estimated cost: $55-80*

**Travel Tips:**
- Ask locals for their favorite spots
- Try street food for authentic flavors

---

## Day 4: {end_date} - Day Trip & Adventure

**Morning (8:00 AM - 12:00 PM)**
- Day trip to nearby town or natural attraction
- Scenic train or bus ride
- Explore charming villages or nature trails
- *Estimated cost: $30-45 (transportation + entry)*

**Afternoon (1:00 PM - 5:00 PM)**
- Continue exploring the surrounding area
- Lunch at a countryside restaurant
- Local wine tasting or specialty experience
- *Estimated cost: $45-65*

**Evening (6:30 PM - 9:00 PM)**
- Return to {destination}
- Casual dinner near your accommodation
- Pack and prepare for departure
- *Estimated cost: $30-45*

**Travel Tips:**
- Start early to maximize day trip time
- Bring layers for changing weather
- Book transportation in advance

---

## Additional Recommendations

**Must-Try Foods:**
- Local specialty dishes
- Regional wines or beverages
- Traditional desserts
- Street food favorites

**Packing Essentials:**
- Comfortable walking shoes
- Weather-appropriate clothing
- Portable charger
- Reusable water bottle
- Travel adapter

**Budget Summary:**
- Daily average: ${70 if budget == "budget" else 100 if budget == "moderate" else 150}-{100 if budget == "budget" else 150 if budget == "moderate" else 250}
- Total estimated: ${350 if budget == "budget" else 500 if budget == "moderate" else 750}-{500 if budget == "budget" else 750 if budget == "moderate" else 1250}
- Excludes: Accommodation, flights, shopping

**Note:** This is a sample itinerary generated in demo mode. Connect your GenAI Lab API key for personalized, AI-powered itineraries!"""
    
    def generate_itinerary(self, preferences: dict) -> str:
        """Generate a complete travel itinerary based on preferences"""
        
        # Try HuggingFace API first if enabled
        if self.use_huggingface:
            print("I'm here!!!!!!!!!!!!!!!!!!!!!!!")
            prompt = f"""Create a detailed travel itinerary for a trip to {preferences.get("destination", "Paris")} from {preferences.get("start_date", "")} to {preferences.get("end_date", "")}.Budget: {preferences.get("budget", "moderate")}Interests: {", ".join(preferences.get("interests", []))}Pace: {preferences.get("pace", "moderate")}Provide a day-by-day itinerary with morning, afternoon, and evening activities. Include specific timings, estimated costs, and travel tips for each day."""
            print("prompt", prompt)
            result = self._generate_with_huggingface(str(prompt), max_length=1500)
            print("Result", result)
            if result:
                # Format the response nicely
                formatted = f"""# {preferences.get("destination", "Travel")} Itinerary**{preferences.get("start_date", "")} to {preferences.get("end_date", "")}**{result}

---
**Generated using Mistral-7B via Hugging Face Inference API**
"""
                return formatted
            else:
                print("HuggingFace unavailable, falling back to mock data...")
        
        # Fallback to mock data
        return self._get_mock_itinerary(preferences)
        
        system_prompt = """You are an expert travel planner with deep knowledge of destinations worldwide. 
        Create detailed, personalized day-by-day itineraries that balance sightseeing, rest, and local experiences.
        
        Consider:
        - Opening hours and typical visit durations
        - Travel time between locations
        - Meal times and local cuisine
        - Budget constraints
        - Personal interests and pace preferences
        
        Format your response as a structured itinerary with:
        - Day number and date
        - Morning, afternoon, and evening activities
        - Specific timings
        - Activity descriptions
        - Estimated costs
        - Travel tips
        """
        
        additional_context = ""
        if preferences.get("accommodation_location"):
            additional_context += f"\nAccommodation Location: {preferences['accommodation_location']}"
        if preferences.get("dietary_restrictions"):
            additional_context += f"\nDietary Restrictions: {', '.join(preferences['dietary_restrictions'])}"
        
        user_prompt = f"""Create a detailed travel itinerary for:
        
        Destination: {preferences["destination"]}
        Duration: {preferences["start_date"]} to {preferences["end_date"]}
        Budget: {preferences.get("budget", "moderate")}
        Interests: {", ".join(preferences.get("interests", []))}
        Pace: {preferences.get("pace", "moderate")}
        {additional_context}
        
        Provide a complete day-by-day itinerary with specific activities, timings, and recommendations."""
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating itinerary: {str(e)}"
    
    def chat_refinement(self, message: str, conversation_history: list, trip_context: dict = None) -> str:
        """Handle conversational refinement of itinerary"""
         
        context = ""
        if trip_context:
            context = f"\nCurrent Trip Context: {trip_context}"
        
        system_prompt = f"""You are a helpful travel assistant helping refine a travel itinerary. 
        You can answer questions, make adjustments, and provide additional recommendations.
        {context}
        
        Be conversational, helpful, and specific in your responses."""
        
        # Build messages array from conversation history
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add last 10 messages for context
        for msg in conversation_history[-10:]:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            messages.append({"role": role, "content": content})
        
        # Add current message
        messages.append({"role": "user", "content": message})
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error in chat: {str(e)}"
        # Use mock responses if no API key configured
        if self.use_mock:
            responses = [
                "That's a great question! Based on your itinerary, I'd recommend adjusting your schedule to allow more time for that activity.",
                "I understand your concern. Let me suggest an alternative that might work better for your preferences.",
                "Absolutely! I can help you modify the itinerary. What specific changes would you like to make?",
                "That's a popular choice! I'd recommend booking tickets in advance to avoid long queues.",
                "Great idea! Let me help you refine that part of your trip to make it even better."
            ]
            import random
            return random.choice(responses) + f" (Demo mode - your message: '{message[:50]}...')"
    
    def extract_preferences_from_chat(self, conversation: str) -> dict:
        """Extract structured trip preferences from natural language conversation"""
        
        # Use mock extraction if no API key configured
        if self.use_mock:
            return """{
            "destination": "Paris",
            "start_date": "2026-06-15",
            "end_date": "2026-06-20",
            "budget": "moderate",
            "interests": ["culture", "food", "history"],
            "pace": "moderate"
        }"""
        
        prompt = f"""Extract travel preferences from this conversation and return them in this exact JSON format:
        {{
            "destination": "city/country name",
            "start_date": "YYYY-MM-DD",
            "end_date": "YYYY-MM-DD",
            "budget": "budget/moderate/luxury",
            "interests": ["interest1", "interest2"],
            "pace": "relaxed/moderate/packed"
        }}
        
        Conversation:
        {conversation}
        
        Return ONLY the JSON, no additional text."""
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that extracts structured data from conversations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error extracting preferences: {str(e)}"
