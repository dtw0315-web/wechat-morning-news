# src/formatter.py
from datetime import datetime
import random
import re


class NewsFormatter:
    def __init__(self):
        self.today = datetime.now()

    def get_lunar_date(self):
        """获取农历日期"""
        try:
            from lunarcalendar import Converter, Solar
            solar = Solar(self.today.year, self.today.month, self.today.day)
            lunar = Converter.Solar2Lunar(solar)
            # 农历月份名称
            lunar_months = ['正', '二', '三', '四', '五', '六', '七', '八', '九', '十', '冬', '腊']
            lunar_days = ['初一', '初二', '初三', '初四', '初五', '初六', '初七', '初八', '初九', '初十',
                          '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九', '二十',
                          '廿一', '廿二', '廿三', '廿四', '廿五', '廿六', '廿七', '廿八', '廿九', '三十']
            return f"农历{lunar_months[lunar.month - 1]}月{lunar_days[lunar.day - 1]}"
        except:
            return "农历日期"

    def get_weekday(self):
        """获取星期"""
        weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        return weekdays[self.today.weekday()]

    def get_greeting(self):
        """获取问候语"""
        from config import QUOTES_LIBRARY

        month, day = self.today.month, self.today.day

        # 检查特殊节日
        special = QUOTES_LIBRARY['special_days'].get((month, day))
        if special:
            return special['greeting']

        # 周末
        if self.today.weekday() >= 5:
            return "周末愉快！"

        return "早上好！"

    def get_quote(self):
        """获取微语"""
        from config import QUOTES_LIBRARY

        month, day = self.today.month, self.today.day

        # 特殊节日
        special = QUOTES_LIBRARY['special_days'].get((month, day))
        if special:
            return random.choice(special['quotes'])

        # 周末
        if self.today.weekday() >= 5:
            return random.choice(QUOTES_LIBRARY['weekend'])

        # 默认
        return random.choice(QUOTES_LIBRARY['default'])

    def clean_title(self, title):
        """清理标题"""
        # 移除来源标记
        title = re.sub(r'【.*?】', '', title)
        # 移除多余空格
        title = re.sub(r'\s+', ' ', title)
        # 限制长度
        if len(title) > 70:
            title = title[:67] + "..."
        return title.strip()

    def format_news(self, news_list):
        """格式化为早报"""
        lines = []

        # 头部
        date_str = self.today.strftime("%Y年%m月%d日")
        weekday = self.get_weekday()
        lunar = self.get_lunar_date()
        greeting = self.get_greeting()

        header = f"{date_str}早报，{weekday}，{lunar}，{greeting}"
        lines.append(header)
        lines.append("")  # 空行

        # 新闻内容
        for i, news in enumerate(news_list, 1):
            clean = self.clean_title(news['title'])
            lines.append(f"{i}、{clean}；")

        # 微语
        lines.append("")
        quote = self.get_quote()
        lines.append(f"【微语】{quote}")

        return "\n".join(lines)

    def format_markdown(self, news_list):
        """企业微信Markdown格式（更美观）"""
        lines = []

        date_str = self.today.strftime("%Y年%m月%d日")
        weekday = self.get_weekday()
        lunar = self.get_lunar_date()
        greeting = self.get_greeting()

        # 标题
        lines.append(f"## 📰 {date_str} 早报")
        lines.append(f"**{weekday} | {lunar} | {greeting}**")
        lines.append("---")

        # 分类展示
        categories = {'国内': [], '国际': [], '财经': [], '科技': [], '热点': []}
        for news in news_list:
            cat = news.get('category', '热点')
            if cat in categories:
                categories[cat].append(news)

        for cat, items in categories.items():
            if items:
                lines.append(
                    f"\n### {'🎯' if cat == '国内' else '🌍' if cat == '国际' else '💰' if cat == '财经' else '🔬' if cat == '科技' else '🔥'} {cat}要闻")
                for i, news in enumerate(items, 1):
                    clean = self.clean_title(news['title'])
                    lines.append(f"{i}. {clean}")

        # 微语
        lines.append("\n---")
        lines.append(f"💡 **{self.get_quote()}**")

        return "\n".join(lines)