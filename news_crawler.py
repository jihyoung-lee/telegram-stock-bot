import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

def get_stock_news(stock_code, count=5):
    url = f"https://finance.naver.com/item/main.naver?code={stock_code}"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://finance.naver.com/"
    }

    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    # 새로 바뀐 뉴스 구조: <span class="txt"> <a href="...">제목</a> </span>
    news_tags = soup.select("span.txt > a")

    news_list = []
    for tag in news_tags:
        # 관련 뉴스 필터: class에 "link_relation" 포함되면 제외
        if "link_relation" in tag.get("class", []):
            continue

        title = tag.text.strip()
        href = tag.get("href", "")
        if not href.startswith("http"):
            href = "https://finance.naver.com" + href

        news_list.append(f"📰 {title}\n🔗 {href}")
        # 관련 뉴스 제외 후 정확히 5개만 수집
        if len(news_list) >= count:
            break


    return news_list if news_list else ["❌ 뉴스가 없습니다."]

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
