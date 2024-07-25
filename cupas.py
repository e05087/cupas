# -*- coding: utf-8 -*-
import time
import clipboard  # clipboard 라이브러리는 pip를 통해 설치 필요
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from db.content import Content
from db.link import Link
import pyperclip

import pandas as pd  # pandas 라이브러리는 pip를 통해 설치 필요
import subprocess
import platform
from urllib.request import urlretrieve

if platform.system() == "Windows":
    CREATE_NO_WINDOW = 0x08000000  # For suppressing command prompt window on Windows



class Coupang:

    def __init__(self, id, pw, connector, max_page_num=10):
        self.id = id
        self.pw = pw
        self.driver = self.get_chromedriver()
        self.connection = connector.get_connection()
        self.connector = connector
        self.page_num = max_page_num

    def get_chromedriver(self) -> webdriver.Chrome:
        chrome_options = Options()
        chrome_options.add_experimental_option("detach", True)

        # 불필요한 에러 메시지 없애기
        chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
        #service = Service(executable_path=ChromeDriverManager().install())
        service = Service()
        service.creation_flags = CREATE_NO_WINDOW
        driver = webdriver.Chrome(options=chrome_options, service=service)
        
        driver.implicitly_wait(30)
        driver.maximize_window()
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": """ Object.defineProperty(navigator, 'webdriver', { get: () => undefined }) """})
    
        return driver

    def login(self): 
            self.driver.get('https://partners.coupang.com/')
            time.sleep(2)
            self.driver.find_element(By.XPATH, '//*[@id="app-header"]/div[2]/div/button[1]').click()
            time.sleep(2)
            self.driver.find_element(By.XPATH,'//*[@id="login-email-input"]').click()
            clipboard.copy(self.id)
            ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()

            self.driver.find_element(By.XPATH,'//*[@id="login-password-input"]').click()
            clipboard.copy(self.pw)
            ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
            time.sleep(5)
            self.driver.find_element(By.CLASS_NAME,'login__button').click()

            time.sleep(3)


    def gen_link(self, user_id, db_batch_size=3):
        self.driver.get('https://partners.coupang.com/#affiliate/ws/link-to-any-page')
        time.sleep(2)
        raw_query = f"SELECT * FROM content c where c.source = 'coupang' and c.id not in (select content_id from link where user_id={user_id})"
        data = pd.read_sql_query(raw_query, self.connector.get_engine())
        results = []
        for idx, row in data.iterrows():
            try:
                content_id = row['id']
                link = row['link']
                clipboard.copy(link)
                self.driver.find_element(By.XPATH,'//*[@id="url"]').click()
                time.sleep(0.2)
                ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).send_keys(Keys.DELETE).perform()
                time.sleep(0.2)
                ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
                time.sleep(0.2)
                self.driver.find_element(By.XPATH,'//*[@id="root"]/div/div/div[2]/div/div/div[1]/div/div/div[2]/div/div/div[2]/div/div/div/div[1]/div[2]/form/div/div/div/span/span/span/button').click()
                time.sleep(1)
                self.driver.find_element(By.XPATH,'//*[@id="root"]/div/div/div[2]/div/div/div[1]/div/div/div[2]/div/div/div[2]/div/div/div/div[2]/div[1]/div[2]/button').click()
                gen_link = pyperclip.paste()
                gen_link = gen_link.strip()
                time.sleep(3)

                results.append({'content_id': content_id, 'link': gen_link, 'user_id': user_id})
                if (idx + 1) % db_batch_size == 0:
                    df_results = pd.DataFrame(results)
                    df_results.to_sql(name=Link.__tablename__, con=self.connection, \
                        if_exists='append',index=False)
                    results = []  # 리스트 초기화
            except Exception as E:
                print(E)
                self.driver.quit()
                return False
        if results:
            df_results = pd.DataFrame(results)
            df_results.to_sql(name=Link.__tablename__, con=self.connection, \
                if_exists='append',index=False)
        return True


            
        

    def search(self, query):
        query = query.replace(" ", "+")
        
        df = pd.DataFrame(columns=['title', 'price', 'link', 'img_link', 'source', 'keyword', 'rank'])
        keyword_idx = 1
        for page in range(1, self.page_num + 1):
            print(page)
            self.driver.get(f'https://www.coupang.com/np/search?q={query}&channel=user&component=&eventCategory=SRP&trcid=&traid=&sorter=scoreDesc&minPrice=&maxPrice=&priceRange=&filterType=&listSize=36&filter=&isPriceRange=false&brand=&offerCondition=&rating=0&page={page}&rocketAll=false&searchIndexingToken=1=9&backgroundColor=')
            
            try:
                # 특정 요소가 나타날 때까지 최대 10초 기다리기
                prods = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, 'search-product'))
                )

                # 요소 출력
                if not prods:
                    print("No elements found with class name 'search-product'")
                    break
                else:
                    print(f"Found {len(prods)} elements with class name 'search-product'")
            except TimeoutException:
                print("Timeout: No elements found within the specified time.")
                break
            except Exception as e:
                print(f"An error occurred: {e}")
                break

            for idx, prod in enumerate(prods):
                
                try:
                    if prod.find_element(By.CLASS_NAME, "name").text in list(df['title']):
                        continue
                    if prod.find_element(By.CLASS_NAME, "name").text == '':
                        continue

                    img = prod.find_element(By.CLASS_NAME, "search-product-wrap-img").get_attribute('src')
                    name = prod.find_element(By.CLASS_NAME, "name").text
                    price = float(prod.find_element(By.CLASS_NAME, "price-value").text.replace(',',''))
                    link = prod.find_element(By.CLASS_NAME, "search-product-link").get_attribute('href')

                    new_row = pd.DataFrame([[name, price, link, img, 'coupang', query, keyword_idx]], columns=df.columns)
                    keyword_idx += 1
                    df = pd.concat([df, new_row], ignore_index=True)
                except Exception as e:
                    print(e)
                    continue
            self.driver.delete_all_cookies()
        df.to_sql(name=Content.__tablename__, con=self.connection, \
            if_exists='append',index=False,chunksize=200)
        '''
        img_local_path_list = []

        for index, link in enumerate(df['img_link']):
            local_path = f'{self.img_path}{index}.jpg'
            img_local_path_list.append(local_path)
            urlretrieve(link, local_path)'''

        # df = pd.DataFrame(columns=['상품명', '판매가격', '상품상세링크', '이미지원본링크', '이미지로컬링크'])
