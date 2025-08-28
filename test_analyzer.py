import unittest
import os
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Import the FastAPI app
from main import app

class TestFinancialDocumentAnalyzer(unittest.TestCase):
    def setUp(self):
        # Create test client
        self.client = TestClient(app)
        
        # Create test data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)
        
        # Create a sample PDF file for testing
        self.test_pdf_path = "data/test_document.pdf"
        with open(self.test_pdf_path, "wb") as f:
            # Create a simple PDF file with some text
            f.write(b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\nendobj\n4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n5 0 obj\n<< /Length 44 >>\nstream\nBT /F1 12 Tf 100 700 Td (Test Financial Document) Tj ET\nendstream\nendobj\nxref\n0 6\n0000000000 65535 f \n0000000009 00000 n \n0000000074 00000 n \n0000000108 00000 n \n0000000173 00000 n \n0000000209 00000 n \ntrailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n300\n%%EOF")

    def tearDown(self):
        # Clean up test files
        if os.path.exists(self.test_pdf_path):
            os.remove(self.test_pdf_path)
        if os.path.exists("executive_summary.md"):
            os.remove("executive_summary.md")

    def test_health_check(self):
        """Test the health check endpoint"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("status", response.json())
        self.assertEqual(response.json()["status"], "running")

    @patch('main.run_crew')
    def test_analyze_document_success(self, mock_run_crew):
        """Test successful document analysis"""
        # Mock the run_crew function to return a success response
        mock_run_crew.return_value = {
            "status": "success",
            "analysis": "Sample analysis result",
            "executive_summary": "Sample executive summary"
        }

        # Test with a sample PDF file
        with open(self.test_pdf_path, "rb") as f:
            response = self.client.post(
                "/analyze",
                files={"file": ("test.pdf", f, "application/pdf")},
                data={"query": "Analyze this document"}
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "success")
        self.assertIn("analysis", response.json())
        self.assertIn("executive_summary", response.json())

    def test_analyze_invalid_file_type(self):
        """Test analysis with invalid file type"""
        # Create a test file with invalid extension
        invalid_file_path = "data/test.txt"
        with open(invalid_file_path, "w") as f:
            f.write("This is not a PDF file")

        try:
            with open(invalid_file_path, "rb") as f:
                response = self.client.post(
                    "/analyze",
                    files={"file": ("test.txt", f, "text/plain")}
                )

            self.assertEqual(response.status_code, 400)
            self.assertIn("detail", response.json())
            self.assertIn("Unsupported file type", response.json()["detail"])
        finally:
            # Clean up
            if os.path.exists(invalid_file_path):
                os.remove(invalid_file_path)

    def test_analyze_missing_file(self):
        """Test analysis with missing file"""
        response = self.client.post("/analyze", data={"query": "Test query"})
        self.assertEqual(response.status_code, 422)  # Validation error

    @patch('main.run_crew')
    def test_analyze_crew_error(self, mock_run_crew):
        """Test error handling when crew execution fails"""
        # Mock the run_crew function to raise an exception
        mock_run_crew.side_effect = Exception("Test error")

        with open(self.test_pdf_path, "rb") as f:
            response = self.client.post(
                "/analyze",
                files={"file": ("test.pdf", f, "application/pdf")}
            )

        self.assertEqual(response.status_code, 500)
        self.assertIn("detail", response.json())
        self.assertIn("Error processing financial document", response.json()["detail"])

if __name__ == "__main__":
    unittest.main()
