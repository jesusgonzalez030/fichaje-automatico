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
        print(f"Abriendo {URL}...")
        page.goto(URL, wait_until="networkidle")

        # Login si hace falta
        if page.locator("input[name=email]").count() > 0:
            page.fill("input[name=email]", USER)
            page.fill("input[name=password]", PASS)
            page.click("button[type=submit]")
            page.wait_for_load_state("networkidle")
            print("Login OK")
        else:
            print("Ya logueado")

        # Abrir dropdown del usuario clicando en cualquier elemento del nav con el nombre
        page.evaluate("""
            const spans = document.querySelectorAll("span.hidden-xs");
            for (const s of spans) {
                if (s.textContent.trim().includes("JESUS GONZALEZ")) {
                    let el = s;
                    for (let i=0; i<5; i++) {
                        el = el.parentElement;
                        if (el.tagName === "A") { el.click(); break; }
                    }
                    break;
                }
            }
        """)
        page.wait_for_timeout(1500)
        print("Dropdown abierto")

        # Clic en entrada o salida
        if ACTION == "entrada":
            css = "button.btn-controlHorarioMiniAcceso.btn-success"
        else:
            css = "button.btn-controlHorarioMiniAcceso.btn-danger"

        page.locator(css).click()
        page.wait_for_timeout(2000)
        print(f"FICHADO: {ACTION.upper()}")
        browser.close()

if __name__ == "__main__":
    fichar()