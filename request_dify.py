import requests
import json
import os
from dotenv import load_dotenv

class DifyAPI:
    """Dify API client for workflow execution."""
    
    def __init__(self):
        load_dotenv()
        self.base_url = "https://api.dify.ai/v1/workflows/run"
        self.api_key = os.getenv('DIFY_WORKFLOW_KEY')
        
    def _get_headers(self):
        """Get API request headers."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _parse_sse_line(self, line):
        """Parse a Server-Sent Events line."""
        if not line:
            return None
            
        decoded_line = line.decode('utf-8')
        if not decoded_line.startswith('data: '):
            return None
            
        try:
            return json.loads(decoded_line[6:])  # Remove 'data: ' prefix
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return None
    
    def execute_workflow(self, user_id="abc-123"):
        """
        Execute a Dify workflow and return the final result.
        
        Args:
            user_id (str): The user identifier
            
        Returns:
            str: The final result from the workflow
        """
        payload = {
            "inputs": {},
            "response_mode": "streaming",
            "user": user_id
        }
        
        try:
            with requests.post(
                self.base_url, 
                headers=self._get_headers(), 
                json=payload, 
                stream=True
            ) as response:
                response.raise_for_status()
                return self._process_response(response)
        except requests.RequestException as e:
            print(f"API request failed: {e}")
            return None
    
    def _process_response(self, response):
        """Process streaming response and extract final result."""
        for line in response.iter_lines():
            chunk = self._parse_sse_line(line)
            if not chunk:
                continue
                
            if chunk.get('event') == 'workflow_finished':
                return chunk['data']['outputs'].get('final_result')
        return None

def get_workflow_result(user_id="abc-123"):
    """Convenience function to execute workflow and get result."""
    client = DifyAPI()
    return client.execute_workflow(user_id)


if __name__ == "__main__":
    result = get_workflow_result()
    print(f"Final result: {result}")
