import pandas as pd
import numpy as np
import os
import shutil
from pathlib import Path

# 配置路径
SOURCE_DIR = "/mnt/data/mycode/my_akshare/data"
QLIB_DATA_DIR = "/mnt/data/mycode/my_qlib/.qlib/qlib_data/cn_data"

# 列名映射
# AkShare 数据列名 -> Qlib 标准列名
COLUMN_MAP = {
    '日期': 'date',
    '开盘': 'open',
    '收盘': 'close',
    '最高': 'high',
    '最低': 'low',
    '成交量': 'volume',
    '成交额': 'amount'
}

def get_symbol_prefix(code):
    """
    确定市场前缀
    """
    if code.startswith(('5', '6')):
        return 'sh'
    elif code.startswith(('0', '1')):
        return 'sz'
    return 'sh'

def convert_to_bin():
    print(f"开始转换数据: {SOURCE_DIR} -> {QLIB_DATA_DIR}")
    
    # 1. 收集所有 CSV 数据并记录日期
    all_data = {}
    all_dates = set()
    
    # 加载现有日历
    calendar_path = os.path.join(QLIB_DATA_DIR, "calendars/day.txt")
    if os.path.exists(calendar_path):
        with open(calendar_path, 'r', encoding='utf-8') as f:
            for line in f:
                date_str = line.strip()
                if date_str:
                    all_dates.add(date_str)
        print(f"  已加载现有日历，包含 {len(all_dates)} 个日期")

    # 处理每个 CSV 文件
    for file in os.listdir(SOURCE_DIR):
        if file.endswith('.csv'):
            # 假设文件名类似 518880_黄金ETF.csv
            code = file.split('_')[0]
            prefix = get_symbol_prefix(code)
            symbol = f"{prefix}{code}".lower()
            
            file_path = os.path.join(SOURCE_DIR, file)
            try:
                df = pd.read_csv(file_path)
                df = df.rename(columns=COLUMN_MAP)
                
                # 转换日期格式
                df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
                df = df.sort_values('date')
                
                all_data[symbol] = df
                all_dates.update(df['date'].tolist())
                print(f"  读取文件: {file} -> {symbol}")
            except Exception as e:
                print(f"  读取文件 {file} 出错: {e}")
    
    if not all_data:
        print("未找到可处理的 CSV 文件。")
        return

    # 2. 更新并保存日历
    sorted_dates = sorted(list(all_dates))
    os.makedirs(os.path.dirname(calendar_path), exist_ok=True)
    with open(calendar_path, 'w', encoding='utf-8') as f:
        for d in sorted_dates:
            f.write(f"{d}\n")
    print(f"  已更新日历文件: {calendar_path} (共 {len(sorted_dates)} 天)")
    
    date_to_idx = {d: i for i, d in enumerate(sorted_dates)}
    
    # 3. 转换为 Qlib 二进制格式 (.bin)
    features_dir = os.path.join(QLIB_DATA_DIR, "features")
    
    for symbol, df in all_data.items():
        symbol_dir = os.path.join(features_dir, symbol)
        os.makedirs(symbol_dir, exist_ok=True)
        
        start_date = df['date'].iloc[0]
        end_date = df['date'].iloc[-1]
        start_idx = date_to_idx[start_date]
        
        # 为了保证数据对齐，我们按日历重采样该股票的数据范围
        df = df.set_index('date')
        symbol_calendar = sorted_dates[start_idx : date_to_idx[end_date] + 1]
        df = df.reindex(symbol_calendar)
        
        # 转换为 float32 并填充 NaN
        fields = ['open', 'close', 'high', 'low', 'volume', 'amount']
        for col in fields:
            if col in df.columns:
                # Qlib 存储格式: [start_index(float32), data1(float32), data2(float32), ...]
                values = df[col].astype(np.float32).values
                bin_path = os.path.join(symbol_dir, f"{col}.day.bin")
                
                with open(bin_path, 'wb') as f:
                    # 写入起始索引
                    np.array([start_idx], dtype='<f4').tofile(f)
                    # 写入序列数据
                    values.tofile(f)
        
        # 必须写入 factor.day.bin (复权因子，如果没有则全 1.0)
        factor_bin_path = os.path.join(symbol_dir, "factor.day.bin")
        with open(factor_bin_path, 'wb') as f:
            np.array([start_idx], dtype='<f4').tofile(f)
            np.ones(len(df), dtype='<f4').tofile(f)
            
        print(f"  完成二进制转换: {symbol} ({start_date} 至 {end_date})")

    # 4. 更新 instruments/all.txt
    inst_path = os.path.join(QLIB_DATA_DIR, "instruments/all.txt")
    os.makedirs(os.path.dirname(inst_path), exist_ok=True)
    
    # 读取现有的 instruments
    existing_inst = {}
    if os.path.exists(inst_path):
        with open(inst_path, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) >= 3:
                    existing_inst[parts[0].upper()] = (parts[1], parts[2])
    
    # 添加/更新新数据
    for symbol, df in all_data.items():
        existing_inst[symbol.upper()] = (df['date'].iloc[0], df['date'].iloc[-1])
    
    # 排序并写回
    with open(inst_path, 'w', encoding='utf-8') as f:
        for s, (sd, ed) in sorted(existing_inst.items()):
            f.write(f"{s}\t{sd}\t{ed}\n")
    
    print(f"  已更新 instruments 列表: {inst_path}")
    print("\n转换任务全部完成！")

if __name__ == "__main__":
    convert_to_bin()
