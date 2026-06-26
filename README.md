# EP3 — Implementación de Automatización de Red con Compliance Auditado

**Alumno:** Pasten Poblete Bastian Jose  
**Código:** 001V-13  
**Asignatura:** DRY7122 — Programación y Redes Virtualizadas  
**Empresa cliente:** Almacenes Generales SA  

---

## 1. Objetivo del Proyecto

Se implementó un ciclo completo de automatización de red para incorporar un router Cisco CSR1000v a la red corporativa de Almacenes Generales SA. El objetivo fue aplicar la configuración estándar de la empresa de forma automatizada y verificar su correcta aplicación mediante herramientas de gestión programática.

---

## 2. Alcance

Se configuró hostname, banner, NTP, interfaz WAN, Loopback de gestión, NETCONF y RESTCONF. No se configuraron protocolos de enrutamiento dinámico ni hardening avanzado. Las herramientas utilizadas fueron pyATS/Genie, Ansible, ncclient y requests.

---

## 3. Infraestructura Utilizada

| Componente | Descripción |
|---|---|
| DEVASC VM (labvm) | Estación de trabajo del ingeniero |
| CSR1kv | Router Cisco IOS XE — IP 192.168.56.101 |
| VirtualBox | Hipervisor con red Host-Only 192.168.56.0/24 |
| GitHub | Repositorio de auditoría ep3-automatizacion-001V-13 |

---

## 4. Tecnologías Empleadas y Justificación

- **pyATS/Genie:** Captura de estado del router vía SSH antes y después de los cambios, permite comparar diferencias objetivamente.
- **Ansible:** Aprovisionamiento idempotente y declarativo, separa datos de lógica mediante vars_files.
- **NETCONF:** Validación independiente vía puerto 830, retorna configuración completa en XML estructurado.
- **RESTCONF:** Validación complementaria vía HTTP/JSON, permite consultar recursos específicos por URL.

---

## 5. Configuración Aplicada

| Parámetro | Valor |
|---|---|
| Hostname | RTR-ALMAGEN |
| Banner | ACCESO RESTRINGIDO - ALMAGEN |
| NTP Server | 1.1.1.1 |
| Descripción GigabitEthernet1 | Enlace-WAN-Copiapo |
| Loopback10 IP | 10.1.13.1 / 255.255.255.0 |
| NETCONF | Habilitado — Puerto 830 |
| RESTCONF | Habilitado — Puerto 443 |

---

## 6. Resultados de Validación

| Criterio | NETCONF | RESTCONF |
|---|---|---|
| Hostname corporativo | ✅ CONFORME | ✅ CONFORME |
| IP Loopback10 | ✅ CONFORME | ✅ CONFORME |
| Máscara Loopback10 | ✅ CONFORME | — |
| Descripción WAN | ✅ CONFORME | ✅ CONFORME |
| Servidor NTP | ✅

