'''

 ______     __  __     ______     __     ______    
/\  ___\   /\ \_\ \   /\  == \   /\ \   /\  ___\   
\ \ \____  \ \  __ \  \ \  __<   \ \ \  \ \___  \  
 \ \_____\  \ \_\ \_\  \ \_\ \_\  \ \_\  \/\_____\ 
  \/_____/   \/_/\/_/   \/_/ /_/   \/_/   \/_____/ 
                                                   

Post to Etsy Bot
April 2022

The goal of this script is to automate the logging on to Etsy and hitting the server api endpoint of /oauth to initiate the draft
posting.

'''
import os
from json import load
from time import sleep
from selenium import webdriver
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

load_dotenv()


# Credentials
account = os.getenv("etsy_account")
password = os.getenv("etsy_password")

options = webdriver.ChromeOptions()
prefs = {"profile.default_content_setting_values.notifications": 1}
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_experimental_option("prefs", prefs)
driver = webdriver.Chrome(options=options)

login_site = "http://127.0.0.1:5000/oauth"

driver.get(login_site)

if driver.title == "Sign in | Etsy":
    try:
        email_bar = driver.find_element(By.ID, "join_neu_email_field")
        pass_bar = driver.find_element(By.ID, "join_neu_password_field")
        sign_in_button = driver.find_element(By.NAME, "submit_attempt")

        email_bar.send_keys(account)
        pass_bar.send_keys(password)
        sign_in_button.click()
    except:
        print("Unable to login")

    try:
        grant_present = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.NAME, 'grant')))

        print("Posting listing onto Etsy. Please wait...")
        grant_button = driver.find_element(By.NAME, "grant")
        grant_button.click()
        print("Posting complete. Please Check Etsy.")
    except:
        print("Unable to Grant Access")
