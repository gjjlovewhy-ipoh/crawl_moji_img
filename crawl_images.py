import requests
from bs4 import BeautifulSoup
import json
import os

# 目标页面
URL = "https://tianqi.moji.com/liveview/china/hainan/nanette-district-(spratly-islands)"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def crawl_image_links():
    try:
        resp = requests.get(URL, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        img_urls = []
        for img in soup.find_all("img"):
            src = img.get("src")
            if src and src.startswith(("http://", "https://")):
                img_urls.append(src)

        # 去重
        img_urls = list(set(img_urls))

        # 写入根目录JSON
        with open("image_links.json", "w", encoding="utf-8") as f:
            json.dump({
                "total": len(img_urls),
                "image_urls": img_urls
            }, f, ensure_ascii=False, indent=2)

        print(f"✅ 抓取完成，共 {len(img_urls)} 张图片")
        return img_urls

    except Exception as e:
        print(f"❌ 抓取失败：{str(e)}")
        with open("image_links.json", "w", encoding="utf-8") as f:
            json.dump({"error": str(e), "image_urls": []}, f, ensure_ascii=False, indent=2)
        return []

if __name__ == "__main__":
    crawl_image_links()
