import sys
from os.path import dirname, realpath
sys.path.insert(0, dirname(dirname(realpath(__file__))))

from Classes.Selenium import Selenium
from Classes.Mysql import Mysql

from selenium.webdriver.common.keys import Keys
from datetime import datetime, timedelta
from time import sleep

import time,json,re
import logging

logging.basicConfig(filename='./Log/crawl.log', encoding='utf-8', level=logging.INFO)

selenium = None

# Variables GLOBAL pour les Logs
count_total_tweets_crawl = 0
count_tweets_valid = 0
nbrequest = 0
count_profil_inactive = 0
start = time.time()

# today = datetime.now()
# today_18h = today.replace(hour=18,minute=0,second=0,microsecond=0)
# yesterday = datetime.now() - timedelta(days=1)
# yesterday_18h = yesterday.replace(hour=18,minute=0,second=0,microsecond=0)

def load_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def account_selection():
    accounts = load_json('./Ressources/Json/twitter_accounts.json')
    use_this_account = None
    for account in accounts:
        # Prends que les comptes qui n'ont aucun timecrawl attribué ou qui datent de plus de 2 JOURS
        if not account['lastCrawl'] or (datetime.now() - datetime.fromisoformat(account['lastCrawl'])) > timedelta(hours=47, minutes=59): 
            account['lastCrawl'] = datetime.now().isoformat()
            use_this_account = account
            break

    if not use_this_account:
        logging.info(f"\nAUCUN COMPTES N'EST DISPONIBLE\n")
        selenium.quit()
        sys.exit()  # Arrête complètement le programme
    
    # Mettre à jour le fichier json
    with open('./Ressources/Json/twitter_accounts.json', 'w') as f:
        json.dump(accounts, f)

    print(use_this_account)
    return use_this_account

def login_twitter(config):
    global selenium
    if selenium is not None:
        selenium.quit()
    
    selenium = Selenium("https://twitter.com/")
    sleep(5)

    account = account_selection()

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

# Cherche et remplit la barre de recherche
def search(config, query):
    fill = selenium.fill_input_by_xpath(config['navigation']['search_bar_right'], Keys.CONTROL + "a" + Keys.DELETE, clear=True)
    if not fill:
        selenium.fill_input_by_xpath(config['navigation']['search_bar_center'], Keys.CONTROL + "a" + Keys.DELETE, clear=True)
        selenium.fill_input_by_xpath(config['navigation']['search_bar_center'], query, submit=True)
    else:
        selenium.fill_input_by_xpath(config['navigation']['search_bar_right'], query, submit=True)
    sleep(3)

# Récupération de tous les éléments d'un tweet
def process_article(config, article, retweet_counter):
    global count_tweets_valid
    global count_total_tweets_crawl
    count_total_tweets_crawl += 1

    type = "Post"
    retweet_pinned = selenium.get_element_from_element_by_css_selector(article, config['tweet']['retweet_path'], get_attribute="textContent")

    if retweet_pinned:
        retweet_counter['count'] += 1
        print(f"Nombres de retweet: {retweet_counter['count']}")
        if retweet_counter['count'] == 10:
            return 'only_retweets'
        return    
    
    # Enlever les Pub des tweets
    ad = selenium.get_element_from_element_by_css_selector(article, config['tweet']['tweet_ad_path'], get_attribute="textContent")
    if ad:
        return

    content = selenium.get_element_from_element_by_css_selector(article, config['tweet']['content_path'], get_attribute="textContent") 
    # Si le tweet ne contient qu'une image, un gif ou une vidéo alors on l'ignore
    if not content:
        return
    
    date = selenium.get_element_from_element_by_css_selector(article, 'time', get_attribute="textContent") 
    date_datetime = selenium.get_element_from_element_by_css_selector(article, 'time', get_attribute="datetime") 
    pseudo = selenium.get_element_from_element_by_css_selector(article, config['tweet']['pseudo_path'], get_attribute="textContent") 
    username = selenium.get_element_from_element_by_css_selector(article, config['tweet']['username_path'], get_attribute="textContent") 
    tweetURL = selenium.get_element_from_element_by_css_selector(article, config['tweet']['tweetURL_path'], get_attribute="href") 

    extract = tweetURL.find("/status/")
    tweetID = tweetURL[extract+8:]

    tweet = {
        "Type": type,
        "TweetURL": tweetURL,
        "TweetID": tweetID,
        "Username": username,
        "Pseudo": pseudo,
        "Date": date,
        "Datetime": date_datetime,
        "Content": content
    }

    count_tweets_valid += 1

    return tweet

def handle_errors(config, request, MODE):
    if account_restricted(config):
        return False

    if retry_exists(config, request, MODE):
        return True

    if page_does_not_exist(config):
        return True
    
    if account_does_not_exist(config):
        return True

    return False

