import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, WebDriverException, TimeoutException, NoAlertPresentException

from Classes.Config import Config

class Selenium:

    def __init__(self, url=None, sleep_duration=None, driver=Config.SELENIUM_DRIVER, width=1350, height=750, private_mode=True, proxy=None):
        if driver == "chrome":
            options = Options()
            if proxy:
                options.add_argument('--proxy-server={0}'.format(proxy))
            if private_mode:
                options.add_argument("--incognito")
            try:
                self.driver = webdriver.Chrome(service=Service(r"C:\Users\dev06\Documents\chromedriver.exe"), options=options)
            except WebDriverException as e:
                print(e)
                time.sleep(10)
                self.driver = webdriver.Chrome(service=Service(r"C:\Users\dev06\Documents\chromedriver.exe"), options=options)

        self.is_free = True
        self.driver.set_page_load_timeout(Config.SELENIUM_LOAD_TIMEOUT)
        self.driver.set_script_timeout(Config.SELENIUM_SCRIPT_TIMEOUT)
        if not private_mode:
            self.driver.set_window_size(width, height)

        if sleep_duration is not None:
            time.sleep(sleep_duration)
        if url is not None:
            self.open(url)

    def open(self, url, nb_retry=0):
        MAX_NB_RETRY = 5
        try:
            self.driver.get(url)
            return True
        except TimeoutException as e:
            print("SeleniumTimeout Open " + url + " !")
            return False
        except ConnectionRefusedError:
            print("SeleniumConnectionRefused Open " + url + " !")
            return False
        except ConnectionResetError as e:
            print(e)
            print("SeleniumConnectionReset Open " + url + " !")
            return False
        except WebDriverException:
            print("SeleniumWebDriverException " + url + " !")
            if nb_retry >= MAX_NB_RETRY:
                print("Cancel")
                return False
            return self.open(url, nb_retry=nb_retry + 1)
    
    def get_current_url(self):
        return self.driver.current_url
    
    def quit(self):
        try:
            self.driver.close()
            self.driver.quit()
        except WebDriverException:
            self.wait(30)
            self.quit()

    def close(self):
        self.quit()
        
    def reload(self):
        self.driver.refresh()

    def get_elements_by_xpath(self, xpath):
        try:
            return self.driver.find_elements(By.XPATH, xpath)
        except TimeoutException:
            print("TimeoutException " + str(xpath))
            return []
    
    def get_element_by_xpath(self, xpath, get_text=False):
        try:
            element = self.driver.find_element(By.XPATH, xpath)
        except NoSuchElementException:
            element = None
        except StaleElementReferenceException:
            element = None

        if not get_text:
            return element

        if element is None:
            return ""
        return str(element.text.encode("utf8"), "utf8")

    def get_element_attribute_by_xpath(self, xpath, get_text=False, get_attribute=None, default_value=""):
        try:
            element = self.get_element_by_xpath(xpath)
        except NoSuchElementException:
            print("NoSuchElementException " + xpath)
            element = None
        except StaleElementReferenceException:
            print("StaleElementReferenceException " + xpath)
            element = None
        except ConnectionResetError:
            print("ConnectionResetError " + xpath)
            element = None
        except TimeoutException:
            print("TimeoutException " + xpath)
            element = None

        if not get_text and get_attribute is None:
            return element

        # On veut récupérer la valeur d'un attribut
        if get_attribute is not None:
            if element is None:
                return default_value

            try:
                return element.get_attribute(get_attribute)
            except StaleElementReferenceException:
                return default_value

        if element is None:
            return default_value

        try:
            return str(element.text.encode("utf8"), "utf8")
        except StaleElementReferenceException:
            print("StaleElementReferenceException " + xpath)
            return default_value

    def click_element_by_xpath(self, xpath):
        try:
            elm = self.get_element_by_xpath(xpath=xpath)
            if elm is not None:
                self.driver.execute_script("arguments[0].click();", elm)
                return True
        except Exception as e:
            print(f"An error occurred: {e}")
            return False
        return False
    
    def get_element_from_element_by_xpath(self, web_element, xpath, get_text=False, get_attribute=None, default_value=""):
        if xpath == ".":
            element = web_element
        else:
            try:
                element = web_element.find_element(By.XPATH, xpath)
            except Exception:
                element = None

        # On veut récupérer le WebElement
        if not get_text and get_attribute is None:
            return element

        # On veut récupérer la valeur d'un attribut
        if get_attribute is not None:
            if element is None:
                return default_value

            try:
                return element.get_attribute(get_attribute)
            except StaleElementReferenceException:
                return default_value

        return self.get_element_text(element, default_value=default_value)
    
    def fill_input_by_xpath(self, xpath, input_value, submit=False, clear=False):
            element = self.get_element_by_xpath(xpath)
            if element is None:
                return False

            try:
                if clear:
                    element.clear()
                element.send_keys(input_value)
                if submit:
                    element.submit()
            except TimeoutException:
                print("Timeout dans le remplissage du formulaire " + str(xpath) + " avec la valeur " + str(input_value))
                return False
            except ConnectionResetError:
                print("ConnectionResetError dans le remplissage du formulaire " + str(xpath) + " avec la valeur " + str(input_value))
                return False
            except StaleElementReferenceException:
                print("StaleElementReferenceException dans le remplissage du formulaire " + str(xpath) + " avec la valeur " + str(input_value))
                return False
            return True
    
    def get_elements_by_css_selector(self, css_selector):
        try:
            return self.driver.find_elements(By.CSS_SELECTOR, css_selector)
        except TimeoutException:
            print("TimeoutException " + str(css_selector))
            return []
        
    def get_element_by_css_selector(self, css_selector, get_text=False, get_attribute=None, default_value=""):
        try:
            element = self.driver.find_element(By.CSS_SELECTOR, css_selector)
        except NoSuchElementException:
            print("NoSuchElementException " + css_selector)
            element = None
        except StaleElementReferenceException:
            print("StaleElementReferenceException " + css_selector)
            element = None
        except ConnectionResetError:
            print("ConnectionResetError " + css_selector)
            element = None
        except TimeoutException:
            print("TimeoutException " + css_selector)
            element = None

        if not get_text and get_attribute is None:
            return element

        # On veut récupérer la valeur d'un attribut
        if get_attribute is not None:
            
            try:
                return element.get_attribute(get_attribute)
            except StaleElementReferenceException:
                return default_value

        if element is None:
            return default_value

        try:
            return str(element.text.encode("utf8"), "utf8")
        except StaleElementReferenceException:
            print("StaleElementReferenceException " + css_selector)
            return default_value

    def click_element_by_css_selector(self, css_selector):
        try:
            elm = self.get_element_by_css_selector(css_selector)
            if elm is not None:
                self.driver.execute_script("arguments[0].click();", elm)
                return True
        except Exception as e:
            print(f"An error occurred: {e}")
            return False
        return False
    
    def get_element_from_element_by_css_selector(self, web_element, css_selector, get_text=False, get_attribute=None, default_value=""):
        if css_selector == ".":
            element = web_element
        else:
            try:
                element = web_element.find_element(By.CSS_SELECTOR, css_selector)
            except Exception:
                element = None

        # On veut récupérer le WebElement
        if not get_text and get_attribute is None:
            return element

        # On veut récupérer la valeur d'un attribut
        if get_attribute is not None:
            if element is None:
                return default_value

            try:
                return element.get_attribute(get_attribute)
            except StaleElementReferenceException:
                return default_value

        return self.get_element_text(element, default_value=default_value)
    
    def fill_input_by_css_selector(self, input_csspath, input_value, submit=False, clear=False):
        element = self.get_element_by_css_selector(input_csspath)
        if element is None:
            return False

        try:
            if clear:
                element.clear()
            element.send_keys(input_value)
            if submit:
                element.submit()
        except TimeoutException:
            print("Timeout dans le remplissage du formulaire " + str(input_csspath) + " avec la valeur " + str(input_value))
            return False
        except ConnectionResetError:
            print("ConnectionResetError dans le remplissage du formulaire " + str(input_csspath) + " avec la valeur " + str(input_value))
            return False
        except StaleElementReferenceException:
            print("StaleElementReferenceException dans le remplissage du formulaire " + str(input_csspath) + " avec la valeur " + str(input_value))
            return False
        return True

    def execute_script(self, script, args=None):
        if args is not None:
            try:
                return self.driver.execute_script(script, args)
            except StaleElementReferenceException:
                print("StaleElementReferenceException " + script)
                return False
        return self.driver.execute_script(script, args)

    def remove_element(self, elmt):
        return self.execute_script("arguments[0].remove();", elmt)

    def scroll_to_element(self, elmt):
        return self.execute_script("arguments[0].scrollIntoView(true);", elmt)

    def scroll_to_down(self):
        return self.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
    def get_element_text(element, default_value=""):
        if element is None:
            return default_value
        try:
            return str(element.text.encode("utf8"), "utf8")
        except StaleElementReferenceException:
            return default_value

    def is_available(self):
        return self.is_free

    def release(self):
        self.is_free = True

    def acquire(self):
        self.is_free = False