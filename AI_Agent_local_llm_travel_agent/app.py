from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import HTMLResponse, StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import json
import uvicorn
import os
from planner import generate_itinerary_stream, parse_itinerary
from agent import agent_reply
from pdf_export import export_pdf
from state import init_state

app = FastAPI()

# Global State (Single User Mode for Local App)
class Session:
    state = init_state()

session = Session()

# Load Data
with open("data/states_cities.json") as f:
    STATES_CITIES = json.load(f)

with open("data/city_places.json") as f:
    CITY_PLACES = json.load(f)

# Models
class GenerateRequest(BaseModel):
    dst_city: str
    days: int

class ChatRequest(BaseModel):
    message: str

@app.get("/")
async def get_index():
    with open("index.html", encoding="utf-8") as f:
        return HTMLResponse(f.read())

@app.get("/api/data")
async def get_data():
    return STATES_CITIES

import asyncio

@app.post("/api/generate")
async def generate_plan(req: GenerateRequest):
    places = CITY_PLACES.get(req.dst_city, [])
    
    async def stream_generator():
        # 1. Yield Initial Status (simulated 'thinking')
        initial_msg = f"🔄 **Generating itinerary for {req.dst_city}...**\n\n"
        yield initial_msg
        
        # Add to history (metadata only, content will be filled later)
        session.state["chat_history"].append({
            "role": "assistant", 
            "content": initial_msg
        })
        
        full_text = ""
        # 2. Stream Real Content
        for chunk in generate_itinerary_stream(req.dst_city, places, req.days):
            full_text += chunk
            yield chunk
            # Artificial delay to ensure UI updates progressively
            await asyncio.sleep(0.05)
        
        # 3. Save Final State
        session.state["itinerary"] = full_text
        session.state["chat_history"][-1]["content"] = initial_msg + full_text

    return StreamingResponse(stream_generator(), media_type="text/plain")


@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    async def stream_chat():
        # Agent reply handles appending to history inside it?
        # Let's check agent.py... 
        # agent_reply(state, input) appends user input, calls llm, then appends assistant.
        # But agent_reply is a generator now.
        
        # We need to act as the consumer of the generator
        gen = agent_reply(session.state, req.message)
        for chunk in gen:
            yield chunk
            await asyncio.sleep(0.05)
            
    return StreamingResponse(stream_chat(), media_type="text/plain")

@app.get("/api/export")
async def export_endpoint():
    if session.state.get("itinerary"):
        export_pdf(session.state["itinerary"])
        return FileResponse("travel_plan.pdf", filename="travel_plan.pdf")
    return {"error": "No plan to export"}

@app.post("/api/reset")
async def reset_endpoint():
    session.state = init_state()
    return {"status": "reset"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8501)
