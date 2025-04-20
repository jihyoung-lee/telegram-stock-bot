import requests
import pandas as pd
import mplfinance as mpf
import matplotlib.font_manager as fm
from io import BytesIO, StringIO



def fetch_daily_price(stock_code, pages=30):
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

def determine_volume_unit(df: pd.DataFrame):
    """
    거래량 컬럼을 보고 단위 자동 조절:
    - 100만 이상: '백만 단위'
    - 1만 이상: '만 단위'
    - 그 외: '단위 없음'

    반환: (스케일 값, 단위 문자열)
    """
    avg_volume = df['volume'].mean()

    if avg_volume >= 1_000_000:
        return 1_000_000, '거래량 (백만 단위)'
    elif avg_volume >= 10_000:
        return 10_000, '거래량 (만 단위)'
    else:
        return 1, '거래량'

def draw_candle_chart(df, title="📊 캔들차트"):
    # 한글 폰트 강제 지정
    font_path = "C:/Windows/Fonts/malgun.ttf"
    font_name = fm.FontProperties(fname=font_path).get_name()

    # 스타일을 charles 기반으로 만들고 폰트 지정
    my_style = mpf.make_mpf_style(base_mpf_style='charles',
                                  rc={'font.family': font_name,})

    # 📦 거래량 단위 자동 결정
    scale, ylabel_lower = determine_volume_unit(df)
    df['volume'] = df['volume'] / scale  # 단위 스케일링

    # 차트 그리기 + 이미지 저장
    buf = BytesIO()
    mpf.plot(
        df,
        type='candle',
        volume=True,
        style=my_style,
        title=title,
        ylabel='가격',
        ylabel_lower=ylabel_lower,
        savefig=dict(fname=buf, format='png')
    )
    buf.seek(0)
    return buf