def account_restricted(config):
    restricted = selenium.click_element_by_xpath(config['errors']['input_account_restricted_path'])
    if restricted:
        print("Account restricted")
        sleep(5)
        return True
    return False

def retry_exists(config, request, MODE):
    retry = selenium.get_element_by_xpath(config['errors']['retry_button'])
    if retry:
        logging.info("Retry button appeared")
        selenium.click_element_by_xpath(config['errors']['retry_button'])
        sleep(1)
        selenium.click_element_by_xpath(config['navigation']['home'])
        sleep(1)
        selenium.reload()
        sleep(2)

        # Gestion quand l'on atteint la limite d'un compte
        unlock = selenium.get_element_by_xpath(config['errors']['unlock_limit'], get_text=True)
        if unlock == "Unlock more posts by subscribing":
            logout_and_login(config, request, MODE)
            return True

        sleep(5)
        scrapping_twitter(config, request, MODE)
        return True
    return False

def account_does_not_exist(config):
    error_account = selenium.get_element_by_xpath(config['errors']['account_restricted_path'],get_text=True)
    if error_account:
        logging.error(error_account)
        return True
    return False

def page_does_not_exist(config):
    error_page = selenium.get_element_by_xpath(config['errors']['error_search_input_path'])
    if error_page:
        logging.error("THIS PAGE DOES NOT EXIST")
        selenium.click_element_by_xpath(config['navigation']['home'])
        sleep(5)
        return True
    return False

def logout_and_login(config, request, MODE):
    # Click on profile picture to logout
    selenium.click_element_by_xpath("/html/body/div[1]/div/div/div[2]/header/div/div/div/div[2]/div/div/div[1]/div/div[2]/div/div[2]/div/div")
    sleep(1)
    # Click on Log Out
    selenium.click_element_by_xpath("/html/body/div[1]/div/div/div[1]/div[2]/div/div/div[2]/div/div[2]/div/div/div/div/div/a[2]")
    sleep(1)
    # Click on 2nd Log Out
    selenium.click_element_by_xpath("/html/body/div[1]/div/div/div[1]/div[2]/div/div/div/div/div/div[2]/div[2]/div[2]/div[1]")
    sleep(1)

    logging.info("\nACCOUNT SWITCH\n")
    login_twitter(config)
    scrapping_twitter(config, request, MODE)
    
def get_new_id(config):

    xpaths = [
        config['navigation']['follow_btn_1'],
        config['navigation']['follow_btn_2'],
        config['navigation']['follow_btn_3']
    ]

    for xpath in xpaths:
        btn_follow = selenium.get_element_attribute_by_xpath(xpath, get_attribute='data-testid')
        if not btn_follow:
            continue
        return re.split('-follow|-unfollow', btn_follow)[0]
    return None

def crawler(config, MODE, request, source):
    global count_profil_inactive
    global nbrequest

    listContent = [] # Liste de tous les tweets récupéré, même les Pinned, Ad, Retweet
    tweets = [] # Liste trié des tweets que l'on veut
    first_tweet = None
    retweet_counter = {'count': 0}  # Utilisation d'un dictionnaire pour le compteur
    save_id = get_new_id(config) # Récupération de l'id de l'utilisateur

    screen_height = selenium.execute_script("return window.screen.height;")
    i = 1
    previous_height = 0
    continue_crawling = True

    # while continue_crawling and (len(tweets) < 10 if mode else True):
    while continue_crawling and len(tweets) < 10:
        body_height = selenium.execute_script("return document.body.scrollHeight")
        articles = selenium.get_elements_by_css_selector(config['tweet']['articles_path'])
        for article in articles:
            if article not in listContent and len(tweets) < 10:
                listContent.append(article)
                tweet = process_article(config,article,retweet_counter)

                if tweet == 'only_retweets':
                    print("Account has only retweets. Stopping crawler.")
                    continue_crawling = False
                    break
                
                if tweet != None:
                    # Stockage du premier tweet pour vérifier l'activité du compte
                    if not first_tweet:
                        first_tweet = tweet 
                        # Conversion de la chaîne de caractères en objet datetime
                        tweet_date_convert = datetime.strptime(tweet['Datetime'], "%Y-%m-%dT%H:%M:%S.%fZ")
                        current_date = datetime.now()
                        one_year_ago = current_date - timedelta(days=365)
                        if tweet_date_convert < one_year_ago:
                            count_profil_inactive += 1
                            print("La date récupérée est de plus d'un an en arrière.")
                            # ? Pour faire une gestion des comptes inactifs
                                
                    if MODE == "Complet":
                        tweets.append(tweet)

                    elif MODE == "Classique":
                        regex = r"([1-5]?[0-9]s|[1-5]?[0-9]m|(1?[0-9]|2[0-3])h)" # Regex pour la date (0 à 59s, 0 à 59m, 0 à 23h)
                        if re.match(regex, tweet['Date']):
                            print("TWEET VALID")
                            tweets.append(tweet)
                        else:
                            print("TWEET +24h")
                            continue_crawling = False
                            break
                        
                        # ? Autre façon de faire pour vérifier si le tweet est récent
                        # global today_18h
                        # global yesterday_18h
                        # tweet_date_convert = datetime.strptime(tweet['Datetime'], "%Y-%m-%dT%H:%M:%S.%fZ")
                        # if yesterday_18h <= tweet_date_convert <= today_18h:
                        #     print("TWEET VALID")
                        #     tweets.append(tweet)
                        # else:
                        #     print("TWEET +24h")
                        #     continue_crawling = False
                        #     break


        # Scroll jusqu'à avoir 10 tweets
        selenium.execute_script("window.scrollTo(0, {screen_height}*{i});".format(screen_height=screen_height, i=i))  
        if body_height < previous_height:
            break
        else:
            previous_height = (screen_height*i)
            i += 1
            sleep(1)
    pourcentage = round((count_profil_inactive / nbrequest) * 100, 2)
    logging.info(f"Nombres de comptes inactive : {count_profil_inactive}")
    logging.info(f"Pourcentage de comptes inactive  : {pourcentage}%")
    logging.info(f"Nombres de tweets pour cette requete : {len(tweets)}")

    print(f"{len(tweets)} tweets récupéré")

    for tweet in tweets:
        user_id = save_id   

        tweet_id = Mysql.tweet_exists(local_id=tweet['TweetID'])
        if tweet_id:
            print("Tweet ID", tweet_id)
            if MODE == "Classique": 
                break 
            elif MODE == "Complet":
                continue 
        print("INSERT Tweet")
        sql = """INSERT INTO tweets (id,profil_id,content,publication_date,id_twitter_profil) VALUES (%s,%s,%s,%s,%s)"""
        params = (tweet['TweetID'],request['id'],tweet['Content'],tweet["Datetime"],user_id)
        Mysql.execute_insert(sql,params=params)

