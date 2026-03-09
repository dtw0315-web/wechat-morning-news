# src/bot.py
import requests
import json
from datetime import datetime


class WeChatWorkBot:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url

    def send_text(self, content, mentioned_list=None, mentioned_mobile_list=None):
        """发送文本消息"""
        data = {
            "msgtype": "text",
            "text": {
                "content": content,
                "mentioned_list": mentioned_list or [],
                "mentioned_mobile_list": mentioned_mobile_list or []
            }
        }
        return self._send(data)

    def send_markdown(self, content):
        """发送Markdown消息"""
        data = {
            "msgtype": "markdown",
            "markdown": {
                "content": content
            }
        }
        return self._send(data)

    def send_news(self, title, description, url, picurl=""):
        """发送图文消息"""
        data = {
            "msgtype": "news",
            "news": {
                "articles": [
                    {
                        "title": title,
                        "description": description,
                        "url": url,
                        "picurl": picurl
                    }
                ]
            }
        }
        return self._send(data)

    def _send(self, data):
        """基础发送方法"""
        try:
            headers = {'Content-Type': 'application/json'}
            response = requests.post(
                self.webhook_url,
                headers=headers,
                data=json.dumps(data),
                timeout=10
            )
            result = response.json()

            if result.get('errcode') == 0:
                print(f"[{datetime.now()}] 推送成功")
                return True
            else:
                print(f"[{datetime.now()}] 推送失败: {result}")
                return False

        except Exception as e:
            print(f"[{datetime.now()}] 推送异常: {e}")
            return False