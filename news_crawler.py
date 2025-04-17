import requests
from bs4 import BeautifulSoup


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

    return results if results else ["❌ 뉴스가 없습니다."]