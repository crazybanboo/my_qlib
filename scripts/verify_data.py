import qlib
from qlib.data import D
import pandas as pd

# 初始化 Qlib
qlib_dir = "/mnt/data/mycode/my_qlib/.qlib/qlib_data/cn_data"
qlib.init(provider_uri=qlib_dir)

# 查询转换后的数据
instruments = ['SH518880', 'SZ159513', 'SZ159338', 'SH511130', 'SH510300']
fields = ['$open', '$close', '$high', '$low', '$volume', '$amount', '$factor']

try:
    df = D.features(instruments, fields, start_time='2025-01-01', end_time='2025-12-31')
    print("\n查询成功！数据样例 (2025年):")
    print(df.head())
    print("\n数据列:")
    print(df.columns)
except Exception as e:
    print(f"\n查询失败: {e}")
