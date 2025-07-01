# Sanskara AI Deployment

This directory contains the deployment configuration for the Sanskara AI multi-agent orchestrator with ADK streaming support.

## Features

- **Text Mode**: Real-time text chat with the Sanskara AI orchestrator
- **Audio Mode**: Voice conversation with streaming audio input/output
- **WebSocket Support**: Bidirectional streaming communication
- **ADK Integration**: Uses Google's Agent Development Kit for robust agent orchestration

## Quick Start

1. **Set up environment**:
   ```bash
   cp .env.template .env
   # Edit .env and add your Google API key
   ```

2. **Install dependencies**:
   ```bash
   pip install -r ../../requirements.txt
   ```

3. **Run the server**:
   ```bash
   python deploy.py
   ```

4. **Access the interface**:
   - Open http://localhost:8000 in your browser
   - Click "Connect (Text Mode)" for text chat
   - Click "Start Audio Mode" for voice interaction

## Configuration

### Environment Variables

- `GOOGLE_API_KEY`: Your Google AI Studio API key
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `DEBUG`: Enable debug mode (default: True)

### WebSocket Endpoints

- `/ws/{user_id}?is_audio=false`: Text mode WebSocket
- `/ws/{user_id}?is_audio=true`: Audio mode WebSocket

### HTTP Endpoints

- `/`: Web interface
- `/health`: Health check endpoint

## Architecture

The deployment follows Google ADK streaming patterns:

1. **InMemoryRunner**: Manages agent sessions and live streaming
2. **LiveRequestQueue**: Handles client-to-agent communication
3. **live_events**: Streams agent responses back to clients
4. **RunConfig**: Configures response modalities (TEXT/AUDIO)

## Audio Support

Audio mode uses:
- PCM audio format (24kHz sample rate)
- Base64 encoding for WebSocket transmission
- Gemini Live API for speech-to-text and text-to-speech
- AudioWorklets for client-side audio processing

## Development

### File Structure

```
deployment/
├── deploy.py              # Main FastAPI application
├── static/               # Web interface files
│   ├── index.html       # Main HTML interface
│   └── js/
│       └── app.js       # WebSocket client
├── .env.template        # Environment template
└── README.md           # This file
```

### Adding Custom Routes

To add custom FastAPI routes, modify the `app` instance in `deploy.py`:

```python
@app.get("/custom-endpoint")
async def custom_handler():
    return {"message": "Custom response"}
```

### Session Management

The current implementation uses `InMemorySessionService`. For production:

1. Replace with persistent session storage
2. Configure session service URI in environment
3. Update Runner initialization accordingly

## Troubleshooting

### Common Issues

1. **WebSocket connection fails**:
   - Check if port 8000 is available
   - Verify firewall settings
   - Try using `wss://` instead of `ws://` for HTTPS

2. **Audio mode not working**:
   - Check browser microphone permissions
   - Ensure HTTPS for audio access (required by browsers)
   - Verify Google API key has Live API access

3. **Agent import errors**:
   - Ensure the multi_agent_orchestrator package is properly installed
   - Check that root_agent is defined in the agent.py file
   - Verify all sub-agents are properly imported

### Logs

The application logs to console with INFO level. Key log messages:

- Agent directory detection
- Static file serving status
- WebSocket connections/disconnections
- Agent session creation
- Audio/text message processing

## Production Deployment

For production use:

1. **Use HTTPS**: Required for audio features
2. **External Session Store**: Replace InMemorySessionService
3. **Load Balancing**: Configure sticky sessions for WebSocket connections
4. **Health Monitoring**: Use `/health` endpoint
5. **Environment Security**: Secure API keys and environment variables

## License

This deployment configuration is part of the Sanskara AI project.
