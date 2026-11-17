"""登录微信，可向指定微信 ID 发送一条测试消息。"""

import argparse
import os

import pyrootutils

pyrootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)

from gewechat_client import GewechatClient


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--test-recipient", metavar="WXID", help="接收测试消息的微信 ID")
    args = parser.parse_args()
    base_url = os.getenv("BASE_URL")
    token = os.getenv("TOKEN")
    app_id = os.getenv("APP_ID")
    if not all((base_url, token, app_id)):
        print("请先在 .env 中配置 BASE_URL、TOKEN 和 APP_ID")
        return 1

    client = GewechatClient(base_url, token)
    try:
        app_id, error_msg = client.login(app_id=app_id)
        if error_msg or not app_id:
            print("登录失败:", error_msg)
            return 1
        if args.test_recipient:
            result = client.post_text(app_id, args.test_recipient, "你好啊")
            if result.get("ret") != 200:
                print("发送测试消息失败")
                return 1
            print("发送测试消息成功")
    except RuntimeError as exc:
        print("操作失败:", exc)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
