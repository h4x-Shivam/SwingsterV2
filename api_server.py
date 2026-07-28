import json
import os
import asyncio
from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse

app = FastAPI(title="SwingsterV2 Scan API")

async def run_scan_generator(mode: str):
    """
    Spawns main.py as a subprocess and yields its stdout line-by-line
    formatted as Server-Sent Events (SSE).
    """
    # Create the subprocess
    process = await asyncio.create_subprocess_exec(
        "python", "main.py", "--mode", mode,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        env={"PYTHONUNBUFFERED": "1", **os.environ}
    )
    
    # Read output line by line and stream it to the client
    while True:
        line = await process.stdout.readline()
        if not line:
            break
        
        # Decode and format as JSON string to match frontend expectations
        decoded_line = line.decode('utf-8').strip()
        if decoded_line:
            yield f"data: {json.dumps(decoded_line)}\n\n"
    
    # Wait for the process to finish
    await process.wait()
    yield f"data: {json.dumps(f'[SYSTEM] Process exited with code {process.returncode}')}\n\n"

@app.get("/scan")
async def scan_endpoint(mode: str = Query("VCP", description="Pattern mode to scan for")):
    """
    Streaming endpoint that triggers a scan and sends logs back as SSE.
    """
    return StreamingResponse(run_scan_generator(mode), media_type="text/event-stream")

@app.get("/health")
def health_check():
    return {"status": "ok"}
