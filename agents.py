import os
from typing import List, Optional, Type
from dotenv import load_dotenv
from crewai import Agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import BaseTool
from tools import FinancialDocumentTool, InvestmentAnalysisTool, RiskAssessmentTool

# Load environment variables
load_dotenv()

def create_llm() -> ChatOpenAI:
    """Create and configure the language model with error handling."""
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
            
        return ChatOpenAI(
            model_name="gpt-3.5-turbo",
            temperature=0.2,  # Lower temperature for more focused, deterministic outputs
            max_retries=3,
            request_timeout=60,
            openai_api_key=api_key,
            model_kwargs={
                "top_p": 0.9,
                "frequency_penalty": 0.1,
                "presence_penalty": 0.1,
            }
        )
    except Exception as e:
        raise RuntimeError(f"Failed to initialize language model: {str(e)}")

class FinancialAnalystAgent(Agent):
    """Enhanced Financial Analyst Agent with specialized configurations."""
    
    def __init__(self, llm: ChatOpenAI, tools: Optional[List[Type[BaseTool]]] = None):
        super().__init__(
            role="Senior Financial Analyst",
            goal=(
                "Provide accurate, comprehensive, and insightful financial analysis "
                "based on documents including financial statements, annual reports, "
                "and market data."
            ),
            backstory=(
                "You are a CFA-certified financial analyst with 15+ years of experience "
                "in equity research and financial modeling. You have a proven track record "
                "of identifying key financial trends, performing ratio analysis, and "
                "providing actionable investment theses. Your analysis is known for "
                "being thorough, data-driven, and forward-looking."
            ),
            verbose=True,
            allow_delegation=False,
            llm=llm,
            tools=tools or [FinancialDocumentTool],
            max_iter=15,  # Limit the number of agent iterations
            max_rpm=10,   # Rate limiting
            step_callback=lambda x: print(f"Financial Analyst Step: {x}")
        )
        self.cache = {}

class InvestmentAdvisorAgent(Agent):
    """Enhanced Investment Advisor Agent with specialized configurations."""
    
    def __init__(self, llm: ChatOpenAI, tools: Optional[List[Type[BaseTool]]] = None):
        super().__init__(
            role="Senior Investment Advisor",
            goal=(
                "Generate well-researched, risk-adjusted investment recommendations "
                "based on thorough financial analysis and market conditions."
            ),
            backstory=(
                "You are a seasoned investment advisor with 12+ years of experience "
                "in portfolio management and wealth advisory. You hold an MBA from a "
                "top business school and are a CFA charterholder. Your expertise lies "
                "in fundamental analysis, valuation techniques, and portfolio "
                "construction across various asset classes."
            ),
            verbose=True,
            allow_delegation=True,  # Can delegate to other agents
            llm=llm,
            tools=tools or [InvestmentAnalysisTool],
            max_iter=12,
            max_rpm=8,
            step_callback=lambda x: print(f"Investment Advisor Step: {x}")
        )

class RiskAssessmentAgent(Agent):
    """Enhanced Risk Assessment Agent with specialized configurations."""
    
    def __init__(self, llm: ChatOpenAI, tools: Optional[List[Type[BaseTool]]] = None):
        super().__init__(
            role="Chief Risk Officer",
            goal=(
                "Identify, assess, and mitigate financial, operational, and market risks "
                "to protect organizational value and ensure regulatory compliance."
            ),
            backstory=(
                "You are a seasoned risk management professional with 18+ years of "
                "experience in enterprise risk management across global financial "
                "institutions. You hold an FRM certification and have deep expertise "
                "in risk modeling, stress testing, and regulatory compliance "
                "frameworks like Basel III and Solvency II."
            ),
            verbose=True,
            allow_delegation=True,
            llm=llm,
            tools=tools or [RiskAssessmentTool],
            max_iter=10,
            max_rpm=6,
            step_callback=lambda x: print(f"Risk Assessment Step: {x}")
        )

# Initialize LLM
try:
    llm = create_llm()
    
    # Initialize tool instances
    financial_doc_tool = FinancialDocumentTool()
    investment_analysis_tool = InvestmentAnalysisTool()
    risk_assessment_tool = RiskAssessmentTool()
    
    # Initialize agents with their respective tools
    financial_analyst = FinancialAnalystAgent(
        llm=llm,
        tools=[financial_doc_tool]
    )
    
    investment_advisor = InvestmentAdvisorAgent(
        llm=llm,
        tools=[investment_analysis_tool]
    )
    
    risk_assessor = RiskAssessmentAgent(
        llm=llm,
        tools=[risk_assessment_tool]
    )
    
    # Create a list of all agents for easy access
    agents = {
        'financial_analyst': financial_analyst,
        'investment_advisor': investment_advisor,
        'risk_assessor': risk_assessor
    }
    
except Exception as e:
    print(f"Error initializing agents: {str(e)}")
    raise
