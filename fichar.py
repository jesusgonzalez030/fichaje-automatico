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
        print("Navegando a " + URL)
        page.goto(URL, wait_until="domcontentloaded")
        time.sleep(3)

        # Login siempre con usuario y password
        print("Haciendo login con usuario: " + USER)
        page.wait_for_selector("input[name=email]", timeout=10000)
        page.fill("input[name=email]", USER)
        page.fill("input[name=password]", PASS)
        page.click("button[type=submit]")
        time.sleep(4)
        print("Login enviado - URL: " + page.url)

        # Abrir dropdown del usuario
        page.wait_for_selector("span.hidden-xs", timeout=10000)
        page.evaluate("""() => {
            const spans = document.querySelectorAll('span.hidden-xs');
            for (const s of spans) {
                if (s.textContent.includes('JESUS')) {
                    let el = s;
                    for (let i=0; i<6; i++) {
                        el = el.parentElement;
                        if (el.tagName === 'A') { el.click(); break; }
                    }
                    break;
                }
            }
        }""")
        time.sleep(2)
        print("Dropdown abierto")

        # Clic en boton entrada o salida
        css = "btn-success" if ACTION == "entrada" else "btn-danger"
        page.wait_for_selector("button.btn-controlHorarioMiniAcceso." + css, timeout=10000)
        page.click("button.btn-controlHorarioMiniAcceso." + css)
        time.sleep(2)
        print("FICHADO OK: " + ACTION.upper())
        browser.close()

if __name__ == "__main__":
    fichar()
