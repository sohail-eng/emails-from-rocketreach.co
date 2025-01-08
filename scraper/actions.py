from selenium.webdriver import ActionChains


BASE_URL = 'https://www.linkedin.com/'


def page_has_loaded(driver):
    page_state = driver.execute_script('return document.readyState;')
    return page_state == 'complete'


def action_click(driver, element):
    action = ActionChains(driver)
    action.click(element)
    action.perform()
