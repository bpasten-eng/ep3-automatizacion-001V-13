#!/usr/bin/env python3
import sys, os, socket, yaml
from datetime import datetime
from ncclient import manager
from lxml import etree

VARS_PATH = os.path.join(os.path.dirname(__file__), "../vars/vars_001V-13.yaml")
with open(VARS_PATH, "r") as f:
    vars_data = yaml.safe_load(f)

alumno  = vars_data["alumno"]
router  = vars_data["router"]

print("=" * 60)
print("Script  : validacion_netconf.py")
print(f"Alumno  : {alumno['codigo']} - {alumno['nombre']}")
print(f"Fecha   : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"VM Host : {socket.gethostname()}")
print("=" * 60)

FILTRO = """
<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
    <hostname/>
    <ntp>
      <server xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-ntp">
        <server-list/>
      </server>
    </ntp>
    <interface>
      <GigabitEthernet>
        <name>1</name>
        <description/>
      </GigabitEthernet>
      <Loopback>
        <name/>
        <ip><address><primary/></address></ip>
      </Loopback>
    </interface>
  </native>
</filter>
"""

print(f"\nConectando a {router['ip']}:830 via NETCONF...")

with manager.connect(
    host=router["ip"], port=830,
    username=router["usuario"], password=router["password"],
    hostkey_verify=False, allow_agent=False, look_for_keys=False, timeout=30
) as m:
    print(f"Sesion ID: {m.session_id}\n")
    reply = m.get_config(source="running", filter=FILTRO)
    xml_raw = reply.xml

    os.makedirs("evidencias", exist_ok=True)
    root = etree.fromstring(xml_raw.encode("utf-8"))
    with open("evidencias/rpc_reply_raw.xml", "w") as f:
        f.write(etree.tostring(root, pretty_print=True, encoding="unicode"))
    print("XML guardado en evidencias/rpc_reply_raw.xml\n")

    NS = {
        "ios": "http://cisco.com/ns/yang/Cisco-IOS-XE-native",
        "ntp": "http://cisco.com/ns/yang/Cisco-IOS-XE-ntp",
    }

    hostname_el = root.find(".//ios:hostname", NS)
    hostname_actual = hostname_el.text.strip() if hostname_el is not None else "NO_ENCONTRADO"

    loopback_ip_actual = loopback_mask_actual = "NO_ENCONTRADO"
    for lo in root.findall(".//ios:Loopback", NS):
        name_el = lo.find("ios:name", NS)
        if name_el is not None and name_el.text.strip() == str(router["loopback_id"]):
            primary = lo.find(".//ios:primary", NS)
            if primary is not None:
                a = primary.find("ios:address", NS)
                m2 = primary.find("ios:mask", NS)
                if a is not None: loopback_ip_actual = a.text.strip()
                if m2 is not None: loopback_mask_actual = m2.text.strip()

    desc_wan_actual = "NO_ENCONTRADO"
    for gig in root.findall(".//ios:GigabitEthernet", NS):
        name_el = gig.find("ios:name", NS)
        if name_el is not None and name_el.text.strip() == "1":
            d = gig.find("ios:description", NS)
            if d is not None: desc_wan_actual = d.text.strip()

    ntp_actual = "NO_ENCONTRADO"
    ntp_servers = root.findall(".//ntp:server-list", NS)
    if ntp_servers:
        ip_el = ntp_servers[0].find("ntp:ip-address", NS)
        if ip_el is not None: ntp_actual = ip_el.text.strip()

    print("=" * 60)
    print("REPORTE DE VALIDACION NETCONF")
    print("=" * 60)

    criterios = [
        ("Hostname corporativo",    router["hostname"],      hostname_actual),
        ("IP Loopback10",           router["loopback_ip"],   loopback_ip_actual),
        ("Mascara Loopback10",      router["loopback_mask"], loopback_mask_actual),
        ("Descripcion WAN",         router["descripcion_wan"], desc_wan_actual),
        ("Servidor NTP",            router["ntp_server"],    ntp_actual),
    ]

    ok_count = 0
    for nombre, esperado, actual in criterios:
        status = "[OK]  " if actual == esperado else "[FAIL]"
        if actual == esperado: ok_count += 1
        print(f"  {status} {nombre}")
        print(f"         Esperado : {esperado}")
        print(f"         Actual   : {actual}\n")

    print("-" * 60)
    print(f"Resultado: {ok_count}/5 criterios conformes")
    print()
    if ok_count == 5:
        print(">>> ESTADO NETCONF: CONFORME <<<")
    else:
        print(">>> ESTADO NETCONF: NO CONFORME <<<")
    print("=" * 60)
