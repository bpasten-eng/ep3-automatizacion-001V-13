#!/usr/bin/env python3
import os, socket, yaml
from datetime import datetime

VARS_PATH = os.path.join(os.path.dirname(__file__), "../vars/vars_001V-13.yaml")
with open(VARS_PATH, "r") as f:
    vars_data = yaml.safe_load(f)

alumno  = vars_data["alumno"]
router  = vars_data["router"]

def leer(path):
    try:
        return open(path).read()
    except:
        return None

def check_netconf():
    c = leer("../fase3_validacion_netconf/evidencias/output_validacion_netconf.txt")
    if c and "ESTADO NETCONF: CONFORME" in c:
        return True, f"{c.count('[OK]')}/5 criterios OK"
    return False, "NO CONFORME"

def check_restconf():
    c = leer("../fase4_validacion_restconf/evidencias/output_validacion_restconf.txt")
    if c and "ESTADO RESTCONF: CONFORME" in c:
        return True, f"{c.count('[OK]')}/4 criterios OK"
    return False, "NO CONFORME"

def check_diff():
    d = "evidencias/diff_001V-13"
    if not os.path.exists(d): return False, "Sin diff"
    archivos = os.listdir(d)
    return (True, f"{len(archivos)} archivos con diferencias") if archivos else (False, "Vacio")

netconf_ok,  nd = check_netconf()
restconf_ok, rd = check_restconf()
diff_ok,     dd = check_diff()

resultado = "CONFORME" if (netconf_ok and restconf_ok) else "NO CONFORME"
fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

cert = f"""
╔══════════════════════════════════════════════════════════════╗
║        CERTIFICADO DE COMPLIANCE DE RED — EP3               ║
║        DRY7122 Programacion y Redes Virtualizadas            ║
╚══════════════════════════════════════════════════════════════╝

ALUMNO        : {alumno['nombre']}
CODIGO        : {alumno['codigo']}
FECHA         : {fecha}
VM            : {socket.gethostname()}

CLIENTE       : Almacenes Generales SA
HOSTNAME      : {router['hostname']}
IP ROUTER     : {router['ip']}
IP LOOPBACK   : {router['loopback_ip']}/{router['loopback_prefix']}

VALIDACIONES
─────────────────────────────────────────────
  NETCONF  : {"✔ CONFORME" if netconf_ok  else "✘ NO CONFORME"}  → {nd}
  RESTCONF : {"✔ CONFORME" if restconf_ok else "✘ NO CONFORME"}  → {rd}
  DIFF     : {"✔ OK"       if diff_ok     else "✘ SIN DIFF"}     → {dd}

RESULTADO GLOBAL
─────────────────────────────────────────────
  >>> COMPLIANCE: {resultado} <

{"Equipo listo para operar en red corporativa." if resultado == "CONFORME" else "Revisar configuracion."}

Firma: {alumno['nombre']} | {alumno['codigo']}
═══════════════════════════════════════════════════════════════
"""

print(cert)
os.makedirs("evidencias", exist_ok=True)
with open(f"evidencias/certificado_compliance_{alumno['codigo']}.txt", "w") as f:
    f.write(cert)
print(f"Certificado guardado.")
