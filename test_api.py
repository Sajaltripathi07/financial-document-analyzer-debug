import requests
import sys

url = "http://127.0.0.1:8000/analyze"
file_path = r"C:\Users\Sajal\Downloads\Sample.pdf"

try:
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(url, files=files, timeout=60)  # 60 seconds timeout
        print("Status Code:", response.status_code)
        print("Response:", response.text)
        
except requests.exceptions.Timeout:
    print("Error: The request timed out after 60 seconds")
    print("This suggests the server is not responding properly")
    print("Please check the server logs for any errors")
    
except Exception as e:
    print(f"Error: {str(e)}")
    print("Please check if the server is running and accessible")