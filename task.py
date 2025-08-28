from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
import os
from crewai import Task, Crew
from pydantic import BaseModel, Field

from agents import financial_analyst, investment_advisor, risk_assessor
from tools import FinancialDocumentTool, InvestmentAnalysisTool, RiskAssessmentTool

class AnalysisResult(BaseModel):
    """Structured output format for analysis results."""
    metrics: Dict[str, str] = Field(..., description="Key financial metrics")
    trends: List[str] = Field(..., description="Identified financial trends")
    insights: List[str] = Field(..., description="Actionable insights")

class InvestmentRecommendation(BaseModel):
    """Structured output for investment recommendations."""
    recommendation: str = Field(..., description="Buy/Hold/Sell recommendation")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score (0-1)")
    time_horizon: str = Field(..., description="Recommended investment horizon")
    key_factors: List[str] = Field(..., description="Key factors influencing the recommendation")
    risks: List[str] = Field(default_factory=list, description="Potential risks")

class RiskAssessment(BaseModel):
    """Structured output for risk assessment."""
    risk_factors: Dict[str, str] = Field(..., description="Risk factors and their severity")
    impact: str = Field(..., description="Overall impact assessment")
    mitigation: List[str] = Field(..., description="Mitigation strategies")
    monitoring: List[str] = Field(..., description="Risk monitoring suggestions")

class ExecutiveSummary(BaseModel):
    """Structured output for the executive summary."""
    overview: str = Field(..., description="Brief overview of financial health")
    recommendations: List[str] = Field(..., description="Key recommendations")
    risks: List[str] = Field(..., description="Major risks and mitigations")
    next_steps: List[str] = Field(..., description="Recommended next steps")

def create_document_analysis_task(file_path: str) -> Task:
    """Create a task for analyzing financial documents."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Document not found: {file_path}")
    
    return Task(
        description=(
            f"Analyze the financial document at '{file_path}'. Extract and analyze:\n"
            f"Document Path: {file_path}\n\n"
            "1. Key financial statements (Balance Sheet, Income Statement, Cash Flow)\n"
            "2. Financial ratios and KPIs (e.g., P/E, ROE, Debt/Equity, Current Ratio)\n"
            "3. Year-over-year and quarter-over-quarter trends\n"
            "4. Any significant events or anomalies in the financial data\n\n"
            "Format your analysis using markdown with clear sections and subsections."
        ),
        expected_output=(
            "A comprehensive financial analysis report in markdown format with:\n"
            "## Financial Overview\n"
            "- Summary of key financial metrics\n"
            "- Major changes from previous periods\n\n"
            "## Detailed Analysis\n"
            "- Revenue and cost breakdown\n"
            "- Profitability analysis\n"
            "- Liquidity and solvency assessment\n\n"
            "## Key Insights\n"
            "- Notable trends and patterns\n"
            "- Areas of concern or opportunity"
        ),
        agent=financial_analyst,
        tools=[FinancialDocumentTool],
        async_execution=True,
        output_json=AnalysisResult,
        context=[]  # Initialize with empty list, we'll add the file path to the task description
    )

def create_investment_analysis_task(document_analysis_task: Task, query: str = "") -> Task:
    """Create a task for investment analysis."""
    return Task(
        description=(
            f"Based on the financial analysis, provide detailed investment recommendations.\n"
            f"User Query: {query if query else 'No specific query provided'}\n\n"
            "Consider the following in your analysis:\n"
            "1. Company's financial health and stability\n"
            "2. Industry position and competitive advantages\n"
            "3. Market conditions and economic outlook\n"
            "4. Valuation metrics compared to peers\n\n"
            "Provide a clear recommendation with supporting rationale."
        ),
        expected_output=(
            "## Investment Recommendation\n"
            "### Recommendation: [Buy/Hold/Sell]\n"
            "- **Confidence Level**: [High/Medium/Low]\n"
            "- **Time Horizon**: [Short/Medium/Long]-term\n\n"
            "### Key Factors\n"
            "1. [Factor 1]\n"
            "2. [Factor 2]\n"
            "3. [Factor 3]\n\n"
            "### Potential Risks\n"
            "- [Risk 1]\n"
            "- [Risk 2]\n"
            "- [Risk 3]\n\n"
            "### Supporting Analysis\n"
            "[Detailed analysis supporting the recommendation]"
        ),
        agent=investment_advisor,
        context=[document_analysis_task],
        tools=[InvestmentAnalysisTool],
        output_json=InvestmentRecommendation,
        async_execution=True
    )

def create_risk_assessment_task(document_analysis_task: Task) -> Task:
    """Create a task for risk assessment."""
    return Task(
        description=(
            "Conduct a comprehensive risk assessment considering:\n"
            "1. **Financial Risks**: Liquidity, credit, market, and operational risks\n"
            "2. **Business Risks**: Competitive position, management, and strategy\n"
            "3. **External Risks**: Regulatory, economic, and geopolitical factors\n\n"
            "For each identified risk, provide:\n"
            "- Likelihood and potential impact\n"
            "- Mitigation strategies\n"
            "- Monitoring recommendations"
        ),
        expected_output=(
            "## Risk Assessment Report\n\n"
            "### Risk Matrix\n"
            "| Risk Category | Risk Description | Likelihood | Impact | Mitigation |\n"
            "|---------------|------------------|------------|--------|-------------|\n"
            "| [Category]    | [Description]    | [High/Med/Low] | [High/Med/Low] | [Mitigation] |\n\n"
            "### Top Risks\n"
            "1. **[Risk 1]\n"
            "   - **Impact**: [Description]\n"
            "   - **Mitigation**: [Strategies]\n\n"
            "2. **[Risk 2]\n"
            "   - **Impact**: [Description]\n"
            "   - **Mitigation**: [Strategies]\n\n"
            "### Risk Monitoring Plan\n"
            "- [Monitoring action 1]\n"
            "- [Monitoring action 2]"
        ),
        agent=risk_assessor,
        context=[document_analysis_task],
        tools=[RiskAssessmentTool],
        output_json=RiskAssessment,
        async_execution=True
    )

def create_executive_summary_task(document_analysis_task: Task, 
                               investment_analysis_task: Task, 
                               risk_assessment_task: Task) -> Task:
    """Create a task for generating an executive summary."""
    return Task(
        description=(
            "Create an executive summary combining the financial analysis, "
            "investment recommendations, and risk assessment. The summary should be "
            "concise yet comprehensive, highlighting key findings, recommendations, "
            "and risks for executive decision-making."
        ),
        expected_output=(
            "A well-structured executive summary in markdown format with sections for "
            "key findings, recommendations, risks, and next steps."
        ),
        agent=financial_analyst,
        context=[document_analysis_task, investment_analysis_task, risk_assessment_task],
        output_file="executive_summary.md"
    )