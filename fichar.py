import os, sys, time
from playwright.sync_api import sync_playwright
from datetime import datetime

URL = "https://electraferre.kubysoft.com/login"
USER = os.environ.get("KUBY_USER", "")
PASS = os.environ.get("KUBY_PASS", "")
ACTION = os.environ.get("FICHAR_ACCION", "entrada")

# Hora objetivo en minutos desde medianoche (hora España)
HORA_ENTRADA = 7 * 60 + 50   # 07:50 = 470 minutos
HORA_SALIDA = 15 * 60 + 3    # 15:03 = 903 minutos
MARGEN = 45  # minutos de margen

def hora_espana_minutos():
    import subprocess
    result = subprocess.run(
        ['date', '-d', 'TZ="Europe/Madrid"', '+%H:%M'],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        # Fallback: usar TZ env
        import os
        os.environ['TZ'] = 'Europe/Madrid'
        time.tzset()
        now = datetime.now()
        return now.hour * 60 + now.minute
    parts = result.stdout.strip().split(':')
    return int(parts[0]) * 60 + int(parts[1])

def es_hora_correcta():
    try:
        import os
        os.environ['TZ'] = 'Europe/Madrid'
        time.tzset()
        now = datetime.now()
        minutos = now.hour * 60 + now.minute
        hora_obj = HORA_ENTRADA if ACTION == "entrada" else HORA_SALIDA
        diferencia = abs(minutos - hora_obj)
        print(f"Hora Espana: {now.strftime('%H:%M')} | Objetivo: {hora_obj//60:02d}:{hora_obj%60:02d} | Diferencia: {diferencia} min")
        if diferencia > MARGEN:
            print(f"FUERA DE MARGEN ({diferencia} min > {MARGEN} min) - NO FICHAR")
            return False
        return True
    except Exception as e:
        print(f"Error verificando hora: {e} - fichando igualmente")
        return True

def es_dia_libre():
    import os
    hoy = datetime.now().strftime("%d/%m/%Y")
    try:
        with open(os.path.expanduser("~/festivos.txt"), "r") as f:
            for linea in f:
                linea = linea.strip()
                if linea and not linea.startswith("#"):
                    if linea == hoy:
                        return True
    except:
        pass
    return False

def fichar():
    import os
    os.environ['TZ'] = 'Europe/Madrid'
    time.tzset()
    hoy = datetime.now().strftime("%d/%m/%Y")
    print(f"Fecha: {hoy} | Accion: {ACTION}")

    if es_dia_libre():
        print("DIA LIBRE - no se ficha")
        sys.exit(0)

    if not es_hora_correcta():
        sys.exit(0)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, wait_until="domcontentloaded")
        time.sleep(2)
        page.wait_for_selector("#email", timeout=10000)
        page.fill("#email", USER)
        page.fill("#password", PASS)
        page.click("#btn-login")
        time.sleep(4)
        page.wait_for_selector("span.hidden-xs", timeout=15000)
        nombre = page.locator("span.hidden-xs").first.inner_text()
        print(f"Usuario: {nombre}")
        if "JESUS" not in nombre.upper():
            print("ERROR: Login fallido")
            sys.exit(1)
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
        btn_entrada = page.locator("button.btn-controlHorarioMiniAcceso.btn-success")
        btn_salida = page.locator("button.btn-controlHorarioMiniAcceso.btn-danger")
        tiene_entrada = btn_entrada.count() > 0
        tiene_salida = btn_salida.count() > 0
        print(f"Boton entrada: {tiene_entrada} | Boton salida: {tiene_salida}")
        if ACTION == "entrada" and tiene_entrada:
            btn_entrada.click()
            print("FICHADO OK: ENTRADA")
        elif ACTION == "salida" and tiene_salida:
            btn_salida.click()
            print("FICHADO OK: SALIDA")
        else:
            print("AVISO: Boton no visible - ya fichado o jornada completa")
        time.sleep(2)
        browser.close()

if __name__ == "__main__":
    fichar()
