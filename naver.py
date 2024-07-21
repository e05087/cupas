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
from db.post_log import PostLog
from utils import *
import pyperclip
import os
from urllib.request import urlretrieve
import pandas as pd  # pandas 라이브러리는 pip를 통해 설치 필요
import subprocess

import platform
import pyshorteners

if platform.system() == "Windows":
    CREATE_NO_WINDOW = 0x08000000  # For suppressing command prompt window on Windows



class Naver:
    def __init__(self, id, pw, connector):
        self.id = id
        self.pw = pw
        self.driver = self.get_chromedriver()
        self.connection = connector.get_connection()
        self.connector = connector

    def get_chromedriver(self) -> webdriver.Chrome:
        chrome_options = Options()
        chrome_options.add_experimental_option("detach", True)

        # 불필요한 에러 메시지 없애기
        chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
        service = Service(executable_path=ChromeDriverManager().install())
        service.creation_flags = CREATE_NO_WINDOW
        driver = webdriver.Chrome(options=chrome_options, service=service)
        
        driver.implicitly_wait(30)
        driver.maximize_window()
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": """ Object.defineProperty(navigator, 'webdriver', { get: () => undefined }) """})
    
        return driver

    def login(self):
        self.driver.delete_all_cookies()
        self.driver.get('https://nid.naver.com/nidlogin.login?mode=form&url=https://www.naver.com/')
        time.sleep(2)

        checkbox = self.driver.find_element(By.ID, 'keep')
        
        keep = checkbox.get_attribute('value')
        if keep == "off":
            print("@@@@@@@@@@@@@@@@")
            self.driver.find_element(By.XPATH, '//*[@id="login_keep_wrap"]/div[1]/label').click()

        time.sleep(2)
        self.driver.find_element(By.XPATH, '//*[@id="id"]').click()
        time.sleep(2)
        

        keyboard_text_input_clipboard(self.driver, self.id)
        time.sleep(1)
        ActionChains(self.driver).send_keys(Keys.TAB).perform()
        time.sleep(1)
        keyboard_text_input_clipboard(self.driver, self.pw)

        time.sleep(2)
        self.driver.find_element(By.XPATH,'//*[@id="log.login"]').click()
        time.sleep(3)
        self.driver.get('https://blog.naver.com/MyBlog.naver')
        time.sleep(2)
            
    def write_post(self, user_id, category_id=1, source = 'coupang'):
        blog_name = self.driver.current_url.split('blog.naver.com/')[-1]
        blog_url = self.driver.current_url
        shortener = pyshorteners.Shortener()
        include_url = 'link.coupang.com'  # SQL 쿼리에서는 백슬래시 없이 사용할 수 있습니다.

        # 올바르게 이스케이프된 쿼리 문자열
        raw_query = f"""
        SELECT c.id, p.id as post_id, p.title, p.body, p.hashtag, l.link, c.keyword, c.img_link
        FROM content c
        JOIN post p ON p.content_id=c.id
        JOIN link l ON l.content_id=c.id
        WHERE c.source='{source}' AND p.id NOT IN (
            SELECT post_id FROM post_log WHERE user_id={user_id}
        )
        """

        data = pd.read_sql_query(raw_query, self.connector.get_engine())
        data = data.sample(frac=1).reset_index(drop=True)

        for idx, row in data.iterrows():
            self.driver.get(f'{blog_url}?Redirect=Write&categoryNo={category_id}')
            content_id = row['id']
            img_link = row['img_link']
            link = row['link']
            if include_url not in link:
                continue
            current_file_path = os.getcwd()
            local_img_path = f"{current_file_path}/data/img/{content_id}.png"
            urlretrieve(img_link, local_img_path)
            #print(row)
            time.sleep(2)

            # iframe으로 전환
            iframe = WebDriverWait(self.driver, 5).until(
                EC.frame_to_be_available_and_switch_to_it((By.ID, 'mainFrame'))  # iframe 선택자 변경 필요
            )

            #self.driver.switch_to.frame('mainFrame')
            wait_and_click(self.driver, 'se-popup-button-cancel', by=By.CLASS_NAME)

            
            
            title = row['title'].replace('"', '')
            body = row['body']
            hashtag = filter_hashtag(row['hashtag'])

            #ActionChains(self.driver).send_keys(Keys.ARROW_UP).perform()
            wait_and_click(self.driver, 'se-documentTitle', by=By.CLASS_NAME)
            time.sleep(1)
            keyboard_text_input_clipboard(self.driver, title)
            wait_and_click(self.driver, 'se-text', by=By.CLASS_NAME)
            wait_and_click(self.driver, 'se-image-toolbar-button', by=By.CLASS_NAME)
            time.sleep(3)
            img_input = self.driver.find_element(By.XPATH, '//*[@id="hidden-file"]')
            img_input.send_keys(local_img_path)
            
            
            #keyboard_text_input_clipboard(self.driver, local_img_path)
            time.sleep(3)
            #ActionChains(self.driver).key_down(Keys.ALT).send_keys('o').key_up(Keys.ALT).perform()
            #time.sleep(5)
            wait_and_click(self.driver, 'se-text', by=By.CLASS_NAME)
            time.sleep(1)
            perform_return(self.driver, 1)
            #ActionChains(self.driver).send_keys(Keys.ARROW_DOWN).perform()
            keyboard_text_input_clipboard(self.driver, body)
            perform_return(self.driver, 3)
            time.sleep(3)
            short_link = shortener.tinyurl.short(link)
            keyboard_text_input_clipboard(self.driver, short_link)
            time.sleep(8)
            perform_return(self.driver, 2)
            keyboard_text_input(self.driver, "위 링크에서 해당 제품과 관련 제품에 대한 더 자세한 정보를 얻을 수 있습니다!")
            perform_return(self.driver, 1)
            keyboard_text_input(self.driver, "이 포스팅은 쿠팡파트너스 활동으로, 일정액의 수수료를 제공받을 수 있습니다.")

            perform_return(self.driver, 2)
            keyboard_text_input(self.driver, hashtag)
            time.sleep(2)
            wait_and_click(self.driver, 'se-help-panel-close-button', by=By.CLASS_NAME)
            wait_and_click(self.driver, 'publish_btn__m9KHH', by=By.CLASS_NAME)
            wait_and_click(self.driver, 'confirm_btn__WEaBq', by=By.CLASS_NAME)
            row['user_id'] = user_id
            row_df = pd.DataFrame([row])

            row_df[['post_id', 'user_id']].to_sql(name=PostLog.__tablename__, con=self.connection, if_exists='append', index=False)
            
            time.sleep(10)
