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
        self.no_results = None
        self.limit_end = None
        self.no_browser = None
        self.driver = driver
        self.base_url = 'https://rocketreach.co/'

        self.sign_up_url = f'{self.base_url}signup?next=%2F'
        self.profile_link = f'{self.base_url}person'
        self.logout_link = f'{self.base_url}logout'
        self.login_url = f'{self.base_url}login'
        self.phone_verify_link = f'{self.base_url}phone_verify'

        self.profile_base_link = 'https://rocketreach.co/person?start=1&pageSize=10&link=https:%2F%2Fwww.linkedin.com%2Fin%2F'

        self.error_email = False

        self.retries_invalid_account = 0

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

    def get_profile_data(self, email: str, profile: str, post_fix: str):
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
            if (
                "You've hit your limit of searches"
                in self.get_elements_by_time(by=By.XPATH, value='//body').text
            ):
                self.limit_end = True
                return False

            if (
                'Get Contact Info'
                in self.get_elements_by_time(by=By.XPATH, value='//body').text
            ):
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

            if (
                'No Results Found.'
                in self.get_elements_by_time(by=By.XPATH, value='//body').text
            ):
                self.no_results = True
                return False

            loop_counter = 0
            while True:
                loop_counter = loop_counter + 1
                limit_reach = self.get_elements_by_time(
                    by=By.XPATH,
                    value='//div[@class="modal-dialog modal-xl"]',
                    single=True,
                    seconds=1,
                )
                if limit_reach:
                    self.limit_end = True
                    return False
                if (
                    'Send Email'
                    in self.get_elements_by_time(by=By.XPATH, value='//body').text
                    or loop_counter > 20
                ):
                    break

            body_text = self.get_elements_by_time(by=By.XPATH, value='//body').text

            if 'Send Email' not in body_text:
                self.retries_invalid_account = self.retries_invalid_account + 1
                if self.retries_invalid_account > 2:
                    self.limit_end = True
                    return False
            else:
                self.retries_invalid_account = 0

            emails = re.findall(
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', body_text
            )
            if email in emails:
                emails.remove(email)
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

    def proceed_next_clicks(self):
        try:
            button = self.get_elements_by_time(
                by=By.XPATH,
                value='//button[@class="driver-popover-close-btn"]',
            )
            if not button:
                return True
            self.click_button(element=button)
        except Exception as e:
            print(e)
            return

    def login_successful_or_error(self, **kwargs):
        self.get_elements_by_time(
            by=By.XPATH, value='//input[@id="id_password"]'
        ).submit()
        inner_count = 0
        self.error_email = False
        while True:
            body_text = self.get_elements_by_time(by=By.XPATH, value='//body').text

            for tx in [
                'The email and password did not match.',
                'This field is required.',
                'Password is required.',
                'Login invalid or expired, try again.',
                'Email is invalid.',
            ]:
                if tx in body_text:
                    return False
            if self.driver.current_url.split('?')[0] == self.phone_verify_link:
                self.error_email = True
                return False
            if self.driver.current_url.split('?')[0] in (
                self.profile_link.split('?')[0],
                self.profile_link.split('?')[0].replace('person', 'dashboard'),
            ):
                self.wait(5)
                body_text = self.get_elements_by_time(
                    by=By.XPATH,
                    value='//body',
                ).text
                if 'Before your search' in body_text:
                    self.proceed_next_clicks()
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
            except AttributeError:
                return False
            count = count + 1
        return False
