import requests
from bs4 import BeautifulSoup
import json
import time

# 目标页面地址
TARGET_URL = "https://tianqi.moji.com/liveview/china/hainan/nanette-district-(spratly-islands)"

# 国内浏览器请求头
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Accept": "text/html,image/webp,*/*",
    "Referer": "https://tianqi.moji.com/"
}

session = requests.Session()
session.headers.update(HEADERS)
MAX_RETRY = 3
TIMEOUT_LIMIT = 12

def parse_absolute_url(base_url, img_src):
    if not img_src:
        return None
    img_src = img_src.strip()
    if img_src.startswith(("http://", "https://")):
        return img_src
    if img_src.startswith("/"):
        return f"https://tianqi.moji.com{img_src}"
    base = base_url.rstrip("/")
    return f"{base}/{img_src.lstrip('/')}"

def fetch_all_images():
    page_html = None
    # 重试请求
    for retry in range(MAX_RETRY):
        try:
            resp = session.get(TARGET_URL, timeout=TIMEOUT_LIMIT)
            resp.raise_for_status()
            resp.encoding = "utf-8"
            page_html = resp.text
            break
        except Exception as err:
            print(f"第{retry+1}次请求失败：{str(err)}")
            time.sleep(1.5)

    if not page_html:
        fail_data = {
            "access_ip_type": "国内IP访问",
            "status": "页面访问失败",
            "image_count": 0,
            "image_links": []
        }
        with open("image_links.json", "w", encoding="utf-8") as f:
            json.dump(fail_data, f, ensure_ascii=False, indent=4)
        return []

    soup = BeautifulSoup(page_html, "html.parser")
    image_link_set = set()

    # 抓取普通img图片
    for img_tag in soup.find_all("img"):
        src = img_tag.get("src")
        full_link = parse_absolute_url(TARGET_URL, src)
        if full_link:
            image_link_set.add(full_link)

    # 抓取懒加载图片
    lazy_keys = ["data-src", "data-original", "data-lazy-src"]
    for dom in soup.find_all():
        for key in lazy_keys:
            lazy_src = dom.get(key)
            full_link = parse_absolute_url(TARGET_URL, lazy_src)
            if full_link:
                image_link_set.add(full_link)

    link_list = list(image_link_set)
    result = {
        "source_page": TARGET_URL,
        "access_ip_type": "国内IP访问",
        "total_images": len(link_list),
        "image_links": link_list
    }

    # 写入根目录JSON
    with open("image_links.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

    print(f"抓取完成，共获取 {len(link_list)} 张图片链接")
    return link_list

if __name__ == "__main__":
    fetch_all_images()
