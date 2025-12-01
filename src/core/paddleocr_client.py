"""
PaddleOCR Client

Handles OCR stuff. VL model support is experimental, might break.
"""
import os
from typing import List, Dict, Any, Optional
from pathlib import Path

paddleocr = None
Image = None


def ensure_imports():
    """Ensure required dependencies are imported."""
    global paddleocr, Image
    if paddleocr is None:
        try:
            from paddleocr import PaddleOCR
            paddleocr = PaddleOCR
        except ImportError:
            raise ImportError("Please install paddleocr: pip install paddleocr")
    if Image is None:
        from PIL import Image as PILImage
        Image = PILImage


class PaddleOCRClient:
    """
    PaddleOCR-VL Client for document recognition.
    
    Supports:
    1. Basic OCR text recognition
    2. PaddleOCR-VL vision-language model for document understanding
    3. Layout analysis
    4. Table recognition
    """
    
    def __init__(self, use_gpu: bool = False, lang: str = "ch", use_vl: bool = True):
        """
        Initialize the OCR client.
        
        Args:
            use_gpu: Whether to use GPU acceleration
            lang: Language setting (ch/en/multilingual)
            use_vl: Whether to use VL model for enhanced understanding
        """
        self.use_gpu = use_gpu
        self.lang = lang
        self.use_vl = use_vl
        self._ocr = None
        self._vl_model = None
        
    @property
    def ocr(self):
        """Lazy init - only loads when first used."""
        if self._ocr is None:
            ensure_imports()
            # show_log=False or it prints a ton of stuff
            self._ocr = paddleocr(
                use_angle_cls=True,
                lang=self.lang,
                use_gpu=self.use_gpu,
                show_log=False,
                layout=True,
                table=True
            )
        return self._ocr
    
    def _init_vl_model(self):
        """Initialize PaddleOCR-VL model."""
        if self._vl_model is None and self.use_vl:
            try:
                from transformers import AutoModel, AutoTokenizer
                
                model_name = "PaddlePaddle/PaddleOCR-VL"
                self._vl_model = {
                    "model": AutoModel.from_pretrained(model_name, trust_remote_code=True),
                    "tokenizer": AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
                }
            except Exception as e:
                self.use_vl = False
    
    def extract_text_from_image(self, image_path: str) -> Dict[str, Any]:
        """
        Extract text from an image file.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary containing extracted text and position information
        """
        result = self.ocr.ocr(image_path, cls=True)
        
        extracted = {
            "text_blocks": [],
            "full_text": "",
            "layout": [],
            "confidence_avg": 0.0
        }
        
        if result and result[0]:
            texts = []
            total_confidence = 0
            
            for line in result[0]:
                box = line[0]
                text_info = line[1]
                
                text_block = {
                    "text": text_info[0],
                    "confidence": text_info[1],
                    "bbox": {
                        "top_left": box[0],
                        "top_right": box[1],
                        "bottom_right": box[2],
                        "bottom_left": box[3]
                    }
                }
                extracted["text_blocks"].append(text_block)
                texts.append(text_info[0])
                total_confidence += text_info[1]
                
                extracted["layout"].append({
                    "text": text_info[0],
                    "x": box[0][0],
                    "y": box[0][1],
                    "width": box[1][0] - box[0][0],
                    "height": box[2][1] - box[0][1]
                })
            
            extracted["full_text"] = "\n".join(texts)
            extracted["confidence_avg"] = total_confidence / len(result[0]) if result[0] else 0
        
        return extracted
    
    def extract_from_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract text and layout from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary containing all pages' text content
        """
        result = {
            "pages": [],
            "full_text": "",
            "page_count": 0,
            "extraction_method": "pypdf2"
        }
        
        # Use PyPDF2 for text extraction (works without Poppler)
        from PyPDF2 import PdfReader
        reader = PdfReader(pdf_path)
        all_texts = []
        
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            page_result = {
                "page_number": i + 1,
                "full_text": text,
                "text_blocks": [{"text": text, "confidence": 1.0}],
                "layout": []
            }
            result["pages"].append(page_result)
            all_texts.append(text)
        
        result["full_text"] = "\n\n--- Page Break ---\n\n".join(all_texts)
        result["page_count"] = len(reader.pages)
        
        return result
    
    def extract_with_vl(self, image_path: str, prompt: str = "Describe the document content in this image") -> Dict[str, Any]:
        """
        Use PaddleOCR-VL for document understanding.
        
        Args:
            image_path: Path to the image file
            prompt: Prompt for the VL model
            
        Returns:
            VL model understanding result
        """
        self._init_vl_model()
        
        if not self._vl_model:
            return self.extract_text_from_image(image_path)
        
        try:
            ensure_imports()
            image = Image.open(image_path)
            
            model = self._vl_model["model"]
            tokenizer = self._vl_model["tokenizer"]
            
            inputs = tokenizer(prompt, return_tensors="pt")
            outputs = model.generate(**inputs, images=image)
            response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            return {
                "vl_response": response,
                "prompt": prompt,
                "method": "paddleocr_vl"
            }
            
        except Exception as e:
            result = self.extract_text_from_image(image_path)
            result["vl_error"] = str(e)
            return result
    
    def to_markdown(self, ocr_result: Dict[str, Any]) -> str:
        """
        Convert OCR result to Markdown format.
        
        Args:
            ocr_result: OCR extraction result
            
        Returns:
            Markdown formatted text
        """
        markdown_lines = []
        
        if "pages" in ocr_result:
            for page in ocr_result["pages"]:
                page_num = page.get("page_number", "?")
                markdown_lines.append(f"## Page {page_num}\n")
                
                text = page.get("full_text", "")
                formatted_text = self._format_text_structure(text)
                markdown_lines.append(formatted_text)
                markdown_lines.append("\n---\n")
        else:
            text = ocr_result.get("full_text", "")
            formatted_text = self._format_text_structure(text)
            markdown_lines.append(formatted_text)
        
        return "\n".join(markdown_lines)
    
    def _format_text_structure(self, text: str) -> str:
        """Format text with basic structure detection."""
        lines = text.split("\n")
        formatted = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                formatted.append("")
                continue
            
            if i < 3 and len(line) < 50 and not line.endswith(('.', ',', ';')):
                formatted.append(f"### {line}")
            else:
                formatted.append(line)
        
        return "\n".join(formatted)


paddleocr_client = PaddleOCRClient()
