"""
ERNIE API Client

Wrapper for Baidu ERNIE LLM. Took me a while to figure out the new auth format...
"""
import os
import httpx
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

load_dotenv()


class ERNIEClient:
    """
    ERNIE Large Language Model Client.
    
    Supports the new BCE API Key authentication.
    """
    
    def __init__(self):
        self.api_key = os.getenv("ERNIE_API_KEY")
        self.base_url = "https://qianfan.baidubce.com/v2"
        
    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: str = "ernie-4.0-8k",
        temperature: float = 0.7,
        top_p: float = 0.9,
        system: Optional[str] = None
    ) -> str:
        """
        Call ERNIE chat completion API.
        
        Args:
            messages: List of message dicts [{"role": "user", "content": "..."}]
            model: Model name
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            system: System prompt
            
        Returns:
            Model response content
        """
        url = f"{self.base_url}/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # Build messages with system prompt
        final_messages = []
        if system:
            final_messages.append({"role": "system", "content": system})
        final_messages.extend(messages)
        
        payload = {
            "model": model,
            "messages": final_messages,
            "temperature": temperature,
            "top_p": top_p
        }
        
        # 60s timeout should be enough, increase if you get timeouts
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            result = response.json()
            
            if "error" in result:
                raise Exception(f"ERNIE API Error: {result.get('error', {}).get('message', 'Unknown error')}")
            
            # Extract response content
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0].get("message", {}).get("content", "")
            
            return result.get("result", "")
    
    async def analyze_document(self, content: str, task: str = "summary") -> str:
        """
        Perform document analysis task.
        
        Args:
            content: Document content
            task: Task type (summary/extract/analyze)
            
        Returns:
            Analysis result
        """
        task_prompts = {
            "summary": "Please summarize the following document content and extract key points:",
            "extract": "Please extract key information from the following document, including: dates, amounts, names, organizations:",
            "analyze": "Please analyze the structure and content of the following document and provide a detailed analysis report:"
        }
        
        prompt = task_prompts.get(task, task_prompts["summary"])
        messages = [{"role": "user", "content": f"{prompt}\n\n{content}"}]
        
        return await self.chat(messages)
    
    async def generate_html(self, markdown_content: str) -> str:
        """
        Convert Markdown content to HTML webpage.
        
        Args:
            markdown_content: Markdown formatted content
            
        Returns:
            Complete HTML page code
        """
        system_prompt = """You are a professional web developer. Please convert the user-provided Markdown content into a beautiful HTML webpage.
Requirements:
1. Use modern CSS styling
2. Responsive design for mobile devices
3. Use an elegant color scheme
4. Include complete HTML structure (DOCTYPE, head, body)
5. Return ONLY the raw HTML code, no markdown code blocks, no explanations"""

        messages = [{"role": "user", "content": f"Please convert the following Markdown to an HTML webpage:\n\n{markdown_content}"}]
        
        html = await self.chat(messages, system=system_prompt, temperature=0.3)
        
        # Clean up markdown code block markers if present
        html = html.strip()
        if html.startswith("```html"):
            html = html[7:]
        elif html.startswith("```"):
            html = html[3:]
        if html.endswith("```"):
            html = html[:-3]
        
        return html.strip()


ernie_client = ERNIEClient()
