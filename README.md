# Financial Document Analyzer

A powerful AI-powered tool for analyzing financial documents, extracting key insights, and generating investment recommendations using CrewAI and LangChain.

## 🎯 Key Features

- **Document Analysis**: Extract key financial metrics and trends from PDF and DOCX documents
- **Investment Recommendations**: Get AI-generated investment advice based on document analysis
- **Risk Assessment**: Identify potential risks and mitigation strategies
- **Graceful Fallback**: Mock responses when API quota is exceeded
- **RESTful API**: Easy integration with other systems via HTTP API

## 🚀 Features

- **Document Analysis**: Extract key financial metrics and trends from PDF and DOCX documents
- **Investment Recommendations**: Get AI-generated investment advice based on document analysis
- **Risk Assessment**: Identify potential risks and mitigation strategies
- **Executive Summaries**: Generate comprehensive executive summaries of financial documents
- **RESTful API**: Easy integration with other systems via a simple HTTP API

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

## 🛠 Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- OpenAI API key (get one from [OpenAI Platform](https://platform.openai.com/))

## ⚠️ OpenAI API Configuration

This application uses OpenAI's API through CrewAI. You have two options:

### Option 1: Use Mock Responses (Default)
- No API key needed
- Returns sample analysis data
- Perfect for testing and demonstration

### Option 2: Use Real OpenAI API
1. Get an API key from [OpenAI](https://platform.openai.com/)
2. Update `.env` file:
   ```env
   OPENAI_API_KEY=your_actual_key_here
   ```
3. Restart the application

## 🚀 Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/financial-document-analyzer.git
   cd financial-document-analyzer
   ```

2. **Set up a virtual environment**:
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

### 1. Install Dependencies
```bash
# Create and activate virtual environment (Windows)
python -m venv venv
.\venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 2. Configure Environment
Create `.env` file:
```env
OPENAI_API_KEY=your_key_here  # Optional for mock responses
LOG_LEVEL=INFO
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_FILE_TYPES=.pdf,.docx,.doc
```

### 3. Start the Server
```bash
uvicorn main:app --reload
```

### 4. Access the API
- API Base URL: `http://127.0.0.1:8000`
- Interactive Docs: `http://127.0.0.1:8000/docs`
- Alternative Docs: `http://127.0.0.1:8000/redoc`

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
# Health Check
curl http://localhost:8000/

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

### Available Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/`      | Health check |
| `POST` | `/analyze` | Analyze document (PDF/DOCX) |

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

## 🤝 Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [CrewAI](https://www.crewai.com/) - For the multi-agent framework
- [FastAPI](https://fastapi.tiangolo.com/) - For the web framework
- [LangChain](https://python.langchain.com/) - For LLM integration
- [OpenAI](https://openai.com/) - For powerful language models
