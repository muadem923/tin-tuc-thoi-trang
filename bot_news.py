import feedparser
import requests
import json
import os

# Lấy chìa khóa từ két sắt của GitHub
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

RSS_URLS = [
    'https://ngoisao.vnexpress.net/rss/thoi-trang.rss',
    'https://vnexpress.net/rss/giai-tri.rss'
    'https://thanhnien.vn/rss/giai-tri.rss'
    'https://kenh14.vn/star.rss'
    'https://afamily.vn/me-va-be.rss'
    'https://afamily.vn/lifestyle.rss'
]
KEYWORDS = ['thời trang', 'mặc đẹp', 'phong cách', 'xu hướng', 'bộ sưu tập', 'bé', 'trẻ', 'tiền tỷ', 'bikini', 'nóng bỏng', 'hoa khôi', 'tư thế']

# Số lượng bài viết tối đa muốn hiển thị trên web
MAX_ARTICLES = 30
DATA_FILE = 'news_data.json'

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
    # 1. Đọc dữ liệu cũ từ file (nếu có) để chuẩn bị cộng dồn
    existing_news = []
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                existing_news = json.load(f)
        except:
            existing_news = []

    # Tạo một danh sách chứa các đường link đã có để tránh copy trùng 1 bài nhiều lần
    existing_links = [item['link'] for item in existing_news]
    
    new_articles = []
    for url in RSS_URLS:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            # Chỉ xử lý nếu bài báo này CHƯA có trong danh sách cũ
            if entry.link not in existing_links:
                if any(kw in (entry.title + entry.summary).lower() for kw in KEYWORDS):
                    content_seo = rewrite_with_ai(entry.title, entry.summary)
                    new_articles.append({
                        "title": entry.title,
                        "link": entry.link,
                        "content_seo": content_seo,
                        "date": entry.published
                    })
                    # Mỗi lần chạy (2 tiếng 1 lần) chỉ lấy tối đa 3-5 bài mới để API AI không bị quá tải
                    if len(new_articles) >= 5: 
                        break
        if len(new_articles) >= 5:
            break

    # 2. Gộp tin mới lên đầu, tin cũ nối tiếp theo sau
    combined_news = new_articles + existing_news

    # 3. Cắt chốt sổ: Chỉ giữ lại đúng 30 bài mới nhất
    final_news = combined_news[:MAX_ARTICLES]

    # 4. Ghi đè lại vào file với tối đa 30 bài
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_news, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    get_news()
