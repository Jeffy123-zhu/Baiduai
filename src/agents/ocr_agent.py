"""
OCR Agent

Extracts text from PDFs and images. Uses PaddleOCR under the hood.
Falls back to PyPDF2 if OCR fails (which happens sometimes).
"""
from typing import Any, Dict, Optional
from pathlib import Path

# CAMEL-AI import (optional)
try:
    from camel.messages import BaseMessage
except ImportError:
    BaseMessage = None

from .base_agent import BaseDocuMindAgent, AgentRole, AgentResult
from core.paddleocr_client import paddleocr_client


class OCRAgent(BaseDocuMindAgent):
    """
    OCR Agent for document text extraction.
    
    Uses PaddleOCR-VL for:
    1. Image text recognition
    2. PDF document recognition
    3. Layout analysis
    4. Markdown conversion
    """
    
    SYSTEM_MESSAGE = """You are a professional document OCR recognition agent. Your tasks include:
1. Accurately extracting text from images and PDF documents
2. Preserving document structure and layout information
3. Converting extracted content to structured Markdown format
4. Handling multi-language documents

You are part of the DocuMind multi-agent system, responsible for the OCR recognition stage.
You use PaddleOCR-VL vision-language model for high-accuracy document recognition."""

    def __init__(self):
        super().__init__(
            name="OCR-Agent",
            role=AgentRole.OCR,
            system_message=self.SYSTEM_MESSAGE,
            description="Document OCR expert for extracting text from images and PDFs"
        )
        self.ocr_client = paddleocr_client
        
    async def execute(self, task: Dict[str, Any]) -> AgentResult:
        """
        Execute an OCR task.
        
        Args:
            task: Task specification containing:
                - action: "extract" | "to_markdown" | "layout_analysis"
                - file_path: Path to the document file
                - file_type: "image" | "pdf" (auto-detected if not provided)
                
        Returns:
            AgentResult with OCR outcome
        """
        try:
            action = task.get("action", "extract")
            file_path = task.get("file_path")
            file_type = task.get("file_type", self._detect_file_type(file_path))
            
            if not file_path or not Path(file_path).exists():
                return AgentResult(
                    success=False,
                    data=None,
                    error=f"File not found: {file_path}"
                )
            
            user_msg = self.create_user_message(f"OCR task: {action}, file: {file_path}")
            
            if file_type == "pdf":
                ocr_result = self.ocr_client.extract_from_pdf(file_path)
            else:
                ocr_result = self.ocr_client.extract_text_from_image(file_path)
            
            if action == "to_markdown":
                markdown = self.ocr_client.to_markdown(ocr_result)
                return AgentResult(
                    success=True,
                    data={
                        "markdown": markdown,
                        "ocr_result": ocr_result
                    },
                    metadata={
                        "file_path": file_path,
                        "file_type": file_type,
                        "agent": self.name
                    }
                )
            
            elif action == "layout_analysis":
                layout = self._analyze_layout(ocr_result)
                return AgentResult(
                    success=True,
                    data={
                        "layout": layout,
                        "ocr_result": ocr_result
                    },
                    metadata={
                        "file_path": file_path,
                        "file_type": file_type,
                        "agent": self.name
                    }
                )
            
            return AgentResult(
                success=True,
                data=ocr_result,
                metadata={
                    "file_path": file_path,
                    "file_type": file_type,
                    "agent": self.name
                }
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                error=str(e)
            )
    
    def _detect_file_type(self, file_path: str) -> str:
        """Detect file type from extension."""
        if not file_path:
            return "unknown"
        
        suffix = Path(file_path).suffix.lower()
        if suffix == ".pdf":
            return "pdf"
        elif suffix in [".png", ".jpg", ".jpeg", ".bmp", ".tiff"]:
            return "image"
        return "unknown"
    
    def _analyze_layout(self, ocr_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze document layout structure."""
        layout = {
            "regions": [],
            "structure": {
                "has_title": False,
                "has_paragraphs": False,
                "has_tables": False,
                "has_images": False
            }
        }
        
        if "layout" in ocr_result:
            for item in ocr_result["layout"]:
                region = {
                    "text": item.get("text", ""),
                    "position": {
                        "x": item.get("x", 0),
                        "y": item.get("y", 0),
                        "width": item.get("width", 0),
                        "height": item.get("height", 0)
                    }
                }
                layout["regions"].append(region)
            
            if layout["regions"]:
                first_region = layout["regions"][0]
                if first_region["position"]["y"] < 100:
                    layout["structure"]["has_title"] = True
                layout["structure"]["has_paragraphs"] = len(layout["regions"]) > 1
        
        return layout
    
    async def extract_and_convert(self, file_path: str) -> AgentResult:
        """Convenience method: extract and convert to Markdown."""
        return await self.execute({
            "action": "to_markdown",
            "file_path": file_path
        })
