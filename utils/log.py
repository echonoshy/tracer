import os
import socket
import sys
from loguru import logger

import pyrootutils

root = pyrootutils.setup_root(
    search_from=__file__,
    indicator=[".project-root"],
    project_root_env_var=True,
    pythonpath=True,
)


from config import CONFIG  # noqa: E402


class StreamToLogger:
    def __init__(self, level="INFO"):
        self.level = level

    def write(self, buffer):
        for line in buffer.rstrip().splitlines():
            logger.log(self.level, line.rstrip())

    def flush(self):
        pass


def setup_logger(logname, log_dir="./", log_level="INFO"):
    logger.remove()
    hostname = socket.gethostname()
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, f"{logname}_{hostname}")

    logger.add(
        log_file + "_{time:YYYY-MM-DD}.log",
        rotation="00:00",
        level=log_level,
        enqueue=True,
        format="{time:YYYY-MM-DD HH:mm:ss:SSS} | {level} | pid: {process} | {module}:{line} - {message}",
    )

    logger.add(
        sys.stderr,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss:SSS}</green> | <level>{level:<8}</level> | <cyan>{module}:{line}</cyan> - <level>{message}</level>",
    )

    # 重定向标准输出和标准错误到logger
    sys.stdout = StreamToLogger("INFO")
    sys.stderr = StreamToLogger("ERROR")

    return logger


logger = setup_logger(
    CONFIG.logging.log_name,
    log_dir=CONFIG.logging.log_dir,
    log_level=CONFIG.logging.log_level,
)

if __name__ == "__main__":
    # 基础日志测试
    logger.info("这是一条信息日志")
    logger.warning("这是一条警告日志")
    logger.error("这是一条错误日志")
    logger.debug("这是一条调试日志")

    # print输出测试
    print("这是一条print输出，将被重定向到日志文件")

    # 异常捕获测试
    try:
        1 / 0
    except Exception as e:
        logger.exception("发生除零错误")

    # 结构化数据测试
    test_data = {"name": "test", "value": 123, "list": [1, 2, 3]}
    logger.info(f"结构化数据测试: {test_data}")

    # 进度条测试
    from tqdm import tqdm

    for _ in tqdm(range(5), desc="进度测试"):
        import time

        time.sleep(1)
        logger.debug(f"进度循环中...")

    # 上下文信息测试
    with logger.contextualize(task_id=123):
        logger.info("带有上下文的日志")
        logger.warning("同样带有上下文的警告")
