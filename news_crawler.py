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

    return results if results else ["뉴스가 없습니다."]

def get_main_news():
    url = "https://finance.naver.com/news/"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    news_list = []

    # 뉴스 목록에서 상위 5개만 선택
    for a in soup.select("div.main_news li a")[:5]:
        title = a.get_text(strip=True)
        href = a.get("href")
        if href and title:
            # 상대 경로 처리
            if not href.startswith("http"):
                href = "https://finance.naver.com" + href
            news_list.append(f"📰 {title}\n🔗 {href}")

    return news_list if news_list else ["뉴스가 없습니다."]