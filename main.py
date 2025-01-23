from crawler import TaobaoCommentCrawler
from analysis import TextAnalyzer
from visualization import WordCloudGenerator
from typing import Optional
import sys
import traceback
import pandas as pd
from utils.output_manager import OutputManager
from utils.log_manager import LogManager
from utils import config

def validate_config():
    """验证配置是否有效"""
    required_configs = [
        'CRAWLER.MAX_PAGES',
        'CRAWLER.WAIT_TIME',
        'CRAWLER.LOGIN_TIMEOUT',
        'VISUALIZATION.WORDCLOUD',
        'OUTPUT.BASE_DIR',
        'OUTPUT.KEEP_RUNS',
        'OUTPUT.SUBDIRS',
        'OUTPUT.FILE_NAMES'
    ]
    
    missing_configs = []
    for key in required_configs:
        if config.get(key) is None:
            missing_configs.append(key)
            
    if missing_configs:
        raise ValueError(f"缺少必要的配置项: {', '.join(missing_configs)}")

def main() -> None:
    """主程序入口"""
    crawler = None
    
    try:
        # 验证配置
        validate_config()
        
        # 初始化输出和日志管理器
        output_manager = OutputManager()
        logger = LogManager(output_manager)
        
        # 记录配置信息
        logger.info("当前配置:")
        logger.info(f"最大爬取页数: {config.get('CRAWLER.MAX_PAGES')}")
        logger.info(f"等待时间范围: {config.get('CRAWLER.WAIT_TIME')}")
        logger.info(f"词云图尺寸: {config.get('VISUALIZATION.WORDCLOUD.WIDTH')}x{config.get('VISUALIZATION.WORDCLOUD.HEIGHT')}")
        
        # 初始化组件
        crawler = TaobaoCommentCrawler()
        analyzer = TextAnalyzer(output_manager)
        word_cloud = WordCloudGenerator(output_manager)
        
        # 登录淘宝
        logger.info("开始登录淘宝...")
        crawler.login()
        
        # 获取商品URL
        product_url = input("\n请输入淘宝商品URL：").strip()
        if not product_url:
            logger.error("URL不能为空")
            return
            
        # 爬取评论
        logger.info("开始爬取评论...")
        crawler.get_comments(product_url)
        
        # 获取评论数据
        comments = crawler.get_all_comments()
        if not comments:
            logger.error("未获取到任何评论，程序终止")
            return
        logger.info(f"成功获取 {len(comments)} 条评论")
            
        # 分析评论
        logger.info("开始分析评论...")
        word_freq = analyzer.analyze_comments(comments)
        if not word_freq:
            logger.error("词频分析结果为空，程序终止")
            return
            
        # 生成词云
        logger.info("正在生成词云...")
        word_cloud.generate(word_freq)
        
        # 输出词频统计
        logger.info("生成词频统计...")
        for word, count in word_freq.most_common(20):
            logger.info(f"{word}: {count}次")
        
        # 主题分析
        logger.info("开始主题分析...")
        topic_df = analyzer.analyze_topics(comments)
        if not topic_df.empty:
            logger.info("\n主题分析结果：")
            # 设置pandas显示选项
            pd.set_option('display.max_columns', None)
            pd.set_option('display.width', None)
            pd.set_option('display.max_colwidth', None)
            logger.info(topic_df.to_string(index=False))
            
            # 保存到CSV文件
            topic_df.to_csv('topic_analysis.csv', index=False, encoding='utf-8-sig')
            logger.info("\n主题分析结果已保存到 topic_analysis.csv")
            
        # 保存评论数据
        comments_file = output_manager.get_path(
            config.get('OUTPUT.FILE_NAMES.COMMENTS', 'comments.txt'),
            subdir=config.get('OUTPUT.SUBDIRS.DATA', 'data')
        )
        with open(comments_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(comments))
        logger.info(f"\n评论数据已保存到: {comments_file}")
        
        # 保存词频数据
        freq_file = output_manager.get_path(
            config.get('OUTPUT.FILE_NAMES.WORD_FREQ', 'word_frequencies.csv'),
            subdir=config.get('OUTPUT.SUBDIRS.DATA', 'data')
        )
        pd.DataFrame(word_freq.most_common(), 
                    columns=['词语', '频次']).to_csv(freq_file, 
                                                 index=False, 
                                                 encoding='utf-8-sig')
        logger.info(f"词频统计已保存到: {freq_file}")
        
        # 保存主题分析结果
        if not topic_df.empty:
            topic_file = output_manager.get_path(
                config.get('OUTPUT.FILE_NAMES.TOPIC_ANALYSIS', 'topic_analysis.csv'),
                subdir=config.get('OUTPUT.SUBDIRS.DATA', 'data')
            )
            topic_df.to_csv(topic_file, index=False, encoding='utf-8-sig')
            logger.info(f"主题分析结果已保存到: {topic_file}")
        
        # 清理旧的运行目录
        output_manager.clean_old_runs()
        logger.info("程序执行完成")
        
    except KeyboardInterrupt:
        logger.warning("程序被用户中断")
    except Exception as e:
        logger.error(f"程序执行出错: {str(e)}")
    finally:
        if crawler:
            crawler.close()

if __name__ == "__main__":
    main() 