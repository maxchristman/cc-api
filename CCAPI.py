import time, tomli
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class CCAPI:
    def __init__(self):
        self.timeout = 10
        self.driver = self.__login()

    def __login(self):

        options = webdriver.ChromeOptions()
        options.add_argument("--incognito")
        driver = webdriver.Chrome(options=options)
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

        return driver

    def get_advisor(self):

        try:
            advisor_element = WebDriverWait(self.driver, self.timeout).until(EC.presence_of_element_located((By.ID, "NC_CS_enr_tile_boxmiddleright")))
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

    def __go_to_student_center(self):

        student_center_button = self.driver.find_element(By.ID, "PTNUI_LAND_REC14$0_row_3")
        student_center_button.click()

    def get_course_schedule(self):
        self.__go_to_student_center()
        try:
            # schedule_table = self.driver.find_element(By.ID, "STDNT_WEEK_SCHD$scroll$0")
            # schedule_table = self.driver.find_element(By.CLASS_NAME, "PSLEVEL1GRIDWBO")
            print(self.driver.page_source)
            # print(schedule_table.get_attribute("innerHTML"))
        except Exception as e:
            print(e)
            time.sleep(6000)