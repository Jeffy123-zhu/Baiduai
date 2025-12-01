# DocuMind

Intelligent document analysis system powered by Baidu's ERNIE and PaddlePaddle.

Built for ERNIE & PaddlePaddle Hackathon 2025.

## What it does

- Extracts text from PDFs using PaddleOCR-VL
- Analyzes documents with Baidu ERNIE LLM
- Generates summaries
- Answers questions about your documents
- Converts PDFs to web pages (warm-up task)

## Tech Stack

- Baidu ERNIE 4.0 - large language model for understanding and generation
- PaddleOCR-VL - PaddlePaddle's vision-language OCR model
- CAMEL-AI - multi-agent coordination framework
- FastAPI backend
- Simple HTML/CSS/JS frontend

## Setup

```bash
pip install -r requirements.txt
```

Create a `.env` file:
```
ERNIE_API_KEY=your_key_here
```

Get your API key from: https://console.bce.baidu.com/qianfan/ais/console/applicationConsole/application

## Usage

### Warm-up Task (PDF to Web)

```bash
cd DocuMind
python warmup_task/pdf_to_web.py your_document.pdf output.html
```

### Run the API server

```bash
cd src
python main.py
```

Then go to http://localhost:8000/docs for the API.

### Quick test

```bash
python test_quick.py
```

## How it works

There are 4 agents that work together:

1. **OCR Agent** - extracts text from documents
2. **Analysis Agent** - figures out what the document is about
3. **Summary Agent** - creates summaries
4. **QA Agent** - answers questions

The Coordinator manages them all and decides which agent to use.

## Project Structure

```
DocuMind/
├── src/
│   ├── agents/          # the multi-agent stuff
│   ├── core/            # ERNIE and PaddleOCR clients
│   └── main.py          # FastAPI server
├── warmup_task/         # PDF to web converter
├── web/                 # frontend
└── examples/            # demo code
```

## Notes

- The VL model support is experimental
- Sometimes the API times out, just retry
- GPU not required but makes OCR faster

## License

Apache 2.0
