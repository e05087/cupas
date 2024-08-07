import random
from selenium.webdriver.common.action_chains import ActionChains
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import random
from bs4 import BeautifulSoup
import clipboard
from settings import Settings
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import re
from openai import OpenAI
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

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
            print(f"No elements found with {path}")
        else:
            driver.find_element(by,path).click()
            print(f"{path} clicked!@@@@@@@@@@@@@@@")
    except TimeoutException:
        print("Timeout: No elements found within the specified time.")
    except Exception as e:
        print(f"An error occurred: {e}")

def get_text_from_class(driver, path, by=By.CLASS_NAME):
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((by, path))
        )
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        element = soup.find('div', class_=path)
        return element.get_text(strip=True) if element else None
    except Exception as e:
        print(f"Error getting text from class {path}: {e}")
        return None
    
def wait_and_accept(driver):
    WebDriverWait(driver, 5).until(EC.alert_is_present())
    alert = driver.switch_to.alert
    alert.accept()

def get_gpt_result_for_qna(title, question):
    s = Settings()
    client = OpenAI(api_key=s.gpt_key)
    system_instruction = "당신은 상세하고 활기찬 지식전문가."
    prompt = f"""
    질문 제목: {title}, 질문 내용: {question} 에 대한 답변을 해주고,
    한우 선물 세트 관련 홍보 진행.
    답변과 홍보를 자연스럽게 연결지어서 완결성있게 답변 생성.
    최고급 품질의 한우를 타임세일 이벤트로 저렴한 가격에 판매한다는 것을 강조.
    선물을 위한 고급스러운 패키지 측면에서 강조.
    구매 시 서비스로 곰탕을 추가하는 이벤트를 진행하고 있다는 것을 강조.
    메타데이터 없이 순수 텍스트로만 작성.
    문단과 문장을 적절하게 나누고, 문장 사이에는 줄바꿈 추가.
    한국어로 작성.
    실제 사람이 작성한 것 처럼 작성. 
    """
    variation_prompts = [
        "50대 주부 말투로 작성해줘.",
        "10대 학생 말투로 작성해줘.",
        "20대 대학생 말투로 작성해줘.",
        "30대 직장인 말투로 작성해줘.",
        "40대 부모님 말투로 작성해줘.",
        "60대 어르신 말투로 작성해줘.",
        "친근하고 편안한 말투로 작성해줘.",
        "격식을 차린 정중한 말투로 작성해줘.",
        "인터넷 커뮤니티 말투로 작성해줘.",
        "유머러스한 말투로 작성해줘.",
        "문어체로 작성해줘.",
        "구어체로 작성해줘.",
        "사투리를 섞어서 작성해줘.",
        "귀엽고 발랄한 말투로 작성해줘.",
        "진지하고 무거운 말투로 작성해줘.",
        "차분하고 따뜻한 말투로 작성해줘.",
        "논리적이고 객관적인 말투로 작성해줘.",
        "친구에게 말하듯이 작성해줘.",
        "뉴스 기사처럼 작성해줘.",
        "블로그 포스트처럼 작성해줘.",
        "간단하고 직설적으로 작성해줘.",
        "복잡하고 자세하게 작성해줘.",
        "심플하고 명료하게 작성해줘.",
        "풍부한 어휘를 사용해서 작성해줘.",
        "트렌디한 말투로 작성해줘.",
        "고전적인 말투로 작성해줘."
    ]
    additional_prompt = random.choice(variation_prompts)
    prompt += additional_prompt
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt},
        ],
        max_tokens=2000,
        temperature=0.7,
    )

    gpt_result = response.choices[0].message.content.strip()
    return gpt_result

def get_gpt_result_for_question(keyword):
    s = Settings()
    client = OpenAI(api_key=s.gpt_key)
    age_list = ['10', '20', '30', '40', '50', '60']
    actor_list = ['남학생', '여학생', '주부', '회사원', '직장인', '백수', '대학생', '노인', '부자', '거지']
    max_token_len_list = list(range(100, 2401, 100))
    system_instruction = f"당신은 질문하는 {random.choice(age_list)}대 {random.choice(actor_list)}"
    prompt = f"""
    {keyword} 추천을 요청하는 글을 작성하고 싶어.
    이를 위한 제목과 내용을 작성해줘.
    제목은 ?로 끝나는 질문으로 작성해줘.
    전반적으로 추천을 부탁하는 형태로 작성해줘.
    200글자 내외로 작성해줘.
    사람이 실제로 쓴 것처럼 오타를 조금씩 섞어줘.
    일반 텍스트 형태로 작성해줘.
    목록 형태로 작성하지 말아줘.
    메타데이터 없이 순수 텍스트로만 작성.
    문단과 문장을 적절하게 나누고, 문장 사이에는 줄바꿈 추가.
    인사와 끝맺음말은 생략해줘.
    {keyword} 가 다양하게 들어갈 수 있도록 작성해줘.
    """
    variation_prompts = [
        "50대 주부 말투로 작성해줘.",
        "10대 학생 말투로 작성해줘.",
        "20대 대학생 말투로 작성해줘.",
        "30대 직장인 말투로 작성해줘.",
        "40대 부모님 말투로 작성해줘.",
        "60대 어르신 말투로 작성해줘.",
        "친근하고 편안한 말투로 작성해줘.",
        "격식을 차린 정중한 말투로 작성해줘.",
        "인터넷 커뮤니티 말투로 작성해줘.",
        "유머러스한 말투로 작성해줘.",
        "문어체로 작성해줘.",
        "구어체로 작성해줘.",
        "사투리를 섞어서 작성해줘.",
        "귀엽고 발랄한 말투로 작성해줘.",
        "진지하고 무거운 말투로 작성해줘.",
        "차분하고 따뜻한 말투로 작성해줘.",
        "논리적이고 객관적인 말투로 작성해줘.",
        "친구에게 말하듯이 작성해줘.",
        "뉴스 기사처럼 작성해줘.",
        "블로그 포스트처럼 작성해줘.",
        "간단하고 직설적으로 작성해줘.",
        "복잡하고 자세하게 작성해줘.",
        "심플하고 명료하게 작성해줘.",
        "풍부한 어휘를 사용해서 작성해줘.",
        "트렌디한 말투로 작성해줘.",
        "고전적인 말투로 작성해줘."
    ]
    additional_prompt = random.choice(variation_prompts)
    prompt += additional_prompt
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt},
        ],
        max_tokens=random.choice(max_token_len_list),
        temperature=0.9,
    )

    gpt_result = response.choices[0].message.content.strip()
    return gpt_result

def remove_query_param(url, param):
    # URL 파싱
    parsed_url = urlparse(url)
    
    # 쿼리 파라미터 파싱
    query_params = parse_qs(parsed_url.query)
    
    # 특정 파라미터 제거
    if param in query_params:
        del query_params[param]
    
    # 남은 쿼리 파라미터를 다시 조합
    new_query = urlencode(query_params, doseq=True)
    
    # 새로운 URL 구성
    new_url = urlunparse((
        parsed_url.scheme,
        parsed_url.netloc,
        parsed_url.path,
        parsed_url.params,
        new_query,
        parsed_url.fragment
    ))
    
    return new_url

