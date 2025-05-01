# 📈 Telegram Stock Bot

<p align="center">
  <img src="https://github.com/user-attachments/assets/c5019b2a-e89f-4385-b3ef-8a8495bf376e" width="600"/>
</p>

A Telegram bot that delivers real-time stock information, daily major news updates before market open, stock charts, and market summaries for Korean stock enthusiasts.

---

## ✨ Features

<table>
  <tr>
    <td align="center">
      <img src="https://github.com/user-attachments/assets/49a15363-d570-4fa9-90a0-016cb15bfbef" width="120"/><br/>
      <b>Market Summaries</b><br/>
      Classification of good/bad sentiment with stock-related news
    </td>
    <td align="center">
      <img src="https://github.com/user-attachments/assets/d1f4a789-1299-4724-9576-501a59e0c2b4" width="120"/><br/>
      <b>Real-Time Charts</b><br/>
      Generate and view up-to-date stock price charts
    </td>
    <td align="center">
      <img src="https://github.com/user-attachments/assets/9b491fb1-4cf8-4ca3-ae33-e5df9b3dcc12" width="120"/><br/>
      <b>News Update</b><br/>
      Sends daily major stock market news before trading starts
    </td>
  </tr>
</table>

---

## 🧰 Tech Stack

- **Python**
- **FastAPI**
- **python-telegram-bot**
- **BeautifulSoup**
- **Matplotlib / Plotly**

---

## 📂 Project Structure

```
telegram-stock-bot/
├── bot.py              # Handles commands and messaging
├── db.py               # Manages database operations
├── main.py             # Main entry point
├── news_crawler.py     # Crawls major news articles
├── stock_chart.py      # Generates stock price charts
├── stock_fetcher.py    # Fetches real-time stock data
├── requirements.txt    # Dependency list
└── README.md
```

---

## ⚙️ Quick Start

```bash
# Clone the repository
git clone https://github.com/jihyoung-lee/telegram-stock-bot.git
cd telegram-stock-bot

# Install dependencies
pip install -r requirements.txt

# Add your Telegram Bot Token in a .env file
# Run the bot
python bot.py
```

---

## 💬 Available Commands

| Command | Description |
|:--------|:------------|
| `/start` | Start the bot |
| `/getcode [stock name]` | Retrieve stock code information |
| `/news [stock code]` | Fetch recent news headlines for a stock |
| `/price [stock code]` | Display stock price trend chart |

---

## 📎 License

This project is licensed under the **MIT License**.

---

## 🙌 Acknowledgements

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)
- [Matplotlib](https://matplotlib.org/)

---

## 📬 Contact

For inquiries, feel free to reach me at: **wlgud3412@naver.com**
