from cupas import Coupang
from naver import Naver
from settings import Settings
import pandas as pd
from db.connector import Connector
from naver_kin_fetcher import NaverKinFetcher
import random
import sys
from datetime import timedelta, datetime
import time



if __name__ == '__main__':
    setting = Settings()
    
    connector = Connector(setting.db_host, setting.db_id, setting.db_passwd, setting.db_name)
    if sys.argv[1] == 'search':
        c = Coupang(setting.coupang_id, setting.coupang_passwd, connector)
        df = pd.read_csv('data/keyword.csv')
        keyword_list = df.iloc[:, 0].tolist()
        for keyword in keyword_list:
            c.search(keyword)
    elif sys.argv[1] == 'gen_link':
        c = Coupang(setting.coupang_id, setting.coupang_passwd, connector)
        while True:
            c.login()
            done = c.gen_link(0)
            if done:
                break
            else:
                time.sleep(5)
                c = Coupang(setting.coupang_id, setting.coupang_passwd, connector)
                continue

    elif sys.argv[1] == 'post':
        acc_cnt = {}
        while True:
            account = random.choice(setting.naver_accounts)
            id = account['id']
            passwd = account['passwd']
            if id not in acc_cnt:
                acc_cnt[id] = 0
            n = Naver(id, passwd, connector, headless=False)
            n.login()
            done = n.write_post(0)
            acc_cnt[id] += 1
            time.sleep(60)

    elif sys.argv[1] == 'wiki':
        acc_cnt = {}
        while True:
            account = random.choice(setting.naver_accounts)
            id = account['id']
            passwd = account['passwd']
            if id not in acc_cnt:
                acc_cnt[id] = 0
            n = Naver(id, passwd, connector)
            n.login()
            done = n.write_info(0)
            acc_cnt[id] += 1
            time.sleep(60)

    elif sys.argv[1] == 'neighbor':
        acc_cnt = {}
        for i in range(6,20):
            account = random.choice(setting.naver_accounts)
            id = account['id']
            passwd = account['passwd']
            if id not in acc_cnt:
                acc_cnt[id] = 0
            n = Naver(id, passwd, connector, headless=False)
            n.login()
            done = n.neighbor(page_seq=i)
            acc_cnt[id] += 1
            time.sleep(20)
            
    elif sys.argv[1] == 'kin_fetch':
        nkf = NaverKinFetcher(connector)
        keyword_list = ["한우 선물", "한우 추천", "한우 업체", "한우 주문", "고급 한우", "프리미엄 한우", 
    "명절 선물", "설날 선물", "추석 선물", "어버이날 선물", "구정 선물", 
    "한우 세트", "선물 세트", "선물 추천", "고기 추천", "고기 선물", "어머니 선물", "엄마 선물", "아버지 선물", "아빠 선물", "부모님 선물", "생신 선물"]
        for keyword in keyword_list:
            #start_date = "2024.01.01"
            start_date = (datetime.now() - timedelta(days=1)).strftime("%Y.%m.%d")
            end_date = datetime.now().strftime("%Y.%m.%d")
            for page_num in range(1, 200):
                results = nkf.fetch_naver_kin(keyword, start_date, end_date, page_num)
                if not results:
                    break
                time.sleep(0.3)
                
