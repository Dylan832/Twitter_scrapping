import sys
from os.path import dirname, realpath
sys.path.insert(0, dirname(dirname(realpath(__file__))))

from Classes.Selenium import Selenium
from Classes.Mysql import Mysql

from time import sleep

import json,re

selenium = None

def load_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def login_twitter(config, account):
    global selenium
    selenium = Selenium("https://twitter.com/")
    sleep(5)

    selenium.click_element_by_xpath(config['cookie']['cookie_path']) # Accepter les cookies
    sleep(2)

    selenium.click_element_by_xpath(config['connect']['connect_path']) # Click sur "Se connecter"
    sleep(5)

    selenium.fill_input_by_xpath(config['connect']['input_mail_fill'], account["email"]) # Fill in email
    sleep(2)
    selenium.click_element_by_xpath(config['connect']['input_next_for_email_path']) # Click sur "Suivant"
    sleep(2)

    label = selenium.get_element_by_xpath(config['connect']['label_pseudo'])
    if label:
        selenium.fill_input_by_xpath(config['connect']['input_pseudo_fill'], account['pseudo']) # Fill in pseudo if asked
        sleep(2)
        selenium.click_element_by_xpath(config['connect']['input_next_for_pseudo_path']) # Click sur "Suivant"
        sleep(2)

    selenium.fill_input_by_xpath(config['connect']['input_password_fill'], account['password']) # Fill in password
    sleep(2)
    selenium.click_element_by_xpath(config['connect']['input_next_for_password_path']) # Click sur 'Valider'
    sleep(3)

def get_new_id():
    xpaths = [
        "/html/body/div[1]/div/div/div[2]/main/div/div/div/div/div/div[3]/div/div/div/div/div[1]/div[2]/div/div[1]/div",
        "/html/body/div[1]/div/div/div[2]/main/div/div/div/div/div/div[3]/div/div/div/div/div[1]/div[2]/div[3]/div[1]/div",
        "/html/body/div[1]/div/div/div[2]/main/div/div/div/div/div/div[3]/div/div/div/div/div[1]/div[2]/div[5]/div[1]/div"
    ]
    for xpath in xpaths:
        try:
            btn_follow = selenium.get_element_attribute_by_xpath(xpath,get_attribute="data-testid")

            if btn_follow:
                return re.split('-follow|-unfollow', btn_follow)[0]
        except:
            continue
    return None

def main():
    global selenium

    profiles = Mysql.execute_select_array("""SELECT * FROM profiles WHERE twitter_id IS NULL""",close=True)

    config = load_json('./Ressources/Json/selenium_xpaths.json')
    accounts = load_json('./Ressources/Json/twitter_accounts.json')
    
    login_twitter(config, accounts[0])

    for profile in profiles:
        try:
            url = "https://twitter.com/" + profile["username"]
            selenium.open(url)
            sleep(3)
            twitter_id = get_new_id()

            sql = """UPDATE profiles SET twitter_id = %s WHERE id = %s"""
            params = (twitter_id, profile['id'],)
            Mysql.execute_insert(sql,params=params)

        except Exception as e:
            print(f"Une erreur s'est produite : {e}")
            continue
    
    if selenium is not None:
        selenium.quit()


if __name__ == "__main__":
    main()