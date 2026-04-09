import time, os, sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

URL = "https://electraferre.kubysoft.com/login"
USER = os.environ.get("KUBY_USER", "jesus@electraferre.es")
PASS = os.environ.get("KUBY_PASS", "Jegoru")
ACTION = os.environ.get("FICHAR_ACCION", "entrada")

def fichar():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 15)
    try:
        driver.get(URL)
        time.sleep(2)
        try:
            ei = wait.until(EC.presence_of_element_located((By.NAME, "email")))
            ei.send_keys(USER)
            driver.find_element(By.NAME, "password").send_keys(PASS)
            driver.find_element(By.XPATH, "//button[@type='submit']").click()
            time.sleep(3)
            print("Login OK")
        except:
            print("Ya logueado")
        ul = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//a[contains(@class,'dropdown-toggle')]//span[contains(text(),'JESUS GONZALEZ RUBIO')]/..")
        ))
        ul.click()
        time.sleep(1)
        css = "button.btn-controlHorarioMiniAcceso.btn-success" if ACTION=="entrada" else "button.btn-controlHorarioMiniAcceso.btn-danger"
        btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css)))
        btn.click()
        time.sleep(2)
        print(f"FICHADO: {ACTION.upper()}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        driver.quit()

if __name__ == "__main__":
    fichar()