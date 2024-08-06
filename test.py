import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
from db.connector import Connector
from settings import Settings
def fetch_naver_kin(query_keyword, start_date, end_date, page_num):
    base_url = "https://kin.naver.com/search/list.nhn"
    params = {
        'sort': 'date',
        'query': query_keyword,
        'period': f'{start_date}|{end_date}',
        'section': 'kin',
        'page': page_num
    }

    response = requests.get(base_url, params=params)
    response.raise_for_status()  # 요청이 성공했는지 확인

    soup = BeautifulSoup(response.text, 'html.parser')
    ul_list = soup.find_all('ul', class_='basic1')

    results = []

    for ul in ul_list:
        li_list = ul.find_all('li')
        for li in li_list:
            title_anchor = li.find('a', class_='_searchListTitleAnchor')
            href = title_anchor['href']
            
            # href URL에서 dirId와 docId만 추출
            dirId = None
            docId = None
            if 'dirId=' in href and 'docId=' in href:
                href_parts = href.split('&')
                for part in href_parts:
                    if part.startswith('dirId='):
                        dirId = part.split('=')[1]
                    if part.startswith('docId='):
                        docId = part.split('=')[1]
            
            # 새로운 href 형식으로 변환
            if dirId and docId:
                href = f"https://kin.naver.com/qna/detail.naver?dirId={dirId}&docId={docId}"

            title_text = title_anchor.get_text(strip=True)

            txt_inline = li.find('dd', class_='txt_inline')
            txt_inline_text = txt_inline.get_text(strip=True) if txt_inline else ""

            # txt_inline_text를 datetime 형식으로 변환
            try:
                content_created_dt = datetime.strptime(txt_inline_text, '%Y.%m.%d.')
            except ValueError:
                content_created_dt = None

            results.append({
                'link': href,
                'title': title_text,
                'content_created_dt': content_created_dt
            })

    return results

# 예시 사용법
query_keyword = "한우"
start_date = "2024.01.01"
end_date = "2024.08.06"
page_num = 2

results = fetch_naver_kin(query_keyword, start_date, end_date, page_num)

# DataFrame으로 변환
df = pd.DataFrame(results)

# 추가 컬럼 설정
df['source'] = 'kin'
df['keyword'] = query_keyword
df['created_by_us'] = 0
setting = Settings()
# 컬럼 순서 재배치
df = df[['source', 'link', 'title', 'keyword', 'created_by_us', 'content_created_dt']]

connector = Connector(setting.db_host, setting.db_id, setting.db_passwd, setting.db_name)

# DataFrame을 to_sql을 사용하여 데이터베이스에 삽입
df.to_sql('qna', con=connector.get_connection(), if_exists='append', index=False)

print("Data inserted into the database successfully.")