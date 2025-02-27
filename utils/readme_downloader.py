import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


def create_session():
    """
    Create a session with retry strategy
    """
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def get_github_readme(url):
    """
    Get README content from GitHub repository and return it as text
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
    }
    
    try:
        session = create_session()
        
        # First try the raw content URL
        raw_url = url.replace('github.com', 'raw.githubusercontent.com').replace('/blob/', '/')
        response = session.get(raw_url, headers=headers, timeout=10)
        
        # If raw URL fails, try the API URL
        if response.status_code != 200:
            # Extract owner and repo from URL
            parts = url.split('github.com/')[1].split('/')
            owner, repo = parts[0], parts[1]
            api_url = f"https://api.github.com/repos/{owner}/{repo}/readme"
            response = session.get(api_url, headers=headers, timeout=10)
            if response.status_code == 200:
                import base64
                return base64.b64decode(response.json()['content']).decode('utf-8')
        
        response.raise_for_status()
        return response.text
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None


if __name__ == "__main__":
    url = "https://github.com/OpenGithubs/github-daily-rank/blob/main/README.md"
    content = get_github_readme(url)
    if content:
        print(content)
