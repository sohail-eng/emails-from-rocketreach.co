from dataclasses import dataclass
import logging
from time import sleep

from selenium import webdriver
from selenium.common import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    JavascriptException,
    NoSuchElementException,
)
from selenium.webdriver import ActionChains, Chrome, Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


@dataclass
class Scraper:
    driver: Chrome = None
    WAIT_FOR_ELEMENT_TIMEOUT = 5
    TOP_CARD = 'pv-top-card'

    invalid_text = [
        'This LinkedIn Page isn’t available',
        'This page doesn’t exist',
        'Page not found',
        'The job you were looking for was not found.',
    ]

    @staticmethod
    def wait(duration):
        sleep(int(duration))

    def focus(self):
        self.driver.execute_script('alert("Focus window")')
        self.driver.switch_to.alert.accept()

    @classmethod
    def initialize(cls, proxy):
        try:
            options = webdriver.ChromeOptions()
            # options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-notifications')
            if proxy:
                options.add_argument(f'--proxy-server={proxy}')
            options.add_argument('start-maximized')
            return webdriver.Chrome(service=Service(), options=options)
        except Exception as e:
            logging.error('Error! creating webdriver', exc_info=e)
            return webdriver.Chrome()

    def click_button(self, element=None, base=None):
        if not base:
            base = self.driver
        if element:
            try:
                action_chains = ActionChains(base)
                action_chains.click(element)
                action_chains.perform()
            except (ElementClickInterceptedException, ElementNotInteractableException):
                pass

    def click_button_error(self, element=None, base=None):
        if not base:
            base = self.driver
        if element:
            action_chains = ActionChains(base)
            action_chains.click(element)
            action_chains.perform()

    def click_button_control(self, element=None, base=None):
        if not base:
            base = self.driver
        if element:
            try:
                action_chains = ActionChains(base)
                action_chains.key_down(Keys.CONTROL)
                action_chains.click(element)
                action_chains.key_up(Keys.CONTROL)
                action_chains.perform()
            except (ElementClickInterceptedException, ElementNotInteractableException):
                pass

    def get_elements_by_time(
        self,
        by=By.CLASS_NAME,
        value='',
        seconds=5,
        base=None,
        single=True,
        element_count=None,
    ):
        counter = 0
        if not base:
            base = self.driver
        while counter < seconds:
            elements = base.find_elements(by=by, value=value)
            if len(elements) == 0:
                pass
            else:
                if single:
                    return elements[0]
                elif not element_count:
                    return elements
                elif len(elements) > element_count + 1:
                    return elements
            counter = counter + 1
            self.wait(1)

    def get_element_text(self, by=By.CLASS_NAME, value='', seconds=3, base=None):
        element = self.get_elements_by_time(
            by=by, value=value, seconds=seconds, base=base
        )
        if element:
            return element.text.strip()
        return ''

    def wait_for_element_to_load(self, by=By.CLASS_NAME, name='pv-top-card', base=None):
        base = base or self.driver
        return WebDriverWait(base, self.WAIT_FOR_ELEMENT_TIMEOUT).until(
            EC.presence_of_element_located((by, name))
        )

    def wait_for_all_elements_to_load(
        self, by=By.CLASS_NAME, name='pv-top-card', base=None
    ):
        base = base or self.driver
        return WebDriverWait(base, self.WAIT_FOR_ELEMENT_TIMEOUT).until(
            EC.presence_of_all_elements_located((by, name))
        )

    def scroll_to_half(self, class_name: str = None):
        try:
            if class_name:
                self.driver.execute_script(
                    f"my_div = document.getElementsByClassName('{class_name}')[0];"
                    f'my_div.scrollTo(0,my_div.scrollHeight);'
                )
            else:
                self.driver.execute_script(
                    'window.scrollTo(0, Math.ceil(document.body.scrollHeight/2));'
                )
        except JavascriptException:
            pass
        except Exception as e:
            logging.warning('Not fount', exc_info=e)

    def scroll_to_top(self, class_name: str = None):
        try:
            if class_name:
                self.driver.execute_script(
                    f"my_div = document.getElementsByClassName('{class_name}')[0];"
                    f'my_div.scrollTo(0,0);'
                )
            else:
                self.driver.execute_script('window.scrollTo(0, 0);')
        except JavascriptException:
            pass
        except Exception as e:
            logging.warning('Not fount', exc_info=e)

    def get_document_height(self, class_name: str = None):
        try:
            if class_name:
                return self.driver.execute_script(
                    f"my_div = document.getElementsByClassName('{class_name}')[0];"
                    f'return my_div.scrollHeight;'
                )
            return self.driver.execute_script('return document.body.scrollHeight;')
        except JavascriptException:
            pass
        except Exception as e:
            logging.warning('Not fount', exc_info=e)

    def scroll_to_bottom(self, class_name: str = None):
        try:
            if class_name:
                self.driver.execute_script(
                    f"my_div = document.getElementsByClassName('{class_name}')[0];"
                    f'my_div.scrollTo(0,my_div.scrollHeight);'
                )
            else:
                self.driver.execute_script(
                    'window.scrollTo(0, document.body.scrollHeight);'
                )
        except JavascriptException:
            pass
        except Exception as e:
            logging.warning('Not fount', exc_info=e)

    def scroll_class_name_element_to_page_percent(
        self, class_name: str, page_percent: float
    ):
        self.driver.execute_script(
            f'elem = document.getElementsByClassName("{class_name}")[0]; '
            f'elem.scrollTo(0, elem.scrollHeight*{str(page_percent)});'
        )

    def __find_element_by_class_name__(self, class_name):
        try:
            self.driver.find_element(By.CLASS_NAME, class_name)
            return True
        except NoSuchElementException:
            pass
        except Exception as e:
            logging.warning('Not fount', exc_info=e)

    def __find_element_by_xpath__(self, tag_name):
        try:
            self.driver.find_element(By.XPATH, tag_name)
            return True
        except NoSuchElementException:
            pass
        except Exception as e:
            logging.warning('Not fount', exc_info=e)

    def __find_enabled_element_by_xpath__(self, tag_name):
        try:
            elem = self.driver.find_element(By.XPATH, tag_name)
            return elem.is_enabled()
        except NoSuchElementException:
            pass
        except Exception as e:
            logging.warning('Not fount', exc_info=e)

    @classmethod
    def __find_first_available_element__(cls, *args):
        for elem in args:
            if elem:
                return elem[0]

    def invalid_link(self):
        text = self.driver.find_element(By.TAG_NAME, 'body').text
        for item in self.invalid_text:
            if item in text:
                return True
