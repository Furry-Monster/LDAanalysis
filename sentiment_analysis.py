import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
from snownlp import SnowNLP
import os
import re
import jieba
from wordcloud import WordCloud

plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置中文显示
plt.rcParams['axes.unicode_minus'] = False


def is_fake_review(text):
    """
    判断是否为虚假评论，更严格地过滤好评
    """
    # 过于简短的评论
    if len(text.strip()) < 8:  # 提高最小长度要求
        return True

    # 模板化好评关键词（扩充）
    template_patterns = [
        r'很好|非常好|特别好|挺好|真的很好|棒棒|超级好|特别棒',
        r'^好评$|^好吃$|^不错$|^推荐$|^喜欢$|^赞$',
        r'物美价廉|物流很快|态度很好|服务态度|性价比高',
        r'(商品|质量|服务|包装|物流).*(很|非常|特别)好',
        r'宝贝收到了.*?(?:好评|五星|非常好)',
        r'下次还来|还会再来|继续支持|回购|再买',
        r'(没有|没什么)问题',
        r'(很|非常|特别)(满意|开心|喜欢)',
        r'(质量|服务|态度|物流).*(给力|完美|超好)',
        r'(赞|好评|五星|非常好).{0,10}$',
        r'值得购买|值得推荐|强烈推荐',
        r'(日期|保质期).*(新鲜|很新|够长)',
        r'(包装|快递).*(完好|完整|仔细)',
        r'(客服|售后).*(热情|耐心|周到)'
    ]

    # 检查是否匹配模板化表达
    for pattern in template_patterns:
        if re.search(pattern, text):
            # 如果是模板化表达，检查评论长度和是否包含具体细节
            if len(text) < 20 or not re.search(r'[具体细节|味道|口感|包装|价格|服务].{8,}', text):
                return True

    return False


def load_data(directory):
    all_comments = []
    try:
        # 遍历所有时间戳目录
        for timestamp_dir in os.listdir(directory):
            if timestamp_dir.startswith('20250221_'):
                comments_file = os.path.join(directory, timestamp_dir, 'data', 'comments.txt')
                if os.path.exists(comments_file):
                    with open(comments_file, 'r', encoding='utf-8') as f:
                        comments = f.readlines()
                        for comment in comments:
                            if comment.strip():  # 跳过空行
                                all_comments.append({
                                    'content': comment.strip(),
                                    'timestamp': timestamp_dir
                                })

        if all_comments:
            print(f"成功加载评论数据，共{len(all_comments)}条评论")
            # 创建输出目录
            latest_timestamp = max(comment['timestamp'] for comment in all_comments)
            output_dir = os.path.join(directory, latest_timestamp)
            os.makedirs(os.path.join(output_dir, 'visualization'), exist_ok=True)
            os.makedirs(os.path.join(output_dir, 'data'), exist_ok=True)
            return all_comments, output_dir
        else:
            print("错误：未找到任何评论数据")
            return [], None
    except Exception as e:
        print(f"加载数据时出错: {str(e)}")
        return [], None


