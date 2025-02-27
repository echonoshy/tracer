"""
群消息发送模块
用于获取GitHub日榜数据并发送到指定的微信群
"""

import os
import argparse
from dotenv import load_dotenv
import pyrootutils

root = pyrootutils.setup_root(
    search_from=__file__,
    indicator=[".project-root"], 
    project_root_env_var=True, 
    pythonpath=True
)


from gewechat_client import GewechatClient
# Import the extract_github_rankings function
from utils.extract_github_rankings import extract_github_rankings

def init_config():
    """初始化配置"""
    load_dotenv()
    return {
        'base_url': os.getenv("BASE_URL"),
        'token': os.getenv("TOKEN"),
        'app_id': os.getenv("APP_ID"),
        'chatroom_id': os.getenv("CHATROOM_ID")
    }

def send_group_message(config, url=None):
    """
    发送GitHub日榜群消息
    
    Args:
        config: 配置信息
        url: GitHub README URL，默认为None时使用官方日榜URL
    """
    try:
        client = GewechatClient(config['base_url'], config['token'])
        
        # 使用默认URL或指定URL获取GitHub日榜信息
        github_url = url or "https://github.com/OpenGithubs/github-daily-rank/blob/main/README.md"
        
        # 获取GitHub日榜数据
        print(f"正在获取GitHub日榜数据: {github_url}")
        result = extract_github_rankings(github_url)
        
        if not result:
            print("获取GitHub日榜数据失败")
            return None
            
        # 发送消息
        message = result["content"]
        prefix_message = "【测试版】🌟github日榜机器人"
        message = f"{prefix_message}\n{message}"
        response = client.post_text(
            config['app_id'], 
            config['chatroom_id'], 
            message
        )
        print(f"Token使用量: {result['total_tokens']}")
        return response
    except Exception as e:
        print(f"发送消息失败: {str(e)}")
        return None

def main():
    """主函数"""
    # 添加命令行参数
    parser = argparse.ArgumentParser(description="发送GitHub日榜到微信群")
    parser.add_argument("--url", type=str, 
                        default="https://github.com/OpenGithubs/github-daily-rank/blob/main/README.md",
                        help="GitHub README URL")
    args = parser.parse_args()
    
    config = init_config()
    if not all(config.values()):
        print("配置信息不完整，请检查环境变量")
        return
    
    result = send_group_message(config, args.url)
    if result:
        print("消息发送成功:", result)
    else:
        print("消息发送失败")


if __name__ == "__main__":
    main()