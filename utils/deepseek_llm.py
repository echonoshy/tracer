import os
from openai import OpenAI
from dotenv import load_dotenv


def init_client():
    """Initialize OpenAI client"""
    load_dotenv()
    return OpenAI(
        api_key=os.environ.get("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com",
    )

def get_ai_response(content: str) -> dict:
    """
    Get AI response
    
    Args:
        content: User input message content
        
    Returns:
        dict: Dictionary containing response text and token usage
    """
    try:
        client = init_client()
        completion = client.chat.completions.create(
            model="deepseek-reasoner",
            messages=[
                {
                    "role": "user",
                    "content": content,
                }
            ],
            stream=False,
        )
        
        return {
            "content": completion.choices[0].message.content,
            "total_tokens": completion.usage.total_tokens
        }
    except Exception as e:
        print(f"Failed to get AI response: {str(e)}")
        return None

def main():
    """Test function"""
    response = get_ai_response("Hello")
    if response:
        print("AI response:", response["content"])
        print("Token usage:", response["total_tokens"])


if __name__ == "__main__":
    main()
