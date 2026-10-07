# installer/server.py | Vitalia SDD v0.6.0 | 06-10-2026 16:05(GMT-04:00)
import os
import json
from fastapi import FastAPI, Depends, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from sse_starlette.sse import EventSourceResponse
from typing import Dict
from . import config_manager
from . import orchestrator

app = FastAPI(title="AI Control Installer")

def verify_token(token: str = Query(...)):
    expected_token = os.environ.get("AI_CONTROL_OTP")
    if not expected_token or token != expected_token:
        raise HTTPException(status_code=403, detail="Acesso negado. Token inválido ou não fornecido.")
    return token

@app.get("/", response_class=HTMLResponse)
async def index(request: Request, token: str = Depends(verify_token)):
    config_data = config_manager.load_config()
    html_path = "ai_control_transition/installer/templates/index.html"
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    content = content.replace("{{token}}", token)
    content = content.replace("{{env_json|safe}}", json.dumps(config_data))
    return content

@app.post("/save")
async def save_config(data: Dict[str, str], token: str = Depends(verify_token)):
    config_manager.save_config(data)
    return JSONResponse(content={"status": "ok"})

@app.post("/install")
async def start_install(token: str = Depends(verify_token)):
    orchestrator.start_installation()
    return JSONResponse(content={"status": "started"})

@app.get("/stream")
async def stream(token: str = Depends(verify_token)):
    return EventSourceResponse(orchestrator.stream_logs())
