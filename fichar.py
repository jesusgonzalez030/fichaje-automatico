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

        # Abrir dropdown del usuario con JavaScript directo
        page.evaluate("""() => {
            const spans = document.querySelectorAll('span.hidden-xs');
            for (const s of spans) {
                if (s.textContent.trim().includes('JESUS')) {
                    let el = s;
                    for (let i = 0; i < 6; i++) {
                        el = el.parentElement;
                        if (el.tagName === 'A') { el.click(); break; }
                    }
                    break;
                }
            }
        }""")
        page.wait_for_timeout(2000)
        print("Dropdown abierto")

        # Clic en botón con JavaScript directo (igual que funciona manualmente)
        if ACTION == "entrada":
            css_class = "btn-success"
        else:
            css_class = "btn-danger"

        result = page.evaluate(f"""() => {{
            const btn = document.querySelector('button.btn-controlHorarioMiniAcceso.{css_class}');
            if (btn) {{ btn.click(); return 'OK: ' + btn.textContent.trim(); }}
            // Listar todos los botones disponibles para debug
            const btns = document.querySelectorAll('button.btn-controlHorarioMiniAcceso');
            return 'NO ENCONTRADO - disponibles: ' + Array.from(btns).map(b => b.className + '|' + b.textContent.trim()).join(', ');
        }}""")
        print(f"Resultado click: {{result}}")

        if not result.startswith("OK"):
            print("ERROR: No se encontro el boton")
            sys.exit(1)

        page.wait_for_timeout(2000)
        print(f"FICHADO: {ACTION.upper()}")
        browser.close()

if __name__ == "__main__":
    fichar()