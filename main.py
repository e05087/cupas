from cupas import Coupang
from naver import Naver
from settings import Settings
import pandas as pd
from db.connector import Connector
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
                time.sleep(100)
                c = Coupang(setting.coupang_id, setting.coupang_passwd, connector)
                continue

    elif sys.argv[1] == 'post':
        n = Naver(setting.naver_id, setting.naver_passwd, connector)
        n.login()
        n.write_post(0)

