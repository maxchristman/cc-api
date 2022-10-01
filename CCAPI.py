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
        iframe = self.driver.find_element(By.ID, "ptifrmtgtframe")
        iframe_link = iframe.get_attribute("src")
        self.driver.get(iframe_link)

    def __go_to_search(self):
        self.__go_to_student_center()
        search_page_button = self.driver.find_element(By.ID, "DERIVED_SSS_SCR_SSS_LINK_ANCHOR1")
        search_page_button.click()
    
    def class_search(self, query):
        self.__go_to_search()

        dept, number = query["dept"], query["number"]
        dept_input = self.driver.find_element(By.ID, "SSR_CLSRCH_WRK_SUBJECT$0")
        number_input = self.driver.find_element(By.ID, "SSR_CLSRCH_WRK_CATALOG_NBR$1")
        dept_input.send_keys(dept)
        # number_input.send_keys(number)

        while True:
            try:
                search_button = self.driver.find_element(By.ID, "CLASS_SRCH_WRK2_SSR_PB_CLASS_SRCH")
                search_button.click()
                break
            except Exception as e:
                print(e)

        results_table = self.driver.find_element(By.ID, "ACE_$ICField$3$$0")
        section_trs = results_table.find_elements(By.TAG_NAME, "tr")[1:]

        results = []

        for section_tr in section_trs:

            course = []
            section_tables = section_tr.find_elements(By.CLASS_NAME, "PSLEVEL1GRIDNBONBO")
            for section_table in section_tables:

                section = {}
                heading_row, data_row = section_table.find_elements(By.TAG_NAME, "tr")
                headings, datas = [], []

                for heading in heading_row.find_elements(By.TAG_NAME, "th"):
                    headings.append(heading.text)
                for data in data_row.find_elements(By.TAG_NAME, "td"):
                    datas.append(data.text)
                for heading, data in zip(headings, datas):
                    section[heading] = data
                
                course.append(section)
            results.append(course)
        return results



    def get_course_schedule(self):
        self.__go_to_student_center()
        try:
            outer_table = self.driver.find_element(By.ID, "STDNT_WEEK_SCHD$scroll$0")
            inner_table = outer_table.find_element(By.TAG_NAME, "table")
            rows = inner_table.find_elements(By.TAG_NAME, "tr")[1:]

            schedule = []

            for row in rows:
                course = {}
                for i, td in enumerate(row.find_elements(By.TAG_NAME, "td")):
                    if i == 0:
                        course_string, section_string = [x.strip() for x in td.text.split("\n")]

                        dept, num_string = [x.strip() for x in course_string.split(' ')]
                        course_number, section_number = [x.strip() for x in num_string.split('-')]
                        course["dept"], course["number"], course["section"] = dept, course_number, section_number

                        course_type, dirty_id = section_string.split(' ')
                        course_id = dirty_id[1:-1]
                        course["type"], course["id"] = course_type, course_id

                    elif i == 1:
                        datetime_string, location_string = [x.strip() for x in td.text.split("\n")]

                        if datetime_string != "TBA":
                            days_string, *time_string = datetime_string.split(' ')
                            time_string = ' '.join(time_string)
                            start_time, end_time = time_string.split(" - ")
                            when = {}
                            when["days"], when["start_time"], when["end_time"] = days_string, start_time, end_time
                            course["when"] = when
                        
                        if location_string != "TBA":
                            *hall, room = location_string.split(" - ")
                            hall = " - ".join(hall)
                            where = {}
                            where["hall"], where["room"] = hall, room
                            course["where"] = where


                schedule.append(course)

            return schedule            

        except Exception as e:
            print(e)
            self.driver.quit()
            time.sleep(6000)