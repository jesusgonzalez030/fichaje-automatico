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
    print("Accion: " + ACTION)

    if es_dia_libre():
        print("HOY ES DIA LIBRE - No se ficha")
        sys.exit(0)

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    })

    # Paso 1: GET pagina login para obtener cookies CSRF iniciales
    print("Cargando pagina login...")
    r0 = session.get(BASE + "/login", allow_redirects=True)
    print("Login page status: " + str(r0.status_code) + " | cookies: " + str(list(session.cookies.keys())))

    # Paso 2: Login con allow_redirects=True para seguir la sesion
    login_url = BASE + "/login/in?" + urlencode({"user": USER, "pass": PASS, "option": "in"})
    print("Haciendo login...")
    r1 = session.get(login_url, allow_redirects=True)
    print("Login status: " + str(r1.status_code) + " | url final: " + r1.url)
    print("Cookies tras login: " + str(dict(session.cookies)))

    # Paso 3: GET al dashboard para consolidar sesion
    print("Consolidando sesion...")
    r2 = session.get(BASE + "/login", allow_redirects=True)
    print("Dashboard status: " + str(r2.status_code))
    print("Cookies consolidadas: " + str(dict(session.cookies)))

    # Verificar que tenemos sesion valida buscando el ID de usuario en la respuesta
    if "JESUS" not in r2.text and "jesus" not in r2.text.lower():
        print("ADVERTENCIA: No se detecta sesion de usuario en la pagina")

    # Paso 4: Fichar
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
    r3 = session.get(fichar_url, headers={"Referer": BASE + "/login"}, allow_redirects=True)
    print("Fichaje status: " + str(r3.status_code))

    try:
        data = r3.json()
        idproc = data.get("recordset", {}).get("idproc", "desconocido")
        id_user = data.get("Params", {}).get("params", {}).get("IDUser", -1)
        errores = data.get("recordset", {}).get("errores", [])
        result = data.get("recordset", {}).get("result", [])
        print("IDUser en respuesta: " + str(id_user))
        print("Tipo fichaje: " + str(idproc))
        print("Errores: " + str(errores))
        print("Resultado: " + str(result))

        if int(id_user) == -1:
            print("ERROR CRITICO: Sesion no establecida (IDUser=-1) - el fichaje NO se ha registrado")
            sys.exit(1)
        if errores:
            print("ERROR en fichaje: " + str(errores))
            sys.exit(1)
        print("FICHADO OK: " + str(idproc).upper())
    except Exception as e:
        print("Error parseando respuesta: " + str(e))
        print("Respuesta raw: " + r3.text[:300])
        sys.exit(1)

if __name__ == "__main__":
    fichar()
