"""webfetch 工具：抓取 HTTP(S) 页面，HTML 剥离为纯文本。"""

import re
from tools import Tool, ToolParameter

try:
    import urllib.request
    import urllib.error
    HAS_URLLIB = True
except ImportError:
    HAS_URLLIB = False


class WebFetchTool(Tool):
    """抓取 HTTP(S) URL 内容，HTML 自动剥离标签返回纯文本。"""

    def __init__(self, max_bytes: int = 100000, timeout: int = 15):
        super().__init__("webfetch", "抓取 HTTP(S) 页面内容，HTML 会被剥离为纯文本")
        self.max_bytes = max_bytes
        self.timeout = timeout

    def get_parameters(self):
        return [
            ToolParameter(name="url", type="string", description="要抓取的 URL"),
            ToolParameter(name="max_bytes", type="integer", description="最大读取字节数", required=False, default=100000),
        ]

    def run(self, url: str, max_bytes: int = None, **kwargs) -> str:
        if not HAS_URLLIB:
            return "❌ urllib 不可用"

        if not url.startswith(("http://", "https://")):
            return "❌ URL 必须以 http:// 或 https:// 开头"

        max_bytes = max_bytes or self.max_bytes

        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (CodingAgent/1.0)"})
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                content_type = resp.headers.get("Content-Type", "")
                raw = resp.read(max_bytes)

            # 尝试解码
            encoding = "utf-8"
            if "charset=" in content_type:
                encoding = content_type.split("charset=")[-1].split(";")[0].strip()
            text = raw.decode(encoding, errors="replace")

            # 如果是 HTML，剥离标签
            if "html" in content_type.lower():
                text = self._strip_html(text)

            # 截断过长内容
            if len(text) > max_bytes:
                text = text[:max_bytes] + "\n... (内容已截断)"

            return text

        except urllib.error.HTTPError as e:
            return f"❌ HTTP 错误 {e.code}: {e.reason}"
        except urllib.error.URLError as e:
            return f"❌ 请求失败: {e.reason}"
        except Exception as e:
            return f"❌ 抓取失败: {e}"

    @staticmethod
    def _strip_html(html: str) -> str:
        """简单剥离 HTML 标签，保留文本内容。"""
        # 移除 script/style 块
        html = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', html, flags=re.DOTALL | re.IGNORECASE)
        # 移除所有标签
        text = re.sub(r'<[^>]+>', ' ', html)
        # 合并多余空白
        text = re.sub(r'\s+', ' ', text).strip()
        # 恢复段落换行
        text = re.sub(r' ([。！？\.\!\?]) ', r'\1\n', text)
        return text
