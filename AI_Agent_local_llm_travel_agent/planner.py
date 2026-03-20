import re
from llm import chat_llm

def generate_itinerary_stream(city, places, days):
    place_list = ", ".join(places)
    
    prompt = f"""
    Act as an expert travel planner. Create a {days}-day trip itinerary for {city}.
    
    Constraints:
    - Use the following available places: {place_list}
    - Format properly with Markdown (Bold, Bullet points).
    - Use Emojis 🌟 for activities.
    - Write in a friendly, engaging ChatGPT style.
    - Do NOT output JSON. Just normal text.
    
    Structure:
    - **Trip Title** (e.g., "✨ Amazing Trip to {city}")
    - **Daily Plan** (Day 1, Day 2...) with timing and details.
    - **Tips** (Where to stay, best time to visit).
    """
    
    # Yield chunks from LLM
    for chunk in chat_llm([{"role": "user", "content": prompt}]):
        yield chunk

def parse_itinerary(full_text):
    # Since we moved to text-based plans, we just return the full text
    # This maintains compatibility with the app.py structure
    return full_text