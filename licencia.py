import uuid
import hashlib

def obtener_device_id():
    node = uuid.getnode()
    return hashlib.md5(str(node).encode()).hexdigest()[:8].upper()

def generar_clave_activacion(device_id):
    secreto = "AGENDA_PRO_2026"
    cadena = f"{device_id.strip().upper()}_{secreto}"
    return hashlib.sha256(cadena.encode()).hexdigest()[:12].upper()

def validar_licencia(licencia_ingresada):
    if not licencia_ingresada:
        return False
    dev_id = obtener_device_id()
    clave_correcta = generar_clave_activacion(dev_id)
    return licencia_ingresada.strip().upper() == clave_correcta