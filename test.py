import time
from selenium import webdriver
from selenium.webdriver.common.by import By

# options = webdriver.Firefox()
# options.add_argument("--incognito")

driver = webdriver.Firefox()
driver.set_page_load_timeout(10)

driver.get("https://connectcarolina.unc.edu/")
login_button = driver.find_element(By.CLASS_NAME, "loginbutton")
login_link = login_button.get_attribute('href')

driver.get(login_link)

time.sleep(10)
driver.quit()