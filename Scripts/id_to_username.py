from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from time import sleep
import json

def load_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def search_element(driver, xpath, input_text=None):
    try:
        element = driver.find_element(By.XPATH, xpath)
        if input_text:
            element.send_keys(input_text)
        else:
            element.send_keys(Keys.ENTER)
        sleep(4)
    except:
        pass

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    driver = webdriver.Chrome(options=options)
    return driver

def login_twitter(driver, account_email, account_pseudo, account_password, config):
    driver.get("https://twitter.com/") 
    sleep(2)
    search_element(driver, config['cookie']['cookie_path']) # Accept cookies
    search_element(driver, config['connect']['connect_path']) # Click on "Se connecter"
    search_element(driver, config['connect']['input_email_path'], account_email) # Fill in email
    search_element(driver, config['connect']['input_next_for_email_path']) # Click on "Suivant"
    search_element(driver, config['connect']['input_pseudo_path'], account_pseudo) # Fill in pseudo if asked
    search_element(driver, config['connect']['input_next_for_pseudo_path']) # Click on "Suivant"
    search_element(driver, config['connect']['input_password_path'], account_password) # Fill in password
    search_element(driver, config['connect']['input_next_for_password_path']) # Click on 'Valider'
    sleep(3)

def process_requests(driver, requests, config):
    all_id = []
    for request in requests:
        if (request['sq_query_value'].isnumeric()):
            url = "https://twitter.com/intent/user?user_id=" + request['sq_query_value']
            driver.get(url) 
            sleep(3)

            try: 
                error_search = driver.find_element(By.XPATH, config['other_element']['error_search_path']).get_attribute("textContent")
                if error_search == "Hmm...this page doesn’t exist. Try searching for something else.":
                    driver.find_element(By.XPATH, config['other_element']['error_search_input_path']).send_keys(Keys.ENTER)
                    sleep(2)
            except:
                pass

            try:
                username = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/div/div/div[2]/div[1]/div/div[2]/div/div/div/span').get_attribute('textContent')
                username = username.split("@")[1]
            except:
                username = None

            request["sq_username"] = username
        
            all_id.append(request)
            
            with open("json/data_id.json","w") as data:
                json.dump(all_id,data)

def main():
    config = load_json('json/config.json')
    requests = load_json('json/a.json')

    account_email = 'd6071611@gmail.com'
    account_pseudo = 'D6071611Dylan'
    account_password = 'kpzRqSLWvKQ593'

    driver = setup_driver()
    login_twitter(driver, account_email, account_pseudo, account_password, config)
    process_requests(driver, requests, config)

if __name__ == "__main__":
    main()
