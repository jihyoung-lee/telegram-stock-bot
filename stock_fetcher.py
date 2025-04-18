import requests
from bs4 import BeautifulSoup
import re

def get_price(stock_code):
    url = f"https://finance.naver.com/item/main.nhn?code={stock_code}"
    res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(res.text, "html.parser")

    price = soup.select_one("p.no_today span.blind")
    name_tag = soup.select_one("div.wrap_company h2 a")

    # 시장 구분 (코스피, 코스닥, 코넥스)
    code_tag = soup.select_one("img.kospi, img.kosdaq, img.konex")
    code_name = code_tag.get("alt").strip() if code_tag else "시장 정보 없음"

    if price and price.text:
        return f"🏷️시장구분: {code_name}\n📌종목명: {name_tag.text}\n 현재 주가는 📈{price.text}원입니다."
    return "📉 주가 정보를 가져올 수 없습니다."

def get_stock_code(keyword):
    url = f"https://search.naver.com/search.naver?query={keyword}+주식"
    res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})

    soup = BeautifulSoup(res.text, "html.parser")

    name_tag = soup.select_one("span.stk_nm")
    code_tag = soup.select_one("em.t_nm")

    if name_tag and code_tag:
        name = name_tag.text.strip()
        full_text = code_tag.get_text(strip=True)

        code = re.search(r"\d+", full_text).group()         # 숫자 (종목코드)
        market = re.search(r"[A-Z]+$", full_text).group()   # 영문 대문자 (시장명)

        return f"📌 {name}\n🔢 종목코드: {code}\n🏷️ 시장구분: {market}"

    return "❌ 종목을 찾을 수 없습니다."

