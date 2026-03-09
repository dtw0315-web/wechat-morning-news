# main.py
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config import WEBHOOK_URL, MAX_NEWS_COUNT, MIN_NEWS_COUNT
from src.news_collector import NewsCollector
from src.formatter import NewsFormatter
from src.bot import WeChatWorkBot


def main():
    # 检查配置
    if not WEBHOOK_URL or "你的" in WEBHOOK_URL:
        print("错误：请设置企业微信Webhook地址")
        print("方法1: 修改 src/config.py 中的 WEBHOOK_URL")
        print("方法2: 设置环境变量 WECHAT_WEBHOOK_URL")
        sys.exit(1)

    print("=" * 50)
    print(f"开始执行早报推送任务 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    # 采集新闻
    collector = NewsCollector()
    news_list = collector.collect_all()

    if len(news_list) < MIN_NEWS_COUNT:
        print(f"警告：新闻数量不足（{len(news_list)}/{MIN_NEWS_COUNT}），仍继续推送")

    # 格式化
    formatter = NewsFormatter()

    # 生成文本版和Markdown版
    text_content = formatter.format_news(news_list)
    markdown_content = formatter.format_markdown(news_list)

    print("\n生成的早报内容：")
    print("-" * 50)
    print(text_content)
    print("-" * 50)

    # 推送（优先使用Markdown，失败则回退到文本）
    bot = WeChatWorkBot(WEBHOOK_URL)

    print("\n开始推送...")
    success = bot.send_markdown(markdown_content)

    if not success:
        print("Markdown推送失败，尝试文本格式...")
        success = bot.send_text(text_content)

    if success:
        print("✅ 早报推送完成！")
    else:
        print("❌ 推送失败")
        sys.exit(1)


if __name__ == "__main__":
    from datetime import datetime

    main()