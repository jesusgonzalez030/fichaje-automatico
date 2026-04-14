import os, sys, time
from playwright.sync_api import sync_playwright
from datetime import datetime

URL = "https://electraferre.kubysoft.com/login"
USER = os.environ.get("KUBY_USER", "")
PASS = os.environ.get("KUBY_PASS", "")
ACTION = os.environ.get("FICHAR_ACCION", "entrada")

def es_dia_libre():
    hoy = datetime.now().strftime("%d/%m/%Y")
    try:
        with open("festivos.txt", "r") as f:
            for linea in f:
                linea = linea.strip()
                if linea and not linea.startswith("#"):
                    if linea == hoy:
                        return True
    except:
        pass
    return False

def fichar():
    hoy = datetime.now().strftime("%d/%m/%Y")
    print("Fecha: " + hoy + " | Accion: " + ACTION)

    if es_dia_libre():
        print("DIA LIBRE - no se ficha")
        sys.exit(0)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Login - usar selectores exactos conocidos
        print("Navegando a login...")
        page.goto(URL, wait_until="domcontentloaded")
        time.sleep(2)

        print("Rellenando formulario...")
        page.wait_for_selector("#email", timeout=10000)
        page.fill("#email", USER)
        page.fill("#password", PASS)
        page.click("#btn-login")
        time.sleep(4)
        print("URL tras login: " + page.url)

        # Verificar sesion buscando el nombre del usuario
        page.wait_for_selector("span.hidden-xs", timeout=15000)
        nombre = page.locator("span.hidden-xs").first.inner_text()
        print("Usuario logueado: " + nombre)

        if "JESUS" not in nombre.upper():
            print("ERROR: Login fallido")
            sys.exit(1)

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

        # Verificar qué botón hay (entrada verde o salida rojo)
        btn_entrada = page.locator("button.btn-controlHorarioMiniAcceso.btn-success")
        btn_salida = page.locator("button.btn-controlHorarioMiniAcceso.btn-danger")

        tiene_entrada = btn_entrada.count() > 0
        tiene_salida = btn_salida.count() > 0
        print("Boton entrada visible: " + str(tiene_entrada))
        print("Boton salida visible: " + str(tiene_salida))

        if ACTION == "entrada" and tiene_entrada:
            btn_entrada.click()
            print("FICHADO OK: ENTRADA")
        elif ACTION == "salida" and tiene_salida:
            btn_salida.click()
            print("FICHADO OK: SALIDA")
        elif ACTION == "entrada" and not tiene_entrada:
            print("AVISO: Boton entrada no visible - ya fichada o fuera de horario")
        elif ACTION == "salida" and not tiene_salida:
            print("AVISO: Boton salida no visible - ya fichada o fuera de horario")

        time.sleep(2)
        browser.close()

if __name__ == "__main__":
    fichar()
