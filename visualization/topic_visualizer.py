import pyLDAvis
import pyLDAvis.gensim_models
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Optional
from gensim import corpora, models
import numpy as np
from pathlib import Path

class TopicVisualizer:
    """LDA主题模型可视化器"""
    
    def __init__(self, output_manager):
        self.output_manager = output_manager
        
    def visualize_lda(self, 
                     texts: List[List[str]], 
                     lda_model: models.LdaModel, 
                     dictionary: corpora.Dictionary) -> None:
        """
        生成交互式LDA可视化
        
        Args:
            texts: 分词后的文本列表
            lda_model: 训练好的LDA模型
            dictionary: 词典对象
        """
        try:
            # 准备数据
            corpus = [dictionary.doc2bow(text) for text in texts]
            
            # 生成pyLDAvis可视化
            vis_data = pyLDAvis.gensim_models.prepare(
                lda_model, corpus, dictionary, 
                mds='mmds',  # 使用多维尺度缩放
                sort_topics=False
            )
            
            # 使用输出管理器获取保存路径
            html_path = self.output_manager.get_path(
                'lda_visualization.html',
                subdir='visualization'
            )
            pyLDAvis.save_html(vis_data, str(html_path))
            print(f"\nLDA交互式可视化已保存到: {html_path}")
            
        except Exception as e:
            print(f"生成LDA可视化时出错: {str(e)}")
    
    def plot_topic_distribution(self, 
                              topic_names: List[str], 
                              proportions: np.ndarray,
                              title: str = "主题分布") -> None:
        """
        绘制主题分布柱状图
        
        Args:
            topic_names: 主题名称列表
            proportions: 主题占比数组
            title: 图表标题
        """
        try:
            plt.figure(figsize=(10, 6))
            
            # 设置颜色主题
            colors = sns.color_palette("husl", len(topic_names))
            
            # 绘制柱状图
            bars = plt.bar(topic_names, proportions, color=colors)
            
            # 添加数值标签
            for bar in bars:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.1%}',
                        ha='center', va='bottom')
            
            # 设置图表样式
            plt.title(title, fontsize=14, pad=20)
            plt.xlabel("主题", fontsize=12)
            plt.ylabel("占比", fontsize=12)
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
            
            # 调整布局并保存
            plt.tight_layout()
            
            # 使用输出管理器获取保存路径
            output_path = self.output_manager.get_path(
                'topic_distribution.png',
                subdir='visualization'
            )
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"主题分布图已保存到: {output_path}")
            
        except Exception as e:
            print(f"绘制主题分布图时出错: {str(e)}") 