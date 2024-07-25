import random
from selenium.webdriver.common.action_chains import ActionChains
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import random
import clipboard
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import re

def keyboard_text_input(driver, text):
    for char in text:
        ActionChains(driver).send_keys(char).perform()
        time.sleep(random.randint(1,5)/100)

def keyboard_text_input_clipboard(driver, text):
    clipboard.copy(text)
    ActionChains(driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()

def perform_return(driver, num):
    for i in range(num):
        ActionChains(driver).send_keys(Keys.RETURN).perform()

def filter_hashtag(text):
    # 영어, 한국어, 숫자, #을 제외한 나머지 문자를 제거하는 정규식 패턴
    text = text.replace('\n','').replace(' ','')
    pattern = r'[^a-zA-Z0-9가-힣#\s]'
    # 정규식 패턴에 해당하는 문자를 빈 문자열로 치환
    cleaned_text = re.sub(pattern, '', text)
    cleaned_text = cleaned_text.replace('#', ' #')
    return cleaned_text

def wait_and_click(driver, path, by=By.XPATH):
    try:
        prods = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((by, path))
        )

        if not prods:
            print("No elements found with class name 'search-product'")
        else:
            driver.find_element(by,path).click()
            print(f"{path} clicked!@@@@@@@@@@@@@@@")
    except TimeoutException:
        print("Timeout: No elements found within the specified time.")
    except Exception as e:
        print(f"An error occurred: {e}")

