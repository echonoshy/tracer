import qrcode

def print_green(text):
    print(f"\033[32m{text}\033[0m")

def print_yellow(text):
    print(f"\033[33m{text}\033[0m")

def print_red(text):
    print(f"\033[31m{text}\033[0m")

def make_and_print_qr(url):
    """生成并打印二维码
    
    Args:
        url: 需要生成二维码的URL字符串
        
    Returns:
        None
        
    功能:
        1. 在终端打印二维码的ASCII图形
    """
    print_green("请扫描下方二维码登录")
    qr = qrcode.QRCode()
    qr.add_data(url)
    qr.make()
    qr.print_ascii(invert=True)
