import pandas as pd
import matplotlib.pyplot as plt
import requests
from io import BytesIO
from io import StringIO


def fetch_daily_price(stock_code, pages=1):
    dfs = []
    for page in range(1, pages + 1):
        url = f"https://finance.naver.com/item/sise_day.naver?code={stock_code}&page={page}"
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        # res.text → StringIO로 감싸기
        html = StringIO(res.text)
        df = pd.read_html(html, encoding="euc-kr")[0]
        dfs.append(df)
    data = pd.concat(dfs)
    data = data.dropna()
    data.columns = ['날짜', '종가', '전일비', '시가', '고가', '저가', '거래량']
    data['날짜'] = pd.to_datetime(data['날짜'])
    data = data.sort_values('날짜')
    return data[['날짜', '종가']]

def draw_graph(df, title="종가 추이"):

    # 한글 깨짐 방지
    plt.rcParams['font.family'] = 'Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] = False

    plt.figure(figsize=(8, 4))
    plt.plot(df['날짜'], df['종가'], marker='o', linestyle='-')
    plt.title(title)
    plt.xlabel("날짜")
    plt.ylabel("종가")
    plt.grid(True)
    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    return buf
