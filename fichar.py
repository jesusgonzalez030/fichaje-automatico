import os, sys, time
from playwright.sync_api import sync_playwright

URL = "https://electraferre.kubysoft.com/login"
USER = os.environ.get("KUBY_USER", "")
PASS = os.environ.get("KUBY_PASS", "")
ACTION = os.environ.get("FICHAR_ACCION", "entrada")

def fichar():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print(f"Abriendo {URL}...")
        page.goto(URL)
        page.wait_for_timeout(2000)

        # Login si hace falta
        if page.locator("input[name=email]").count() > 0:
            page.fill("input[name=email]", USER)
            page.fill("input[name=password]", PASS)
            page.click("button[type=submit]")
            page.wait_for_timeout(3000)
            print("Login OK")
        else:
            print("Ya estaba logueado")

        # Abrir dropdown del usuario
        page.locator("a.dropdown-toggle:has(span.hidden-xs)").click()
        page.wait_for_timeout(1000)
        print("Dropdown abierto")

        # Clic en entrada o salida
        if ACTION == "entrada":
            btn = page.locator("button.btn-controlHorarioMiniAcceso.btn-success")
        else:
            btn = page.locator("button.btn-controlHorarioMiniAcceso.btn-danger")

        btn.click()
        page.wait_for_timeout(2000)
        print(f"FICHADO correctamente: {ACTION.upper()}")
        browser.close()

if __name__ == "__main__":
    fichar()