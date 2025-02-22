""" 登陆微信并发送消息给指定好友进行测试

1. 请先完成initialize.py中的初始化操作，获取到app_id和token
2. 更多接口参考： https://apifox.com/apidoc/shared-69ba62ca-cb7d-437e-85e4-6f3d3df271b1/api-196794504
"""


from gewechat_client import GewechatClient
import os
from dotenv import load_dotenv

def main():
    # 加载.env文件
    load_dotenv()
    
    # 从.env文件中读取配置
    base_url = os.getenv("BASE_URL")
    token = os.getenv("TOKEN")
    app_id = os.getenv("APP_ID")
    send_msg_nickname = "胖虎遛二狗" # 要发送消息的好友昵称

    # 创建 GewechatClient 实例
    client = GewechatClient(base_url, token)

    # 登录, 自动创建二维码，扫码后自动登录
    app_id, error_msg = client.login(app_id=app_id)
    if error_msg:
        print("登录失败")
        return
    try:

        # 获取好友列表
        fetch_contacts_list_result = client.fetch_contacts_list(app_id)
        print(fetch_contacts_list_result)
        print("====================================")
        if fetch_contacts_list_result.get('ret') != 200 or not fetch_contacts_list_result.get('data'):
            print("获取通讯录列表失败:", fetch_contacts_list_result)
            return
        # {'ret': 200, 'msg': '操作成功', 'data': {'friends': ['weixin', 'fmessage', 'medianote', 'floatbottle', 'wxid_abcxx'], 'chatrooms': ['1234xx@chatroom'], 'ghs': ['gh_xx']}}
        friends = fetch_contacts_list_result['data'].get('friends', [])
        if not friends:
            print("获取到的好友列表为空")
            return
        print("获取到的好友列表:", friends)

        # 获取好友的简要信息
        friends_info = client.get_brief_info(app_id, friends)
        if friends_info.get('ret') != 200 or not friends_info.get('data'):
            print("获取好友简要信息失败:", friends_info)
            return
        
        # 找对目标好友的wxid
        friends_info_list = friends_info['data']
        if not friends_info_list:
            print("获取到的好友简要信息列表为空")
            return
        wxid = None
        for friend_info in friends_info_list:
            if friend_info.get('nickName') == send_msg_nickname:
                print("找到好友:", friend_info)
                wxid = friend_info.get('userName')
                break
        if not wxid:
            print(f"没有找到好友: {send_msg_nickname} 的wxid")
            return
        print("找到好友:", wxid)

        # 发送消息
        send_msg_result = client.post_text(app_id, wxid, "你好啊")
        if send_msg_result.get('ret') != 200:
            print("发送消息失败:", send_msg_result)
            return
        print("发送消息成功:", send_msg_result)
    except Exception as e:
        print("Failed to fetch contacts list:", str(e))

if __name__ == "__main__":
    main()
