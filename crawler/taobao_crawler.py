from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
import time
import random
from utils import config

class TaobaoCommentCrawler:
    def __init__(self):
        # 从配置获取爬虫参数
        crawler_config = config.get('CRAWLER')
        self.max_pages = crawler_config.get('MAX_PAGES', 50)
        self.retry_times = crawler_config.get('RETRY_TIMES', 3)
        self.login_timeout = crawler_config.get('LOGIN_TIMEOUT', 15)
        self.wait_time = crawler_config.get('WAIT_TIME', {'MIN': 2, 'MAX': 5})
        self.user_agent = crawler_config.get('USER_AGENT')
        
        self.driver = self._init_driver()
        self.comments = []
        
    def _init_driver(self):
        """初始化Chrome驱动"""
        options = Options()
        if self.user_agent:
            options.add_argument(f'user-agent={self.user_agent}')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        driver = webdriver.Chrome(options=options)
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
        })
        return driver
    
    def random_sleep(self):
        """随机等待"""
        time.sleep(random.uniform(self.wait_time['MIN'], self.wait_time['MAX']))
    
    def _scroll_to_element(self, element):
        """滚动到元素位置"""
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        self.random_sleep()
    
    def _click_element(self, element):
        """使用JavaScript点击元素"""
        try:
            self.driver.execute_script("arguments[0].click();", element)
            return True
        except Exception as e:
            print(f"JavaScript点击失败: {str(e)}")
            return False
    
    def _wait_for_element(self, selector, timeout=10):
        """等待元素出现"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            return element
        except TimeoutException:
            return None
    
    def _find_and_click(self, selectors, text_conditions=None):
        """查找并点击符合条件的元素"""
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if text_conditions is None or any(cond in element.text for cond in text_conditions):
                        self._scroll_to_element(element)
                        if self._click_element(element) or self._try_normal_click(element):
                            return True
            except Exception as e:
                print(f"点击元素时出错: {str(e)}")
                continue
        return False
    
    def _try_normal_click(self, element):
        """尝试普通点击"""
        try:
            element.click()
            return True
        except Exception as e:
            print(f"普通点击失败: {str(e)}")
            return False
    
    def _get_comments_from_page(self):
        """从当前页面获取评论"""
        comment_selectors = [
            "div.Comment--KkPcz74T div.content--FpIOzHeP",
            "div.contentWrapper--uAdAlCgC div.content--FpIOzHeP",
            "div.Comment--KkPcz74T div[class*='content']",
            "div[class*='comment'] div[class*='content']",
            # 添加更多可能的选择器
            "div.rate-content",
            "div.tb-rev-item div.J_KgRate_ReviewContent",
            "div.review-details"
        ]
        
        # 添加固定等待时间,等待评论加载
        print("等待页面加载评论...")
        time.sleep(3)  # 固定等待3秒
        
        for selector in comment_selectors:
            try:
                # 等待评论加载
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                comments = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if comments:
                    return [comment.text.strip() for comment in comments if comment.text.strip()]
            except TimeoutException:
                continue
            except Exception as e:
                print(f"获取评论时出错 (选择器: {selector}): {str(e)}")
        return []
    
    def login(self):
        """手动登录淘宝"""
        self.driver.get("https://login.taobao.com/")
        print(f"请在{self.login_timeout}秒内完成手动登录")
        time.sleep(self.login_timeout)
    
    def get_comments(self, product_url, pages=None):
        """爬取商品评论"""
        try:
            # 使用配置的最大页数
            if pages is None:
                pages = self.max_pages
            
            # 访问商品页面
            print(f"正在访问商品页面: {product_url}")
            self.driver.get(product_url)
            self.random_sleep()
            
            # 点击全部评价按钮
            if not self._show_all_comments(product_url):
                print("无法访问评价页面，程序终止")
                return
            
            # 爬取评论
            page_count = 0
            retry_count = 0
            
            while page_count < pages and retry_count < self.retry_times:
                # 获取当前页评论
                new_comments = self._get_comments_from_page()
                
                if new_comments:
                    self.comments.extend(new_comments)
                    print(f"已爬取第{page_count + 1}页评论，当前共{len(self.comments)}条评论")
                    page_count += 1
                    retry_count = 0
                    
                    # 尝试进入下一页
                    if not self._go_to_next_page():
                        print("已到达最后一页")
                        break
                else:
                    retry_count += 1
                    print(f"第{page_count + 1}页未找到评论，重试第{retry_count}次")
                    self.random_sleep()
            
            if not self.comments:
                print("警告：未获取到任何评论")
            else:
                print(f"爬取完成，共获取到 {len(self.comments)} 条评论")
            
        except Exception as e:
            print(f"爬取评论出错: {str(e)}")
    
    def _show_all_comments(self, product_url):
        """显示所有评论"""
        # 尝试点击"全部评价"按钮
        show_all_selectors = [
            "div.ShowButton--o4XEG7ih",
            "div.footer--h5lcc85O div[class*='ShowButton']",
            "a[href*='rate']",
            "div[data-index='1']",
            "div.tabTitleItem--z4AoobEz",
            # 添加更多可能的选择器
            "a.tb-tab-anchor[href*='rate']",
            "li.J_TabBarItem"
        ]
        
        retry_count = 0
        while retry_count < self.retry_times:
            if self._find_and_click(show_all_selectors, ['全部评价', '查看全部', '评价']):
                self.random_sleep()
                return True
                
            print(f"尝试第 {retry_count + 1} 次切换到评价页面...")
            retry_count += 1
            
            try:
                # 尝试直接访问评价页面
                rate_url = f"{product_url.split('?')[0]}/rate.htm"
                self.driver.get(rate_url)
                self.random_sleep()
                return True
            except Exception as e:
                print(f"访问评价页面失败: {str(e)}")
        
        print("无法显示评价页面")
        return False
    
    def _go_to_next_page(self):
        """进入下一页"""
        next_selectors = [
            "div.ShowButton--o4XEG7ih",
            "div.footer--h5lcc85O div[class*='ShowButton']",
            "div[class*='pagination'] button:last-child",
            "button:contains('下一页')",
            "div:contains('下一页')"
        ]
        
        if self._find_and_click(next_selectors, ['下一页', '显示更多']):
            self.random_sleep()
            return True
        
        print("没有更多页面")
        return False
    
    def get_all_comments(self):
        """获取所有评论"""
        return self.comments
    
    def close(self):
        """关闭浏览器"""
        self.driver.quit() 