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
        print("Titulo: " + page.title())
        print("URL: " + page.url)

        # Buscar y hacer login con email/password
        email_count = page.locator("input[name=email]").count()
        print("Campos email encontrados: " + str(email_count))

        if email_count > 0:
            page.fill("input[name=email]", USER)
            page.fill("input[name=password]", PASS)
            page.click("button[type=submit]")
            time.sleep(4)
            print("Login enviado - URL: " + page.url)
        else:
            # Intentar con selector alternativo
            inputs = page.locator("input").count()
            print("Total inputs en pagina: " + str(inputs))
            # Forzar login via URL directa con parametros
            page.goto("https://electraferre.kubysoft.com/dashboard", wait_until="domcontentloaded")
            time.sleep(2)
            print("URL tras goto dashboard: " + page.url)
            if "login" in page.url:
                print("Redirigido a login, buscando formulario...")
                page.wait_for_selector("form", timeout=5000)
                inputs2 = page.locator("input").all()
                for inp in inputs2:
                    tp = inp.get_attribute("type") or ""
                    nm = inp.get_attribute("name") or ""
                    print("Input encontrado: type=" + tp + " name=" + nm)

        # Ver estado final
        print("URL final: " + page.url)
        print("Titulo final: " + page.title())

        # Contar botones de fichar
        btns = page.locator("button.btn-controlHorarioMiniAcceso").count()
        print("Botones fichaje encontrados: " + str(btns))

        if btns == 0:
            # Mostrar todos los botones para debug
            all_btns = page.locator("button").all()
            for b in all_btns[:20]:
                cls = b.get_attribute("class") or ""
                txt = b.inner_text()[:30] if b.is_visible() else "[hidden]"
                print("BTN: " + cls[:50] + " | " + txt)

        browser.close()

if __name__ == "__main__":
    fichar()
