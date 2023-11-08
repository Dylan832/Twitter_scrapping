from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from time import sleep
import time,json,re
# import undetected_chromedriver as uc 
start = time.time()

def load_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def setup_driver():
    options = webdriver.ChromeOptions()
    # options.add_argument('--user-data-dir=C:/Users/dev06/AppData/Local/Google/Chrome/User Data')
    # options.add_argument('--profile-directory=Profile 2')
    options.add_argument("start-maximized")
    driver = webdriver.Chrome(options=options)
    return driver

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

def search(driver, config, query):
    try:
        search_bar = driver.find_element(By.XPATH, config['other_element']['search_bar_right_path'])
    except:
        search_bar = driver.find_element(By.XPATH, config['other_element']['search_bar_center_path'])

    search_bar.send_keys(Keys.CONTROL + "a" + Keys.DELETE)
    sleep(2)
    search_bar.send_keys(query,Keys.ENTER)
    sleep(3)

def process_article(config, article):
    type = "Post"
    
    try:
        retweet = article.find_element(By.CSS_SELECTOR, config['tweet']['retweet_path']).get_attribute("textContent")
        index = retweet.find("reposted")
        # Attribution du type si ce n'est pas un post
        type = 'Retweet' if index != -1 else 'Pinned'
        if type == "Pinned":
            return
    except:
        pass
    
    try:
        # Enlever les Pub des tweets
        ad = article.find_element(By.CSS_SELECTOR, config['tweet']['tweet_ad_path']).get_attribute('textContent')
        if ad == 'Ad':
            return
    except:
        pass

    try:
        content = article.find_element(By.CSS_SELECTOR, config['tweet']['content_path']).get_attribute('textContent')
    except:
        content = "Aucun Contenu"
    try:
        date = article.find_element(By.CSS_SELECTOR , 'time').get_attribute('textContent')
    except:
        date = "Aucune Date"
    try:
        pseudo = article.find_element(By.CSS_SELECTOR , config['tweet']['pseudo_path']).get_attribute('textContent')
    except:
        pseudo = "Aucun Pseudo"
    try:
        username = article.find_element(By.CSS_SELECTOR , config['tweet']['username_path']).get_attribute('textContent')
    except:
        username = "Aucun Username"
    try:
        tweetURL = article.find_element(By.CSS_SELECTOR, config['tweet']['tweetURL_path']).get_attribute("href")
    except:
        tweetURL = "Aucun TweetURL"

    extract = tweetURL.find("/status/")
    tweetID = tweetURL[extract+8:]

    tweet = {
        "Type": type,
        "TweetURL": tweetURL,
        "TweetID": tweetID,
        "Username": username,
        "Pseudo": pseudo,
        "Date": date,
        "Content": content
    }

    return tweet

def crawler(driver, config, request, mode, all):
    listContent = []
    tweets = []
    account = {
        "query": request,
        "tweets": tweets
    }

    screen_height = driver.execute_script("return window.screen.height;")
    i = 1
    previous_height = 0
    continue_crawling = True

    while continue_crawling and len(tweets) < 10:
        body_height = driver.execute_script("return document.body.scrollHeight")
        articles = driver.find_elements(By.CSS_SELECTOR, config['tweet']['articles_path'])
        sleep(2)

        for article in articles:
            if article not in listContent and len(tweets) < 10:
                listContent.append(article)
                tweet = process_article(config,article)
                if tweet != None:

                    if mode == "Complet":
                        tweets.append(tweet)

                    elif mode == "Classique":
                        regex = r"([1-5]?[0-9]s|[1-5]?[0-9]m|(1?[0-9]|2[0-3])h)" # Regex pour la date (0 à 59s, 0 à 59m, 0 à 23h)
                        if re.match(regex, tweet['Date']):
                            tweets.append(tweet)
                        else:
                            continue_crawling = False
                            break

        driver.execute_script("window.scrollTo(0, {screen_height}*{i});".format(screen_height=screen_height, i=i))  
        if body_height < previous_height:
            break
        else:
            previous_height = (screen_height*i)
            i += 1
            sleep(1)

    with open("json/data.json","w") as data:
        json.dump(account,data)
    all.append(account)
    sleep(5)


