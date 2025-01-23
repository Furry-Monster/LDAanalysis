import jieba
from collections import Counter
import re
from typing import Dict, List
from .topic_analyzer import TopicAnalyzer
import pandas as pd

class TextAnalyzer:
    """文本分析器，用于处理和分析评论文本"""
    
    def __init__(self, output_manager=None):
        self.stopwords = self._get_stopwords()
        self.topic_analyzer = TopicAnalyzer(output_manager)
        
    def _get_stopwords(self) -> set:
        """获取停用词集合"""
        return {
            '的', '了', '和', '是', '就', '都', '而', '及', '与', '着',
            '或', '一个', '没有', '这个', '那个', '这样', '那样', '还是',
            '什么', '这些', '那些', '一些', '一样', '很多', '不是'
        }
    
    def _clean_text(self, text: str) -> str:
        """清理文本，去除特殊字符"""
        return re.sub(r'[^\w\s]', '', text)
    
    def _segment_text(self, text: str) -> List[str]:
        """对文本进行分词"""
        return [word for word in jieba.cut(text)
                if word not in self.stopwords and len(word) > 1]
    
    def _segment_comments(self, comments: List[str]) -> List[List[str]]:
        """对所有评论进行分词"""
        segmented_comments = []
        for comment in comments:
            cleaned_text = self._clean_text(comment)
            words = self._segment_text(cleaned_text)
            if words:  # 只添加非空的分词结果
                segmented_comments.append(words)
        return segmented_comments
    
    def analyze_comments(self, comments: List[str]) -> Counter:
        """分析评论文本，返回词频统计"""
        if not comments:
            print("警告：没有评论数据")
            return Counter()
            
        try:
            # 合并所有评论
            all_comments = " ".join(comments)
            
            # 清理文本
            cleaned_text = self._clean_text(all_comments)
            
            # 分词并统计
            words = self._segment_text(cleaned_text)
            word_freq = Counter(words)
            
            print(f"分析完成，共统计 {len(word_freq)} 个不同词语")
            return word_freq
            
        except Exception as e:
            print(f"分析评论时出错: {str(e)}")
            return Counter()
    
    def analyze_topics(self, comments: List[str]) -> pd.DataFrame:
        """
        对评论进行主题分析
        
        Args:
            comments: 评论列表
            
        Returns:
            包含主题分析结果的DataFrame
        """
        try:
            # 分词预处理
            texts = self._segment_comments(comments)
            if not texts:
                raise ValueError("没有有效的分词结果")
            
            # 进行主题分析
            results = self.topic_analyzer.analyze(texts)
            if not results:
                raise ValueError("主题分析失败")
            
            # 格式化结果
            df = self.topic_analyzer.format_results(results)
            if not df.empty:
                print("\n主题分析完成！")
            return df
            
        except Exception as e:
            print(f"主题分析时出错: {str(e)}")
            return pd.DataFrame() 