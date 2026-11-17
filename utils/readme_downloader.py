from urllib.parse import urlsplit

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
    """Fetch the default README or the exact file named by a GitHub blob URL."""
    try:
        parsed = urlsplit(url)
        if parsed.scheme not in ("http", "https") or parsed.hostname != "github.com":
            raise ValueError("Expected a github.com repository or blob URL")
        parts = parsed.path.strip("/").split("/", 3)
        if len(parts) < 2 or not all(parts[:2]):
            raise ValueError("Missing GitHub repository name")
        owner, repo = parts[:2]
        with create_session() as session:
            endpoint = f"https://api.github.com/repos/{owner}/{repo}"
            params = {}
            if len(parts) == 2:
                endpoint += "/readme"
                path = "HEAD/README.md"
            elif len(parts) == 4 and parts[2] == "blob" and "/" in parts[3]:
                path = parts[3]
                ref, filename = path.split("/", 1)
                endpoint += f"/contents/{filename}"
                params["ref"] = ref
            else:
                raise ValueError("Expected a GitHub file URL containing /blob/")

            try:
                response = session.get(
                    endpoint, params=params, headers={"Accept": "application/vnd.github.raw+json"},
                    timeout=10,
                )
                response.raise_for_status()
                response.encoding = "utf-8"
                return response.text
            except requests.RequestException:
                pass

            response = session.get(
                f"https://raw.githubusercontent.com/{owner}/{repo}/{path}", timeout=10,
            )
            response.raise_for_status()
            response.encoding = "utf-8"
            return response.text

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None


if __name__ == "__main__":
    # Example for the requested repository
    repo_url = "https://github.com/OpenGithubs/github-daily-rank"
    print(f"Fetching README from: {repo_url}")
    content = get_github_readme(repo_url)
    if content:
        print("\nREADME Content Preview (first 500 chars):")
        print(content[:500] + "...")
    else:
        print("Failed to fetch README content")
