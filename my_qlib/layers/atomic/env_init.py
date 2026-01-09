import qlib
from qlib.config import REG_CN

def init_qlib_env(provider_uri: str = "/mnt/data/mycode/my_qlib/.qlib/qlib_data/cn_data"):
    """
    初始化 Qlib 环境
    """
    qlib.init(provider_uri=provider_uri, region=REG_CN)
