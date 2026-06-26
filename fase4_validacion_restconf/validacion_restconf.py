#!/usr/bin/env python3
import sys, os, json, socket, yaml, requests, urllib3
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

VARS_PATH = os.path.join(os.path.dirname(__file__), "../vars/vars_001V-13.yaml")
with open(VARS_PATH, "r") as f:
    vars_data = yaml.safe_load(f)

alumno  = vars_data["alumno"]
router  = vars_data["router"]

BASE_URL = f"https://{router['ip']}/restconf/data"
AUTH     = (router["usuario"], router["password"])
HEADERS  = {"Accept": "application/yang-data+json"}
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "evidencias", "responses")
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 60)
print("Script  : validacion_restconf.py")
print(f"Alumno  : {alumno['codigo']} - {alumno['nombre']}")
print(f"Fecha   : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"VM Host : {socket.gethostname()}")
print("=" * 60)

def consultar(endpoint, archivo):
    url = f"{BASE_URL}/{endpoint}"
    print(f"Consultando: {url}")
    try:
        r = requests.get(url, auth=AUTH, headers=HEADERS, verify=False, timeout=15)
        r.raise_for_status()
        data = r.json()
        with open(os.path.join(OUTPUT_DIR, archivo), "w") as f:
            json.dump(data, f, indent=2)
        return data
    except Exception as e:
        print(f"  ERROR: {e}")
        return None

data_hostname   = consultar("Cisco-IOS-XE-native:native/hostname", "get_hostname.json")
data_loopback   = consultar(f"ietf-interfaces:interfaces/interface=Loopback{router['loopback_id']}", "get_loopback.json")
data_interfaces = consultar("ietf-interfaces:interfaces/interface=GigabitEthernet1", "get_interfaces.json")
data_ntp        = consultar("Cisco-IOS-XE-native:native/ntp", "get_ntp.json")

hostname_actual = "NO_ENCONTRADO"
if data_hostname:
    hostname_actual = data_hostname.get("Cisco-IOS-XE-native:hostname", "NO_ENCONTRADO")

loopback_ip_actual = "NO_ENCONTRADO"
if data_loopback:
    iface = data_loopback.get("ietf-interfaces:interface", {})
    addrs = iface.get("ietf-ip:ipv4", {}).get("address", [])
    if addrs: loopback_ip_actual = addrs[0].get("ip", "NO_ENCONTRADO")

desc_wan_actual = "NO_ENCONTRADO"
if data_interfaces:
    iface = data_interfaces.get("ietf-interfaces:interface", {})
    desc_wan_actual = iface.get("description", "NO_ENCONTRADO")

ntp_actual = "NO_ENCONTRADO"
if data_ntp:
    ntp_block = data_ntp.get("Cisco-IOS-XE-native:ntp", {})
    server_list = ntp_block.get("Cisco-IOS-XE-ntp:server", {}).get("server-list", [])
    if server_list: ntp_actual = server_list[0].get("ip-address", "NO_ENCONTRADO")

print("\n" + "=" * 60)
print("REPORTE DE VALIDACION RESTCONF")
print("=" * 60)

criterios = [
    ("Hostname corporativo",  router["hostname"],       hostname_actual),
    (f"IP Loopback{router['loopback_id']}", router["loopback_ip"], loopback_ip_actual),
    ("Descripcion WAN",       router["descripcion_wan"], desc_wan_actual),
    ("Servidor NTP",          router["ntp_server"],     ntp_actual),
]

ok_count = 0
for nombre, esperado, actual in criterios:
    status = "[OK]  " if actual == esperado else "[FAIL]"
    if actual == esperado: ok_count += 1
    print(f"  {status} {nombre}")
    print(f"         Esperado : {esperado}")
    print(f"         Actual   : {actual}\n")

print("-" * 60)
print(f"Resultado: {ok_count}/4 criterios conformes")
print()
if ok_count == 4:
    print(">>> ESTADO RESTCONF: CONFORME <<<")
else:
    print(">>> ESTADO RESTCONF: NO CONFORME <<<")
print("=" * 60)
