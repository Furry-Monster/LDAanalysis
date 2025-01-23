from pathlib import Path
import json
from typing import Any, Dict
import os

class ConfigManager:
    """配置管理器，处理全局常量设置"""
    
    # 默认配置
    DEFAULT_CONFIG = {
        # 爬虫设置
        'CRAWLER': {
            'MAX_PAGES': 10,              # 最大爬取页数
            'WAIT_TIME': {                # 等待时间设置（秒）
                'MIN': 1,
                'MAX': 3
            },
            'LOGIN_TIMEOUT': 30,          # 登录等待时间
            'RETRY_TIMES': 3              # 重试次数
        },
        
        # 分析设置
        'ANALYSIS': {
            'MIN_WORD_LENGTH': 2,         # 最小词长度
            'TOP_WORDS_COUNT': 100,       # 词频统计TOP N
            'TOPIC_COUNT': 3,             # 主题数量
            'WORDS_PER_TOPIC': 10         # 每个主题的关键词数量
        },
        
        # 可视化设置
        'VISUALIZATION': {
            'WORDCLOUD': {
                'WIDTH': 800,
                'HEIGHT': 400,
                'MAX_WORDS': 100,
                'MAX_FONT_SIZE': 100
            },
            'TOPIC_PLOT': {
                'FIGURE_WIDTH': 10,
                'FIGURE_HEIGHT': 6,
                'DPI': 300
            }
        },
        
        # 输出设置
        'OUTPUT': {
            'BASE_DIR': 'output',         # 基础输出目录
            'KEEP_RUNS': 5,               # 保留最近N次运行的结果
            'ENCODING': 'utf-8-sig'       # 文件编码
        }
    }
    
    def __init__(self):
        self.config_file = Path('config.json')
        self.config = self._load_config()
        
    def _load_config(self) -> Dict:
        """加载配置文件，如果不存在则创建默认配置"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                # 合并用户配置和默认配置
                return self._merge_configs(self.DEFAULT_CONFIG, user_config)
            except Exception as e:
                print(f"加载配置文件出错: {str(e)}，使用默认配置")
                return self.DEFAULT_CONFIG.copy()
        else:
            # 创建默认配置文件
            self.save_config(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG.copy()
            
    def _merge_configs(self, default: Dict, user: Dict) -> Dict:
        """递归合并配置字典"""
        merged = default.copy()
        
        for key, value in user.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._merge_configs(merged[key], value)
            else:
                merged[key] = value
                
        return merged
    
    def save_config(self, config: Dict = None):
        """保存配置到文件"""
        if config is None:
            config = self.config
            
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            print(f"配置已保存到: {self.config_file}")
        except Exception as e:
            print(f"保存配置文件时出错: {str(e)}")
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key_path: 配置键路径，如 'CRAWLER.MAX_PAGES'
            default: 默认值
        """
        try:
            value = self.config
            for key in key_path.split('.'):
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any, save: bool = True):
        """
        设置配置值
        
        Args:
            key_path: 配置键路径，如 'CRAWLER.MAX_PAGES'
            value: 新值
            save: 是否立即保存到文件
        """
        try:
            keys = key_path.split('.')
            current = self.config
            
            # 遍历到最后一个键之前
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]
                
            # 设置值
            current[keys[-1]] = value
            
            if save:
                self.save_config()
                
        except Exception as e:
            print(f"设置配置值时出错: {str(e)}")
    
    def reset(self, key_path: str = None):
        """
        重置配置到默认值
        
        Args:
            key_path: 要重置的配置键路径，None表示重置所有
        """
        if key_path is None:
            self.config = self.DEFAULT_CONFIG.copy()
            self.save_config()
        else:
            try:
                value = self.DEFAULT_CONFIG
                for key in key_path.split('.'):
                    value = value[key]
                self.set(key_path, value)
            except (KeyError, TypeError):
                print(f"未找到默认配置: {key_path}") 