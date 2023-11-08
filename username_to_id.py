import time,json,re,sys,subprocess
import mysql.connector
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from time import sleep

def load_config(script_path):
    path = script_path.split("username_to_id.py")[0]
    with open(path+'json/config.json', 'r') as f:
        return json.load(f)

def search_element(driver, xpath, input_text=None):
        element = driver.find_element(By.XPATH, xpath)
        if input_text:
            element.send_keys(input_text)
        else:
            element.send_keys(Keys.ENTER)
        sleep(4)

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    return webdriver.Chrome(options=options)

def login_twitter(driver, config, account_email, account_pseudo, account_password):
    driver.get("https://twitter.com/") 
    sleep(2)
    try:
        search_element(driver, config['cookie']['cookie_path']) # Accept cookies
    except:
        pass
    search_element(driver, config['connect']['connect_path']) # Click on "Se connecter"
    search_element(driver, config['connect']['input_email_path'], account_email) # Fill in email
    search_element(driver, config['connect']['input_next_for_email_path']) # Click on "Suivant"
    search_element(driver, config['connect']['input_pseudo_path'], account_pseudo) # Fill in pseudo if asked
    search_element(driver, config['connect']['input_next_for_pseudo_path']) # Click on "Suivant"
    search_element(driver, config['connect']['input_password_path'], account_password) # Fill in password
    search_element(driver, config['connect']['input_next_for_password_path']) # Click on 'Valider'
    sleep(3)

def connect_to_db():
    DB_CONFIG = {
        "host": "localhost",
        "user": "root",
        "password": "",
        "database": "twitter"
    }
    return mysql.connector.connect(**DB_CONFIG)

def get_row_count(cursor):
    cursor.execute("""SELECT COUNT(*) FROM mytwip""")
    return cursor.fetchone()[0]

def get_new_rows(cursor, count_initial):
    # Récuperer que l'id de la requête et l'username
    cursor.execute("""
        SELECT sq_id,sq_query_value FROM mytwip
        LIMIT %s, 18446744073709551615;
    """, (count_initial,))
    return cursor.fetchall()

def update_rows(cursor, driver, new_rows, config):
    for row in new_rows:
        url = "https://twitter.com/" + row[1]
        driver.get(url) 
        sleep(5)

        try: 
            error_search = driver.find_element(By.XPATH, config['other_element']['error_search_path']).get_attribute("textContent")
            if error_search == "Hmm...this page doesn’t exist. Try searching for something else.":
                driver.find_element(By.XPATH, config['other_element']['error_search_input_path']).send_keys(Keys.ENTER)
                sleep(2)
        except:
            pass

        new_id = get_new_id(driver)

        cursor.execute("""UPDATE mytwip SET sq_twitter_id = %s WHERE sq_id = %s""",(new_id,row[0]))

def get_new_id(driver):
    xpaths = [
        "/html/body/div[1]/div/div/div[2]/main/div/div/div/div/div/div[3]/div/div/div/div/div[1]/div[2]/div/div[1]/div",
        "/html/body/div[1]/div/div/div[2]/main/div/div/div/div/div/div[3]/div/div/div/div/div[1]/div[2]/div[3]/div[1]/div",
        "/html/body/div[1]/div/div/div[2]/main/div/div/div/div/div/div[3]/div/div/div/div/div[1]/div[2]/div[5]/div[1]/div"
    ]
    for xpath in xpaths:
        try:
            btn_follow = driver.find_element(By.XPATH, xpath).get_attribute('data-testid')
            return re.split('-follow|-unfollow', btn_follow)[0]
        except:
            continue
    return None

def main():
    while True:
        try:
            db = connect_to_db()
            cursor = db.cursor()
            
            script_path = sys.argv[0] # Chemin actuelle du fichier
            config = load_config(script_path)
            
            driver = setup_driver()
            
            account_email = 'd6071611@gmail.com'
            account_pseudo = 'D6071611Dylan'
            account_password = 'kpzRqSLWvKQ593'
            # account_email = 'jacheres_farineuse_0z@icloud.com'
            # account_pseudo = '0zF58596'
            # account_password = 'zU@m2%%GHeS47q'

            login_twitter(driver, config, account_email, account_pseudo, account_password)

            # Récupération du nombre de lignes initial
            count_initial = get_row_count(cursor)
            
            while True:
                try:
                    # Récupération du nombre de lignes actuel
                    count_actuel = get_row_count(cursor)

                    # Comparaison des deux nombres de lignes
                    if count_actuel != count_initial:
                        # Le nombre de lignes a changé
                        new_rows = get_new_rows(cursor, count_initial)
                        # Mise à jour des nouvelles lignes
                        update_rows(cursor, driver, new_rows, config)
                    else:
                        # Le nombre de lignes n'a pas changé
                        time.sleep(10)

                    # Mise à jour du nombre de lignes initial
                    count_initial = count_actuel

                except:
                        try:
                            driver.close()
                            driver.quit()
                        except:
                            pass

                        break
                        # Relance le script
                        # subprocess.run(["python", script_path])

        except Exception as e:
            print(f"Une erreur s'est produite : {e}")
            sleep(5)

if __name__ == "__main__":
    main()