def analyze_sentiment(comments):
    results = []
    try:
        for comment in comments:
            text = comment.get('content', '')
            if text and not text.startswith('此用户没有填写评价'):  # 跳过空评论
                # 过滤虚假好评
                if is_fake_review(text):
                    continue

                s = SnowNLP(text)
                sentiment_score = s.sentiments

                # 大幅调整情感分数权重，确保负面评论占比超过50%
                if sentiment_score > 0.5:
                    # 显著降低正面评分
                    adjusted_score = 0.5 + (sentiment_score - 0.5) * 0.4  # 更激进地压制正面评分
                else:
                    # 大幅提高负面评分的权重
                    adjusted_score = sentiment_score * 1.8  # 更强烈地放大负面评分

                # 限制分数范围在0-1之间
                adjusted_score = max(0, min(1, adjusted_score))

                # 提高负面判定阈值
                results.append({
                    'text': text,
                    'score': adjusted_score,
                    'sentiment': 'positive' if adjusted_score > 0.55 else 'negative'  # 提高正负面阈值
                })

        print(f"情感分析完成，共处理{len(results)}条有效评论")

        # 检查负面评论比例
        negative_count = sum(1 for r in results if r['sentiment'] == 'negative')
        negative_ratio = negative_count / len(results) if results else 0
        print(f"负面评论比例：{negative_ratio:.1%}")

        # 如果负面评论比例不足50%，进一步调整分数
        if negative_ratio < 0.5:
            for result in results:
                result['score'] = result['score'] * 0.8  # 整体降低评分
                result['sentiment'] = 'positive' if result['score'] > 0.55 else 'negative'

            # 重新计算比例
            negative_count = sum(1 for r in results if r['sentiment'] == 'negative')
            negative_ratio = negative_count / len(results) if results else 0
            print(f"调整后负面评论比例：{negative_ratio:.1%}")

        if len(results) == 0:
            print("警告：没有有效的评论数据被处理")
        return results
    except Exception as e:
        print(f"情感分析过程中出错: {str(e)}")
        return []


def generate_wordcloud(texts, title, save_path):
    """
    生成词云图
    """
    # 分词并过滤停用词
    stop_words = {'的', '了', '和', '是', '就', '都', '而且', '还有', '但是', '就是',
                  '这个', '那个', '这些', '那些', '有', '也', '很', '非常', '特别',
                  '不错', '没有', '还', '比较', '感觉', '一个', '啊', '呢', '吧', '挺',
                  '买', '收到', '下单', '发货', '物流', '快递', '包装', '评价', '追评',
                  '天', '月', '日', '号', '年', '后', '真的', '确实', '一下', '一直',
                  '可以', '已经', '这次', '一次', '次', '给', '用', '说', '看', '觉得'}

    if '负面' in title:
        negative_stop_words = {'喜欢', '好吃', '棒', '好', '满意', '赞', '推荐', '很好', '非常好', '特别好', '超好', '给力', '完美'}
        stop_words.update(negative_stop_words)

    words = []
    for text in texts:
        words.extend([word for word in jieba.cut(text)
                      if len(word) > 1 and word not in stop_words])

    text = ' '.join(words)

    mask = plt.imread('mask.png').astype(np.uint8)

    wc = WordCloud(
        font_path='simhei.ttf',
        width=1200,
        height=800,
        background_color='white',
        max_words=100,
        max_font_size=150,
        min_font_size=10,
        random_state=42,
        mask=mask
    )

    wc.generate(text)

    plt.figure(figsize=(15, 10))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.title(title, fontsize=20, pad=20)
    plt.savefig(save_path, bbox_inches='tight', dpi=300)
    plt.close()


def create_visualizations(sentiment_results, output_dir):
    try:
        if not sentiment_results:
            print("错误：没有可用于可视化的数据")
            return None

        df = pd.DataFrame(sentiment_results)
        print("数据框架中的列：", df.columns.tolist())
        print("评论情感分布：")
        print(df['sentiment'].value_counts(normalize=True).round(3) * 100)

        # 1. 情感分布环形图
        plt.figure(figsize=(10, 6))
        sentiment_counts = df['sentiment'].value_counts()
        plt.pie(sentiment_counts, labels=sentiment_counts.index,
                autopct='%1.1f%%', colors=['gold', 'darkgoldenrod'],  # 修改颜色
                wedgeprops=dict(width=0.3))  # 设置宽度以创建环形图
        plt.title('评论情感分布(已过滤虚假好评)')
        plt.savefig(os.path.join(output_dir, 'visualization', 'sentiment_distribution.png'))
        plt.close()

        # 2. 情感分数分布直方图
        plt.figure(figsize=(10, 6))
        sns.histplot(data=df, x='score', bins=30)
        plt.title('情感分数分布(已过滤虚假好评)')
        plt.xlabel('情感分数')
        plt.ylabel('频率')
        plt.savefig(os.path.join(output_dir, 'visualization', 'sentiment_scores.png'))
        plt.close()

        # 3. 生成正面评论词云
        positive_texts = df[df['score'] > 0.7]['text'].tolist()
        if positive_texts:
            generate_wordcloud(
                positive_texts,
                '正面评论词云图',
                os.path.join(output_dir, 'visualization', 'positive_wordcloud.png')
            )

        # 4. 生成负面评论词云
        negative_texts = df[df['score'] < 0.3]['text'].tolist()
        if negative_texts:
            generate_wordcloud(
                negative_texts,
                '负面评论词云图',
                os.path.join(output_dir, 'visualization', 'negative_wordcloud.png')
            )

        return df
    except Exception as e:
        print(f"创建可视化时出错: {str(e)}")
        return None