def calculate_execution_time(start):
    end = time.time()
    elapsed_time = end - start
    hours, remainder = divmod(elapsed_time, 3600)
    minutes, seconds = divmod(remainder, 60)
    return "{:02}:{:02}:{:02}".format(int(hours), int(minutes), int(seconds))


def scrapping_twitter(config, request, MODE):
    global nbrequest
    global start

    search_username = request['username']

    # Enlève les requêtes qui ne sont pas des USERS
    if search_username[0] in ["#", "("]:
        logging.error("Ce n'est pas un username")
        return
    
    start_requete = time.time()
    logging.info(request)

    url = "https://twitter.com/" + search_username
    sleep(3)

    search(config, search_username)

    # Cherche puis click sur la photo de profil sinon passe directement par l'URL
    selenium.click_element_by_xpath(config['navigation']['profil_path'])
    sleep(2)
    if selenium.get_current_url() != url:
        selenium.open(url)
        sleep(5)

    # Gestions des différentes erreurs
    if handle_errors(config,request,MODE):
        return   
    
    print("Passe la gestion d'erreurs")
    nbrequest += 1
    logging.info(f'Nombres de requêtes (valide) effectué : {nbrequest}')

    source =  'user=' + search_username
    crawler(config, MODE, request, source)

    if nbrequest % 100 == 0:
        sleep(60)

    query_execution_time = calculate_execution_time(start_requete)
    logging.info(f'Temps écoulé pour la requête : {query_execution_time}')
    logging.warning(f'Temps passé pour l\'instant : {calculate_execution_time(start)}')
    sleep(5)

# & ------------------------------------------------------------------------------------
# & Début du scrapping
# & ------------------------------------------------------------------------------------
def main():
    global selenium
    global count_total_tweets_crawl
    global count_tweets_valid
    lancement_script = datetime.now()

    # Requête SQL qui permet de récupérer les requêtes que l'on veut
    requests = Mysql.execute_select_array("""
    SELECT id, username FROM profiles ORDER BY id
    """,close=True)
    
    config = load_json('./Ressources/Json/selenium_xpaths.json')

    MODE = "Complet"
    # MODE = "Classique"

    login_twitter(config)

    for request in requests:        
        print(request)
        try:
            scrapping_twitter(config, request, MODE)
            logging.warning(f'Nombres de tweets total potentiel lu : {count_total_tweets_crawl}')
            logging.warning(f'Nombres de tweets valide : {count_tweets_valid}\n')

        except Exception as e:
            print(f"Une erreur s'est produite : {e}")
            continue

    script_execution_time = calculate_execution_time(start)
    logging.info(f'\nLancement {lancement_script}\nFin {datetime.now()}\nTemps écoulé en tout : {script_execution_time}')
    if selenium is not None:
        selenium.quit()

if __name__ == "__main__":
    main()