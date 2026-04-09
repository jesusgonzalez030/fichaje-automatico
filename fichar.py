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

        if page.locator("input[name=email]").count() > 0:
            page.fill("input[name=email]", USER)
            page.fill("input[name=password]", PASS)
            page.click("button[type=submit]")
            page.wait_for_load_state("networkidle")
            print("Login OK")
        else:
            print("Ya logueado")

        # Abrir dropdown
        page.evaluate("""() => {
            const spans = document.querySelectorAll("span.hidden-xs");
            for (const s of spans) {
                if (s.textContent.includes("JESUS")) {
                    let el = s;
                    for (let i=0; i<6; i++) {
                        el = el.parentElement;
                        if (el.tagName === "A") { el.click(); break; }
                    }
                    break;
                }
            }
        }""")
        page.wait_for_timeout(2000)
        print("Dropdown abierto")

        # Clic en boton con JS
        css_class = "btn-success" if ACTION == "entrada" else "btn-danger"
        js = """(css) => {
            const btn = document.querySelector("button.btn-controlHorarioMiniAcceso." + css);
            if (btn) { btn.click(); return "OK:" + btn.textContent.trim(); }
            const all = document.querySelectorAll("button.btn-controlHorarioMiniAcceso");
            return "NOENCONTRADO:" + Array.from(all).map(b=>b.className+"|"+b.textContent.trim()).join(",");
        }"""
        result = page.evaluate(js, css_class)
        print("Resultado: " + result)

        if not result.startswith("OK"):
            print("ERROR: boton no encontrado - " + result)
            sys.exit(1)

        page.wait_for_timeout(2000)
        print("FICHADO: " + ACTION.upper())
        browser.close()

if __name__ == "__main__":
    fichar()