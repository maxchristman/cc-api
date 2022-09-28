import time, tomli
from selenium import webdriver
from selenium.webdriver.common.by import By

class CCAPI:
    def __login(self):

        driver = webdriver.Firefox()
        driver.set_page_load_timeout(10)

        driver.get("https://connectcarolina.unc.edu/")
        login_button = driver.find_element(By.CLASS_NAME, "loginbutton")
        login_link = login_button.get_attribute('href')

        driver.get(login_link)

        with open("onyen-creds.toml", 'rb') as f:
            credentials = tomli.load(f)["credentials"]
        username, password = credentials["username"], credentials["password"]

        _ = driver.implicitly_wait(10)

        sso_form = driver.find_element(By.CLASS_NAME, "sso-form")
        username_input = driver.find_element(By.ID, "username")
        password_input = driver.find_element(By.ID, "password")
        login_button = sso_form.find_elements(By.CLASS_NAME, "form-group")[3].find_element(By.TAG_NAME, "button")

        username_input.send_keys(username)
        password_input.send_keys(password)
        login_button.click()
        
        return driver
