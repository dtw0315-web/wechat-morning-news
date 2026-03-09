# src/news_collector.py
import requests
import json
import random
import re
import time
from datetime import datetime
from bs4 import BeautifulSoup


class NewsCollector:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
        self.timeout = 15

    def safe_get(self, url, **kwargs):
        """安全请求"""
        try:
            time.sleep(0.5)  # 礼貌延迟
            resp = self.session.get(url, timeout=self.timeout, **kwargs)
            resp.raise_for_status()
            return resp
        except Exception as e:
            print(f"  ✗ 请求失败 {url[:50]}... : {e}")
            return None

    def safe_post(self, url, data=None, json=None, **kwargs):
        """安全POST请求"""
        try:
            time.sleep(0.3)
            resp = self.session.post(url, data=data, json=json, timeout=self.timeout, **kwargs)
            resp.raise_for_status()
            return resp
        except Exception as e:
            print(f"  ✗ POST失败 {url[:50]}... : {e}")
            return None

    # ========== 稳定新闻源 ==========

    def get_sina_news(self, count=3):
        """新浪新闻（稳定）"""
        try:
            url = "https://news.sina.com.cn/roll/"
            resp = self.safe_get(url)
            if not resp:
                return []

            soup = BeautifulSoup(resp.text, 'html.parser')
            news = []

            # 解析新闻列表
            items = soup.select('.news-item') or soup.select('li')
            for item in items[:count + 3]:
                title_elem = item.select_one('h2 a') or item.select_one('a')
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    if title and len(title) > 10:
                        news.append({
                            'source': '新浪',
                            'category': '国内',
                            'title': title
                        })
                        if len(news) >= count:
                            break
            return news
        except Exception as e:
            print(f"  ✗ 新浪新闻失败: {e}")
            return []

    def get_netEase_news(self, count=3):
        """网易新闻（稳定）"""
        try:
            url = "https://news.163.com/domestic/"
            resp = self.safe_get(url)
            if not resp:
                return []

            soup = BeautifulSoup(resp.text, 'html.parser')
            news = []

            items = soup.select('.news_title h3 a') or soup.select('.hidden-title')
            for item in items[:count]:
                title = item.get_text(strip=True)
                if title and len(title) > 10:
                    news.append({
                        'source': '网易',
                        'category': '国内',
                        'title': title
                    })
            return news
        except Exception as e:
            print(f"  ✗ 网易新闻失败: {e}")
            return []

    def get_tencent_news(self, count=3):
        """腾讯新闻（API稳定）"""
        try:
            url = "https://i.news.qq.com/trpc.qqnews_web.kv_srv.kv_srv_http_proxy/list"
            params = {
                "sub_srv_id": "24hours",
                "srv_id": "pc",
                "limit": count * 2,
                "page": 1
            }
            headers = {
                'Referer': 'https://news.qq.com/',
                'Origin': 'https://news.qq.com'
            }
            resp = self.safe_get(url, params=params, headers=headers)
            if not resp:
                return []

            data = resp.json()
            news = []
            for item in data.get("data", {}).get("list", [])[:count]:
                title = item.get("title", "")
                if title and len(title) > 5:
                    news.append({
                        'source': '腾讯',
                        'category': '热点',
                        'title': title
                    })
            return news
        except Exception as e:
            print(f"  ✗ 腾讯新闻失败: {e}")
            return []

    def get_baidu_hot(self, count=3):
        """百度热搜（稳定）"""
        try:
            url = "https://top.baidu.com/api/board?platform=wise&tab=realtime"
            resp = self.safe_get(url)
            if not resp:
                return []

            data = resp.json()
            news = []
            items = data.get("data", {}).get("cards", [{}])[0].get("content", [])

            for item in items[:count]:
                title = item.get("word", "")
                if title:
                    news.append({
                        'source': '百度',
                        'category': '热点',
                        'title': title
                    })
            return news
        except Exception as e:
            print(f"  ✗ 百度热搜失败: {e}")
            return []

    def get_36kr_news(self, count=2):
        """36氪（科技财经）"""
        try:
            url = "https://36kr.com/api/newsflash"
            headers = {
                'Referer': 'https://36kr.com/newsflashes'
            }
            resp = self.safe_get(url, headers=headers)
            if not resp:
                return []

            data = resp.json()
            news = []
            items = data.get('data', {}).get('items', [])

            for item in items[:count]:
                title = item.get('title', '')
                desc = item.get('description', '')
                content = title if len(title) > len(desc) else desc

                if content and len(content) > 10:
                    category = '科技' if any(kw in content for kw in ['AI', '芯片', '科技', '智能']) else '财经'
                    news.append({
                        'source': '36氪',
                        'category': category,
                        'title': content[:80]
                    })
            return news
        except Exception as e:
            print(f"  ✗ 36氪失败: {e}")
            return []

    def get_ithome_news(self, count=2):
        """IT之家（科技）"""
        try:
            url = "https://api.ithome.com/json/newslist/news"
            resp = self.safe_get(url)
            if not resp:
                return []

            data = resp.json()
            news = []
            for item in data.get('newslist', [])[:count]:
                title = item.get('title', '')
                if title:
                    news.append({
                        'source': 'IT之家',
                        'category': '科技',
                        'title': title
                    })
            return news
        except Exception as e:
            print(f"  ✗ IT之家失败: {e}")
            return []

    def get_wallstreet_news(self, count=2):
        """华尔街见闻（财经）"""
        try:
            url = "https://api.wallstcn.com/apiv1/content/articles"
            params = {"platform": "pc", "limit": count}
            resp = self.safe_get(url, params=params)
            if not resp:
                return []

            data = resp.json()
            news = []
            for item in data.get('data', {}).get('items', [])[:count]:
                title = item.get('title', '')
                if title:
                    news.append({
                        'source': '华尔街见闻',
                        'category': '财经',
                        'title': title
                    })
            return news
        except Exception as e:
            print(f"  ✗ 华尔街见闻失败: {e}")
            return []

    def get_thepaper_news(self, count=2):
        """澎湃新闻（时政）"""
        try:
            url = "https://www.thepaper.cn/searchResult/search"
            params = {"searchWord": "要闻", "page": 1}
            resp = self.safe_get(url, params=params)
            if not resp:
                return []

            soup = BeautifulSoup(resp.text, 'html.parser')
            news = []
            items = soup.select('.search_res') or soup.select('.news_li')

            for item in items[:count]:
                title_elem = item.select_one('h2 a') or item.select_one('a')
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    if title:
                        news.append({
                            'source': '澎湃',
                            'category': '国内',
                            'title': title
                        })
            return news
        except Exception as e:
            print(f"  ✗ 澎湃新闻失败: {e}")
            return []

    def get_jiemian_news(self, count=2):
        """界面新闻（商业）"""
        try:
            url = "https://www.jiemian.com/lists/4.html"  # 要闻频道
            resp = self.safe_get(url)
            if not resp:
                return []

            soup = BeautifulSoup(resp.text, 'html.parser')
            news = []
            items = soup.select('.news-list .news-item') or soup.select('.news-view')

            for item in items[:count]:
                title_elem = item.select_one('h3 a') or item.select_one('.news-title')
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    if title:
                        news.append({
                            'source': '界面',
                            'category': '财经',
                            'title': title
                        })
            return news
        except Exception as e:
            print(f"  ✗ 界面新闻失败: {e}")
            return []

    # ========== 预置新闻池 ==========

    def get_policy_news(self, count=3):
        """政府政策新闻"""
        from config import POLICY_NEWS_POOL
        today = datetime.now()
        random.seed(today.strftime("%Y%m%d"))
        selected = random.sample(POLICY_NEWS_POOL, min(count, len(POLICY_NEWS_POOL)))

        return [{
            'source': '政策',
            'category': '国内',
            'title': item
        } for item in selected]

    def get_international_news(self, count=3):
        """国际新闻"""
        from config import INTERNATIONAL_NEWS_POOL
        today = datetime.now()
        random.seed(today.strftime("%Y%m%d") + "intl")
        selected = random.sample(INTERNATIONAL_NEWS_POOL, min(count, len(INTERNATIONAL_NEWS_POOL)))

        return [{
            'source': '国际',
            'category': '国际',
            'title': item
        } for item in selected]

    # ========== 处理逻辑 ==========

    def deduplicate_and_rank(self, news_list):
        """去重并排序"""
        seen = set()
        unique_news = []

        # 优先级：国内政策 > 国际 > 财经 > 科技 > 热点
        priority = {'国内': 1, '国际': 2, '财经': 3, '科技': 4, '热点': 5}

        for news in news_list:
            key = news['title'][:15]
            if key in seen:
                continue
            seen.add(key)

            p = priority.get(news.get('category', '热点'), 5)
            # 长度适中优先
            length_score = 0 if 20 <= len(news['title']) <= 60 else 1
            news['_score'] = p * 10 + length_score
            unique_news.append(news)

        unique_news.sort(key=lambda x: x['_score'])
        return unique_news

    def collect_all(self):
        """采集所有新闻"""
        all_news = []

        print("开始采集新闻...")

        # 1. 预置政策新闻（保底3条）
        print("  → 加载政策新闻...")
        all_news.extend(self.get_policy_news(3))

        # 2. 预置国际新闻（保底3条）
        print("  → 加载国际新闻...")
        all_news.extend(self.get_international_news(3))

        # 3. 腾讯新闻（稳定）
        print("  → 采集腾讯新闻...")
        all_news.extend(self.get_tencent_news(2))

        # 4. 百度热搜（稳定）
        print("  → 采集百度热搜...")
        all_news.extend(self.get_baidu_hot(2))

        # 5. 36氪（科技财经）
        print("  → 采集36氪...")
        all_news.extend(self.get_36kr_news(2))

        # 6. IT之家（科技）
        print("  → 采集IT之家...")
        all_news.extend(self.get_ithome_news(2))

        # 7. 华尔街见闻（财经）
        print("  → 采集华尔街见闻...")
        all_news.extend(self.get_wallstreet_news(2))

        # 8. 澎湃新闻（时政）
        print("  → 采集澎湃新闻...")
        all_news.extend(self.get_thepaper_news(2))

        # 9. 界面新闻（商业）
        print("  → 采集界面新闻...")
        all_news.extend(self.get_jiemian_news(2))

        # 10. 新浪、网易（备用）
        if len(all_news) < 10:
            print("  → 采集新浪新闻...")
            all_news.extend(self.get_sina_news(2))
            print("  → 采集网易新闻...")
            all_news.extend(self.get_netEase_news(2))

        # 去重排序
        final_news = self.deduplicate_and_rank(all_news)

        print(f"✓ 采集完成，共 {len(final_news)} 条新闻")
        return final_news[:12]