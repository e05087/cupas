from cupas import Coupang
from naver import Naver
from settings import Settings
import pandas as pd
from db.connector import Connector
import random
import sys
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
                
