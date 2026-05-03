import feedparser
import requests
import json
import os

# Lấy chìa khóa từ két sắt của GitHub
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Link báo và từ khóa
RSS_URLS = [
    'https://ngoisao.vnexpress.net/rss/thoi-trang.rss',
    'https://vnexpress.net/rss/giai-tri.rss'
    'https://thanhnien.vn/rss/giai-tri.rss'
    'https://kenh14.vn/star.rss'
    'https://afamily.vn/me-va-be.rss'
    'https://afamily.vn/lifestyle.rss'
]
KEYWORDS = ['thời trang', 'mặc đẹp', 'phong cách', 'xu hướng', 'bộ sưu tập', 'bé', 'trẻ', 'tiền tỷ', 'bikini', 'nóng bỏng', 'hoa khôi', 'tư thế']

def rewrite_with_ai(title, summary):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    prompt = f"Hãy đóng vai biên tập viên. Viết lại tóm tắt này cho mới lạ, chuẩn SEO:\nTiêu đề: {title}\nTóm tắt: {summary}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, json=payload)
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return f"{summary}"

def get_news():
    news_list = []
    for url in RSS_URLS:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            if any(kw in (entry.title + entry.summary).lower() for kw in KEYWORDS):
                content_seo = rewrite_with_ai(entry.title, entry.summary)
                news_list.append({
                    "title": entry.title,
                    "link": entry.link,
                    "content_seo": content_seo,
                    "date": entry.published
                })
                if len(news_list) >= 5: # Lấy tối đa 5 tin để tránh lỗi AI
                    break
        if len(news_list) >= 5:
            break
            
    with open('news_data.json', 'w', encoding='utf-8') as f:
        json.dump(news_list, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    get_news()
