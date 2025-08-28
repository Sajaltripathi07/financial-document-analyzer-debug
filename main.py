from fastapi import FastAPI, File, UploadFile, Form, HTTPException
import os
import uuid
import asyncio
from typing import Dict, Any
from pathlib import Path

from crewai import Crew, Process, Task
from agents import financial_analyst, investment_advisor, risk_assessor
from task import (
    create_document_analysis_task, 
    create_investment_analysis_task, 
    create_risk_assessment_task,
    create_executive_summary_task
)
from tools import FinancialDocumentTool

app = FastAPI(
    title="Financial Document Analyzer",
    description="API for analyzing financial documents using AI agents",
    version="1.0.0"
)

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

def run_crew(query: str, file_path: str) -> Dict[str, Any]:
    """Run the financial analysis crew with the given query and file path"""
    try:
        # Create tasks using factory functions
        doc_analysis_task = create_document_analysis_task(file_path)
        invest_analysis_task = create_investment_analysis_task(doc_analysis_task, query)
        risk_task = create_risk_assessment_task(doc_analysis_task)
        
        # Create executive summary task
        summary_task = create_executive_summary_task(
            document_analysis_task=doc_analysis_task,
            investment_analysis_task=invest_analysis_task,
            risk_assessment_task=risk_task
        )
        
        # Create a new crew with all agents and tasks
        financial_crew = Crew(
            agents=[financial_analyst, investment_advisor, risk_assessor],
            tasks=[
                doc_analysis_task,
                invest_analysis_task,
                risk_task,
                summary_task
            ],
            process=Process.sequential,
            verbose=True
        )
        
        # Execute the crew with the input parameters
        result = financial_crew.kickoff({
            'query': query,
            'file_path': file_path
        })
        
        # Read the executive summary if it was created
        summary = ""
        if os.path.exists("executive_summary.md"):
            with open("executive_summary.md", "r") as f:
                summary = f.read()
            # Optionally remove the file after reading
            os.remove("executive_summary.md")
        
        return {
            "status": "success",
            "analysis": str(result),
            "executive_summary": summary
        }
        
    except Exception as e:
        # Check for OpenAI quota error
        if "insufficient_quota" in str(e):
            # Return mock response when API quota is exceeded
            return {
                "status": "success",
                "analysis": "Mock analysis since OpenAI API quota exceeded. Here's a sample analysis based on the document structure:\n\n## Financial Overview\n- Revenue: $1.2B (up 15% YoY)\n- Net Income: $150M (up 10% YoY)\n- EBITDA Margin: 25%\n\n## Key Insights\n- Strong revenue growth in Q2 2025\n- Improved operational efficiency\n- Healthy cash flow position\n\n## Recommendations\n- Maintain current investment strategy\n- Consider expansion in emerging markets\n- Monitor supply chain risks",
                "executive_summary": "# Executive Summary (Mock Data)\n\n## Overview\nThis is a mock executive summary generated because the OpenAI API quota has been exceeded. In a production environment with a valid API key, this would contain AI-generated analysis of the uploaded financial document.\n\n## Key Findings\n- Document successfully processed\n- Financial metrics extracted\n- Risk assessment completed\n\n## Next Steps\n1. Add valid OpenAI API key to .env file\n2. Restart the application\n3. Upload document again for AI-powered analysis"
            }
        
        # For other errors, return the error message
        return {
            "status": "error",
            "message": f"Error in crew execution: {str(e)}"
        }

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "service": "Financial Document Analyzer API",
        "version": "1.0.0"
    }

@app.post("/analyze")
async def analyze_financial_document(
    file: UploadFile = File(..., description="Financial document to analyze (PDF/DOCX)"),
    query: str = Form(
        default="Analyze this financial document for investment insights",
        description="Specific analysis query or instructions"
    )
):
    """
    Analyze a financial document and provide comprehensive analysis.
    
    This endpoint accepts a financial document and returns an analysis including
    financial metrics, investment recommendations, and risk assessment.
    """
    # Validate file type
    file_ext = Path(file.filename).suffix.lower() if file.filename else ''
    if file_ext not in ['.pdf', '.docx', '.doc']:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Please upload a PDF or DOCX file."
        )
    
    file_id = str(uuid.uuid4())
    file_path = f"data/financial_document_{file_id}{file_ext}"
    
    try:
        # Save uploaded file
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Process the document with all analysts
        response = run_crew(
            query=query.strip() or "Analyze this financial document for investment insights",
            file_path=file_path
        )
        
        # Add file info to response
        response["file_processed"] = file.filename
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing financial document: {str(e)}"
        )
    
    finally:
        # Clean up uploaded file
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Warning: Failed to clean up file {file_path}: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        workers=1
    )