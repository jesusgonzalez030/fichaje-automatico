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
        print("URL: " + page.url + " | Titulo: " + page.title())

        # Login con selectores correctos: id=email, name=password, button#btn-login
        print("Esperando formulario login...")
        page.wait_for_selector("#email", timeout=15000)
        print("Formulario encontrado, haciendo login...")
        page.fill("#email", USER)
        page.fill("#password", PASS)
        page.click("#btn-login")
        time.sleep(4)
        print("Login enviado - URL: " + page.url)

        # Esperar a que cargue el dashboard
        page.wait_for_selector("span.hidden-xs", timeout=15000)
        print("Dashboard cargado")

        # Abrir dropdown del usuario
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

        # Esperar y clicar boton de fichaje
        css = "button.btn-controlHorarioMiniAcceso.btn-success" if ACTION == "entrada" else "button.btn-controlHorarioMiniAcceso.btn-danger"
        page.wait_for_selector(css, timeout=10000)
        page.click(css)
        time.sleep(2)
        print("FICHADO OK: " + ACTION.upper())
        browser.close()

if __name__ == "__main__":
    fichar()
