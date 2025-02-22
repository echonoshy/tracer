"""
群消息发送模块
用于获取工作流结果并发送到指定的微信群
"""

import os
from dotenv import load_dotenv

from gewechat_client import GewechatClient
from request_dify import get_workflow_result

def init_config():
    """初始化配置"""
    load_dotenv()
    return {
        'base_url': os.getenv("BASE_URL"),
        'token': os.getenv("TOKEN"),
        'app_id': os.getenv("APP_ID"),
        'chatroom_id': os.getenv("CHATROOM_ID")
    }

def send_group_message(config):
    """发送群消息"""
    try:
        client = GewechatClient(config['base_url'], config['token'])
        message = get_workflow_result()
        response = client.post_text(
            config['app_id'], 
            config['chatroom_id'], 
            message
        )
        return response
    except Exception as e:
        print(f"发送消息失败: {str(e)}")
        return None

def main():
    """主函数"""
    config = init_config()
    if not all(config.values()):
        print("配置信息不完整，请检查环境变量")
        return
    
    result = send_group_message(config)
    if result:
        print("消息发送成功:", result)


if __name__ == "__main__":
    main()