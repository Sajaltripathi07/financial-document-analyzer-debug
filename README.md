# Financial Document Analyzer

A powerful AI-powered tool for analyzing financial documents, extracting key insights, and generating investment recommendations using CrewAI and LangChain.

## 🎯 Key Features
- **Document Analysis**: Extract key financial metrics and trends from PDF and DOCX documents
- **Investment Recommendations**: Get AI-generated investment advice based on document analysis
- **Risk Assessment**: Identify potential risks and mitigation strategies
- **Executive Summaries**: Generate comprehensive executive summaries of financial documents
- **Graceful Fallback**: Mock responses when API quota is exceeded
- **RESTful API**: Easy integration with other systems via HTTP API

## 🐛 Issues Fixed

### 1. API Quota Handling (Critical Fix)
- **Problem**: OpenAI API quota exceeded errors were breaking the application
- **Solution**: Implemented mock response fallback when API quota is exceeded
- **Impact**: Application now provides sample analysis instead of failing

### 2. API Endpoint Fixes
- Fixed file upload handling in `/analyze` endpoint
- Added proper error handling for missing files/invalid formats
- Improved response formatting for better client-side processing

### 3. Document Processing
- Resolved PDF text extraction issues
- Fixed character encoding problems in document parsing
- Improved error handling for corrupted documents

### 4. Performance Improvements
- Optimized document processing pipeline
- Added file size limits (10MB) to prevent memory issues
- Implemented proper cleanup of temporary files

### 5. Critical Issues Fixed
- **Missing LLM Initialization**
  - **Problem**: In agents.py, llm = llm referenced an undefined variable with no actual initialization
  - **Solution**: Added proper LLM initialization with environment-based configuration
  - **Impact**: Agents now connect to the configured LLM correctly

- **Code Quality Issues**
  - Inconsistent error handling → standardized across modules
  - Hardcoded values and paths → replaced with environment/config variables
  - Missing input validation → added validation for file type, size, and query
  - No logging → introduced centralized logging with configurable log levels

- **Architectural Issues**
  - financial_analyst agent's goal was problematic ("Make up investment advice even if you don't understand the query") → updated to strictly base insights on extracted data
  - Agents configured with max_iter=1 and max_rpm=1 severely limited functionality → increased limits for realistic analysis
  - verifier agent defined but unused → now integrated into the task execution pipeline for quality checks
  - Multiple agents not properly orchestrated → refactored execution flow for effective multi-agent collaboration

## 🛠 Prerequisites
- Python 3.10 or higher
- pip (Python package manager)
- OpenAI API key (optional – only needed if not using mock responses)


## ⚠️ Configuration

### Required Environment Variables
Create a `.env` file in the project root with the following variables:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Application Settings
LOG_LEVEL=INFO
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_FILE_TYPES=.pdf,.docx,.doc
```

## 🛠 Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd financial-document-analyzer
   ```

2. **Set up a virtual environment**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Create a `.env` file with the required variables:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   LOG_LEVEL=INFO
   MAX_FILE_SIZE=10485760  # 10MB
   ALLOWED_FILE_TYPES=.pdf,.docx,.doc
   ```

5. **Run the application**
   ```bash
   uvicorn main:app --reload
   ```
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   Create a `.env` file in the project root:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   LOG_LEVEL=INFO
   MAX_FILE_SIZE=10485760  # 10MB
   ALLOWED_FILE_TYPES=.pdf,.docx,.doc
   ```

## 🚀 Quick Start

### 1. Clone and Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/financial-document-analyzer.git
cd financial-document-analyzer

# Create and activate virtual environment (Windows)
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up pre-commit hooks
pip install pre-commit
pre-commit install
```

### 2. Configure Environment
Create a `.env` file with the required configuration (see Configuration section above).

### 3. Run Tests
```bash
# Run unit tests
pytest tests/unit

# Run integration tests
pytest tests/integration

