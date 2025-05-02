"""
===================
微信 gewechat 登录说明
===================

概述
----
通过 iPad 协议登录微信是一种模拟登录方式，存在一定风控风险。建议仅在初始化时执行一次，
将获取的 appId 等信息保存至 .env 文件中，避免频繁认证触发风控机制。

登录步骤
-------
1. 获取认证令牌（Token）
   - 系统首次认证必须步骤

2. 获取登录二维码
   - 使用令牌获取二维码、app_id
   - appId 说明：
     * 首次登录：留空，系统自动创建设备ID
     * 重复登录：必须使用之前获取的 appId
     * 注意：同一账号避免创建多个设备，防止触发风控
   - 接口返回：
     * qrImgBase64：二维码图片的 base64 编码
     * qrData：用于手动生成二维码的原始数据

3. 执行扫码登录
   - 扫码后每隔 5 秒轮询一次登录状态
   - 新设备注意事项：
     * 首次登录设备会在次日凌晨自动断线
     * 断线后使用保存的 appId 重新登录
     * 完成首次完整登录流程后可保持长期在线
   - 重要：请务必保存 appId 和 wxid 的对应关系


⚠️ 注意事项
-------
- 妥善保存首次登录获取的设备信息
- 避免频繁切换设备，保持登录状态稳定
"""

from gewechat_client import GewechatClient


def get_token():
    """获取认证令牌"""
    base_url = "http://127.0.0.1:2531/v2/api"
    client = GewechatClient(base_url=base_url, token="")
    res = client.get_token()

    if res["ret"] != 200:
        print("获取认证令牌失败:", res)
    else:
        print("获取认证令牌成功， 请手动保存到.env中")
        token = res["data"]
        print("====================================")
        print("认证令牌:", token)
        print("====================================")
    return token


def get_app_id():
    """获取appId, uuid"""
    base_url = "http://127.0.0.1:2531/v2/api"
    token = get_token()
    client = GewechatClient(base_url=base_url, token=token)

    app_id, error_msg = client.login(app_id="")

    if app_id:
        print("====================================")
        print("获取appId成功, 请保存到.env中。 appId:", app_id)
        print("====================================")
    else:
        print("获取appId失败:", error_msg)


if __name__ == "__main__":
    # 手动记录一下 token 和 app_id 并保存到 .env 文件中
    get_app_id()
