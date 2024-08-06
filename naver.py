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
from bs4 import BeautifulSoup
from db.info_log import InfoLog
from db.neighbor import Neighbor
import requests
from utils import *
import pyperclip
import os
from urllib.request import urlretrieve
import pandas as pd  # pandas 라이브러리는 pip를 통해 설치 필요
import subprocess
import random
import platform
import pyshorteners

if platform.system() == "Windows":
    CREATE_NO_WINDOW = 0x08000000  # For suppressing command prompt window on Windows



class Naver:
    def __init__(self, id, pw, connector, headless=False):
        self.id = id
        self.pw = pw
        
        self.driver = self.get_chromedriver(headless=headless)
        self.connection = connector.get_connection()
        self.connector = connector

    def get_chromedriver(self, headless=False) -> webdriver.Chrome:
        chrome_options = Options()
        chrome_options.add_experimental_option("detach", True)
        if headless:
            chrome_options.add_argument("--headless")

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
    
    def neighbor(self, page_seq=0):
        df = pd.read_csv('data/neighbor_msg.csv', header=None)
        msg_list = df[0].tolist()
        try:
            url = f"https://section.blog.naver.com/ThemePost.naver?directoryNo=0&activeDirectorySeq=0&currentPage={page_seq}"
            self.driver.get(url)
            author_elements = self.driver.find_elements(By.CLASS_NAME, 'author')
            links = []
            for elem in author_elements:
                links.append(elem.get_attribute('href'))
            print(links)

            for link in links:
                try:
                    #wait_and_click(self.driver, By.CLASS_NAME, '_addBuddyPop')
                    self.driver.get(link)

                    time.sleep(3)
                    iframe = WebDriverWait(self.driver, 5).until(
                        EC.frame_to_be_available_and_switch_to_it((By.ID, 'mainFrame'))  # iframe 선택자 변경 필요
                    )

                    print("iframe success")
                    wait_and_click(self.driver, '_addBuddyPop', by=By.CLASS_NAME)
                    time.sleep(3)
                    # 모든 창 핸들을 가져옴
                    main_window_handle = self.driver.current_window_handle
                    window_handles = self.driver.window_handles

                    print(main_window_handle)
                    print(window_handles)
                    # 팝업 창 핸들을 찾아 전환
                    for handle in window_handles:
                        if handle != main_window_handle:
                            popup_window_handle = handle
                            self.driver.switch_to.window(popup_window_handle)
                            break
                    
                    wait_and_click(self.driver, 'radio_bothbuddy', by=By.CLASS_NAME)
                    time.sleep(1)
                    element = self.driver.find_element(By.CLASS_NAME, 'radio_bothbuddy')
                    class_attribute = element.get_attribute('class')
                    # checked 클래스가 있는지 확인
                    if 'checked' in class_attribute.split():
                        pass
                    else:
                        self.driver.switch_to.window(main_window_handle)
                        print(f"Element does not have 'checked' class.")
                        continue
                    time.sleep(0.5)
                    wait_and_click(self.driver, '_buddyAddNext', by=By.CLASS_NAME)
                    time.sleep(0.5)
                    wait_and_click(self.driver, 'message_box', by=By.CLASS_NAME)
                    time.sleep(0.5)
                    keyboard_text_input(self.driver, random.choice(msg_list))
                    wait_and_click(self.driver, '_addBothBuddy', by=By.CLASS_NAME)
                    time.sleep(0.5)
                    self.driver.switch_to.window(main_window_handle)
                    #self.driver.close()
                    time.sleep(5)
                except Exception as E:
                    print(E)
                    self.driver.switch_to.window(main_window_handle)
                    continue

        except Exception as E:
            print(E)
            self.driver.quit()
            return
        self.driver.quit()
                  

        

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
        WHERE  p.target='naver_blog' and c.source='{source}' AND p.id NOT IN (
            SELECT post_id FROM post_log WHERE user_id={user_id}
        ) limit 5
        """

        data = pd.read_sql_query(raw_query, self.connector.get_engine())
        data = data.sample(frac=1).reset_index(drop=True)

        for idx, row in data.iterrows():
            try:
                self.driver.get(f'{blog_url}?Redirect=Write&categoryNo={category_id}')
                print(1)
                content_id = row['id']
                img_link = row['img_link']
                link = row['link']
                if include_url not in link:
                    continue
                current_file_path = os.getcwd()
                local_img_path = f"{current_file_path}/data/img/{content_id}.png"
                urlretrieve(img_link, local_img_path)
                print(2)
                #print(row)
                time.sleep(8)
                file_size = os.path.getsize(local_img_path)
                file_size_mb = file_size / (1024 * 1024)
                if file_size_mb > 25:
                    continue
                print(3)
                # iframe으로 전환
                iframe = WebDriverWait(self.driver, 5).until(
                    EC.frame_to_be_available_and_switch_to_it((By.ID, 'mainFrame'))  # iframe 선택자 변경 필요
                )
                #self.driver.switch_to.frame('mainFrame')
                wait_and_click(self.driver, 'se-popup-button-cancel', by=By.CLASS_NAME)

                
                
                title = row['title'].replace('"', '')
                body = row['body']
                #hashtag = filter_hashtag(row['hashtag'])


                wait_and_click(self.driver, 'se-popup-dim', by=By.CLASS_NAME)
                wait_and_click(self.driver, 'se-text', by=By.CLASS_NAME)
                ActionChains(self.driver).send_keys(Keys.ARROW_UP).perform()
                #wait_and_click(self.driver, 'se-documentTitle', by=By.CLASS_NAME)
                #time.sleep(5)
                keyboard_text_input(self.driver, title)
                time.sleep(1)
                #wait_and_click(self.driver, 'se-text', by=By.CLASS_NAME)
                ActionChains(self.driver).send_keys(Keys.ARROW_DOWN).perform()
                wait_and_click(self.driver, 'se-image-toolbar-button', by=By.CLASS_NAME)
                time.sleep(5)
                img_input = self.driver.find_element(By.XPATH, '//*[@id="hidden-file"]')
                img_input.send_keys(local_img_path)
                
                
                #keyboard_text_input_clipboard(self.driver, local_img_path)
                time.sleep(5)
                #ActionChains(self.driver).key_down(Keys.ALT).send_keys('o').key_up(Keys.ALT).perform()
                #time.sleep(5)
                wait_and_click(self.driver, 'se-insert-quotation-default-toolbar-button', by=By.CLASS_NAME)
                time.sleep(3)
                keyboard_text_input(self.driver, title)
                ActionChains(self.driver).send_keys(Keys.ARROW_DOWN).perform()
                ActionChains(self.driver).send_keys(Keys.ARROW_DOWN).perform()
                perform_return(self.driver, 2)
                wait_and_click(self.driver, 'se-toolbar-item-font-family', by=By.CLASS_NAME)
                time.sleep(2)
                wait_and_click(self.driver, 'se-toolbar-option-font-family-nanumbareunhipi-button', by=By.CLASS_NAME)
                
                time.sleep(2)
                perform_return(self.driver, 1)
                lines = body.split('\n')
                for idx, line in enumerate(lines):
                    if idx == 0:
                        continue
                    line = line.strip()
                    #if len(line) == 0:
                    #    perform_return(self.driver, 1)
                    if len(line) > 1 and line[0:2] == '##':
                        line = line.split('##')[-1].strip()
                        wait_and_click(self.driver, 'se-toolbar-item-font-size-code', by=By.CLASS_NAME)
                        time.sleep(1)
                        wait_and_click(self.driver, 'se-toolbar-option-font-size-code-fs19-button', by=By.CLASS_NAME)
                        time.sleep(1)
                        perform_return(self.driver, 1)
                    else:
                        wait_and_click(self.driver, 'se-toolbar-item-font-size-code', by=By.CLASS_NAME)
                        time.sleep(1)
                        wait_and_click(self.driver, 'se-toolbar-option-font-size-code-fs15-button', by=By.CLASS_NAME)
                        time.sleep(1)
                    
                    keyboard_text_input(self.driver, line)
                    perform_return(self.driver, 1)
                perform_return(self.driver, 3)
                short_link = shortener.tinyurl.short(link)
                if len(short_link) < 10:
                    short_link = link
                time.sleep(2)
                keyboard_text_input(self.driver, short_link)
                perform_return(self.driver, 2)
                time.sleep(15)
                keyboard_text_input(self.driver, "위 링크에서 해당 제품과 관련 제품에 대한 더 자세한 정보를 얻을 수 있습니다!")
                perform_return(self.driver, 1)
                keyboard_text_input(self.driver, "이 포스팅은 쿠팡파트너스 활동으로, 일정액의 수수료를 제공받을 수 있습니다.")

                perform_return(self.driver, 2)
                #keyboard_text_input(self.driver, hashtag)
                time.sleep(3)
                wait_and_click(self.driver, 'se-help-panel-close-button', by=By.CLASS_NAME)
                wait_and_click(self.driver, 'publish_btn__m9KHH', by=By.CLASS_NAME)
                wait_and_click(self.driver, 'confirm_btn__WEaBq', by=By.CLASS_NAME)
                row['user_id'] = user_id
                row_df = pd.DataFrame([row])

                row_df[['post_id', 'user_id']].to_sql(name=PostLog.__tablename__, con=self.connection, if_exists='append', index=False)
                
                time.sleep(30)

            except Exception as E:
                print(E)
                self.driver.quit()
                return False
        self.driver.quit()
        return True
    
    def write_info(self, user_id, category_id=6):
        blog_name = self.driver.current_url.split('blog.naver.com/')[-1]
        blog_url = self.driver.current_url
        # 올바르게 이스케이프된 쿼리 문자열
        raw_query = f"""
        SELECT i.id, i.title, i.body, w.img_link
        FROM info i
        JOIN wiki w ON w.id = i.wiki_id
        WHERE  i.target='naver_blog' AND i.id NOT IN (
            SELECT info_id FROM info_log WHERE user_id={user_id}
        ) limit 5
        """

        data = pd.read_sql_query(raw_query, self.connector.get_engine())

        for idx, row in data.iterrows():
            try:
                self.driver.get(f'{blog_url}?Redirect=Write&categoryNo={category_id}')
                info_id = row['id']
                img_link = row['img_link']
                current_file_path = os.getcwd()
                local_img_path = f"{current_file_path}/data/img/{info_id}.png"
                try:
                    urlretrieve(img_link, local_img_path)
                    row['user_id'] = user_id
                    row['info_id'] = info_id
                    row_df = pd.DataFrame([row])
                    row_df[['info_id', 'user_id']].to_sql(name=InfoLog.__tablename__, con=self.connection, if_exists='append', index=False)
                except:
                    continue
                #print(row)
                time.sleep(8)
                file_size = os.path.getsize(local_img_path)
                file_size_mb = file_size / (1024 * 1024)
                if file_size_mb > 25:
                    continue

                # iframe으로 전환
                iframe = WebDriverWait(self.driver, 5).until(
                    EC.frame_to_be_available_and_switch_to_it((By.ID, 'mainFrame'))  # iframe 선택자 변경 필요
                )

                #self.driver.switch_to.frame('mainFrame')
                wait_and_click(self.driver, 'se-popup-button-cancel', by=By.CLASS_NAME)

                
                
                title = row['title'].replace('"', '')
                body = row['body']
                #hashtag = filter_hashtag(row['hashtag'])


                wait_and_click(self.driver, 'se-popup-dim', by=By.CLASS_NAME)
                ActionChains(self.driver).send_keys(Keys.ARROW_UP).perform()
                #wait_and_click(self.driver, 'se-documentTitle', by=By.CLASS_NAME)
                #time.sleep(5)
                keyboard_text_input(self.driver, title)
                time.sleep(1)
                #wait_and_click(self.driver, 'se-text', by=By.CLASS_NAME)
                ActionChains(self.driver).send_keys(Keys.ARROW_DOWN).perform()
                wait_and_click(self.driver, 'se-image-toolbar-button', by=By.CLASS_NAME)
                time.sleep(5)
                img_input = self.driver.find_element(By.XPATH, '//*[@id="hidden-file"]')
                img_input.send_keys(local_img_path)
                
                
                #keyboard_text_input_clipboard(self.driver, local_img_path)
                time.sleep(5)
                #ActionChains(self.driver).key_down(Keys.ALT).send_keys('o').key_up(Keys.ALT).perform()
                #time.sleep(5)
                wait_and_click(self.driver, 'se-insert-quotation-default-toolbar-button', by=By.CLASS_NAME)
                time.sleep(3)
                keyboard_text_input(self.driver, title)
                ActionChains(self.driver).send_keys(Keys.ARROW_DOWN).perform()
                ActionChains(self.driver).send_keys(Keys.ARROW_DOWN).perform()
                perform_return(self.driver, 2)
                wait_and_click(self.driver, 'se-toolbar-item-font-family', by=By.CLASS_NAME)
                time.sleep(2)
                wait_and_click(self.driver, 'se-toolbar-option-font-family-nanummaruburi-button', by=By.CLASS_NAME)
                
                time.sleep(2)
                perform_return(self.driver, 1)
                lines = body.split('\n')
                for idx, line in enumerate(lines):
                    if idx == 0:
                        continue
                    line = line.strip()
                    #if len(line) == 0:
                    #    perform_return(self.driver, 1)
                    if len(line) > 1 and line[0:2] == '##':
                        line = line.split('##')[-1].strip()
                        wait_and_click(self.driver, 'se-toolbar-item-font-size-code', by=By.CLASS_NAME)
                        time.sleep(1)
                        wait_and_click(self.driver, 'se-toolbar-option-font-size-code-fs19-button', by=By.CLASS_NAME)
                        time.sleep(1)
                        perform_return(self.driver, 1)
                    else:
                        wait_and_click(self.driver, 'se-toolbar-item-font-size-code', by=By.CLASS_NAME)
                        time.sleep(1)
                        wait_and_click(self.driver, 'se-toolbar-option-font-size-code-fs15-button', by=By.CLASS_NAME)
                        time.sleep(1)
                    
                    keyboard_text_input(self.driver, line)
                    perform_return(self.driver, 1)
                perform_return(self.driver, 3)

                time.sleep(2)
                wait_and_click(self.driver, 'se-help-panel-close-button', by=By.CLASS_NAME)
                wait_and_click(self.driver, 'publish_btn__m9KHH', by=By.CLASS_NAME)
                wait_and_click(self.driver, 'confirm_btn__WEaBq', by=By.CLASS_NAME)
                row['user_id'] = user_id
                row['info_id'] = info_id
                row_df = pd.DataFrame([row])
                
                row_df[['info_id', 'user_id']].to_sql(name=InfoLog.__tablename__, con=self.connection, if_exists='append', index=False)
                
                time.sleep(30)

            except Exception as E:
                print(E)
                self.driver.quit()
                return False
        self.driver.quit()
        return True
