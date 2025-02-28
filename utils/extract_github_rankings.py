import os
import argparse

import pyrootutils
root = pyrootutils.setup_root(
    search_from=__file__,
    indicator=[".project-root"], 
    project_root_env_var=True, 
    pythonpath=True
)

from utils.readme_downloader import get_github_readme
# from utils.hunyuan_llm import get_ai_response
from utils.deepseek_llm import get_ai_response

def read_prompt_template():
    """Read the prompt template from the prompt.txt file"""
    # Go up one directory level from utils to the project root
    prompt_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts", "github_rankings.txt")
    with open(prompt_path, "r", encoding="utf-8") as file:
        return file.read()


def extract_github_rankings(url):
    """
    Extract GitHub rankings from README
    
    Args:
        url: URL to the GitHub README
        
    Returns:
        dict: Extracted information or None if extraction failed
    """
    # Download the README content
    print(f"Downloading README from {url}...")
    readme_content = get_github_readme(url)
    if not readme_content:
        print("Failed to download README content")
        return None
    
    # Read the prompt template
    prompt_template = read_prompt_template()
    
    # Combine the prompt with the README content
    full_prompt = f"{prompt_template}\n\n{readme_content}"
    
    # Send to deepseek LLM for extraction
    print("Extracting information using deepseek LLM...")
    response = get_ai_response(full_prompt)
    
    if not response:
        print("Failed to extract information")
        return None
    
    return response


def main():
    parser = argparse.ArgumentParser(description="Extract GitHub rankings from README")
    parser.add_argument("--url", type=str, 
                        default="https://github.com/OpenGithubs/github-daily-rank/blob/main/README.md",
                        help="URL to the GitHub README")
    args = parser.parse_args()
    
    result = extract_github_rankings(args.url)
    if result:
        print("\n===== EXTRACTED INFORMATION =====\n")
        print(result["content"])
        print(f"\nToken usage: {result['total_tokens']}")
    else:
        print("Extraction failed")


if __name__ == "__main__":
    main()