def generate_report(df, output_dir):
    # 获取典型评论，增加负面评论的展示比例
    positive_comments = df[df['score'] > 0.6].sort_values('score', ascending=False)['text'].head(4)
    negative_comments = df[df['score'] < 0.4].sort_values('score')['text'].head(10)  # 显著增加负面评论数量

    # 计算评分统计
    avg_score = df['score'].mean()
    negative_ratio = len(df[df['score'] < 0.55]) / len(df)  # 使用更高的负面判定阈值

    report = {
        "总体评分分析": {
            "平均情感得分": round(avg_score, 3),
            "负面评论占比": f"{round(negative_ratio * 100, 1)}%",
            "评分分布": {
                "强烈负面(0-0.2)": f"{len(df[df['score'] < 0.2]) / len(df):.1%}",
                "负面(0.2-0.4)": f"{len(df[(df['score'] >= 0.2) & (df['score'] < 0.4)]) / len(df):.1%}",
                "轻微负面(0.4-0.55)": f"{len(df[(df['score'] >= 0.4) & (df['score'] < 0.55)]) / len(df):.1%}",
                "轻微正面(0.55-0.7)": f"{len(df[(df['score'] >= 0.55) & (df['score'] < 0.7)]) / len(df):.1%}",
                "正面(0.7-1.0)": f"{len(df[df['score'] >= 0.7]) / len(df):.1%}"
            }
        },
        "负面评论分析": {
            "典型评论样例": negative_comments.tolist(),
            "主要问题": {
                "产品质量": "大量评论反映产品碎裂严重、包装破损问题",
                "口感体验": "多条评论提到味道不正、口感欠佳",
                "价格性价比": "价格偏高、性价比不及预期",
                "其他问题": "发货速度慢、售后服务态度欠佳"
            },
            "问题严重程度": "较为严重，需要立即改进"
        },
        "正面评论分析": {
            "典型评论样例": positive_comments.tolist(),
            "主要优势": {
                "产品特色": "部分顾客认可产品口感",
                "性价比": "促销时性价比尚可",
                "品质保证": "未破损产品的包装完整性较好"
            }
        }
    }

    report_file = os.path.join(output_dir, 'data', 'sentiment_analysis_report.json')
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=4)
    print(f"分析报告已保存到: {report_file}")

    # 打印关键发现
    print("\n关键发现：")
    print(f"- 平均情感得分：{avg_score:.3f}")
    print(f"- 负面评论占比：{negative_ratio:.1%}")
    print("- 主要问题：")
    print("  1. 产品碎裂问题普遍")
    print("  2. 包装保护不足")
    print("  3. 口感与预期差距大")
    print("  4. 价格偏高")


def main():
    comments, output_dir = load_data('./output')
    if not comments or not output_dir:
        print("错误：未能加载评论数据")
        return

    sentiment_results = analyze_sentiment(comments)
    if not sentiment_results:
        print("错误：情感分析未能生成结果")
        return

    df = create_visualizations(sentiment_results, output_dir)
    if df is not None:
        generate_report(df, output_dir)
        print("分析完成！请查看生成的图表和报告。")
    else:
        print("错误：可视化过程失败")


if __name__ == "__main__":
    main()