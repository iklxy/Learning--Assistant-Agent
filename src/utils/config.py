#加载配置文件
import yaml
import os
from typing import Any

def load_config(config_path) -> Any:
    "参数"
    "config_path:配置文件绝对路径"
    with open(config_path,'r') as f:
        config = yaml.safe_load(f)
    
    # 获取文件所在目录及其根目录
    config_dir = os.path.dirname(os.path.abspath(config_path))                                                                                                               
    project_root = os.path.dirname(config_dir)    
    
    # 转换data_dir为绝对路径                                                                                                                                                 
    if 'data' in config and 'data_dir' in config['data']:                                                                                                                    
        relative_data_dir = config['data']['data_dir']                                                                                                                       
        # 去掉"./"前缀                                                                                                                                                       
        relative_data_dir = relative_data_dir.lstrip("./")                                                                                                                   
        config['data']['data_dir'] = os.path.join(project_root, relative_data_dir) 

    return config