def scrape_twitter_by_username(driver, config, request, mode, all):
    search_username = request['sq_query_value']

    # Redirection pour les query dans les user
    error_username = search_username[0]
    if error_username == "#" or error_username == '(':
        scrape_twitter_by_query(driver, config, request, mode, all)
        return

    url = "https://twitter.com/" + search_username
    sleep(3)

    search(driver, config, search_username)

    try:
        # Cherche puis click sur la photo de profil sinon passe directement par l'url
        profil = driver.find_element(By.XPATH, config['other_element']['profil_path'])
        profil.send_keys(Keys.ENTER)
        sleep(2)

        if driver.current_url != url:
            driver.get(url)
        sleep(5)
    except:
        driver.get(url)
        sleep(5)

    try: 
        # Gestion des comptes restricted
        error_account = driver.find_element(By.XPATH, config['other_element']['account_restricted_path']).get_attribute("textContent")
        if error_account == "Caution: This account is temporarily restricted":
            driver.find_element(By.XPATH, config['other_element']['input_account_restricted_path']).send_keys(Keys.ENTER)
            sleep(5)
        else:
            return 
    except:
        pass

    try: 
        # Gestion des noms de comptes avec un espace
        error_search = driver.find_element(By.XPATH, config['other_element']['error_search_path']).get_attribute("textContent")
        if error_search == "Hmm...this page doesn’t exist. Try searching for something else.":
            driver.find_element(By.XPATH, config['other_element']['error_search_input_path']).send_keys(Keys.ENTER)
            sleep(5)
            return
    except:
        pass

    crawler(driver, config, search_username,mode, all)


def scrape_twitter_by_query(driver, config, request, mode, all):
    search_query = request['sq_query_value']

    search(driver, config, search_query)

    search_element(driver, config['other_element']['latest_request_path']) # Click on "Latest_request"
    sleep(2)

    crawler(driver, config, search_query,mode, all)

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

def calculate_execution_time(start):
    end = time.time()
    elapsed_time = end - start
    hours, remainder = divmod(elapsed_time, 3600)
    minutes, seconds = divmod(remainder, 60)
    return "{:02}:{:02}:{:02}".format(int(hours), int(minutes), int(seconds))

# & ------------------------------------------------------------------------------------
# & Début du scrapping
# & ------------------------------------------------------------------------------------

def main():
    config = load_json('json/config.json')
    type_request = load_json('json/type_request.json')
    driver = setup_driver()

    account_email = 'd6071611@gmail.com'
    account_pseudo = 'D6071611Dylan'
    account_password = 'kpzRqSLWvKQ593'

    # account_email = 'jacheres_farineuse_0z@icloud.com'
    # account_pseudo = '0zF58596'
    # account_password = 'zU@m2%%GHeS47q'

    # mode = "Complet"
    mode = "Classique"

    login_twitter(driver, account_email, account_pseudo, account_password, config)

    # Variable pour envoyer tous les tweets des plusieurs requêtes dans un même JSON
    all = []

    for request in type_request:
        start_requete = time.time()
        
        try:
            match request['sq_query_type'].upper():
                case 'USER':
                    scrape_twitter_by_username(driver, config, request, mode, all)
                case 'QUERY':
                    scrape_twitter_by_query(driver, config, request, mode, all)

        except Exception as e:
            print(f"Une erreur s'est produite : {e}")
            continue

        query_execution_time = calculate_execution_time(start_requete)
        print("Temps écoulé pour la requête : " + query_execution_time)

        with open("json/all.json","w") as all_data:
            json.dump(all,all_data)

    driver.close()
    driver.quit()

    script_execution_time = calculate_execution_time(start)
    print("Temps écoulé en tout : " + script_execution_time)

    # ! Ne pas oublier d'enlever les 2 timers

if __name__ == "__main__":
    main()