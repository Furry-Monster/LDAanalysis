from typing import List, Dict
from gensim import corpora, models
import numpy as np
import pandas as pd
from collections import namedtuple
from visualization.topic_visualizer import TopicVisualizer
from utils import config

TopicAnalysisResult = namedtuple('TopicAnalysisResult', ['topics', 'proportions'])

class TopicAnalyzer:
    """主题分析器，使用LDA模型进行评论主题分析"""
    
    def __init__(self, output_manager=None):
        analysis_config = config.get('ANALYSIS')
        self.num_topics = analysis_config.get('TOPIC_COUNT', 5)
        self.num_words = analysis_config.get('WORDS_PER_TOPIC', 15)
        self.visualizer = TopicVisualizer(output_manager) if output_manager else None
        
    def analyze(self, texts: List[List[str]]) -> TopicAnalysisResult:
        """
        对分词后的文本进行主题分析
        
        Args:
            texts: 分词后的文本列表，每个元素是一个词语列表
            
        Returns:
            TopicAnalysisResult，包含主题词和主题分布
        """
        try:
            if not texts:
                raise ValueError("输入文本为空")
                
            # 创建词典和语料库
            dictionary = corpora.Dictionary(texts)
            corpus = [dictionary.doc2bow(text) for text in texts]
            
            # 训练LDA模型
            lda_model = models.LdaModel(
                corpus=corpus,
                id2word=dictionary,
                num_topics=self.num_topics,
                random_state=42,
                update_every=1,
                passes=10,
                alpha='auto',
                per_word_topics=True
            )
            
            # 获取主题词分布
            topics = []
            for topic_id in range(self.num_topics):
                topic_words = lda_model.show_topic(topic_id, topn=self.num_words)
                topics.append(topic_words)
            
            # 计算主题分布
            topic_proportions = np.zeros(self.num_topics)
            for bow in corpus:
                topic_dist = lda_model.get_document_topics(bow)
                main_topic = max(topic_dist, key=lambda x: x[1])[0]
                topic_proportions[main_topic] += 1
            
            topic_proportions = topic_proportions / len(corpus)
            
            # 生成可视化
            print("\n生成主题模型可视化...")
            self.visualizer.visualize_lda(texts, lda_model, dictionary)
            
            # 生成主题分布图
            topic_names = [f'主题 {i+1}' for i in range(self.num_topics)]
            self.visualizer.plot_topic_distribution(
                topic_names, 
                topic_proportions,
                title="评论主题分布"
            )
            
            return TopicAnalysisResult(topics=topics, proportions=topic_proportions)
            
        except Exception as e:
            print(f"主题分析出错: {str(e)}")
            return None
    
    def format_results(self, results: TopicAnalysisResult) -> pd.DataFrame:
        """将分析结果格式化为DataFrame"""
        if not results:
            return pd.DataFrame()
            
        formatted_data = []
        for topic_id in range(self.num_topics):
            # 格式化主题词和概率
            topic_words = results.topics[topic_id]
            formatted_words = [f"{word} ({prob:.3f})" for word, prob in topic_words]
            
            formatted_data.append({
                '主题ID': f'主题 {topic_id + 1}',
                '主题词': ' | '.join(formatted_words),
                '文档占比': f'{results.proportions[topic_id]:.1%}'
            })
        
        return pd.DataFrame(formatted_data) 