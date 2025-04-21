import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

def get_stock_news(stock_code, count=5):
    url = f"https://finance.naver.com/item/news_news.naver?code={stock_code}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": "https://finance.naver.com/"
    }

    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    news_links = soup.select("td.title a")

    results = []
    for a in news_links:
        title = a.text.strip()
        href = a.get("href", "")
        if not href.startswith("http"):
            href = "https://finance.naver.com" + href
        results.append(f"📰 {title}\n🔗 {href}")
        if len(results) >= count:
            break

    return results if results else ["뉴스가 없습니다."]

def normalize_naver_url(href):
    """상대 경로 URL을 정규 네이버 뉴스 URL로 변환"""
    parsed = urlparse(href)
    qs = parse_qs(parsed.query)
    article_id = qs.get("article_id", [""])[0]
    office_id = qs.get("office_id", [""])[0]

    if article_id and office_id:
        return f"https://n.news.naver.com/mnews/article/{office_id}/{article_id}"
    return None

def get_main_news():
    url = "https://finance.naver.com/news/"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    news_list = []

    # 뉴스 목록에서 상위 5개 추출
    for a in soup.select("div.main_news li a")[:5]:
        title = a.get_text(strip=True)
        href = a.get("href")
        if href and title:
            if href.startswith("http"):
                news_list.append(f"📰 {title}\n🔗 {href}")
            else:
                normalized = normalize_naver_url(href)
                if normalized:
                    news_list.append(f"📰 {title}\n🔗 {normalized}")

    return news_list if news_list else ["❌ 뉴스가 없습니다."]