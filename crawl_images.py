import requests
from bs4 import BeautifulSoup
import json
import time

TARGET_URL = "https://tianqi.moji.com/liveview/china/hainan/nanette-district-(spratly-islands)"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9",
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
        return "https://tianqi.moji.com" + img_src
    base = base_url.rstrip("/")
    return base + "/" + img_src.lstrip("/")

def fetch_all_images():
    page_html = None
    for retry in range(MAX_RETRY):
        try:
            resp = session.get(TARGET_URL, timeout=TIMEOUT_LIMIT)
            resp.raise_for_status()
            resp.encoding = "utf-8"
            page_html = resp.text
            break
        except Exception as err:
            print("请求失败:", str(err))
            time.sleep(1.5)

    if not page_html:
        fail_data = {
            "access_ip_type": "访问失败",
            "image_count": 0,
            "image_links": []
        }
        with open("image_links.json", "w", encoding="utf-8") as f:
            json.dump(fail_data, f, ensure_ascii=False, indent=4)
        return

    soup = BeautifulSoup(page_html, "html.parser")
    image_link_set = set()

    # 普通图片
    for img_tag in soup.find_all("img"):
        src = img_tag.get("src")
        full_link = parse_absolute_url(TARGET_URL, src)
        if full_link:
            image_link_set.add(full_link)

    # 懒加载图片
    lazy_keys = ["data-src", "data-original"]
    for dom in soup.find_all():
        for key in lazy_keys:
            lazy_src = dom.get(key)
            full_link = parse_absolute_url(TARGET_URL, lazy_src)
            if full_link:
                image_link_set.add(full_link)

    link_list = list(image_link_set)
    result = {
        "source_page": TARGET_URL,
        "total_images": len(link_list),
        "image_links": link_list
    }

    with open("image_links.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

    print("抓取完成，图片数量：", len(link_list))

if __name__ == "__main__":
    fetch_all_images()
