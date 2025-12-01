"""
DocuMind API Server

FastAPI backend. Run with: python main.py
"""
import os
import asyncio
from pathlib import Path
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from agents import AgentOrchestrator
from core.ernie_client import ernie_client
from core.paddleocr_client import paddleocr_client

orchestrator = AgentOrchestrator()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management."""
    orchestrator.initialize()
    yield


app = FastAPI(
    title="DocuMind API",
    description="Intelligent Document Analysis Multi-Agent System",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


class AnalyzeRequest(BaseModel):
    content: str
    action: str = "analyze"


class QARequest(BaseModel):
    question: str
    document: Optional[str] = None


class GenerateWebRequest(BaseModel):
    markdown: str


@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "name": "DocuMind API",
        "version": "1.0.0",
        "description": "Intelligent Document Analysis Multi-Agent System",
        "endpoints": {
            "upload": "/api/upload",
            "analyze": "/api/analyze",
            "qa": "/api/qa",
            "generate_web": "/api/generate-web"
        }
    }


@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and process a document with OCR.
    
    Supported formats: PDF, PNG, JPG, JPEG
    """
    allowed_types = [".pdf", ".png", ".jpg", ".jpeg"]
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_ext}. Supported: {allowed_types}"
        )
    
    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    try:
        result = await orchestrator.process_document(str(file_path))
        return JSONResponse(content={
            "success": True,
            "filename": file.filename,
            "result": result
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze")
async def analyze_content(request: AnalyzeRequest):
    """Analyze text content using multi-agent system."""
    try:
        result = await orchestrator.analyze(request.content)
        return JSONResponse(content={
            "success": True,
            "result": result
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/qa")
async def question_answer(request: QARequest):
    """Document-based question answering."""
    try:
        answer = await orchestrator.ask(request.question, request.document)
        return JSONResponse(content={
            "success": True,
            "question": request.question,
            "answer": answer
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-web")
async def generate_web_page(request: GenerateWebRequest):
    """
    Convert Markdown to HTML webpage.
    
    Used for Warm-up Task.
    """
    try:
        html = await ernie_client.generate_html(request.markdown)
        return JSONResponse(content={
            "success": True,
            "html": html
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "agents": list(orchestrator.coordinator.agents.keys())}


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug
    )
