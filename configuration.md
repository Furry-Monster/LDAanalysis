# 配置文档

## 配置概述

本文档详细说明了系统的配置项，包括爬虫、分析、可视化、输出和日志等各个模块的设置。

## 配置项说明

### 1. 爬虫配置 (CRAWLER)

爬虫模块的相关配置，控制数据采集行为。

| 配置项          | 说明             | 默认值    | 建议范围 |
| --------------- | ---------------- | --------- | -------- |
| MAX_PAGES       | 最大爬取页数     | 50        | 10-100   |
| WAIT_TIME.MIN   | 最小等待时间(秒) | 2         | 1-3      |
| WAIT_TIME.MAX   | 最大等待时间(秒) | 5         | 3-8      |
| LOGIN_TIMEOUT   | 登录等待时间(秒) | 15        | 30-60    |
| RETRY_TIMES     | 操作失败重试次数 | 3         | 2-5      |
| USER_AGENT      | 浏览器标识       | Chrome UA | -        |
| SCROLL_WAIT.MIN | 滚动最小等待(秒) | 1         | 0.5-2    |
| SCROLL_WAIT.MAX | 滚动最大等待(秒) | 2         | 1.5-4    |

### 2. 分析配置 (ANALYSIS)

文本分析模块的配置，控制数据处理和分析行为。

| 配置项          | 说明           | 默认值       | 建议范围 |
| --------------- | -------------- | ------------ | -------- |
| MIN_WORD_LENGTH | 最小词长度     | 2            | 1-3      |
| TOP_WORDS_COUNT | 保留高频词数量 | 200          | 100-500  |
| TOPIC_COUNT     | 主题分析主题数 | 5            | 3-10     |
| WORDS_PER_TOPIC | 每主题关键词数 | 15           | 10-20    |
| STOPWORDS       | 停用词列表     | [见配置文件] | 可自定义 |

### 3. 可视化配置 (VISUALIZATION)

#### 3.1 词云图配置 (WORDCLOUD)

| 配置项            | 说明           | 默认值 | 建议范围 |
| ----------------- | -------------- | ------ | -------- |
| WIDTH             | 图片宽度(像素) | 1200   | 800-2000 |
| HEIGHT            | 图片高度(像素) | 800    | 600-1500 |
| MAX_WORDS         | 最大显示词数   | 150    | 100-300  |
| MAX_FONT_SIZE     | 最大字体大小   | 150    | 100-200  |
| MIN_FONT_SIZE     | 最小字体大小   | 10     | 8-15     |
| BACKGROUND_COLOR  | 背景颜色       | white  | 任意颜色 |
| PREFER_HORIZONTAL | 水平词比例     | 0.9    | 0.6-1.0  |
| MARGIN            | 词间距         | 10     | 5-20     |

#### 3.2 主题分布图配置 (TOPIC_PLOT)

| 配置项          | 说明           | 默认值   | 建议范围 |
| --------------- | -------------- | -------- | -------- |
| FIGURE_WIDTH    | 图形宽度(英寸) | 12       | 8-16     |
| FIGURE_HEIGHT   | 图形高度(英寸) | 8        | 6-12     |
| DPI             | 图像分辨率     | 300      | 150-600  |
| COLORS          | 主题配色方案   | [见配置] | 可自定义 |
| FONT_SIZE.TITLE | 标题字号       | 16       | 14-20    |
| FONT_SIZE.LABEL | 标签字号       | 12       | 10-14    |
| FONT_SIZE.TICK  | 刻度字号       | 10       | 8-12     |

### 4. 输出配置 (OUTPUT)

输出文件和目录的相关配置。

| 配置项    | 说明           | 默认值    |
| --------- | -------------- | --------- |
| BASE_DIR  | 基础输出目录   | output    |
| KEEP_RUNS | 保留运行记录数 | 10        |
| ENCODING  | 文件编码       | utf-8-sig |

#### 4.1 子目录配置 (SUBDIRS)

- DATA: 数据文件目录
- VISUALIZATION: 可视化文件目录
- LOGS: 日志文件目录

#### 4.2 文件命名 (FILE_NAMES)

- COMMENTS: 评论原文 (comments.txt)
- WORD_FREQ: 词频统计 (word_frequencies.csv)
- TOPIC_ANALYSIS: 主题分析 (topic_analysis.csv)
- WORDCLOUD: 词云图 (wordcloud.png)
- TOPIC_DIST: 主题分布图 (topic_distribution.png)
- LDA_VIS: LDA可视化 (lda_visualization.html)

### 5. 日志配置 (LOGGING)

日志记录的相关配置。

| 配置项       | 说明           | 默认值            |
| ------------ | -------------- | ----------------- |
| LEVEL        | 日志级别       | INFO              |
| FORMAT       | 日志格式       | [见配置]          |
| DATE_FORMAT  | 时间格式       | %Y-%m-%d %H:%M:%S |
| MAX_BYTES    | 单文件最大大小 | 10MB              |
| BACKUP_COUNT | 备份文件数量   | 5                 |

#### 5.1 日志文件 (FILES)

- ERROR: 错误日志 (error.log)
- INFO: 信息日志 (info.log)
- DEBUG: 调试日志 (debug.log)

## 配置修改方法

### 方法一：直接修改配置文件

编辑 `config.json` 文件，修改相应的值。

### 方法二：通过代码修改

```python
from utils import config
```

# 修改单个配置

config.set('CRAWLER.MAX_PAGES', 20)

# 修改多个配置

config.set('VISUALIZATION.WORDCLOUD', {

'WIDTH': 1500,

'HEIGHT': 1000

})

# 重置配置

config.reset() # 重置所有配置

config.reset('VISUALIZATION.WORDCLOUD') # 重置特定配置
