import os
import re
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime

import PyPDF2
from docx import Document
from dotenv import load_dotenv
from pydantic import Field, FilePath, HttpUrl, validator
from crewai_tools import BaseTool
from langchain_core.tools import tool

load_dotenv()

class FinancialDocumentTool(BaseTool):
    """Tool for reading and extracting text from financial documents (PDF, DOCX)."""
    
    name: str = "financial_document_reader"
    description: str = """
    Reads and extracts text from financial documents in PDF or DOCX format.
    
    Args:
        file_path: Path to the financial document (PDF or DOCX)
        
    Returns:
        str: Extracted text content from the document
    """
    file_path: str = Field(default="", description="Path to the financial document (PDF or DOCX)")
    
    def __init__(self, **data):
        super().__init__(**data)
        self.name = "financial_document_reader"
    
    @validator('file_path')
    def validate_file_path(cls, v):
        """Validate that the file exists and has a supported extension."""
        if not os.path.exists(v):
            raise FileNotFoundError(f"File not found: {v}")
            
        ext = os.path.splitext(v)[1].lower()
        if ext not in ['.pdf', '.docx', '.doc']:
            raise ValueError(f"Unsupported file format: {ext}. Please provide a PDF or DOCX file.")
            
        # Check file size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if os.path.getsize(v) > max_size:
            raise ValueError(f"File size exceeds maximum limit of 10MB")
            
        return v
    
    def _run(self) -> str:
        """Read and process the financial document."""
        try:
            self.validate_file_path(self.file_path)
            
            if self.file_path.lower().endswith('.pdf'):
                return self._read_pdf()
            else:  # .doc or .docx
                return self._read_docx()
                
        except Exception as e:
            error_msg = f"Error processing document {self.file_path}: {str(e)}"
            print(error_msg)  # Log the error
            raise RuntimeError(error_msg) from e
    
    def _read_pdf(self) -> str:
        """Extract text from PDF file with improved error handling and formatting."""
        try:
            text = []
            with open(self.file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                
                # Check if PDF is encrypted
                if reader.is_encrypted:
                    # Try empty password as many PDFs have empty owner passwords
                    try:
                        reader.decrypt('')
                    except Exception as e:
                        raise ValueError("Cannot read encrypted PDF file") from e
                
                for page_num in range(len(reader.pages)):
                    try:
                        page = reader.pages[page_num]
                        page_text = page.extract_text() or ""
                        text.append(page_text.strip())
                    except Exception as e:
                        print(f"Warning: Could not read page {page_num + 1}: {str(e)}")
                        continue
                        
            return "\n\n".join(filter(None, text))
            
        except PyPDF2.PdfReadError as e:
            raise ValueError(f"Error reading PDF file: {str(e)}") from e
            
    def _read_docx(self) -> str:
        """Extract text from DOCX file with improved error handling."""
        try:
            doc = Document(self.file_path)
            return "\n\n".join([
                para.text.strip() 
                for para in doc.paragraphs 
                if para.text.strip()
            ])
        except Exception as e:
            raise ValueError(f"Error reading DOCX file: {str(e)}") from e


class InvestmentAnalysisTool(BaseTool):
    """Tool for analyzing financial documents for investment opportunities."""
    
    name: str = "investment_analysis"
    description: str = """
    Analyzes financial documents to identify investment opportunities, 
    key financial metrics, and growth potential.
    
    Args:
        document_text: Text content of the financial document
        
    Returns:
        str: Analysis of investment opportunities and key metrics
    """
    document_text: str = Field(default="", description="Text content of the financial document")
    
    def __init__(self, **data):
        super().__init__(**data)
        self.name = "investment_analysis"
    
    def _run(self) -> str:
        """Analyze financial document for investment opportunities."""
        try:
            if not self.document_text.strip():
                return "No text content provided for analysis."
                
            # Extract key metrics and indicators
            metrics = self._extract_financial_metrics()
            opportunities = self._identify_opportunities()
            
            # Generate analysis report
            report = [
                "# Investment Analysis Report\n",
                "## Key Financial Metrics"
            ]
            
            if metrics:
                for metric, value in metrics.items():
                    report.append(f"- {metric}: {value}")
            else:
                report.append("No specific financial metrics found in the document.")
                
            report.append("\n## Investment Opportunities")
            if opportunities:
                for opp in opportunities:
                    report.append(f"- {opp}")
            else:
                report.append("No specific investment opportunities identified.")
                
            return "\n".join(report)
            
        except Exception as e:
            error_msg = f"Error in investment analysis: {str(e)}"
            print(error_msg)
            return error_msg
    
    def _extract_financial_metrics(self) -> Dict[str, str]:
        """Extract key financial metrics from the document text."""
        metrics = {}
        
        # Common financial metrics patterns
        patterns = {
            'Revenue': r'(?:revenue|sales)[\s:]*[\$\d\.\s]+(?:million|billion|M|B)?',
            'Net Income': r'net income[\s:]*[\$\d\.\s-]+(?:million|billion|M|B)?',
            'EBITDA': r'EBITDA[\s:]*[\$\d\.\s-]+(?:million|billion|M|B)?',
            'EPS': r'EPS[\s:]*[\$\d\.\s-]+',
            'P/E Ratio': r'P[/\s]?E[\s:]*[\d\.]+',
            'Dividend Yield': r'dividend yield[\s:]*[\d\.]+%?',
            'ROE': r'return on equity[\s:]*[\d\.]+%?',
            'Debt to Equity': r'debt[\s-]to[\s-]equity[\s:]*[\d\.]+',
        }
        
        for name, pattern in patterns.items():
            matches = re.finditer(pattern, self.document_text, re.IGNORECASE)
            for match in matches:
                metrics[name] = match.group(0)
                break  # Just get the first match for each metric
                
        return metrics
    
    def _identify_opportunities(self) -> List[str]:
        """Identify potential investment opportunities."""
        opportunities = []
        
        # Look for growth indicators
        growth_indicators = [
            ('growth', 'Potential growth opportunity'),
            ('expansion', 'Company is expanding operations'),
            ('market share', 'Growing market share'),
            ('new product', 'New product launch'),
            ('acquisition', 'Recent or planned acquisitions'),
            ('innovation', 'Innovation in products/services'),
            ('partnership', 'Strategic partnerships formed'),
        ]
        
        for keyword, opportunity in growth_indicators:
            if re.search(r'\b' + re.escape(keyword) + r'\b', 
                        self.document_text, re.IGNORECASE):
                opportunities.append(opportunity)
                
        # Look for financial strength indicators
        strength_indicators = [
            ('profit margin', 'Healthy profit margins'),
            ('cash flow', 'Strong cash flow generation'),
            ('dividend', 'Consistent dividend payments'),
            ('low debt', 'Low debt levels'),
            ('efficiency', 'Operational efficiency improvements'),
        ]
        
        for keyword, strength in strength_indicators:
            if re.search(r'\b' + re.escape(keyword) + r'\b', 
                        self.document_text, re.IGNORECASE):
                opportunities.append(strength)
                
        return list(set(opportunities))  # Remove duplicates


class RiskAssessmentTool(BaseTool):
    """Tool for assessing risks in financial documents."""
    
    name: str = "risk_assessment"
    description: str = """
    Identifies and assesses risks mentioned in financial documents,
    including financial, operational, and market risks.
    
    Args:
        document_text: Text content of the financial document
        
    Returns:
        str: Risk assessment report
    """
    document_text: str = Field(default="", description="Text content of the financial document")
    
    def __init__(self, **data):
        super().__init__(**data)
        self.name = "risk_assessment"
    
    def _run(self) -> str:
        """Assess risks from financial document."""
        try:
            if not self.document_text.strip():
                return "No text content provided for risk assessment."
                
            # Identify different types of risks
            financial_risks = self._identify_financial_risks()
            operational_risks = self._identify_operational_risks()
            market_risks = self._identify_market_risks()
            
            # Generate risk assessment report
            report = ["# Risk Assessment Report\n"]
            
            # Financial Risks
            report.append("## Financial Risks")
            if financial_risks:
                for risk in financial_risks:
                    report.append(f"- {risk}")
            else:
                report.append("No significant financial risks identified.")
                
            # Operational Risks
            report.append("\n## Operational Risks")
            if operational_risks:
                for risk in operational_risks:
                    report.append(f"- {risk}")
            else:
                report.append("No significant operational risks identified.")
                
            # Market Risks
            report.append("\n## Market Risks")
            if market_risks:
                for risk in market_risks:
                    report.append(f"- {risk}")
            else:
                report.append("No significant market risks identified.")
                
            # Overall Risk Assessment
            report.append("\n## Overall Risk Assessment")
            risk_level, risk_summary = self._assess_overall_risk(
                financial_risks, operational_risks, market_risks)
                
            report.append(f"**Risk Level:** {risk_level}")
            report.append(f"**Summary:** {risk_summary}")
            
            return "\n".join(report)
            
        except Exception as e:
            error_msg = f"Error in risk assessment: {str(e)}"
            print(error_msg)
            return error_msg
    
    def _identify_financial_risks(self) -> List[str]:
        """Identify financial risks."""
        financial_risk_indicators = [
            (r'debt[\s-]to[\s-]equity', 'High debt-to-equity ratio'),
            (r'interest[\s-]coverage', 'Low interest coverage ratio'),
            (r'liquidity[\s-]crisis', 'Potential liquidity crisis'),
            (r'going[\s-]concern', 'Going concern issues'),
            (r'default', 'Risk of default on obligations'),
            (r'credit[\s-]rating[\s-]downgrade', 'Credit rating downgrade risk'),
        ]
        
        return self._find_risks(financial_risk_indicators)
    
    def _identify_operational_risks(self) -> List[str]:
        """Identify operational risks."""
        operational_risk_indicators = [
            (r'cyber[\s-]security', 'Cybersecurity vulnerabilities'),
            (r'data[\s-]breach', 'Data breach risks'),
            (r'supply[\s-]chain', 'Supply chain disruptions'),
            (r'regulatory[\s-]compliance', 'Regulatory compliance issues'),
            (r'key[\s-]person[\s-]risk', 'Key person risk'),
            (r'operational[\s-]disruption', 'Operational disruption risks'),
        ]
        
        return self._find_risks(operational_risk_indicators)
    
    def _identify_market_risks(self) -> List[str]:
        """Identify market risks."""
        market_risk_indicators = [
            (r'market[\s-]volatility', 'Market volatility'),
            (r'economic[\s-]downturn', 'Economic downturn risks'),
            (r'competition', 'Increased competition'),
            (r'commodity[\s-]prices', 'Commodity price fluctuations'),
            (r'foreign[\s-]exchange', 'Foreign exchange risk'),
            (r'interest[\s-]rate', 'Interest rate risk'),
        ]
        
        return self._find_risks(market_risk_indicators)
    
    def _find_risks(self, risk_indicators: List[Tuple[str, str]]) -> List[str]:
        """Helper method to find risks based on indicators."""
        risks = []
        for pattern, risk_description in risk_indicators:
            if re.search(pattern, self.document_text, re.IGNORECASE):
                risks.append(risk_description)
        return risks
    
    def _assess_overall_risk(self, financial_risks: List[str], 
                           operational_risks: List[str],
                           market_risks: List[str]) -> Tuple[str, str]:
        """Assess overall risk level based on identified risks."""
        total_risks = len(financial_risks) + len(operational_risks) + len(market_risks)
        
        if total_risks == 0:
            return "Low", "No significant risks identified in the document."
        
        risk_score = 0
        risk_score += len(financial_risks) * 1.5  # Financial risks are weighted more heavily
        risk_score += len(operational_risks) * 1.0
        risk_score += len(market_risks) * 1.0
        
        if risk_score >= 5:
            return "High", "Significant risks identified across multiple categories that could materially impact the company's performance."
        elif risk_score >= 3:
            return "Moderate to High", "Several risks identified that warrant careful consideration and monitoring."
        elif risk_score >= 1:
            return "Low to Moderate", "Some risks identified but appear manageable with proper controls."
        else:
            return "Low", "Minimal risks identified in the document."