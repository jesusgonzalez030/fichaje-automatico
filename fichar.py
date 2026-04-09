import os, sys
from playwright.sync_api import sync_playwright

URL = "https://electraferre.kubysoft.com/login"
USER = os.environ.get("KUBY_USER", "")
PASS = os.environ.get("KUBY_PASS", "")
ACTION = os.environ.get("FICHAR_ACCION", "entrada")

def fichar():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print("Abriendo " + URL)
        page.goto(URL, wait_until="networkidle")
        page.screenshot(path="01_inicio.png")
        print("Titulo pagina: " + page.title())
        print("URL actual: " + page.url)

        # Siempre intentar login
        try:
            page.wait_for_selector("input[name=email]", timeout=5000)
            print("Formulario login encontrado, haciendo login...")
            page.fill("input[name=email]", USER)
            page.fill("input[name=password]", PASS)
            page.screenshot(path="02_antes_login.png")
            page.click("button[type=submit]")
            page.wait_for_load_state("networkidle")
            page.screenshot(path="03_despues_login.png")
            print("Login OK - URL: " + page.url)
        except:
            print("Sin formulario login - URL: " + page.url)

        page.screenshot(path="04_dashboard.png")
        print("Titulo tras login: " + page.title())

        # Ver todos los botones disponibles en la pagina
        botones = page.evaluate("""() => {
            const btns = document.querySelectorAll("button");
            return Array.from(btns).map(b => b.className + "|" + b.textContent.trim().substring(0,30)).join("\n");
        }""")
        print("Botones en pagina:\n" + botones)

        # Ver si hay dropdown toggle
        dropdown = page.evaluate("""() => {
            const items = document.querySelectorAll(".dropdown-toggle");
            return Array.from(items).map(i => i.tagName + "|" + i.textContent.trim().substring(0,40)).join("\n");
        }""")
        print("Dropdowns disponibles:\n" + dropdown)

        browser.close()

if __name__ == "__main__":
    fichar()