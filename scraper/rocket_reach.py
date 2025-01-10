import logging
import re

from selenium.common.exceptions import NoSuchWindowException
from selenium.webdriver.common.by import By

from .objects import Scraper
from .utils.profiles import write_final_profile


logging.basicConfig()


class RocketReach(Scraper):
    first_name = ''
    last_name = ''
    location = ''
    company_name = ''
    keywords = ''
    find_profile = False

    def __init__(self, driver=None, proxy=None):
        self.limit_end = None
        self.no_browser = None
        self.driver = driver
        self.base_url = 'https://rocketreach.co/'

        self.sign_up_url = f'{self.base_url}signup?next=%2F'
        self.profile_link = f'{self.base_url}person'
        self.logout_link = f'{self.base_url}logout'
        self.login_url = f'{self.base_url}login'

        self.profile_base_link = 'https://rocketreach.co/person?start=1&pageSize=10&link=https:%2F%2Fwww.linkedin.com%2Fin%2F'

        self.error_email = False

        if not self.driver:
            self.driver = self.initialize(proxy=proxy)

    def login(self, email, password):
        self.no_browser = None
        response = self.middle_method_for_retry(method_name=self.successful_logout)
        if not response:
            print('Failed to open login url, Retry again')
            if self.no_browser:
                return False
            return self.login(email=email, password=password)

        self.get_elements_by_time(
            by=By.XPATH, value='//input[@id="id_email"]'
        ).send_keys(email)
        self.wait(2)
        self.get_elements_by_time(
            by=By.XPATH, value='//input[@id="id_password"]'
        ).send_keys(password)
        self.wait(2)

        return self.middle_method_for_retry(method_name=self.login_successful_or_error)

    def get_profile_data(self, profile: str, post_fix: str):
        self.no_browser = None
        self.limit_end = None
        try:
            self.driver.get(f'{self.profile_base_link}{profile}')
            self.get_elements_by_time(
                by=By.XPATH,
                value='//span[@class="search-results-query__num-results"]',
                single=True,
                seconds=10,
            )
            limit_reach = self.get_elements_by_time(
                by=By.XPATH, value='//div[@class="modal-dialog modal-xl"]', single=True
            )
            if limit_reach:
                self.limit_end = True
                return False

            self.driver.execute_script(
                """
const svelteComponent = document.querySelector('svelte-component[type="ProfileCard"]'); 

// Check if the shadow root exists
if (svelteComponent && svelteComponent.shadowRoot) {
    const shadowRoot = svelteComponent.shadowRoot;

    const button = Array.from(shadowRoot.querySelectorAll('button')
    ).find(btn => btn.textContent.trim() === 'Get Contact Info');

    if (button) {
        console.log("Button found:", button);
        button.click()
    } else {
        console.log("Button not found inside the shadow DOM.");
    }
} else {
    console.log("Shadow root not found.");
}
                """
            )

            self.wait(10)
            limit_reach = self.get_elements_by_time(
                by=By.XPATH, value='//div[@class="modal-dialog modal-xl"]', single=True
            )
            if limit_reach:
                self.limit_end = True
                return False

            body_text = self.get_elements_by_time(by=By.XPATH, value='//body').text

            emails = re.findall(
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', body_text
            )
            if not emails:
                emails = []
            emails = list(set(list(emails)))
            if emails:
                self.find_profile = True

            emails = ', '.join([profile, *emails])
            write_final_profile(emails, post_fix)
            return True

        except NoSuchWindowException as e:
            self.no_browser = True
            print(e)
            return False

    def login_successful_or_error(self, **kwargs):
        self.get_elements_by_time(
            by=By.XPATH, value='//input[@id="id_password"]'
        ).submit()
        inner_count = 0
        self.error_email = False
        while True:
            if self.driver.current_url.split('?')[0] == self.profile_link.split('?')[0]:
                return True
            if self.get_elements_by_time(
                by=By.XPATH, value='//ul[@class="errorlist"]/li', seconds=1
            ):
                self.error_email = True
                return False
            inner_count = inner_count + 1
            if inner_count > 60:
                break
        return False

    def successful_logout(self, **kwargs):
        self.driver.get(self.logout_link)
        inner_counter = 0
        while True:
            try:
                self.wait(1)
                if self.driver.current_url == self.login_url:
                    return True
                inner_counter = inner_counter + 1
                if inner_counter > 60:
                    break
            except NoSuchWindowException as e:
                self.no_browser = True
                print(e)
                return False
            except Exception as e:
                print(e)
                break
        return False

    def middle_method_for_retry(self, method_name, **kwargs):
        count = 0
        while count < 3:
            try:
                response = method_name(**kwargs)
                if response:
                    return True
            except NoSuchWindowException as e:
                self.no_browser = True
                print(e)
                return False
            count = count + 1
        return False
