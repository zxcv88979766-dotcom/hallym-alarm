import requests
from bs4 import BeautifulSoup
import telegram
import asyncio
import os

# 깃허브 금고(Secrets)에서 꺼내오기
bot_token = os.environ['BOT_TOKEN']
chat_id = os.environ['CHAT_ID']

async def check_new_post():
    # 한림대 공지 URL
    url = "https://www.hallym.ac.kr/hallym/1135/subview.do?enc=Zm5jdDF8QEB8JTJGYmJzJTJGaGFsbHltJTJGMTU2JTJGYXJ0Y2xMaXN0LmRvJTNGcGFnZSUzRDElMjZmaW5kVHlwZSUzRCUyNmZpbmRXb3JkJTNEJTI2ZmluZENsU2VxJTNEJTI2ZmluZE9wbndyZCUzRCUyNnJnc0JnbmRlU3RyJTNEJTI2cmdzRW5kZGVTdHIlM0QlMjY%3D"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    # 1. 이전 기록 읽어오기 (없으면 빈칸)
    try:
        with open("latest.txt", "r") as f:
            last_title = f.read().strip()
    except FileNotFoundError:
        last_title = ""

    # 2. 웹사이트 크롤링
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        rows = soup.select("tbody tr")
        found_title = ""
        found_link = ""

        # 공지 건너뛰고 최신글 찾기
        for row in rows:
            cols = row.select("td")
            if not cols: continue
            if cols[0].text.strip().isdigit(): # 번호가 숫자면 진짜 글
                link_tag = row.select_one("a")
                found_title = link_tag.text.strip()
                if link_tag['href'].startswith("http"):
                    found_link = link_tag['href']
                else:
                    found_link = "https://www.hallym.ac.kr" + link_tag['href']
                break
        
        # 3. 비교 및 발송
        if found_title and (found_title != last_title):
            print(f"새 글 발견! {found_title}")
            bot = telegram.Bot(token=bot_token)
            await bot.send_message(chat_id=chat_id, text=f"[한림대 새 장학공지]\n{found_title}\n{found_link}")
            
            # 4. 파일에 기록하기
            with open("latest.txt", "w") as f:
                f.write(found_title)
        else:
            print("새로운 공지가 없습니다.")

    except Exception as e:
        print(f"에러 발생: {e}")

# 실행
if __name__ == "__main__":
    asyncio.run(check_new_post())
