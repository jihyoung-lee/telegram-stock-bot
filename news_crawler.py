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

    news_tags = soup.select("span.txt > a")

    news_list = []
    for tag in news_tags:
        if "link_relation" in tag.get("class", []):
            continue

        title = tag.text.strip()
        href = tag.get("href", "")
        if not href.startswith("http"):
            href = "https://finance.naver.com" + href

        #  제목 하이퍼링크 (Markdown)
        news_list.append(f"📰 [{title}]({href})")
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
                news_list.append(f"📰 [{title}]({href})")
            else:
                normalized = normalize_naver_url(href)
                if normalized:
                    news_list.append(f"📰 {title}\n🔗 {normalized}")

    return news_list if news_list else ["❌ 뉴스가 없습니다."]

def request_prediction(text):
    url = "https://2ff8-211-213-33-230.ngrok-free.app/predict"
    payload = {"text": text}
    try:
        response = requests.post(url, json=payload)
        result=response.json()
        return result["result"], result["confidence"]
    except Exception as e:
        print(f"❌ 오류 발생: {e}")  # 콘솔에 오류 이유 출력
        return "오류", 0