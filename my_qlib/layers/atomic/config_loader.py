import yaml

def load_yaml_config(file_path: str):
    """
    加载 YAML 配置文件原子
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
