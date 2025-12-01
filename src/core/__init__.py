"""
DocuMind Core Module
"""
from .ernie_client import ERNIEClient, ernie_client
from .paddleocr_client import PaddleOCRClient, paddleocr_client

__all__ = [
    "ERNIEClient",
    "ernie_client", 
    "PaddleOCRClient",
    "paddleocr_client"
]