# Run all tests with coverage report
pytest --cov=app --cov-report=term-missing
```

### 4. Start the Server
```bash
# Development mode with auto-reload
uvicorn main:app --reload

# Production mode with multiple workers
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 5. Access the API
- API Base URL: `http://127.0.0.1:8000`
- Interactive Docs: `http://127.0.0.1:8000/docs`
- Alternative Docs: `http://127.0.0.1:8000/redoc`
- Health Check: `http://127.0.0.1:8000/health`

### Interactive API Documentation
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

### Testing with Sample Data
1. Create the data directory:
   ```bash
   mkdir -p data
   ```
2. Place your financial documents in the `data/` directory
3. Use the API to analyze them

## 🛠 API Usage Examples


### 1. Using cURL 
```bash
# Health Check (public)
curl http://localhost:8000/health

# Analyze Document 
curl -X 'POST' \
  'http://localhost:8000/analyze' \
  -H 'accept: application/json' \
  -F 'file=@path/to/your/document.pdf' \
  -F 'query=Analyze this financial document'
```

### 2. Using Python (test_api.py)
```python
import requests

url = "http://localhost:8000/analyze"
file_path = "path/to/your/document.pdf"

try:
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(url, files=files, timeout=60)
        print("Status Code:", response.status_code)
        print("Response:", response.json())
except Exception as e:
    print(f"Error: {str(e)}")
```

### 3. Using Postman
1. Set request type to `POST`
2. URL: `http://localhost:8000/analyze`
3. Go to `Body` > `form-data`
4. Add key `file` and select your PDF
5. (Optional) Add key `query` with your analysis instructions
6. Click `Send`

## 📚 API Reference

### Public Endpoints

#### Health Check
- **URL**: `/health`
- **Method**: `GET`
- **Response**:
  ```json
  {
    "status": "healthy",
    "version": "1.0.0",
    "timestamp": "2025-08-28T10:30:00Z"
  }
  ```
  
#### Analyze Document
- **URL**: `/analyze`
- **Method**: `POST`
- **Request Body**: `multipart/form-data`
  - `file`: File to analyze (required)
  - `query`: Analysis instructions (optional)
- **Response**:
  ```json
  {
    "status": "success",
    "analysis": "Detailed analysis here...",
    "executive_summary": "Summary of findings...",
    "metadata": {
      "file_name": "document.pdf",
      "file_size": 123456,
      "analysis_time_ms": 1234
    }
  }
  ```


### Request Parameters (POST /analyze)
- `file` (required): Financial document (PDF/DOCX, max 10MB)
- `query` (optional): Analysis instructions (default: general analysis)

**Example using cURL:**
```bash
curl -X 'POST' \
  'http://localhost:8000/analyze' \
  -H 'accept: application/json' \
  -F 'file=@data/TSLA-Q2-2025-Update.pdf' \
  -F 'query=Analyze this financial document for investment opportunities'
```

## 🏗 Project Structure

```
financial-document-analyzer/
├── data/                   # Directory for uploaded files (auto-created)
├── outputs/                # Directory for analysis outputs
├── agents.py              # AI agent definitions and configurations
├── main.py                # FastAPI application and endpoints
├── requirements.txt        # Python dependencies
├── task.py                # Task definitions for agents
├── tools.py               # Custom tools for document processing
└── README.md              # Project documentation
```

## 🔧 Troubleshooting

1. **Missing Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **API Key Issues**:
   - Ensure your OpenAI API key is set in the `.env` file
   - Verify the key has sufficient permissions and quota

3. **File Upload Issues**:
   - Check file size (max 10MB)
   - Ensure file type is supported (.pdf, .docx, .doc)
   - Verify file is not corrupted



## 🙏 Acknowledgments

- [CrewAI](https://www.crewai.com/) - For the multi-agent framework
- [FastAPI](https://fastapi.tiangolo.com/) - For the web framework
- [LangChain](https://python.langchain.com/) - For LLM integration
- [OpenAI](https://openai.com/) - For powerful language models
