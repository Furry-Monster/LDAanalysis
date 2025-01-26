from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os
from pathlib import Path
from collections import Counter
from typing import Optional, Union
from utils import config

class WordCloudGenerator:
    """词云生成器，用于生成词云图像"""
    
    def __init__(self, output_manager):
        # 从配置获取词云参数
        wordcloud_config = config.get('VISUALIZATION.WORDCLOUD', {})
        self.width = wordcloud_config.get('WIDTH', 1200)
        self.height = wordcloud_config.get('HEIGHT', 800)
        self.max_words = wordcloud_config.get('MAX_WORDS', 150)
        self.max_font_size = wordcloud_config.get('MAX_FONT_SIZE', 150)
        self.min_font_size = wordcloud_config.get('MIN_FONT_SIZE', 10)
        self.background_color = wordcloud_config.get('BACKGROUND_COLOR', 'white')
        self.prefer_horizontal = wordcloud_config.get('PREFER_HORIZONTAL', 0.9)
        self.margin = wordcloud_config.get('MARGIN', 10)
        
        self.font_path = self._get_font_path()
        self.output_manager = output_manager
        
    def _get_font_path(self) -> str:
        """获取字体文件路径"""
        # 可能的字体路径
        possible_paths = [
            # Windows字体
            'C:\\Windows\\Fonts\\simhei.ttf',  # 微软雅黑
            'C:\\Windows\\Fonts\\msyh.ttf',  # 微软雅黑
            'C:\\Windows\\Fonts\\simfang.ttf',  # 楷体
            'C:\\Windows\\Fonts\\simsun.ttf',  # 宋体
            'C:\\Windows\\Fonts\\simkai.ttf',  # 楷体
            # Ubuntu字体
            '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',
            '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
            '/usr/share/fonts/wqy/wqy-microhei.ttc',
            # 当前目录字体
            'simhei.ttf',
            'msyh.ttf',
            'NotoSansCJK-Regular.ttc'
        ]
        
        # 检查环境变量
        env_font = os.environ.get('WORDCLOUD_FONT_PATH')
        if env_font and Path(env_font).exists():
            return env_font
            
        # 检查可能的路径
        for path in possible_paths:
            if Path(path).exists():
                return str(path)
                
        raise FileNotFoundError(
            "未找到可用的中文字体文件。\n"
            "请尝试以下方法：\n"
            "1. 安装字体：sudo apt-get install fonts-noto-cjk\n"
            "2. 设置WORDCLOUD_FONT_PATH环境变量\n"
            "3. 将字体文件放在当前目录"
        )
    
    def generate(self, word_freq: Counter) -> None:
        """生成词云图"""
        try:
            if not word_freq:
                raise ValueError("词频数据为空")
                
            # 创建词云对象
            wc = WordCloud(
                font_path=self.font_path,
                width=self.width,
                height=self.height,
                background_color=self.background_color,
                max_words=self.max_words,
                max_font_size=self.max_font_size,
                min_font_size=self.min_font_size,
                random_state=42,
                prefer_horizontal=self.prefer_horizontal,
                margin=self.margin
            )
            
            # 生成词云
            wc.generate_from_frequencies(word_freq)
            
            # 使用输出管理器获取保存路径
            output_path = self.output_manager.get_path(
                'wordcloud.png', 
                subdir='visualization'
            )
            plt.figure(figsize=(10, 5))
            plt.imshow(wc, interpolation='bilinear')
            plt.axis('off')
            plt.savefig(output_path, bbox_inches='tight', pad_inches=0.1, dpi=300)
            plt.close()
            
            print(f"词云图已保存到: {output_path}")
            
        except Exception as e:
            print(f"生成词云图时出错: {str(e)}")
            # 输出词频统计作为备选
            print("\n词频统计:")
            for word, freq in sorted(word_freq.items(), 
                                   key=lambda x: x[1], 
                                   reverse=True)[:20]:
                print(f"{word}: {freq}次") 