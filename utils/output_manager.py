from pathlib import Path
from datetime import datetime
import shutil
from utils import config

class OutputManager:
    """输出文件管理器"""
    
    def __init__(self, base_dir: str = 'output'):
        # 创建基础输出目录
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        
        # 创建带时间戳的运行目录
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.run_dir = self.base_dir / timestamp
        self.run_dir.mkdir(exist_ok=True)
        
        # 创建子目录
        self.visualization_dir = self.run_dir / 'visualization'
        self.visualization_dir.mkdir(exist_ok=True)
        
        self.data_dir = self.run_dir / 'data'
        self.data_dir.mkdir(exist_ok=True)
        
    def get_path(self, filename: str, subdir: str = None) -> Path:
        """获取输出文件路径"""
        if subdir:
            return self.run_dir / subdir / filename
        return self.run_dir / filename
    
    def clean_old_runs(self):
        """清理旧的运行目录，保留最近的几个"""
        keep_runs = config.get('OUTPUT.KEEP_RUNS', 5)
        all_runs = sorted(
            [d for d in self.base_dir.iterdir() if d.is_dir()],
            key=lambda x: x.name,
            reverse=True
        )
        
        for old_run in all_runs[keep_runs:]:
            try:
                shutil.rmtree(old_run)
            except Exception as e:
                print(f"清理旧目录时出错 {old_run}: {str(e)}") 