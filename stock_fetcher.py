import requests
from bs4 import BeautifulSoup


def get_price(stock_code):
    url = f"https://finance.naver.com/item/main.nhn?code={stock_code}"
    res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(res.text, "html.parser")

    price = soup.select_one("p.no_today span.blind")

    if price:
        return f"📈 현재 주가는 {price.text}원입니다."
    return "📉 주가 정보를 가져올 수 없습니다."
