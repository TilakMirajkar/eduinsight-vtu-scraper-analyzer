from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    UnexpectedAlertPresentException,
    WebDriverException,
    NoSuchElementException,
)
from bs4 import BeautifulSoup
import os
import time
from apps.scraper.services.captcha import CaptchaHandler

service = Service(os.environ.get('CHROME_DRIVER', '/usr/bin/chromedriver'))

class Connection:

    def _get_options(self, headless=True):
        options = Options()
        if headless:
            options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-dev-shm-usage')
        chrome_binary = os.environ.get('CHROME_BINARY')
        if chrome_binary:
            options.binary_location = chrome_binary

        return options

    def check_internet(self):
        options = self._get_options()
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.get('https://www.feynmanlectures.caltech.edu/III_toc.html')

    def connect(self, url, mode=False):
        options = self._get_options(headless=not mode)
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.get(url)

    def enter_usn(self, usn):
        field = self.driver.find_element(By.NAME, 'lns')
        field.clear()
        field.send_keys(usn)

    def get_captcha(self):
        captcha_image = self.driver.find_element(By.CSS_SELECTOR, '[alt="CAPTCHA code"]').screenshot_as_png

        text = ''
        error = False

        try:
            text = CaptchaHandler().get_captcha_from_image(captcha_image)
        except Exception as e:
            error = True

        return text, error
    
    def captcha_submit(self, captcha):
        self.driver.find_element(By.NAME, 'captchacode').send_keys(captcha)
        self.driver.find_element(By.ID, 'submit').click()

    def get_info(self, soup_dict):
        td_elements = self.driver.find_elements(By.TAG_NAME, 'td')

        student_usn = td_elements[1].text.split(':')[1].strip().upper()
        student_name = td_elements[3].text.split(':')[1].strip()

        soup_dict[f'{student_usn}+{student_name}'] = BeautifulSoup(self.driver.page_source, 'lxml')

        return soup_dict

    def sleep(self, secs):
        time.sleep(secs)

    def check_alert(self):
        return WebDriverWait(self.driver, 1).until(EC.alert_is_present())
    
    def stuck_page(self):
        soup = BeautifulSoup(self.driver.page_source, 'lxml')
        return soup.find_all('b', string='University Seat Number')
