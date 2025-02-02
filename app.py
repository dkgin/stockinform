import os
import requests
from bs4 import BeautifulSoup
import requests
import schedule
import time
import threading
from flask import Flask

app = Flask(__name__)
def stock():
    msg = ['找不到股票資訊']
    try:
        url = f'https://tw.stock.yahoo.com/quote/2330'
        web = requests.get(url)                          # 取得網頁內容
        soup = BeautifulSoup(web.text, "html.parser")    # 轉換內容
        div = soup.select_one('div.D\\(f\\).Ai\\(c\\).Mb\\(6px\\)')
        title = div.find('h1').get_text() if div else 'N/A'

        a = soup.select('.Fz\\(32px\\)')[0].get_text() if soup.select('.Fz\\(32px\\)') else 'N/A'
        #b = soup.select('.Fz\\(20px\\)')[0].get_text() if soup.select('.Fz\\(20px\\)') else 'N/A'
        b = soup.select('[class^="Fz\\(20px\\)"]')[0].get_text() if soup.select('.Fz\\(20px\\)') else 'N/A'
        c = soup.select('.Jc\\(fe\\)')[0].get_text() if soup.select('.Jc\\(fe\\)') else 'N/A'
        s = ''                              # 漲或跌的狀態
        try:
            main_div = soup.select('#main-0-QuoteHeader-Proxy')[0]
            if main_div:
                trend_divs = main_div.select('div.D\\(f\\).Ai\\(fe\\).Mb\\(4px\\)')[0]
                if any(div.select('.C\\(\\$c-trend-down\\)') for div in trend_divs):
                    s = '-'
                else:
                    s = ''
        except Exception as e:
            print(f'Error: {e}')
            s = 'error'
            # 如果 main-0-QuoteHeader-Proxy id 的 div 裡有 C($c-trend-down) 的 class
            # 表示狀態為下跌
            '''
            if soup.select('#main-0-QuoteHeader-Proxy')[0].select('.C\\(\\$c-trend-down\\)')[0]:
                s = '-'
        except:
            try:
                # 如果 main-0-QuoteHeader-Proxy id 的 div 裡有 C($c-trend-up) 的 class
                # 表示狀態為上漲
                if soup.select('#main-0-QuoteHeader-Proxy')[0].select('.C\\(\\$c-trend-up\\)')[0]:
                    s = '+'
            except:
                # 如果都沒有包含，表示平盤
                s = ''
            '''
        mod_text = float(s + c[1:-2])
        buy=''

        if mod_text <= -3.0:
            buy = '>>>趕快加碼20股喔'
        elif mod_text <= -2.0:
            buy = '>>>加碼10股吧'
        elif mod_text <= -1.0:
            buy = '>>>加碼5股'
        else:
            buy = '<<<繼續觀望'
        msg = f'{title} : {a} ( {s}{b} ) {mod_text}%\n{buy}'
    except Exception as e:
        msg = f'發生錯誤: {str(e)}'
    return msg

lineToken = 'GMCJTP8H4zALBrLwqfuji5xmiJynmJhYcLz5XUVMahE'
def sendToLine(lineToken):
  url = "https://notify-api.line.me/api/notify"
  message = stock()
  payload={'message':message}

  headers = {'Authorization': 'Bearer ' + lineToken}
  response = requests.post(url, headers=headers, data=payload)
  print(response.text)
#sendToLine(lineToken)

#schedule.every(20).seconds.do(sendToLine,lineToken) # 20秒跑一次

for hour in range(1,6):
    schedule.every().day.at(f"{hour:02d}:10").do(sendToLine, lineToken)
    schedule.every().day.at(f"{hour:02d}:11").do(sendToLine, lineToken)

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

@app.route('/')
def home():
    return "Stock Notification Service is running."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    schedule_thread = threading.Thread(target=run_schedule)
    schedule_thread.start()
    app.run(host='0.0.0.0', port=port)

#if __name__ == "__main__":
    #port = int(os.environ.get("PORT", 5000))
    #app.run(host='0.0.0.0', port=port)
