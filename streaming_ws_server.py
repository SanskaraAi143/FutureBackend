# streaming_ws_server.py
# FastAPI WebSocket server for ADK-style streaming conversational AI

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
from streaming_agent_wrapper import stream_agent_response
from fastapi import UploadFile
import base64
from google.genai import client as gemini_client
from google.genai import types as gemini_types
from gemini_streaming import adk_streaming_response, gemini_multimodal_streaming

app = FastAPI()

# Allow CORS for local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            if msg.get("type") == "user_utterance":
                user_text = msg.get("text", "")
                user_audio = msg.get("audio", None)
                audio_bytes = base64.b64decode(user_audio) if user_audio else None
                if audio_bytes:
                    # Use Gemini direct multi-modal API for audio
                    for chunk, is_final in gemini_multimodal_streaming(user_text, audio_bytes):
                        await websocket.send_text(json.dumps({
                            "type": "ai_stream_chunk",
                            "chunk": chunk,
                            "is_final": is_final
                        }))
                        if is_final:
                            break
                else:
                    # Use ADK agent for text-only
                    async for chunk, is_final in adk_streaming_response(user_text, None):
                        await websocket.send_text(json.dumps({
                            "type": "ai_stream_chunk",
                            "chunk": chunk,
                            "is_final": is_final
                        }))
                        if is_final:
                            break
            else:
                await websocket.send_text(json.dumps({"type": "error", "message": "Unknown message type"}))
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_text(json.dumps({"type": "error", "message": str(e)}))
