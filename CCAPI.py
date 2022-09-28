import time, tomli
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class CCAPI:
    def __init__(self):
        self.timeout = 10

    def __login(self, driver):

        driver.set_page_load_timeout(10)

        driver.get("https://connectcarolina.unc.edu/")
        login_button = driver.find_element(By.CLASS_NAME, "loginbutton")
        login_link = login_button.get_attribute('href')

        driver.get(login_link)

        with open("onyen-creds.toml", 'rb') as f:
            credentials = tomli.load(f)["credentials"]
        username, password = credentials["username"], credentials["password"]

        _ = driver.implicitly_wait(self.timeout)

        sso_form = driver.find_element(By.CLASS_NAME, "sso-form")
        username_input = driver.find_element(By.ID, "username")
        password_input = driver.find_element(By.ID, "password")
        login_button = sso_form.find_elements(By.CLASS_NAME, "form-group")[3].find_element(By.TAG_NAME, "button")

        username_input.send_keys(username)
        password_input.send_keys(password)
        login_button.click()

    def get_advisor(self):
        driver = webdriver.Chrome()
        self.__login(driver)

        try:
            advisor_element = WebDriverWait(driver, self.timeout).until(EC.presence_of_element_located((By.ID, "NC_CS_enr_tile_boxmiddleright")))
        except TimeoutException:
            print("Timeout loading CC.")


        advisor = advisor_element.find_element(By.TAG_NAME, "a")
        advisor_name = advisor.get_attribute("innerHTML").strip()
        advisor_email = advisor.get_attribute("href")[7:].strip().lower()

        advisor_info = {
            "name": advisor_name,
            "email": advisor_email
        }

        return advisor_info
        