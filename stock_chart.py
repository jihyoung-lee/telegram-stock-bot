import requests
import pandas as pd
import mplfinance as mpf
import matplotlib.font_manager as fm
from io import BytesIO, StringIO



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
    data.columns = ['날짜', 'close', '전일비', 'open', 'high', 'low', 'volume']
    data['날짜'] = pd.to_datetime(data['날짜'])
    data = data.set_index('날짜')
    data = data.sort_index()
    return data[['open', 'high', 'low', 'close', 'volume']]

def draw_candle_chart(df, title="📊 캔들차트"):
    # 한글 폰트 강제 지정
    font_path = "C:/Windows/Fonts/malgun.ttf"
    font_name = fm.FontProperties(fname=font_path).get_name()

    # 스타일을 charles 기반으로 만들고 폰트 지정
    my_style = mpf.make_mpf_style(base_mpf_style='charles', rc={'font.family': font_name})

    # 차트 그리기 + 이미지 저장
    buf = BytesIO()
    mpf.plot(
        df[-10:],
        type='candle',
        style=my_style,
        title=title,
        ylabel='가격',
        savefig=dict(fname=buf, format='png')
    )
    buf.seek(0)
    return buf