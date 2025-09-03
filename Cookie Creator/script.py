from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time
import os
from webdriver_manager.chrome import ChromeDriverManager
import random
import threading
from queue import Queue
import shutil



LIVESTREAM_URL = input("Livestream URL: ") #"https://www.youtube.com/watch?v=dQkgHmrvabY"  # replace with your livestream
ACCOUNTS_FILE = "accounts.txt"  # email:password per line
COOKIES_DIR = "cookies"  

# CONFIG
MAX_THREADS = int(input("Max Threads: ")) #3            # maximum concurrent threads
LOOP_FOREVER = bool(input("Infinite Loop True/False: "))#False       # True = keep refreshing forever, False = capture cookies once

account_queue = Queue()


def setup_driver():
    chrome_options = Options()
    # chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--profile-directory=Default")
    chrome_options.add_argument("--disable-plugins-discovery")
    chrome_options.add_argument("--mute-audio")

    prefs = {
        "profile.managed_default_content_settings.images": 2,
        "profile.managed_default_content_settings.stylesheets": 2,
        "profile.managed_default_content_settings.fonts": 2
    }
    chrome_options.add_experimental_option("prefs", prefs)

    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
    chrome_options.add_argument(f"user-agent={user_agent}")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver


def login_to_youtube(driver, email, password):
    driver.get("https://www.youtube.com/account")
    try:
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "identifierId"))
        )
        email_input.send_keys(email)
        time.sleep(random.uniform(1, 2))
        email_input.send_keys(Keys.ENTER)

        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "Passwd"))
        )
        password_input.send_keys(password)
        time.sleep(random.uniform(1, 2))
        password_input.send_keys(Keys.ENTER)

        try:
            WebDriverWait(driver, 30).until(EC.url_contains("youtube.com"))
            print(f"[{email}] Login successful")
        except:
            print(f"[{email}] Possible CAPTCHA. Complete manually.")
            time.sleep(60)
            driver.get("https://www.youtube.com")
    except Exception as e:
        print(f"[{email}] Login issue: {e}")
        return False
    return True


def open_livestream(driver, email):
    driver.get(LIVESTREAM_URL)
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "video")))
        print(f"[{email}] Opened livestream: {LIVESTREAM_URL}")
        time.sleep(random.uniform(2, 4))
    except Exception as e:
        print(f"[{email}] Error loading livestream: {e}")
        return False
    return True


def save_cookies_file(email, cookie_str):
    """Save each account's cookies into its own file in cookies/"""
    safe_email = email.replace("@", "_at_").replace(":", "_")
    filepath = os.path.join(COOKIES_DIR, f"{safe_email}.txt")
    with open(filepath, "w") as f:
        f.write(cookie_str)
    print(f"[{email}] Cookies saved to {filepath}")


def capture_cookies(driver, email):
    cookies = driver.get_cookies()
    cookie_str = ";".join([f"{c['name']}={c['value']}" for c in cookies])
    save_cookies_file(email, cookie_str)
    return cookie_str


def account_worker():
    while not account_queue.empty():
        email, password = account_queue.get()
        driver = setup_driver()
        try:
            if not login_to_youtube(driver, email, password):
                return

            time.sleep(5)
            if not open_livestream(driver, email):
                return

            capture_cookies(driver, email)

            if LOOP_FOREVER:
                while True:
                    time.sleep(60)
                    driver.refresh()
                    capture_cookies(driver, email)
        except KeyboardInterrupt:
            print(f"[{email}] Stopping thread.")
        finally:
            driver.quit()
            account_queue.task_done()


def main():
    # Ensure cookies dir exists & clear it
    if os.path.exists(COOKIES_DIR):
        shutil.rmtree(COOKIES_DIR)
    os.makedirs(COOKIES_DIR)

    if not os.path.exists(ACCOUNTS_FILE):
        print(f"{ACCOUNTS_FILE} not found.")
        return

    with open(ACCOUNTS_FILE, "r") as f:
        accounts = [line.strip() for line in f if ":" in line]

    for account in accounts:
        email, password = account.split(":", 1)
        account_queue.put((email, password))

    threads = []
    for _ in range(min(MAX_THREADS, len(accounts))):
        t = threading.Thread(target=account_worker)
        t.start()
        threads.append(t)
        time.sleep(2)  # stagger thread starts

    account_queue.join()

    for t in threads:
        t.join()


if __name__ == "__main__":
    main()