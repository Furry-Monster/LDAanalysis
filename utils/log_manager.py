import logging
from pathlib import Path
from datetime import datetime
import sys

class LogManager:
    """日志管理器，处理程序运行日志"""
    
    def __init__(self, output_manager):
        self.log_dir = output_manager.run_dir / 'logs'
        self.log_dir.mkdir(exist_ok=True)
        
        # 设置日志格式
        self.formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # 创建日志记录器
        self.logger = logging.getLogger('TextMining')
        self.logger.setLevel(logging.DEBUG)
        
        # 添加文件处理器
        self._add_file_handler('error.log', logging.ERROR)
        self._add_file_handler('info.log', logging.INFO)
        
        # 添加控制台处理器
        self._add_console_handler()
        
    def _add_file_handler(self, filename: str, level: int):
        """添加文件日志处理器"""
        handler = logging.FileHandler(
            self.log_dir / filename,
            encoding='utf-8'
        )
        handler.setLevel(level)
        handler.setFormatter(self.formatter)
        self.logger.addHandler(handler)
        
    def _add_console_handler(self):
        """添加控制台日志处理器"""
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        handler.setFormatter(self.formatter)
        self.logger.addHandler(handler)
        
    def info(self, message: str):
        """记录信息日志"""
        self.logger.info(message)
        
    def error(self, message: str, exc_info=True):
        """记录错误日志"""
        self.logger.error(message, exc_info=exc_info)
        
    def debug(self, message: str):
        """记录调试日志"""
        self.logger.debug(message)
        
    def warning(self, message: str):
        """记录警告日志"""
        self.logger.warning(message) 