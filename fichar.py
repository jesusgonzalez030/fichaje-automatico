import os, sys, requests
from urllib.parse import urlencode
from datetime import datetime

BASE = "https://electraferre.kubysoft.com"
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
    print("Fecha hoy: " + hoy)

    if es_dia_libre():
        print("HOY ES DIA LIBRE - No se ficha (" + hoy + ")")
        sys.exit(0)

    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"})

    # Login
    login_url = BASE + "/login/in?" + urlencode({"user": USER, "pass": PASS, "option": "in"})
    print("Haciendo login...")
    r = session.get(login_url)
    print("Login status: " + str(r.status_code))
    if r.status_code != 200:
        print("ERROR login")
        sys.exit(1)

    # Cargar sesion
    session.get(BASE + "/login")

    # Fichar
    fichar_url = (
        BASE +
        "/node/kudaby/nodeFN/fn"
        "?fnID=registroEntradaSalidaControlHorario"
        "&params%5Bmpersonal%5D=0"
        "&params%5Bempresa%5D=1"
        "&params%5Bcentro%5D="
        "&params%5Bcoord%5D%5Blat%5D="
        "&params%5Bcoord%5D%5Blng%5D="
        "&params%5Boperari%5D=11"
        "&DBtoken=ELECT202502ERRE"
        "&xmlConf=Control.Horarios.Schema"
    )
    print("Fichando " + ACTION + "...")
    r3 = session.get(fichar_url, headers={"Referer": BASE + "/login"})
    print("Fichaje status: " + str(r3.status_code))
    print("Respuesta: " + r3.text[:300])

    if r3.status_code == 200:
        print("FICHADO OK: " + ACTION.upper())
    else:
        print("ERROR fichaje")
        sys.exit(1)

if __name__ == "__main__":
    fichar()
