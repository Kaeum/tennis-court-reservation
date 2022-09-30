import time

import pause
import pyperclip
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from threading import RLock


class Reservation(object):
    def __init__(self, court_id, date, start_time, end_time, dt, bank_name='신한'):
        self.lock = RLock()
        self.court_id = court_id
        self.date = date
        self.start_time = start_time
        self.end_time = end_time
        self.dt = dt
        self.bank_name = bank_name

    _BASE_URL = "https://nid.naver.com/nidlogin.login?url=https%3A%2F%2Fbooking.naver.com%2Fbooking%2F10%2Fbizes%2F210031%2Fitems"

    user = {
        "id": "oror2930",
        "pw": "skrkdma1",
        "address": "고양시 덕양구 행신동"
    }

    def init_driver(self, headless=True):
        options = Options()
        if headless:
            options.add_argument('--headless')
            options.add_argument('lang=en')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('disable-gpu')
            options.add_argument('disable-infobars')
            options.add_argument('--disable-extensions')
        options.add_argument('--window-size=1020,680')
        return webdriver.Chrome(service=Service(executable_path=ChromeDriverManager().install()), options=options)

    def clipboard_input(self, user_xpath, user_input, driver):
        with self.lock:
            time.sleep(0.5)
            pyperclip.copy(user_input)
            time.sleep(0.5)
            driver.find_element(By.XPATH, user_xpath).click()
            ActionChains(driver) \
                .key_down(Keys.COMMAND) \
                .send_keys('v') \
                .key_up(Keys.COMMAND) \
                .perform()
            time.sleep(0.5)

    def make_court_url(self, court_id):
        return f'{self._BASE_URL}%2F{court_id}'

    def process(self):
        print('reservation started.')
        driver = self.init_driver()
        wait = WebDriverWait(driver, 10)
        driver.get(self.make_court_url(self.court_id))

        # 로그인
        self.clipboard_input('//*[@id="id"]', self.user.get("id"), driver)
        self.clipboard_input('//*[@id="pw"]', self.user.get("pw"), driver)
        print('pause...')
        pause.until(self.dt)
        driver.find_element(By.XPATH, '//*[@id="log.login"]').click()
        ##일정선택(날짜,시간)
        # 날짜
        wait.until(ec.element_to_be_clickable((By.XPATH, ('//td[@data-tst_cal_datetext="%s"]' % self.date)))).click()

        opened = True
        while opened:
            try:
                driver.find_element(By.XPATH, '//button[@data-tst_next_step_click="0"]')
                opened = False
            except NoSuchElementException:
                driver.refresh()
                wait.until(ec.element_to_be_clickable((By.XPATH, ('//td[@data-tst_cal_datetext="%s"]' % self.date)))).click()

        # 회차선택
        wait.until(ec.element_to_be_clickable((By.XPATH, (
                '//ul[preceding-sibling::span[contains(., "오후")]]/li/a/span/span[text()="%s"]' % self.start_time)))).click()
        driver.find_element(By.XPATH, (
                '//ul[preceding-sibling::span[contains(., "오후")]]/li/a/span/span[text()="%s"]' % self.end_time)).click()

        # 예약시간 선택 클릭
        driver.find_element(By.XPATH, '//button[@data-tst_search_time_click="1"]').click()

        # 다음단계
        wait.until(ec.element_to_be_clickable((By.XPATH, '//button[@data-tst_next_step_click="0"]'))).click()
        # 결제하기 버튼
        driver.find_element(By.XPATH, '//button[@data-tst_submit_click="0"]').click()
        ##주문/결제

        # 일반결제 클릭
        wait.until(ec.element_to_be_clickable((By.XPATH, '//span[contains(@class, "radio-checked")]')))

        wait.until(ec.element_to_be_clickable(
            (By.XPATH, '//li[contains(@class, "_generalPaymentsTab")]/div/span[following-sibling::span]'))).click()

        # 나중에 결제
        ActionChains(driver).send_keys(Keys.TAB) \
            .send_keys(Keys.TAB) \
            .send_keys(Keys.ARROW_DOWN) \
            .perform()

        # 환불 방법 - 환불정산액 적립
        ActionChains(driver).send_keys(Keys.TAB) \
            .send_keys(Keys.TAB) \
            .send_keys(Keys.TAB) \
            .send_keys(Keys.ARROW_DOWN) \
            .perform()

        # 입금은행
        driver.find_element(By.XPATH, '//div[@id="bankCodeList"]').click()

        wait.until(ec.element_to_be_clickable((By.XPATH, ('//li[contains(., "%s")]' % self.bank_name)))).click()

        # 주문하기
        driver.find_element(By.XPATH, '//button[contains(., "주문하기")]').click()
        wait.until(ec.element_to_be_clickable((By.XPATH, '//a[@class="naver_pay_button"]')))

        # 종료
        driver.quit()
