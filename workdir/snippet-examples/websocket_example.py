import asyncio
import json

from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

app = FastAPI()

# HTML template for the WebSocket client
html = """
<!DOCTYPE html>
<html>
    <head>
        <title>WebSocket Test</title>
    </head>
    <body>
        <h1>WebSocket Test</h1>
        <div id="status"></div>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws");

            ws.onmessage = function(event) {
                var status = document.getElementById('status');
                var message = JSON.parse(event.data);
                status.innerHTML = message.text;
            };
        </script>
    </body>
</html>
"""


# Serve the WebSocket client HTML
@app.get("/")
async def get():
    return HTMLResponse(html)


# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    for i in range(1, 6):  # Simulate 5 steps
        await asyncio.sleep(1)  # Simulate work being done
        message = {"text": f"Step {i} completed"}
        await websocket.send_text(json.dumps(message))
